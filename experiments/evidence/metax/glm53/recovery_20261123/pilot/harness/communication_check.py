"""Post-recovery basic compute + default-path TP8 all-reduce; bounded by launcher."""
import datetime,json,os
from pathlib import Path
import torch
import torch.distributed as dist
import torch.multiprocessing as mp

def worker(rank):
    torch.cuda.set_device(rank)
    a=torch.arange(64,device='cuda',dtype=torch.float32).reshape(8,8)
    y=a@a.T
    ref=torch.arange(64,dtype=torch.float32).reshape(8,8)
    assert torch.equal(y.cpu(),ref@ref.T)
    dist.init_process_group('nccl',init_method=os.environ['GEMM_COMM_INIT'],rank=rank,world_size=8,timeout=datetime.timedelta(seconds=45))
    for n in [1,16,1024]:
        x=torch.full((n,),rank+1.,device='cuda')
        dist.all_reduce(x);torch.cuda.synchronize()
        assert torch.equal(x.cpu(),torch.full((n,),36.))
    Path(f'/experiment/evidence/comm_rank{rank}.json').write_text(json.dumps({'rank':rank,'local_matmul_exact':True,'all_reduce_lengths':[1,16,1024],'expected_sum':36,'passed':True}))
    dist.destroy_process_group()

if __name__=='__main__':
    assert os.environ.get('MCCL_P2P_DISABLE','0')=='0','Default communication path required'
    assert not Path('/experiment/evidence/communication_check.json').exists()
    mp.spawn(worker,nprocs=8,join=True)
    Path('/experiment/evidence/communication_check.json').write_text(json.dumps({'status':'passed','ranks':8,'default_p2p':True,'scope':'Small compute/collectives only; not a hardware stress certification.'}))
