"""One explicitly authorized warm reset; never reboot/reload drivers/retry."""
import datetime,fcntl,json,shutil,subprocess,sys,time
from pathlib import Path
ROOT=Path('/home/metax/glm53-recovery-20261123')
def run(cmd,**kw):
    p=subprocess.run(cmd,capture_output=True,text=True,timeout=25,**kw)
    return {'argv':cmd,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
def main():
    password=sys.stdin.readline().rstrip('\r\n')
    e=ROOT/'evidence';result=e/'warm_reset_result.json'
    assert not result.exists(),'One attempt only; existing receipt found'
    with Path('/home/metax/.glm53-c500-tp8.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        ref=Path('/sys/module/metax/refcnt').read_text().strip()
        processes=run(['mx-smi','--show-all-process'])
        containers=run(['docker','ps','--format','{{.Names}}'])
        assert ref=='0' and 'no process found' in processes['stdout'] and not containers['stdout'].strip()
        boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
        start=time.time();since=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        cmd=['sudo','-S','-p','','--',shutil.which('mx-smi'),'-r','-i','0000:5b:00.0','-y']
        record={'authorization':'User explicitly approved one warm reset after R5330 G7 risk disclosure. No host reboot or driver change authorized.',
          'started_epoch':start,'started_utc':since,'boot_id_before':boot,'metax_refcnt_before':ref,'processes_before':processes,
          'containers_before':containers,'command':cmd,'status':'started','expected_group':[4,5,6,7]}
        with result.open('x') as f:json.dump(record,f,indent=2)
        print('Executing one authorized warm reset',flush=True)
        try:
            p=subprocess.run(cmd,input=password+'\n',capture_output=True,text=True,timeout=120)
            record.update(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr,status='command_returned')
        except subprocess.TimeoutExpired as exc:
            record.update(status='command_timeout_no_retry',returncode=None,stdout=str(exc.stdout or ''),stderr=str(exc.stderr or ''))
        result.write_text(json.dumps(record,indent=2));print(record['status'],flush=True)
        remaining=max(0,90-(time.time()-start))
        while remaining>0:
            time.sleep(min(30,remaining));remaining=max(0,90-(time.time()-start))
        # Queries only after >=90 seconds; no further recovery mutation.
        record['waited_seconds']=time.time()-start
        record['boot_id_after']=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
        record['after']={name:run(args) for name,args in {
          'gpu':['mx-smi'],'reason':['mx-smi','-i','0000:5b:00.0','--show-unavailable-reason'],
          'links':['mx-smi','mxlk','-i','4,5,6,7','--show-state','--show','--show-aer'],
          'topology':['mx-smi','topo','-m'],'processes':['mx-smi','--show-all-process']}.items()}
        logs=run(['sudo','-S','-p','','journalctl','-k','--since',since,'--no-pager','-o','short-iso'],input=password+'\n')
        record['selected_kernel_events']=[line for line in logs['stdout'].splitlines() if any(x in line.lower() for x in ['metax','metalk','aer','pcie']) and not any(x in line.lower() for x in ['serial','uuid'])]
        record['kernel_query_returncode']=logs['returncode']
        record['status']='inspection_complete_no_model_started'
        result.write_text(json.dumps(record,indent=2))
        print(json.dumps({'status':record['status'],'reset_rc':record['returncode'],'boot_unchanged':boot==record['boot_id_after'],'gpu_rc':record['after']['gpu']['returncode']}),flush=True)
if __name__=='__main__':main()
