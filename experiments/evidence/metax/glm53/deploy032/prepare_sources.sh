#!/usr/bin/env bash
set -euo pipefail
unset HTTP_PROXY HTTPS_PROXY ALL_PROXY http_proxy https_proxy all_proxy
root=/home/metax/glm53-vllm032
mkdir -p "$root/src" "$root/logs" "$root/evidence" "$root/scripts"
if [ ! -d "$root/src/vllm-metax/.git" ]; then
  git clone --no-hardlinks --branch v0.32.0-dev /home/metax/DCC_workspace/glm/vLLM-metax "$root/src/vllm-metax"
  git -C "$root/src/vllm-metax" checkout --detach 0962c8735ffe4795800030680311410848512b82
fi
test "$(git -C "$root/src/vllm-metax" rev-parse HEAD)" = 0962c8735ffe4795800030680311410848512b82
if [ ! -d "$root/src/vllm/.git" ]; then
  git -c http.proxy= -c https.proxy= clone --depth 1 --branch v0.32.0 https://github.com/vllm-project/vllm.git "$root/src/vllm"
fi
test "$(git -C "$root/src/vllm" rev-parse HEAD)" = 5df63a7203cdb9328d824a27b682e77c7b9928be
git -C "$root/src/vllm-metax" status --porcelain
git -C "$root/src/vllm" status --porcelain
printf 'SOURCES_READY\n'
