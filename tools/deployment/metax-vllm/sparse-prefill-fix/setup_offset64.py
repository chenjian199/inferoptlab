# Copyright (c) 2023, Tri Dao.

import sys
import warnings
import os
import re
import ast
from pathlib import Path
from packaging.version import parse, Version
import platform

from setuptools import setup, find_packages
import subprocess

import urllib.request
import urllib.error
from wheel.bdist_wheel import bdist_wheel as _bdist_wheel

from typing import Optional, Union

import torch
from torch.utils.cpp_extension import (
    BuildExtension,
    CppExtension,
    CUDAExtension,
    CUDA_HOME,
)

# HACK: we monkey patch pytorch's _write_ninja_file to pass
# "--offload-arch=xcore1000" to files ending in '_xcore1000.cu',
# "--offload-arch=xcore1500" to files ending in '_xcore1500.cu'
from torch.utils.cpp_extension import (
    IS_HIP_EXTENSION,
    COMMON_HIP_FLAGS,
    SUBPROCESS_DECODE_ARGS,
    IS_WINDOWS,
    get_cxx_compiler,
    _join_rocm_home,
    _join_cuda_home,
    _is_cuda_file,
    _maybe_write,
)
def _write_ninja_file(path,
                      cflags,
                      post_cflags,
                      cuda_cflags,
                      cuda_post_cflags,
                      cuda_dlink_post_cflags,
                      sources,
                      objects,
                      ldflags,
                      library_target,
                      with_cuda,
                      **kwargs,  # kwargs (ignored) to absorb new flags in torch.utils.cpp_extension
                      ) -> None:
    r"""Write a ninja file that does the desired compiling and linking.

    `path`: Where to write this file
    `cflags`: list of flags to pass to $cxx. Can be None.
    `post_cflags`: list of flags to append to the $cxx invocation. Can be None.
    `cuda_cflags`: list of flags to pass to $nvcc. Can be None.
    `cuda_postflags`: list of flags to append to the $nvcc invocation. Can be None.
    `sources`: list of paths to source files
    `objects`: list of desired paths to objects, one per source.
    `ldflags`: list of flags to pass to linker. Can be None.
    `library_target`: Name of the output library. Can be None; in that case,
                      we do no linking.
    `with_cuda`: If we should be compiling with CUDA.
    """
    def sanitize_flags(flags):
        if flags is None:
            return []
        else:
            return [flag.strip() for flag in flags]

    cflags = sanitize_flags(cflags)
    post_cflags = sanitize_flags(post_cflags)
    cuda_cflags = sanitize_flags(cuda_cflags)
    cuda_post_cflags = sanitize_flags(cuda_post_cflags)
    cuda_dlink_post_cflags = sanitize_flags(cuda_dlink_post_cflags)
    ldflags = sanitize_flags(ldflags)

    # Sanity checks...
    assert len(sources) == len(objects)
    assert len(sources) > 0

    compiler = get_cxx_compiler()

    # Version 1.3 is required for the `deps` directive.
    config = ['ninja_required_version = 1.3']
    config.append(f'cxx = {compiler}')
    if with_cuda or cuda_dlink_post_cflags:
        if "PYTORCH_NVCC" in os.environ:
            nvcc = os.getenv("PYTORCH_NVCC")    # user can set nvcc compiler with ccache using the environment variable here
        else:
            if IS_HIP_EXTENSION:
                nvcc = _join_rocm_home('bin', 'hipcc')
            else:
                nvcc = _join_cuda_home('bin', 'nvcc')
        config.append(f'nvcc = {nvcc}')

    if IS_HIP_EXTENSION:
        post_cflags = COMMON_HIP_FLAGS + post_cflags
    flags = [f'cflags = {" ".join(cflags)}']
    flags.append(f'post_cflags = {" ".join(post_cflags)}')
    if with_cuda:
        flags.append(f'cuda_cflags = {" ".join(cuda_cflags)}')
        flags.append(f'cuda_post_cflags = {" ".join(cuda_post_cflags)}')
        maca_post_cflags_xcore1000 = cuda_post_cflags + ['--offload-arch=xcore1000']
        flags.append(f'maca_post_cflags_xcore1000 = {" ".join(maca_post_cflags_xcore1000)}')
        maca_post_cflags_xcore1500 = cuda_post_cflags + ['--offload-arch=xcore1500']
        flags.append(f'maca_post_cflags_xcore1500 = {" ".join(maca_post_cflags_xcore1500)}')
    flags.append(f'cuda_dlink_post_cflags = {" ".join(cuda_dlink_post_cflags)}')
    flags.append(f'ldflags = {" ".join(ldflags)}')

    # Turn into absolute paths so we can emit them into the ninja build
    # file wherever it is.
    sources = [os.path.abspath(file) for file in sources]

    # See https://ninja-build.org/build.ninja.html for reference.
    compile_rule = ['rule compile']
    if IS_WINDOWS:
        compile_rule.append(
            '  command = cl /showIncludes $cflags -c $in /Fo$out $post_cflags')
        compile_rule.append('  deps = msvc')
    else:
        compile_rule.append(
            '  command = $cxx -MMD -MF $out.d $cflags -c $in -o $out $post_cflags')
        compile_rule.append('  depfile = $out.d')
        compile_rule.append('  deps = gcc')

    if with_cuda:
        cuda_compile_rule = ['rule cuda_compile']
        nvcc_gendeps = ''
        # --generate-dependencies-with-compile is not supported by ROCm
        # Nvcc flag `--generate-dependencies-with-compile` is not supported by sccache, which may increase build time.
        if torch.version.cuda is not None and os.getenv('TORCH_EXTENSION_SKIP_NVCC_GEN_DEPENDENCIES', '0') != '1':
            cuda_compile_rule.append('  depfile = $out.d')
            cuda_compile_rule.append('  deps = gcc')
            # Note: non-system deps with nvcc are only supported
            # on Linux so use --generate-dependencies-with-compile
            # to make this work on Windows too.
            nvcc_gendeps = '--generate-dependencies-with-compile --dependency-output $out.d'
        maca_compile_rule_xcore1000 = ['rule maca_compile_xcore1000'] + cuda_compile_rule[1:] + [
            f'  command = $nvcc {nvcc_gendeps} $cuda_cflags -c $in -o $out $maca_post_cflags_xcore1000'
        ]
        maca_compile_rule_xcore1500 = ['rule maca_compile_xcore1500'] + cuda_compile_rule[1:] + [
            f'  command = $nvcc {nvcc_gendeps} $cuda_cflags -c $in -o $out $maca_post_cflags_xcore1500'
        ]
        cuda_compile_rule.append(
            f'  command = $nvcc {nvcc_gendeps} $cuda_cflags -c $in -o $out $cuda_post_cflags')

    # Emit one build rule per source to enable incremental build.
    build = []
    for source_file, object_file in zip(sources, objects):
        is_cuda_source = _is_cuda_file(source_file) and with_cuda
        rule = 'cuda_compile' if is_cuda_source else 'compile'
        if is_cuda_source:
            if source_file.endswith('_xcore1000.cu'):
                rule = 'maca_compile_xcore1000'
            elif source_file.endswith('_xcore1500.cu'):
                rule = 'maca_compile_xcore1500'
            else:
                rule = 'cuda_compile'
        else:
            rule = 'compile'
        if IS_WINDOWS:
            source_file = source_file.replace(':', '$:')
            object_file = object_file.replace(':', '$:')
        source_file = source_file.replace(" ", "$ ")
        object_file = object_file.replace(" ", "$ ")
        build.append(f'build {object_file}: {rule} {source_file}')

    if cuda_dlink_post_cflags:
        devlink_out = os.path.join(os.path.dirname(objects[0]), 'dlink.o')
        devlink_rule = ['rule cuda_devlink']
        devlink_rule.append('  command = $nvcc $in -o $out $cuda_dlink_post_cflags')
        devlink = [f'build {devlink_out}: cuda_devlink {" ".join(objects)}']
        objects += [devlink_out]
    else:
        devlink_rule, devlink = [], []

    if library_target is not None:
        link_rule = ['rule link']
        if IS_WINDOWS:
            cl_paths = subprocess.check_output(['where',
                                                'cl']).decode(*SUBPROCESS_DECODE_ARGS).split('\r\n')
            if len(cl_paths) >= 1:
                cl_path = os.path.dirname(cl_paths[0]).replace(':', '$:')
            else:
                raise RuntimeError("MSVC is required to load C++ extensions")
            link_rule.append(f'  command = "{cl_path}/link.exe" $in /nologo $ldflags /out:$out')
        else:
            link_rule.append('  command = $cxx $in $ldflags -o $out')

        link = [f'build {library_target}: link {" ".join(objects)}']

        default = [f'default {library_target}']
    else:
        link_rule, link, default = [], [], []

    # 'Blocks' should be separated by newlines, for visual benefit.
    blocks = [config, flags, compile_rule]
    if with_cuda:
        blocks.append(cuda_compile_rule)  # type: ignore[possibly-undefined]
        blocks.append(maca_compile_rule_xcore1000)  # type: ignore[possibly-undefined]
        blocks.append(maca_compile_rule_xcore1500)  # type: ignore[possibly-undefined]
    blocks += [devlink_rule, link_rule, build, devlink, link, default]
    content = "\n\n".join("\n".join(b) for b in blocks)
    # Ninja requires a new lines at the end of the .ninja file
    content += "\n"
    _maybe_write(path, content)

# Monkey patching
torch.utils.cpp_extension._write_ninja_file = _write_ninja_file

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()



root=Path(__file__).resolve().parent
os.environ['CUCC_TARGETS']='xcore1000'
setup(name='inferoptlab-flashmla-offset64',version='0.0.1',packages=[],ext_modules=[CUDAExtension(
    name='_inferoptlab_flashmla_offset64',sources=['offset64_api.cpp','offset64_xcore1000.cu'],
    include_dirs=[str(root/'csrc'/p) for p in ['flash_api','flash_dispatch','flash_kernel','flash_kernel/feature','flash_run','utils','mctlass/include']],
    extra_compile_args={'cxx':['-O3','-std=c++17'], 'nvcc':['-O3','-std=c++17','-U__CUDA_NO_HALF_OPERATORS__','-U__CUDA_NO_HALF_CONVERSIONS__','-U__CUDA_NO_HALF2_OPERATORS__','-U__CUDA_NO_BFLOAT16_CONVERSIONS__','--expt-relaxed-constexpr','--expt-extended-lambda','--use_fast_math','-fno-strict-aliasing','-mllvm','-enable-tbaa=false','-D__FAST_HALF_CVT__']},
)],cmdclass={'build_ext':BuildExtension})
