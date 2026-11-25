#!/usr/bin/env bash
set -euo pipefail
client_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
image='sha256:43af58b15b63b6095611b257590466632433d6786d66386839e1c5b8027d30ad'
model='/mnt/ufs1/models/models/metax-tech/GLM-5.3-Flash-W8A8'
test -x "$client_dir/venv/bin/aiperf" || { echo 'AIPerf installation is incomplete' >&2; exit 1; }
exec docker run --pull=never --rm --network host \
  --user "$(id -u):$(id -g)" \
  --mount "type=bind,source=$client_dir,target=/work" \
  --mount "type=bind,source=$model,target=/model,readonly" \
  --workdir /work \
  -e HOME=/work -e VIRTUAL_ENV=/work/venv \
  -e PATH=/work/venv/bin:/opt/conda/bin:/usr/local/bin:/usr/bin:/bin \
  --entrypoint /work/venv/bin/aiperf "$image" "$@"
