"""Generate input-only fixtures and run the reproducible reference smoke suite."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from test_harness import CASES

p=argparse.ArgumentParser()
p.add_argument('output',type=Path)
a=p.parse_args()
root=a.output
root.mkdir(parents=True,exist_ok=False)
inputs=root/'inputs'
inputs.mkdir()
runs=root/'runs'
runs.mkdir()
harness=Path(__file__).resolve().with_name('harness.py')
cases={**CASES, 'timeout': {'alphabet':list('abcdefghi'),'positive':[['a']],'negative':[['a']]}}
for name,d in cases.items():
    f=inputs/(name+'.json')
    f.write_text(json.dumps(d,separators=(',',':'))+'\n')
    cmd=[sys.executable,'-B',str(harness),str(f),str(runs/name)]
    if name=='timeout':
        cmd+=['--seconds','0.000001']
    subprocess.run(cmd,check=True)
rows=[]
for f in sorted(runs.glob('*/summary.json')):
    d=json.loads(f.read_text())
    rows.append({'case':f.parent.name,**d})
    if f.parent.name=='timeout':
        if d['producer']['process_status']!='TIMEOUT' or d['structural_gap'] is not None:
            raise RuntimeError('expected censored timeout; very fast hosts may need a larger corpus')
    elif d['verifier'].get('result',{}).get('status')!='VERIFIED':
        raise RuntimeError('unverified smoke case: '+f.parent.name)
(root/'measurements.json').write_text(json.dumps(rows,indent=2)+'\n')
