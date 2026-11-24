"""Run with torchrun --standalone --nproc_per_node=8; no model allocation."""
import datetime
import json
import os
from pathlib import Path

import torch
import torch.distributed as dist

rank = int(os.environ['LOCAL_RANK'])
assert torch.cuda.device_count() == 8, torch.cuda.device_count()
torch.cuda.set_device(rank)
name = torch.cuda.get_device_name(rank)
assert 'C500' in name, name
dist.init_process_group('nccl', timeout=datetime.timedelta(seconds=120))
assert dist.get_world_size() == 8
a = torch.arange(64, device='cuda', dtype=torch.float32).reshape(8, 8) / 64
b = torch.eye(8, device='cuda', dtype=torch.bfloat16)
actual = a.to(torch.bfloat16) @ b
torch.testing.assert_close(actual.float(), a, atol=0, rtol=0)
value = torch.tensor([rank + 1.0], device='cuda')
dist.all_reduce(value)
assert value.item() == 36, value.item()
gathered = [torch.empty_like(value) for _ in range(8)]
dist.all_gather(gathered, torch.tensor([float(rank)], device='cuda'))
assert [x.item() for x in gathered] == list(range(8))
torch.cuda.synchronize()
report = {'rank': rank, 'gpu': name, 'torch': torch.__version__,
          'bf16_matmul': 'pass', 'all_reduce': 'pass', 'all_gather': 'pass'}
out = Path('/work/evidence/gpu8')
out.mkdir(parents=True, exist_ok=True)
(out / f'rank-{rank}.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report), flush=True)
dist.destroy_process_group()
