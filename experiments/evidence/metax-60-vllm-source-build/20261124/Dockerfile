ARG BASE_IMAGE=inferoptlab/metax-build-base:20261124
FROM ${BASE_IMAGE} AS builder
USER root
ENV PYTHONPATH="" PIP_DISABLE_PIP_VERSION_CHECK=1 INFEROPTLAB_BUILD_CONTAINER=1
COPY scripts/install_sdk.py /opt/build-scripts/install_sdk.py
COPY evidence/sources.json /opt/build-evidence/sources.json
RUN --mount=type=bind,source=inputs/sdk,target=/inputs/sdk python3 /opt/build-scripts/install_sdk.py
RUN /opt/conda/bin/python3 -m venv /opt/vllm-env
ENV VIRTUAL_ENV=/opt/vllm-env
ENV PATH=/opt/vllm-env/bin:/opt/maca/tools/cu-bridge/tools:/opt/maca/tools/cu-bridge/bin:/opt/maca/bin:/opt/maca/mxgpu_llvm/bin:/opt/conda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV MACA_PATH=/opt/maca CUCC_PATH=/opt/maca/tools/cu-bridge CUCC_CMAKE_ENTRY=2
ENV CUBRIDGE_HOME=/opt/build-tools CUDA_HOME=/opt/build-tools/cu-bridge/CUDA_DIR
ENV LD_LIBRARY_PATH=/opt/maca/lib:/opt/maca/mxgpu_llvm/lib:/opt/maca/ompi/lib:/opt/maca/ucx/lib:/opt/mxdriver/lib
ENV USE_PRECOMPILED_KERNEL=1 MAX_JOBS=16 VLLM_USE_RUST_FRONTEND=0 VLLM_REQUIRE_RUST_FRONTEND=0
COPY src/ /opt/src/
COPY patches/ /opt/patches/
RUN cd /opt/src/vllm-metax && patch -p1 < /opt/patches/glm-w8a8.patch && cp /opt/patches/moe_align_legacy_abi.py vllm_metax/patch/bugfix/
COPY scripts/build_frameworks.py /opt/build-scripts/build_frameworks.py
RUN --mount=type=bind,source=inputs/wheelhouse,target=/inputs/wheelhouse --mount=type=cache,target=/root/.cache/pip python -m pip install --index-url https://pypi.tuna.tsinghua.edu.cn/simple packaging && python /opt/build-scripts/build_frameworks.py

FROM ${BASE_IMAGE}
USER root
COPY --from=builder /opt/maca-3.9.0 /opt/maca-3.9.0
COPY --from=builder /opt/vllm-env /opt/vllm-env
COPY --from=builder /opt/src /opt/src
COPY --from=builder /opt/built-wheels /opt/built-wheels
COPY --from=builder /opt/build-evidence /opt/build-evidence
COPY evidence/dependencies.json /opt/build-evidence/dependencies.json
COPY patches/ /opt/build-evidence/patches/
RUN ln -sfn /opt/maca-3.9.0 /opt/maca && printf '/opt/maca/lib\n/opt/maca/mxgpu_llvm/lib\n' > /etc/ld.so.conf.d/maca.conf && ldconfig
ENV VIRTUAL_ENV=/opt/vllm-env PYTHONPATH=""
ENV PATH=/opt/vllm-env/bin:/opt/maca/tools/cu-bridge/tools:/opt/maca/tools/cu-bridge/bin:/opt/maca/bin:/opt/maca/mxgpu_llvm/bin:/opt/conda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV MACA_PATH=/opt/maca LD_LIBRARY_PATH=/opt/maca/lib:/opt/maca/mxgpu_llvm/lib:/opt/maca/ompi/lib:/opt/maca/ucx/lib:/opt/mxdriver/lib
ENV USE_PRECOMPILED_KERNEL=1 VLLM_USE_V2_MODEL_RUNNER=1 VLLM_USE_RUST_FRONTEND=0 VLLM_REQUIRE_RUST_FRONTEND=0 OMP_NUM_THREADS=4
LABEL org.opencontainers.image.title="inferoptlab vLLM-MetaX GLM-5.3 C500 source build"
LABEL io.inferoptlab.vllm.commit="5df63a7203cdb9328d824a27b682e77c7b9928be"
LABEL io.inferoptlab.vllm-metax.commit="0962c8735ffe4795800030680311410848512b82"
WORKDIR /work
ENTRYPOINT ["/opt/vllm-env/bin/python", "-m", "vllm.entrypoints.openai.api_server"]
