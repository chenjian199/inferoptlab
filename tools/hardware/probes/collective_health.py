"""Eight-rank deterministic communication/compute sanity, without performance claims.

Run using torch.distributed.run in the exact serving image. Does not certify
exhaustive memory health or all model kernels. Never resets devices/counters.
"""
import datetime
import json
import os

import torch
import torch.distributed as dist


def main():
    rank = int(os.environ['LOCAL_RANK'])
    world = int(os.environ['WORLD_SIZE'])
    torch.cuda.set_device(rank)
    dist.init_process_group('nccl', timeout=datetime.timedelta(seconds=180))
    device = torch.device('cuda', rank)
    # Integer-valued FP32 checks avoid an arbitrary floating-point tolerance.
    for count in (1024, 1048576):
        original = torch.full((count,), float(rank + 1), device=device)
        total = original.clone()
        dist.all_reduce(total)
        assert bool(torch.all(total == world * (world + 1) // 2)), 'all_reduce mismatch'
        gathered = torch.empty(world * count, device=device)
        dist.all_gather_into_tensor(gathered, original)
        for peer in range(world):
            assert bool(torch.all(gathered[peer * count:(peer + 1) * count] == peer + 1)), 'all_gather mismatch'
        scattered = torch.empty(count, device=device)
        dist.reduce_scatter_tensor(scattered, gathered)
        assert bool(torch.all(scattered == world * (rank + 1))), 'reduce_scatter mismatch'
        assert bool(torch.all(original.cpu() == rank + 1)), 'device-to-host mismatch'
    a = torch.full((64, 64), float(rank + 1), device=device)
    b = torch.ones((64, 64), device=device)
    assert bool(torch.all(a @ b == 64 * (rank + 1))), 'FP32 GEMM sanity mismatch'
    torch.cuda.synchronize()
    dist.barrier()
    record = dict(rank=rank, world_size=world, status='passed',
                  checks=['all_reduce', 'all_gather', 'reduce_scatter', 'device_copy', 'fp32_gemm_sanity'])
    for reporting_rank in range(world):
        if rank == reporting_rank:
            os.write(1, (json.dumps(record) + '\n').encode())
        dist.barrier()
    dist.destroy_process_group()


if __name__ == '__main__':
    main()
