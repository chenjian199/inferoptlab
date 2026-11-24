#!/usr/bin/env bash
set -euo pipefail
root=/home/metax/glm53-vllm032
name=glm53-vllm032
test "$(docker inspect --format '{{index .Config.Labels "com.codex.task"}}' "$name")" = "$name"
test "$(docker inspect --format '{{.State.Running}}' "$name")" = true
exec 9>"$root/inference.lock"
flock -n 9 || { echo 'Another acceptance run holds the task lock.' >&2; exit 1; }
if docker top "$name" -eo pid,args | grep -Eqi 'python.*infer_smoke.py|vllm::'; then
  echo 'Inference workers already exist in the task container.' >&2
  exit 1
fi
log="$root/logs/inference-$(date +%Y%m%dT%H%M%S).log"
docker exec \
  -e PYTHONPATH=/work/scripts \
  -e VLLM_USE_V2_MODEL_RUNNER=1 \
  -e GLM53_MAX_SEQS=1 -e GLM53_SYNC_SCHEDULING=1 \
  -e VLLM_WORKER_MULTIPROC_METHOD=spawn \
  -e HF_HUB_OFFLINE=1 -e TRANSFORMERS_OFFLINE=1 \
  "$name" python -u /work/scripts/infer_smoke.py 2>&1 | tee "$log"
