"""Bounded all-reduce diagnostic, run only with experiment-local P2P disabled."""
import datetime,json,os
from pathlib import Path
import torch
import torch.distributed as dist
import torch.multiprocessing as mp


def worker(rank):
    torch.cuda.set_device(rank)
    x=torch.tensor([rank+1.0],device='cuda')
    print(json.dumps({'rank':rank,'local_value':x.item()}),flush=True)
    dist.init_process_group('nccl',init_method='file:///experiment/evidence/comm_rendezvous',rank=rank,world_size=8,timeout=datetime.timedelta(seconds=45))
    dist.all_reduce(x);torch.cuda.synchronize()
    assert x.item()==36.0
    Path(f'/experiment/evidence/comm_rank{rank}.json').write_text(json.dumps({'rank':rank,'sum':x.item(),'passed':True}))
    dist.destroy_process_group()


if __name__=='__main__':
    assert os.environ.get('MCCL_P2P_DISABLE')=='1'
    mp.spawn(worker,nprocs=8,join=True)
    Path('/experiment/evidence/communication_probe.json').write_text(json.dumps({'status':'passed','ranks':8,'MCCL_P2P_DISABLE':'1','scope':'Small all-reduce only; does not clear hardware health fault or certify full inference'}))
