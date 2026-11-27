import json, subprocess
script = r'''
import json,subprocess
from pathlib import Path
root=Path('/home/ubuntu/CJ_workspace/inferoptlab-capacity-20261127')
receipt=json.loads((root/'launch.json').read_text())
controller=json.loads(subprocess.check_output(['docker','inspect',receipt['id']]))[0]
assert controller['Config']['Labels']['io.inferoptlab.role']=='capacity-controller'
subprocess.run(['docker','stop','--time','5',receipt['id']],check=True)
p=root/'experiments/runs/capacity/state.json'
state=json.loads(p.read_text())
cid=state.get('container_id')
if cid:
    info=json.loads(subprocess.check_output(['docker','inspect',cid]))[0]
    attempt=Path(state['deployments'][-1]['directory'])
    launch=json.loads((attempt/'launch.json').read_text())
    assert launch['container_id']==cid
    owner=info['Config']['Labels'].get('io.inferoptlab.owner')
    assert owner and ('io.inferoptlab.owner='+owner) in launch['command']
    subprocess.run(['docker','stop','--time','20',cid],check=True)
    logs=subprocess.run(['docker','logs',cid],capture_output=True,text=True)
    (attempt/'server.log').write_text(logs.stdout+logs.stderr)
state['status']='stopped_by_user_switch_to_inline_capacity'
p.write_text(json.dumps(state,indent=2))
print('Stopped owned capacity controller and its model container; artifacts retained.')
'''
p=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=8','metax-60','python3 -'],input=script.encode(),capture_output=True,timeout=60)
print(p.stdout.decode());print(p.stderr.decode());p.check_returncode()
