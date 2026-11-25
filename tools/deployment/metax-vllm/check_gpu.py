"""Eight-rank BF16 arithmetic and MCCL checks, without loading model weights."""
import datetime
import json
import os
from pathlib import Path

import torch
import torch.distributed as dist

rank = int(os.environ['LOCAL_RANK'])
assert torch.cuda.device_count() == 8
torch.cuda.set_device(rank)
dist.init_process_group('nccl', timeout=datetime.timedelta(seconds=120))
assert dist.get_world_size() == 8
matrix = torch.arange(64, dtype=torch.float32, device='cuda').reshape(8, 8) / 64
actual = matrix.bfloat16() @ torch.eye(8, dtype=torch.bfloat16, device='cuda')
torch.testing.assert_close(actual.float(), matrix, rtol=0, atol=0)
value = torch.tensor([float(rank + 1)], device='cuda')
dist.all_reduce(value)
assert value.item() == 36
values = [torch.empty_like(value) for _ in range(8)]
dist.all_gather(values, torch.tensor([float(rank)], device='cuda'))
assert [value.item() for value in values] == list(range(8))
torch.cuda.synchronize()
report = {'rank': rank, 'gpu': torch.cuda.get_device_name(rank), 'torch': torch.__version__,
          'bf16_matmul': 'pass', 'all_reduce': 'pass', 'all_gather': 'pass'}
destination = Path('/work/evidence/gpu8')
destination.mkdir(parents=True, exist_ok=True)
(destination / f'rank-{rank}.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report), flush=True)
dist.destroy_process_group()
