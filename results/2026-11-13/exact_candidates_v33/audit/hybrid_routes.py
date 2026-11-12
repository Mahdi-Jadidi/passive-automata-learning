"""Untimed independent branch-predicate diagnostic for frozen timing corpus."""
import json,sys
from pathlib import Path
import check_contract as cc
HERE=Path(__file__).resolve().parent
source=Path(sys.argv[1]).resolve(); sha=sys.argv[2].lower()
assert cc.digest(source)==sha
assert cc.digest(HERE/'timing_cases.jsonl')=='013e2b60dc1d5740d766a9b0f77c458c4fbb92f203ee67977f3fe7104b48215b'
mod=cc.load(source,'route_diagnostic_hybrid')
rows=[json.loads(s) for s in (HERE/'timing_cases.jsonl').read_text(encoding='utf8').splitlines()]
out=[]
for row in rows:
    a,p,n=mod._ref._normalize(row['input'])
    if set(p)&set(n): route='contradiction'
    elif mod._c030._certified_all(a,p,n) is not None: route='singleton_certificate'
    else:
        owners,q=mod._graph._components(a,p,n); finest=mod._graph._expand(owners,tuple(range(q)))
        route='atom_certificate' if mod._ref._candidate(a,p,n,finest) is not None else 'dp_fallback'
    out.append({'case':row['case'],'route':route})
print(json.dumps({'source_sha256':sha,'diagnostic':'untimed predicate replay, not timed instrumentation','cases':out},ensure_ascii=False))
