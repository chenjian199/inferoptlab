import argparse
from pathlib import Path
import subprocess
import time

parser=argparse.ArgumentParser();parser.add_argument('host');parser.add_argument('job');parser.add_argument('--timeout',type=int,default=120);args=parser.parse_args()
root=Path(__file__).resolve().parent
for attempt in range(3):
    p=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=8','-o','ServerAliveInterval=5',
                      '-o','ServerAliveCountMax=2','metax-'+args.host,'python3 -'],
                     input=(root/(args.job+'.py')).read_bytes(),capture_output=True,timeout=args.timeout)
    if p.returncode==0:
        destination=root/(args.host+'-'+args.job+'.json');destination.write_bytes(p.stdout)
        print(str(destination),len(p.stdout));break
    if attempt==2:raise SystemExit(p.stderr.decode(errors='replace'))
    time.sleep(2)
