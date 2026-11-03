"""Exclusive persistent launch marker prevents a second auditor/master launch."""
import json,os,time
from pathlib import Path
def claim(audit):
    runs=audit/'runs'
    if runs.exists() and any(runs.iterdir()):raise RuntimeError('Existing run detected; inspect coordination/ledger, do not duplicate')
    marker=audit/'RUN_STARTED_V1.json'
    with marker.open('x',encoding='utf-8') as f:
        json.dump({'pid':os.getpid(),'epoch':time.time(),'status':'launch_claimed','note':'Persistent; failed/partial runs also require explicit reviewed continuation, never deletion.'},f);f.flush();os.fsync(f.fileno())
    return marker
