"""Correctness-first symmetric INT8 GEMM prototype for one dense GLM layer.

Quantization is deliberately outside this operator. No MoE, AZP or packed layout.
"""
import torch
import triton as tr
import triton.language as tl


@tr.jit
def _gemm(A,B,SA,SB,Y,C,M:tl.constexpr,N:tl.constexpr,K:tl.constexpr,
          AS0:tl.constexpr,AS1:tl.constexpr,BS0:tl.constexpr,BS1:tl.constexpr,
          PER_ROW:tl.constexpr,PER_COL:tl.constexpr,
          BM:tl.constexpr=16,BN:tl.constexpr=64,BK:tl.constexpr=64):
    rows=tl.program_id(0)*BM+tl.arange(0,BM)
    cols=tl.program_id(1)*BN+tl.arange(0,BN)
    kk=tl.arange(0,BK)
    acc=tl.zeros((BM,BN),tl.int32)
    for start in range(tr.cdiv(K,BK)):
        k=start*BK+kk
        a=tl.load(A+rows[:,None]*AS0+k[None,:]*AS1,(rows[:,None]<M)&(k[None,:]<K),0)
        b=tl.load(B+k[:,None]*BS0+cols[None,:]*BS1,(k[:,None]<K)&(cols[None,:]<N),0)
        acc=tl.dot(a,b,acc)
    sa=tl.load(SA+tl.where(PER_ROW,rows,0),rows<M,0)
    sb=tl.load(SB+tl.where(PER_COL,cols,0),cols<N,0)
    out=(acc.to(tl.float32)*sa[:,None])*sb[None,:]
    mask=(rows[:,None]<M)&(cols[None,:]<N)
    tl.store(Y+rows[:,None]*N+cols[None,:],out,mask)
    tl.store(C+rows[:,None]*N+cols[None,:],acc,mask)


def supported(a,b,sa,sb,out_dtype,bias=None):
    return (a.ndim==b.ndim==2 and a.dtype==b.dtype==torch.int8 and a.is_cuda and b.is_cuda
        and a.device==b.device==sa.device==sb.device and a.shape[1]==b.shape[0]
        and all(v>0 for v in (*a.shape,*b.shape)) and a.shape[1]<=131071
        and all(v>0 for v in (*a.stride(),*b.stride()))
        and sa.dtype==sb.dtype==torch.float32 and sa.is_contiguous() and sb.is_contiguous()
        and sa.numel() in [1,a.shape[0]] and sb.numel() in [1,b.shape[1]]
        and out_dtype==torch.bfloat16 and bias is None)


def gemm(a,b,sa,sb,out_dtype=torch.bfloat16,bias=None):
    if not supported(a,b,sa,sb,out_dtype,bias):
        raise ValueError('Outside frozen INT8 GEMM contract')
    m,k=a.shape;n=b.shape[1]
    y=torch.empty((m,n),device=a.device,dtype=out_dtype)
    c=torch.empty((m,n),device=a.device,dtype=torch.int32)
    _gemm[(tr.cdiv(m,16),tr.cdiv(n,64))](a,b,sa,sb,y,c,m,n,k,*a.stride(),*b.stride(),
        sa.numel()!=1,sb.numel()!=1,num_warps=4,num_stages=2,enable_fp_fusion=False)
    return y,c


def difference(a,b):
    """One BF16 ulp at the larger magnitude, including subnormal floor."""
    x=a.float();y=b.float();mag=torch.maximum(x.abs(),y.abs())
    ulp=torch.pow(2.0,torch.floor(torch.log2(mag.clamp_min(2.0**-126)))-7)
    delta=(x-y).abs()
    return {'finite':bool(torch.isfinite(x).all() and torch.isfinite(y).all()),
        'exact':bool(torch.equal(a,b)),'max_abs':float(delta.max()),
        'max_bf16_ulp':float((delta/ulp).max()),'changed':int((a!=b).sum()),'elements':a.numel()}
