import json,subprocess,pathlib,time,os
os.environ["PYTHONPATH"]=str(pathlib.Path(__file__).parent/".host-deps")
root=pathlib.Path(__file__).parent
original="inferoptlab-glm53-vllm-r1"
info=json.loads(subprocess.check_output(["docker","inspect",original]))[0]
assert info["Image"]=="sha256:9d82e3b3cc52430770a02b00d8c763b62e9c8bc64c4be871d9be25148e4fdf8b"
assert info["Config"]["Labels"].get("io.inferoptlab.task")=="glm53-source-reproduction"
restore=info["State"]["Running"]
state={"original_container":original,"restore_required":restore,"stages":[]}
def save(): (root/"qualification-driver.json").write_text(json.dumps(state,indent=2))
save()
try:
 if restore: subprocess.run(["docker","stop","--time","30",original],check=True)
 for name in ["00-layout","01-scheduling","02-context64k","03-context128k","04-cache"]:
  dest=root/"experiments/evidence/startup-r2"/name
  cmd=["python3","-u","-m","benchmark.load","qualify",f"recipes/plans/benchmark/glm53-vllm/{name}.yaml","--out",str(dest)]
  print("STAGE",name,flush=True)
  result=subprocess.run(cmd,cwd=root)
  state["stages"].append({"stage":name,"exit":result.returncode});save()
finally:
 if restore:
  result=subprocess.run(["docker","start",original]);state["restore_exit"]=result.returncode
 save()
