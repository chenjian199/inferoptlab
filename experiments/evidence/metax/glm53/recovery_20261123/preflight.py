"""Read-only GPU recovery preflight. No reset/reboot/driver changes."""
import datetime,json,subprocess
from pathlib import Path
ROOT=Path('/home/metax/glm53-recovery-20261123')
def main():
    e=ROOT/'evidence';e.mkdir(parents=True,exist_ok=True)
    commands={
      'gpu':['mx-smi'],
      'reason':['mx-smi','-i','0000:5b:00.0','--show-unavailable-reason'],
      'processes':['mx-smi','--show-all-process'],
      'links':['mx-smi','mxlk','-i','4,5,6,7','--show-state','--show','--show-peer','--show-aer'],
      'topology':['mx-smi','topo','-m'],
      'ecc_pcie':['mx-smi','-i','6,7','--count-ecc','--show-pcie'],
      'versions':['mx-smi','-i','4,5,6,7','--show-version'],
      'virtualization':['systemd-detect-virt'],
      'running_containers':['docker','ps','--format','{{.Names}} {{.Status}}']}
    result={'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commands':{},'read_only':True}
    for name,cmd in commands.items():
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=25)
        result['commands'][name]={'argv':cmd,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
    result['host']={}
    for key,path in {'vendor':'/sys/class/dmi/id/sys_vendor','product':'/sys/class/dmi/id/product_name','metax_refcnt':'/sys/module/metax/refcnt','boot_id':'/proc/sys/kernel/random/boot_id'}.items():
        result['host'][key]=Path(path).read_text().strip()
    result['containers']={}
    for name in ['dcc','glm53-vllm032','glm53-heval-v1','glm53-repeat-v1','glm53-gemm-v1']:
        d=json.loads(subprocess.check_output(['docker','inspect',name]))[0]
        result['containers'][name]={k:d[k] for k in ['Id','Image','Created','Mounts']}
        result['containers'][name]['State']={k:d['State'][k] for k in ['Running','Paused','StartedAt','FinishedAt','Restarting']}
    with (e/'preflight.json').open('x') as f:json.dump(result,f,indent=2)
    print(json.dumps({'host':result['host'],'saved':str(e/'preflight.json'),'gpu_rc':result['commands']['gpu']['returncode']}))
if __name__=='__main__':main()
