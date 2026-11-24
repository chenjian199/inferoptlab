#!/usr/bin/env bash
set -euo pipefail
unset HTTP_PROXY HTTPS_PROXY ALL_PROXY http_proxy https_proxy all_proxy
name=glm53-vllm032
root=/home/metax/glm53-vllm032
image=mxcr.metax-tech.com/mim-pub/vllm/model-free@sha256:c0bf5876cc334521408bd54f4028f36d171e31a6ab05136da4174344e057d76d
docker image inspect "$image" > "$root/evidence/base_image_inspect.json"
if docker container inspect "$name" >/dev/null 2>&1; then
  test "$(docker inspect --format '{{index .Config.Labels "com.codex.task"}}' "$name")" = glm53-vllm032
  test "$(docker inspect --format '{{.State.Running}}' "$name")" = true
else
  docker run -d --name "$name" --hostname "$name" \
    --label com.codex.task=glm53-vllm032 \
    --device=/dev/dri --device=/dev/mxcd --group-add video \
    --network=host --ipc=private --shm-size=64g \
    --ulimit memlock=-1:-1 --ulimit stack=67108864:67108864 \
    --mount type=bind,source="$root",target=/work \
    --mount type=bind,source=/NFS_62/Models/GLM_Series/GLM-5.3-Flash-W8A8,target=/models/GLM-5.3-Flash-W8A8,readonly \
    -e GLM53_ISOLATED_ENV=1 -e USE_PRECOMPILED_KERNEL=1 \
    -e VLLM_USE_RUST_FRONTEND=0 -e MACA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 \
    -e OMP_NUM_THREADS=4 --workdir=/work --entrypoint=sleep "$image" infinity
fi
docker inspect "$name" > "$root/evidence/container_inspect.json"
