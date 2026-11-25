import json,os,pathlib,subprocess,time,urllib.request
root=pathlib.Path(__file__).parent
state={"status":"waiting_for_qualification"}
path=root/"experiments/evidence/pipeline-smoke-launch.json"
def save():path.write_text(json.dumps(state,indent=2))
save()
deadline=time.monotonic()+10800
while time.monotonic()<deadline:
 try:
  driver=json.loads((root/"qualification-driver.json").read_text())
  if len(driver.get("stages",[]))==5 and driver.get("restore_exit")==0:break
 except (OSError,ValueError):pass
 time.sleep(5)
else:
 state["status"]="qualification_wait_timeout";save();raise SystemExit(1)
original="inferoptlab-glm53-vllm-r1"
info=json.loads(subprocess.check_output(["docker","inspect",original]))[0]
assert info["Config"]["Labels"].get("io.inferoptlab.task")=="glm53-source-reproduction"
assert info["Image"]=="sha256:9d82e3b3cc52430770a02b00d8c763b62e9c8bc64c4be871d9be25148e4fdf8b"
restore=info["State"]["Running"]
env=os.environ.copy();env["PYTHONPATH"]=str(root/".host-deps")
command=["python3","tools/deployment/metax-vllm/run_scan.py","--client-root","/home/ubuntu/CJ_workspace/inferoptlab-client-20261124","--client-image","sha256:43af58b15b63b6095611b257590466632433d6786d66386839e1c5b8027d30ad","run","recipes/plans/benchmark/glm53-vllm/08-pipeline.yaml","--qualification","experiments/evidence/startup-r2/00-layout/qualification.json"]
state.update(status="running",command=command,restore_required=restore);save()
try:
 if restore:subprocess.run(["docker","stop","--time","30",original],check=True)
 with (root/"pipeline-smoke.log").open("wb") as log:
  result=subprocess.run(command,cwd=root,env=env,stdout=log,stderr=subprocess.STDOUT)
 state.update(exit=result.returncode,status="completed" if result.returncode==0 else "failed");save()
finally:
 if restore:
  result=subprocess.run(["docker","start",original]);state["restore_exit"]=result.returncode;save()
  end=time.monotonic()+900
  state["restored_http_ready"]=False
  while time.monotonic()<end:
   try:
    with urllib.request.urlopen("http://127.0.0.1:18081/health",timeout=3) as response:
     if response.status==200:state["restored_http_ready"]=True;break
   except OSError:pass
   time.sleep(5)
  save()
