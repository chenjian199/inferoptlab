"""Generate the C500 NoPE sparse-prefill repair from the pinned source archive."""
import hashlib
import json
from pathlib import Path
import tarfile
import sys

ROOT=Path(sys.argv[1]).resolve()
archive=ROOT/'FlashMLA.tar.gz'
receipt=json.loads((ROOT/'source.json').read_text())
assert hashlib.sha256(archive.read_bytes()).hexdigest()==receipt['archive_sha256']
work=ROOT/'build-source'
work.mkdir(exist_ok=False)
with tarfile.open(archive) as tar:
    for item in tar:
        parts=Path(item.name).parts[1:]
        if not parts:
            continue
        target=work.joinpath(*parts).resolve()
        assert target.is_relative_to(work.resolve()) and not item.issym() and not item.islnk()
        if item.isdir():
            target.mkdir(parents=True,exist_ok=True)
        elif item.isfile():
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(tar.extractfile(item).read())

utils=work/'csrc/utils/utils.h'
s=utils.read_text()
old='const int64_t global_kv_sparse_offset = topk_sparse_idx * row_stride + col_offset;'
assert s.count(old)==1
s=s.replace(old,'const int64_t global_kv_sparse_offset = int64_t(topk_sparse_idx) * int64_t(row_stride) + col_offset;')
utils.write_text(s)

# This public revision has a 576/512 RoPE path. GLM5Next uses NoPE 512/512:
# use the existing 512-wide NoPE fragment directly, without a zero-width tile.
traits=work/'csrc/flash_kernel/kernel_traits.h'
s=traits.read_text().replace('Shape<Int<kBlockM>, Int<kHeadDim - kHeadDimV>>{}',
                            'Shape<Int<kBlockM>, Int<(kHeadDim > kHeadDimV ? kHeadDim-kHeadDimV : 64)>>{}')
traits.write_text(s)
kernel=work/'csrc/flash_kernel/xcore1000/sparse_prefill_kernel_64x16_8waves_xcore1000.h'
s=kernel.read_text()
start=s.index('    Tensor gRopeQ =')
end=s.index('    Tensor gK =',start)
s=s[:start]+s[end:]
for text in [
    '    Tensor sRopeQ = make_tensor(make_smem_ptr(reinterpret_cast<Element *>(smem_)),\n                            typename Kernel_traits::SmemLayoutRopeQ{});\n',
    '    Tensor tRopeQgRopeQ = gmem_thr_copy_Q.partition_S(gRopeQ);\n',
    '    Tensor tRopeQsRopeQ = gmem_thr_copy_Q.partition_D(sRopeQ);\n',
    '    Tensor tSrRopeQ  = thr_mma_s.partition_fragment_A(sRopeQ);                           // (MMA,MMA_M,MMA_K)\n',
    '    auto tSsRopeQ = smem_thr_copy_Q.partition_S(sRopeQ);\n',
    '    Tensor tSsRopeQ = smem_thr_copy_Q.partition_S(sRopeQ);\n',
    '    Tensor tRopeQrRopeQ = make_fragment_like(tRopeQgRopeQ);\n',
    '    flash::copy_b128</*Is_even_MN*/ true, true>(tRopeQgRopeQ, tRopeQrRopeQ, tQcQ, params.d_qk, params.h_q - q_block_idx);\n',
]:
    s=s.replace(text,'')
start=s.index('    cute::copy(tRopeQrRopeQ, tRopeQsRopeQ);')
end=s.index('    int n_block =',start)
s=s[:start]+'    cute::copy(tSrNopeQ, tSrQ);\n\n'+s[end:]
assert 'sRopeQ' not in s and 'gRopeQ' not in s
kernel.write_text(s)

api=(work/'csrc/flash_api/flash_api.cpp').read_text()
header=api[:api.index('// Note: should match the kernel dispatch tile size')]
header=header.replace('#include "run_mla.h"','')
body=api[api.index('std::vector<at::Tensor> sparse_prefill_fwd('):api.index('std::vector<at::Tensor>\nget_mla_decoding_metadata(')]
body=body.replace('run_mla_fwd(params);','launch_offset64(params);')
body=body.replace('    auto dprops = flash::mcGetCurrentDeviceProperties();',
                  '    TORCH_CHECK(q.size(2)==512 && d_v==512 && kv.size(1)==1);\n    auto dprops = flash::mcGetCurrentDeviceProperties();')
body=body.replace('    int arch = dprops.major * 100 + dprops.minor;',
                  '    int arch = dprops.major * 100 + dprops.minor;\n    TORCH_CHECK(arch == 1000, "offset64 prototype is C500 only");')
(work/'offset64_api.cpp').write_text(header+'\nvoid launch_offset64(SparsePrefillParams&);\n'+body+
    '\nPYBIND11_MODULE(TORCH_EXTENSION_NAME, m) { m.def("prefill", &sparse_prefill_fwd); }\n')
(work/'offset64_xcore1000.cu').write_text('''#include "flash_mla.h"
#include "xcore1000/sparse_prefill_kernel_64x16_8waves_xcore1000.h"
using Traits = Flash_fwd_kernel_traits<512,64,16,8,true,true,mctlass::bfloat16_t,true,512,2>;
__global__ void offset64_prefill(SparsePrefillParams params) {
    flash::sparse_attn_fwd_kernel<Traits,false,true>(params);
}
void launch_offset64(SparsePrefillParams &params) {
    const int smem = std::min(Traits::kSmemSize, 64*1024);
    CUDA_CHECK(cudaFuncSetAttribute(offset64_prefill,cudaFuncAttributeMaxDynamicSharedMemorySize,smem));
    offset64_prefill<<<dim3(params.h_q/64*params.s_q,1,1),Traits::kNThreads,smem,params.stream>>>(params);
    CUDA_KERNEL_LAUNCH_CHECK();
}
''')
setup=(work/'setup.py').read_text()
prefix=setup[:setup.index('# ninja build does not work unless include_dirs are abs path')]
(work/'setup_offset64.py').write_text(prefix+'''
root=Path(__file__).resolve().parent
os.environ['CUCC_TARGETS']='xcore1000'
setup(name='inferoptlab-flashmla-offset64',version='0.0.1',packages=[],ext_modules=[CUDAExtension(
    name='_inferoptlab_flashmla_offset64',sources=['offset64_api.cpp','offset64_xcore1000.cu'],
    include_dirs=[str(root/'csrc'/p) for p in ['flash_api','flash_dispatch','flash_kernel','flash_kernel/feature','flash_run','utils','mctlass/include']],
    extra_compile_args={'cxx':['-O3','-std=c++17'], 'nvcc':['-O3','-std=c++17','--expt-relaxed-constexpr','--expt-extended-lambda','--use_fast_math','-fno-strict-aliasing','-mllvm','-enable-tbaa=false','-D__FAST_HALF_CVT__']},
)],cmdclass={'build_ext':BuildExtension})
''')
(ROOT/'prepared.json').write_text(json.dumps(dict(source=receipt,scope='experimental C500 BF16 NoPE 512/512 prefill only',
    files={str(p.relative_to(work)):hashlib.sha256(p.read_bytes()).hexdigest() for p in work.glob('offset64*')}),indent=2))
