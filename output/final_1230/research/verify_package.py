"""Fast package/interface checks. Full mathematical audits are separate."""
from pathlib import Path
import ast,json,hashlib,zipfile
from compiled_selector import CompiledSelector
from static_selector import select
from total_selector import decide
from rpni_work_reference import run,split_run

root=Path(__file__).parent
for name,allowed in [('static_selector.py',{'math','collections','json','sys'}),
                     ('compiled_selector.py',{'pathlib','json','hashlib','sys'})]:
    imports=set()
    for node in ast.walk(ast.parse((root/name).read_text(encoding='utf8'))):
        if isinstance(node,ast.Import):imports.update(a.name for a in node.names)
        if isinstance(node,ast.ImportFrom):imports.add(node.module)
    assert imports<=allowed,(name,imports)

reports=[json.loads((root/name).read_text(encoding='utf8')) for name in
         ('audit_results.json','extension_audit_results.json','tree_audit_results.json','compiled_audit_results.json','amortized_audit_results.json')]
assert all(r['status']=='passed' for r in reports)
assert sum(r['independent_candidate_checks'] for r in reports)==174998
assert reports[0]['valid_case_executions']==12866
assert reports[1]['valid_case_executions']==3119
assert reports[2]['case_executions']==738 and reports[3]['all_domain_inputs_checked']==2187
assert reports[4]['case_executions']==36714

table=CompiledSelector(root/'table_binary_length2.json')
assert table.data['reference_sha256']==hashlib.sha256((root/'rpni_work_reference.py').read_bytes()).hexdigest()
assert table.data['counts']=={'GLOBAL':754,'SPLIT':493,'TIE':15,'GLOBAL_ONLY':925}
assert table.data['offline_work']==405921 and table.setup_work==2215
x=json.loads((root/'compiled_example.json').read_text(encoding='utf8'))
r=table.query(x['positive'],x['negative'])
assert r['status']=='SPLIT' and not r['training_started']
assert (r['global_work'],r['split_work'],r['query_work'])==(387,78,7)
assert table.query(['aaa'],[])['status']=='OUT_OF_DOMAIN'

examples=json.loads((root/'worked_examples.json').read_text(encoding='utf8'))
for example in examples.values():
    x=example['input'];P,Q,B=x['positive'],x['negative'],x['blocks']
    assert select(P,Q,B)==example['certificate']
    assert run(P,Q)['W']==example['WG'] and split_run(P,Q,B)['W']==example['WS']
assert examples['new_split_n4']['certificate']['decision']=='NET_SPLIT_EQUAL'
assert (examples['new_split_n4']['WG'],examples['new_split_n4']['WS'])==(466,170)
assert examples['new_split_n4']['certificate']['selector_work']==99
assert examples['new_split_n4']['certificate']['global_interval'][0]==274
counter=json.loads((root/'counterexample_unary_informative.json').read_text(encoding='utf8'))
assert decide(counter['positive'],counter['negative'],counter['blocks'],False)['status']=='UNKNOWN'
assert decide(counter['positive'],counter['negative'],counter['blocks'])['status']=='SPLIT'

paths=sorted(p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts
             and p.name not in {'manifest.json','Research_1230.zip'})
manifest={str(p.relative_to(root)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
(root/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
archive=root/'Research_1230.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p in paths:z.write(p,p.relative_to(root))
    z.write(root/'manifest.json','manifest.json')
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for name,digest in manifest.items():assert hashlib.sha256(z.read(name)).hexdigest()==digest
print(json.dumps(dict(status='passed',case_executions=55624,independent_candidate_checks=174998,
                      archive_bytes=archive.stat().st_size,packaged_files=len(paths)+1),indent=2))
