from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import ast,hashlib,json
from extended_selector import select
from rpni_work_reference import run,split_run
from independent_oracle import oracle_learner,exact_equivalent,independent_accept
from deletion_budget import bound

root=Path(__file__).parent
tree=ast.parse((root/'extended_selector.py').read_text(encoding='utf8'))
imports=[n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
imports +=[a.name for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names]
assert set(imports)<={'math','collections','json','sys'},imports
audit=json.loads((root/'extension_audit_results.json').read_text(encoding='utf8'))
assert audit['status']=='passed' and audit['valid_case_executions']==3119
assert audit['independent_candidate_checks']==13425 and audit['invalid_inputs_rejected']==5
assert sum(audit['decisions'].values())==3119
for n,R in [(3,2),(4,7),(5,22),(6,71)]:
    assert all(bound(n,r)['guaranteed_net_split'] for r in range(1,R+1))
for name in ('incomplete_net_equal','informative_net_cost','simple_informative_global'):
    x=json.loads((root/(name+'.json')).read_text(encoding='utf8'))
    c=select(x['positive'],x['negative'],x['blocks'])
    assert c==json.loads((root/(name+'_certificate.json')).read_text(encoding='utf8'))
    H=c['selector_work'];g=run(x['positive'],x['negative']);s=split_run(x['positive'],x['negative'],x['blocks'])
    if name=='incomplete_net_equal':assert (H,c['global_interval'][0],s['W'])==(142,269,124)
    if name=='informative_net_cost':assert (H,c['global_interval'][0],c['split_interval'][1])==(530,3109,594)
    if name=='simple_informative_global':assert (H,g['W'],s['W'])==(12,25,41)
    if 'SPLIT' in c['decision']:assert H+s['W']<g['W']
    else:assert H+g['W']<s['W']

x=json.loads((root/'quality_counterexample.json').read_text(encoding='utf8'))
g=run(x['positive'],x['negative']);s=split_run(x['positive'],x['negative'],x['blocks'])
assert oracle_learner(set(x['positive']),set(x['negative']))[0]==g['model']
eq,w=exact_equivalent(g['model'],[r['model'] for r in s['runs']],x['blocks'])
assert not eq and w==x['witness']==''
assert independent_accept(g['model'],'') and not all(independent_accept(r['model'],'') for r in s['runs'])
def serialize(m):
    states,edges,finals,start=m
    return dict(states=sorted(states),initial=start,finals=sorted(finals),
                transitions=[dict(source=q,symbol=a,target=t) for (q,a),t in sorted(edges.items())])
payload=dict(input={k:x[k] for k in ('positive','negative','blocks')},witness=w,
             global_model=serialize(g['model']),factor_models=[serialize(r['model']) for r in s['runs']],
             certificate=select(x['positive'],x['negative'],x['blocks']),
             conclusion='Global accepts epsilon; the a factor rejects epsilon. Net cost does not imply language equality.')
(root/'quality_counterexample_models.json').write_text(json.dumps(payload,indent=2),encoding='utf8')
files=sorted(p for p in root.iterdir() if p.is_file() and p.name not in ('manifest.json','Extensions_Package.zip'))
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(root/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
with ZipFile(root/'Extensions_Package.zip','w',ZIP_DEFLATED) as z:
    for p in files+[root/'manifest.json']:z.write(p,p.name)
with ZipFile(root/'Extensions_Package.zip') as z:
    for name,digest in manifest.items():assert hashlib.sha256(z.read(name)).hexdigest()==digest
print(json.dumps(dict(status='passed',valid_cases=3119,independent_candidate_checks=13425,
                     learner_imports_in_selector=False,files=len(files)+1,
                     package_bytes=(root/'Extensions_Package.zip').stat().st_size),indent=2))
