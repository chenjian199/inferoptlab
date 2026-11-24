"""Install pinned sources only in the dedicated container; preserve private ABI packages."""
import importlib.metadata as md
import json
import os
import subprocess
import sys
from pathlib import Path
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

root = Path('/work')
assert Path('/.dockerenv').exists(), 'Container only'
assert os.environ.get('GLM53_ISOLATED_ENV') == '1', 'Dedicated container only'
plugin = root/'src/vllm-metax'
upstream = root/'src/vllm'
expected = {plugin:'0962c8735ffe4795800030680311410848512b82',
            upstream:'5df63a7203cdb9328d824a27b682e77c7b9928be'}
for repo, commit in expected.items():
    assert subprocess.check_output(['git','-c',f'safe.directory={repo}',
                                    '-C',str(repo),'rev-parse','HEAD'],text=True).strip() == commit
    subprocess.run(['git','config','--global','--add','safe.directory',str(repo)],check=True)

def installed():
    return {canonicalize_name(d.metadata['Name']): d.version for d in md.distributions() if d.metadata['Name']}

before = installed()
assert before['torch'] == '2.10.0+metax3.9.0.8', before['torch']
assert before['triton'] == '3.6.0+metax3.9.0.8', before['triton']
assert before['mcoplib'].split('+')[0] == '0.4.14', before['mcoplib']
assert before.get('mctlassex') == '0.1.1+metax3.9.0.8torch2.10', before.get('mctlassex')
private = {}
for line in (plugin/'requirements/maca_private.txt').read_text().splitlines():
    line = line.split('#',1)[0].strip()
    if not line or line.startswith('-'):
        continue
    req = Requirement(line)
    name = canonicalize_name(req.name)
    if name in before:
        private[name] = before[name]
for name, version in before.items():
    if '+metax' in version or '+maca' in version:
        private[name] = version
lock = root/'evidence/private_constraints.txt'
lock.write_text(''.join(f'{k}=={v}\n' for k,v in sorted(private.items())))
(root/'evidence/packages_before_build.json').write_text(json.dumps(before,indent=2))
extra = root/'evidence/maca_public_extra.txt'
extra.write_text('\n'.join(line for line in (plugin/'requirements/maca.txt').read_text().splitlines()
                           if line.strip() and not line.strip().startswith(('#','-r'))) + '\n')

env = os.environ.copy()
for key in ['HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','http_proxy','https_proxy','all_proxy','PYTHONPATH']:
    env.pop(key,None)
env.update(USE_PRECOMPILED_KERNEL='1',MAX_JOBS='16',PIP_DISABLE_PIP_VERSION_CHECK='1',
           VLLM_USE_RUST_FRONTEND='0',VLLM_REQUIRE_RUST_FRONTEND='0')
env['PATH'] = '/opt/maca/tools/cu-bridge/tools:/opt/maca/tools/cu-bridge/bin:' + env['PATH']
env['CUCC_PATH'] = '/opt/maca/tools/cu-bridge'
env.update(CUCC_CMAKE_ENTRY='2',CUBRIDGE_HOME='/opt/glm53-build-tools',
           CUDA_HOME='/opt/glm53-build-tools/cu-bridge/CUDA_DIR')

def run(args, cwd=None, extra=None):
    print('RUN', args, flush=True)
    subprocess.run(args,cwd=cwd,env={**env,**(extra or {})},check=True)

if '--plugin-only' not in sys.argv:
    # Keep the vendor ABI packages pinned during public dependency resolution.
    run([sys.executable,'-m','pip','install','--index-url','https://pypi.tuna.tsinghua.edu.cn/simple',
         '--timeout','60','--retries','8',
         '--find-links','/wheelhouse','--find-links','/wheelhouse/public','-c',str(lock),'-r',str(plugin/'requirements/common.txt'),
         '-r',str(plugin/'requirements/build.txt'),'-r',str(extra)])
    run([sys.executable,'-m','pip','uninstall','-y','vllm','vllm-metax'])
    run([sys.executable,'-m','pip','install','--no-deps','--no-build-isolation','-e',str(upstream)],
        cwd=upstream,extra={'VLLM_TARGET_DEVICE':'empty'})
else:
    assert before['vllm'].startswith('0.32.0'), before['vllm']
run([sys.executable,'-m','pip','install','--no-deps','--no-build-isolation','-e',str(plugin)],cwd=plugin)
after = installed()
assert all(after.get(k)==v for k,v in private.items()), 'Private dependency drift'
(root/'evidence/packages_after_build.json').write_text(json.dumps(after,indent=2))
print('FRAMEWORK_INSTALL_FINISHED',flush=True)
