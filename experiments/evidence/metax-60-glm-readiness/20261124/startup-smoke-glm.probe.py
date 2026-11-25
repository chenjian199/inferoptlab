"""Bounded isolated GLM startup qualification; no benchmark/performance claims."""
from pathlib import Path
import datetime, json, subprocess, time, urllib.request, urllib.error

stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
work=Path('/home/ubuntu/CJ_workspace')/('glm53-flash-preflight-'+stamp)
work.mkdir(exist_ok=False)
name='inferoptlab-glm53-flash-smoke-'+stamp.lower()
image='sha256:e636eb63ab7408be62ce15e3dd25fb2ffb38649074fb2fb5852c42a8c8e1047d'
model='/mnt/ufs1/models/models/metax-tech/GLM-5.3-Flash-W8A8'
def command(args, timeout=30):
    p=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
    return {'argv':args,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
before=command(['mx-smi'])
(work/'gpu-before.json').write_text(json.dumps(before,indent=2))
if 'no process found' not in before['stdout']:
    raise SystemExit('GPU idle precheck failed; no service started')
import socket
with socket.socket() as sock:
    sock.bind(('127.0.0.1',18081))
args=['docker','run','-d','--pull=never','--name',name,'--network','host','--shm-size','16g',
      '--device','/dev/mxcd','--device','/dev/dri',
      '--mount',f'type=bind,source={model},target=/model,readonly',
      '-e','MACA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7','-e','HF_HUB_OFFLINE=1',
      '-e','TRANSFORMERS_OFFLINE=1','-e','OMP_NUM_THREADS=4',
      '-e','SGLANG_C500_DSV41_MIXED_LOAD=0','-e','SGLANG_C500_DSV41_PRECISION_REFERENCE=0',
      '--entrypoint','python3',image,'-m','sglang.launch_server',
      '--model-path','/model','--tokenizer-path','/model','--served-model-name','glm53-flash',
      '--host','127.0.0.1','--port','18081','--tp-size','8','--pp-size','1','--ep-size','1','--dp-size','1',
      '--dtype','bfloat16','--quantization','compressed-tensors','--context-length','4096',
      '--max-running-requests','1','--chunked-prefill-size','4096','--mem-fraction-static','0.85',
      '--disable-radix-cache','--disable-cuda-graph','--disable-custom-all-reduce',
      '--stream-interval','1','--enable-metrics']
result={'host':'metax-60','workdir':str(work),'container':name,'startup_timeout_s':600,
        'status':'not_started','new_performance_measurement':False}
started=False
try:
    launched=command(args)
    (work/'launch.json').write_text(json.dumps(launched,indent=2))
    if launched['returncode']:
        result.update(status='launch_failed',error=launched['stderr'])
    else:
        started=True;result['status']='startup_timeout'
        print(json.dumps({'workdir':str(work),'container':name,'event':'started'}),flush=True)
        deadline=time.monotonic()+600
        while time.monotonic()<deadline:
            state=command(['docker','inspect',name,'--format','{{json .State}}'])
            result['container_state']=json.loads(state['stdout'])
            if not result['container_state']['Running']:
                result['status']='startup_failed';break
            try:
                with urllib.request.urlopen('http://127.0.0.1:18081/health',timeout=3) as response:
                    if response.status==200:
                        result['status']='ready';break
            except (OSError,urllib.error.URLError):pass
            time.sleep(5)
        if result['status']=='ready':
            payload={'model':'glm53-flash','messages':[{'role':'user','content':'Reply with the word hello.'}],
                     'max_tokens':16,'temperature':0,'stream':False}
            request=urllib.request.Request('http://127.0.0.1:18081/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
            try:
                with urllib.request.urlopen(request,timeout=60) as response:result['smoke_response']=json.load(response)
                result['status']='generated'
            except Exception as exc:result.update(status='generation_failed',error=str(exc))
finally:
    if started:
        logs=command(['docker','logs',name])
        (work/'server.log').write_text(logs['stdout']+'\n'+logs['stderr'])
        result['stop']=command(['docker','stop','--time','10',name],timeout=30)
        result['remove']=command(['docker','rm',name])
    result['gpu_after']=command(['mx-smi'])
    (work/'result.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result),flush=True)
