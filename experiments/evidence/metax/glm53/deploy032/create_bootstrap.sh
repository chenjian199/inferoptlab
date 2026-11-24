#!/usr/bin/env bash
set -euo pipefail
unset HTTP_PROXY HTTPS_PROXY ALL_PROXY http_proxy https_proxy all_proxy
root=/home/metax/glm53-vllm032
name=glm53-vllm032
base="${GLM53_IMAGE:-sha256:96bbee871d4ea038b123276eacd65f77825b093b9255157938e0b1628e121f0b}"
mkdir -p "$root/wheelhouse" "$root/downloads"
docker image inspect "$base" > "$root/evidence/bootstrap_image_inspect.json"
if docker container inspect "$name" >/dev/null 2>&1; then
  test "$(docker inspect --format '{{index .Config.Labels "com.codex.task"}}' "$name")" = glm53-vllm032
  test "$(docker inspect --format '{{.State.Running}}' "$name")" = true
else
  docker run -d --name "$name" --hostname "$name" \
    --add-host "$name:127.0.0.1" \
    --label com.codex.task=glm53-vllm032 \
    --label com.codex.base-route=official-sdk-and-wheels \
    --device=/dev/dri --device=/dev/mxcd --group-add video \
    --network=host --ipc=private --shm-size=64g \
    --ulimit memlock=-1:-1 --ulimit stack=67108864:67108864 \
    --mount type=bind,source="$root/src",target=/work/src \
    --mount type=bind,source="$root/scripts",target=/work/scripts \
    --mount type=bind,source="$root/evidence",target=/work/evidence \
    --mount type=bind,source="$root/downloads",target=/install,readonly \
    --mount type=bind,source="$root/wheelhouse",target=/wheelhouse \
    --mount type=bind,source=/NFS_62/Models/GLM_Series/GLM-5.3-Flash-W8A8,target=/models/GLM-5.3-Flash-W8A8,readonly \
    -e GLM53_ISOLATED_ENV=1 -e USE_PRECOMPILED_KERNEL=1 \
    -e VLLM_USE_RUST_FRONTEND=0 -e MACA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 \
    -e OMP_NUM_THREADS=4 --workdir=/work --entrypoint=sleep "$base" infinity
fi
docker inspect "$name" > "$root/evidence/container_inspect.json"
