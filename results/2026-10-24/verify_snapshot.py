"""Read-only checks of archived hashes, stored audit status and one current example."""
from pathlib import Path
import hashlib,json,sys
sys.dont_write_bytecode=True
root=Path(__file__).resolve().parent
manifest=json.loads((root/'INTEGRITY_SHA256.json').read_text(encoding='utf8'))
for name,digest in manifest.items():
    path=root/name
    assert path.is_file(),('missing',name)
    assert hashlib.sha256(path.read_bytes()).hexdigest()==digest,('changed',name)
sys.path.insert(0,str(root/'research'))
from static_selector import select
from rpni_work_reference import run,split_run
x=json.loads((root/'research/two_trace_example.json').read_text(encoding='utf8'))
c=select(x['positive'],x['negative'],x['blocks'])
assert c['decision']=='NET_SPLIT_EQUAL'
assert c['selector_work']==99 and c['global_interval'][0]==274 and c['split_interval']==[170,170]
assert run(x['positive'],x['negative'])['W']==466
assert split_run(x['positive'],x['negative'],x['blocks'])['W']==170
names=['audit_results.json','extension_audit_results.json','tree_audit_results.json','compiled_audit_results.json','amortized_audit_results.json']
r=[json.loads((root/'research'/n).read_text(encoding='utf8')) for n in names]
assert all(a['status']=='passed' for a in r)
assert sum(a['independent_candidate_checks'] for a in r)==174998
cases=r[0]['valid_case_executions']+r[1]['valid_case_executions']+r[2]['case_executions']+r[3]['all_domain_inputs_checked']+r[4]['case_executions']
assert cases==55624
print(json.dumps(dict(status='passed',files_checked=len(manifest),stored_case_executions=cases,stored_independent_candidate_checks=174998,example='99+170=269<274<=WG; reference WG=466',full_audits_rerun=False),indent=2))
