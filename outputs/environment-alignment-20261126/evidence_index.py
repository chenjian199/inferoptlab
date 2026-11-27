import json,os,socket
from pathlib import Path
host=socket.gethostname()[-3:]
roots={'060':['/home/ubuntu/CJ_workspace/glm53-vllm-build-20261124','/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/evidence'],
 '061':['/data/glm53/work/evidence','/data/glm53/work/scripts','/home/ubuntu/LYQ_workspace'],
 '064':['/home/ubuntu/c500-glm-rebuild-20261124/runtime-evidence','/data/c500-operator-reproduction-20261125'],
 '065':['/home/ubuntu/DCC_workspace/inferoptlab/experiments/evidence','/data/heyi/c500-glm5.3/restore-20261124/evidence']}
files=[]
prune={'.git','.venv','venv','__pycache__','node_modules','cache','.cache','models','src','site-packages','modelscope-download-venv','triton','aiperf','observations'}
for root in roots.get(host,[]):
 if not Path(root).is_dir():continue
 for folder,dirs,names in os.walk(root):
  dirs[:]=[d for d in dirs if d not in prune and not d.startswith('triton-')]
  if len(Path(folder).relative_to(root).parts)>8:dirs.clear();continue
  for name in names:
   p=Path(folder)/name
   if p.suffix.lower() not in {'.log','.json','.md','.sh','.yaml','.py','.txt'}:continue
   try:st=p.stat();files.append(dict(path=str(p),bytes=st.st_size,mtime=st.st_mtime))
   except OSError:pass
print(json.dumps(files))
