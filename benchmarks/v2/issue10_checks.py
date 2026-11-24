"""Reproduce telemetry and P1 benchmark replay corruption checks."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
from harness import pinned_source, observe_oracle, encode
from sparse_bench import replay


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('legacy',type=Path); p.add_argument('scale_run',type=Path); a=p.parse_args()
    sys.path.insert(0,str(pinned_source(a.legacy,True)))
    from model import ProjectionOracle
    from sample import DeadlineExpired
    with tempfile.TemporaryDirectory() as t:
        events=Path(t)/'events.jsonl'; old=ProjectionOracle.__call__
        try:
            ProjectionOracle.__call__=observe_oracle(old,events)
            o=ProjectionOracle(((0,1),),((1,0),),lambda:None)
            r1=o((1,2),'regular'); r2=o((3,),'regular')
            def timeout(): raise DeadlineExpired
            o=ProjectionOracle(((0,1),),((1,0),),timeout)
            try: o((1,2),'regular')
            except DeadlineExpired: pass
            else: raise RuntimeError('expected interrupted query')
            rows=[json.loads(l) for l in events.read_text().splitlines()]
            if ([x['status'] for x in rows if 'status' in x]!=[r1['status'],r2['status']] or
                [x['response_bytes'] for x in rows if 'response_bytes' in x]!=[len(encode(r1)),len(encode(r2))] or
                len(rows)!=5 or rows[-1]!={'attempt':[1,2]}):
                raise RuntimeError('bad telemetry')
            print(json.dumps(rows)); print('actual simulator complete+interrupted telemetry PASS')
        finally: ProjectionOracle.__call__=old
    d=json.loads((a.scale_run/'input.json').read_bytes()); c=json.loads((a.scale_run/'proof.json').read_bytes())
    if replay(d,c)['status']!='VERIFIED_STRUCTURAL_OPTIMUM': raise RuntimeError('valid proof failed')
    for tag, mutate in [('digest',lambda x:x.update(sample_digest='bad')),('edge',lambda x:x['edges'][0].__setitem__(2,-1)),('owner',lambda x:x['owner'].__setitem__(1,1)),('separator',lambda x:x['separating_groups'].__setitem__(0,999))]:
        b=deepcopy(c); mutate(b)
        try: replay(d,b)
        except ValueError as e: print(tag,'rejected:',e)
        else: raise RuntimeError(tag+' accepted')


if __name__=='__main__': main()
