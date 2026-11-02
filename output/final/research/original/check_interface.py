from pathlib import Path
import json
from defense_selector import select

cases=[
    ({'ab','ba'},{'c'},['a','b','c'],'NET_SPLIT'),
    ({'a','aa'},{'aaa'},['a','b'],'NET_GLOBAL'),
    ({''},set(),['a','b'],'COST_ONLY'),
    ({'ab','ba'},set(),['a','b'],'UNKNOWN'),
    ({'ab'},{'ba'},['a','b'],'INFEASIBLE')]
results=[]
for pos,neg,blocks,expected in cases:
    r=select(pos,neg,blocks)
    assert r['status']==expected,r
    results.append({'positive':sorted(pos),'negative':sorted(neg),'blocks':blocks,'result':r})
Path(__file__).with_name('interface_checks.json').write_text(json.dumps(results,indent=2),encoding='utf8')
print('All five presentation-facing certificate statuses verified.')
