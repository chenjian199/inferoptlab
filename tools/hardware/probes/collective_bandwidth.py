"""Single-node collective bandwidth, launched with torch.distributed.run.

S is the full array size for AG/RS and per-rank array size for A2A/AR.
Bus bandwidth is the NCCL-tests analytical normalization, not a link counter.
Each sample is the maximum rank wall time of a synchronized batch / iterations.
"""
import argparse
import datetime
import json
import math
import os
from pathlib import Path
import statistics
import time

import torch
import torch.distributed as dist


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--operation',choices=['all_to_all','all_gather','reduce_scatter','all_reduce','all_gather_reduce_scatter','all_to_all_roundtrip'],required=True)
    p.add_argument('--sizes',type=int,nargs='+',required=True,help='Full array bytes, divisible by ranks * dtype bytes')
    p.add_argument('--warmup',type=int,default=10)
    p.add_argument('--iterations',type=int,default=20)
    p.add_argument('--repeats',type=int,default=5)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--physical-devices',required=True)
    a=p.parse_args()
    rank=int(os.environ['LOCAL_RANK']);world=int(os.environ['WORLD_SIZE'])
    assert a.warmup>=1 and a.iterations>=1 and a.repeats>=3
    assert all(0<s<=256*1024**2 and s%(world*2)==0 for s in a.sizes)
    torch.cuda.set_device(rank)
    dist.init_process_group('nccl',timeout=datetime.timedelta(seconds=120))
    device=torch.device('cuda',rank)
    if rank==0:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        assert not a.out.exists(),'Do not overwrite an earlier measurement'
    dist.barrier()
    for size in a.sizes:
        n=size//2;part=n//world
        small=torch.full((part,),float(rank+1),dtype=torch.bfloat16,device=device)
        full=torch.full((n,),float(rank+1),dtype=torch.bfloat16,device=device)
        gathered=torch.empty_like(full);reduced=torch.empty_like(small)
        exchanged=torch.empty_like(full);returned=torch.empty_like(full)
        op=a.operation
        if op=='all_reduce':returned.copy_(full)

        def execute():
            if op=='all_gather':dist.all_gather_into_tensor(gathered,small)
            elif op=='reduce_scatter':dist.reduce_scatter_tensor(reduced,full)
            elif op=='all_reduce':dist.all_reduce(returned)
            elif op=='all_to_all':dist.all_to_all_single(exchanged,full)
            elif op=='all_gather_reduce_scatter':
                dist.all_gather_into_tensor(gathered,small)
                dist.reduce_scatter_tensor(reduced,gathered)
            else:
                dist.all_to_all_single(exchanged,full)
                dist.all_to_all_single(returned,exchanged)

        execute();torch.cuda.synchronize()
        if op=='all_gather':
            for peer in range(world):assert bool(torch.all(gathered[peer*part:(peer+1)*part]==peer+1))
        elif op in ['reduce_scatter','all_reduce']:
            output=reduced if op=='reduce_scatter' else returned
            assert bool(torch.all(output==world*(world+1)//2))
        elif op=='all_to_all':
            for peer in range(world):assert bool(torch.all(exchanged[peer*part:(peer+1)*part]==peer+1))
        elif op=='all_gather_reduce_scatter':assert bool(torch.all(reduced==world*(rank+1)))
        else:assert bool(torch.all(returned==rank+1))
        # Validate nonzero data once, then keep AR input at zero to avoid
        # repeated in-place sum overflow without adding a copy to timing.
        if op=='all_reduce':returned.zero_()
        for _ in range(a.warmup):execute()
        torch.cuda.synchronize();samples=[];rank_times=[]
        for _ in range(a.repeats):
            dist.barrier();torch.cuda.synchronize()
            start=time.perf_counter()
            for _ in range(a.iterations):execute()
            torch.cuda.synchronize()
            elapsed=(time.perf_counter()-start)*1000/a.iterations
            timing=torch.tensor([elapsed],dtype=torch.float64,device=device)
            times=[torch.empty_like(timing) for _ in range(world)]
            dist.all_gather(times,timing)
            values=[t.item() for t in times]
            samples.append(max(values));rank_times.append(values)
        factor=(world-1)/world
        calls=2 if op in ['all_reduce','all_gather_reduce_scatter','all_to_all_roundtrip'] else 1
        bus_bytes=size*factor*calls
        median=statistics.median(samples)
        local_input=size//world if op in ['all_gather','all_gather_reduce_scatter'] else size
        local_output=size//world if op in ['reduce_scatter','all_gather_reduce_scatter'] else size
        record=dict(operation=op,world_size=world,physical_devices=a.physical_devices,dtype='bfloat16',
                    size_bytes=size,input_bytes_per_rank=local_input,output_bytes_per_rank=local_output,
                    logical_bus_bytes_per_rank=bus_bytes,bus_bytes_are_formula_not_counter=True,
                    warmup=a.warmup,iterations=a.iterations,repeats=a.repeats,samples_ms=samples,
                    rank_samples_ms=rank_times,mean_ms=statistics.fmean(samples),median_ms=median,
                    min_ms=min(samples),max_ms=max(samples),algorithm_GBps=size/(median*1e6),
                    bus_GBps=bus_bytes/(median*1e6),correctness='passed',torch_version=torch.__version__,
                    timing='synchronized host batch maximum across ranks; includes Python dispatch',
                    extra_copy_in_timing=False,
                    recorded_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
        if rank==0:
            with a.out.open('a',encoding='utf-8') as stream:stream.write(json.dumps(record)+'\n');stream.flush()
            print(json.dumps(record),flush=True)
        del small,full,gathered,reduced,exchanged,returned
        torch.cuda.empty_cache()
    dist.barrier();dist.destroy_process_group()


if __name__=='__main__':main()
