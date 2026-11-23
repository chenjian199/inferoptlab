"""Live read-only MetaX inventory for the benchmark client on the server host."""
import json
import subprocess

from tools.hardware.metax import gpu_blocks


def inventory():
    result=dict(provider='mx-smi',status='unavailable',output=None,commands={})
    try:
        for name,args in [('gpu',['mx-smi','-j']),('hwinfo',['mx-smi','--show-hwinfo'])]:
            p=subprocess.run(args,capture_output=True,text=True,timeout=10,check=False)
            result['commands'][name]=dict(args=args,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)
            if p.returncode:
                result['status']='failed'
                return result
        text=result['commands']['gpu']['stdout']
        gpu=json.loads(text[text.index('{'):])
        blocks=gpu_blocks(result['commands']['hwinfo']['stdout'])
        rows={int(v['device_id']):(k.lower(),v) for k,v in gpu.items() if isinstance(v,dict) and 'device_id' in v}
        if not rows or set(rows)!=set(blocks) or len(rows)!=gpu['attached_gpus']:
            raise ValueError('MetaX inventory device counts differ')
        devices={}
        for ordinal,(bdf,fields) in blocks.items():
            if rows[ordinal][0]!=bdf:
                raise ValueError('MetaX inventory ordinal/BDF differs')
            devices[str(ordinal)]=dict(pci_bus_id=bdf,board_serial=fields['Board Serial Number'])
        # mx-smi reports its own userspace MACA library, which can differ inside
        # a collector container from both the host and inference server runtime.
        result.update(status='observed',devices=devices,driver_version=gpu['driver_version'],
                      management_runtime_version=gpu['maca_version'],runtime_scope='collector_process')
    except (OSError,subprocess.TimeoutExpired,ValueError,KeyError,TypeError) as exc:
        result.update(status='failed',error=str(exc))
    return result


def binding_issues(probe,bindings,hardware):
    declared={d['device_id']:d.get('observed',{}) for node in hardware['resources']['nodes'] for d in node['devices']}
    issues=[]
    for binding in bindings:
        expected=declared.get(binding['device_id'],{})
        actual=probe.get('devices',{}).get(str(binding['visible_index']),{})
        if not expected or any(not actual.get(k) or actual.get(k)!=expected.get(k) for k in ('board_serial','pci_bus_id')):
            issues.append(f'MetaX ordinal/serial/BDF mapping is unverified: rank {binding["rank"]}')
    discovery=hardware.get('discovery',{})
    for key in ('driver_version',):
        if not probe.get(key) or probe.get(key)!=discovery.get(key):
            issues.append('MetaX '+key+' differs from HardwareSpec')
    return issues
