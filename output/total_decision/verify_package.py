"""Fast integrity and interface check; full audits are separate commands."""
from pathlib import Path
import ast,json,hashlib,zipfile
from total_selector import decide
from bounded_policy import choose
from rpni_work_reference import run,split_run

root=Path(__file__).parent
tree=ast.parse((root/'static_selector.py').read_text(encoding='utf8'))
imports=set()
for node in ast.walk(tree):
    if isinstance(node,ast.Import):imports.update(a.name for a in node.names)
    if isinstance(node,ast.ImportFrom):imports.add(node.module)
assert imports<={'math','collections','json','sys'},imports

samples={
    'distinct_word_split':dict(positive=['abcd'],negative=[],blocks=[['a','b'],['c','d']]),
    'local_informative':dict(positive=['aa'],negative=['ba'],blocks=[['b'],['a']]),
    'unary_global_net':dict(positive=['aa'],negative=['bb','bbb'],blocks=[['a'],['b']]),
    'root_only':dict(positive=[''],negative=[],blocks=[['a'],['b']]),
    'nontrivial_tie':dict(positive=['abcde'],negative=[],blocks=[['a','b'],['c','d','e']]+[[a] for a in 'fghijklmnop']),
    'unary_informative':json.loads((root/'counterexample_unary_informative.json').read_text(encoding='utf8')),
}
results={}
for name,x in samples.items():
    P,Q,B=x['positive'],x['negative'],x['blocks']
    g=run(P,Q)['W'];s=split_run(P,Q,B)['W']
    result=decide(P,Q,B);static=decide(P,Q,B,exact_fallback=False)
    expected='GLOBAL' if g<s else 'SPLIT' if s<g else 'TIE'
    assert result['status']==expected
    policy=choose(P,Q,B);w=g if policy['action']=='GLOBAL' else s
    assert w-min(g,s)<=policy['excess_pipeline_work_bound']
    results[name]=dict(input=x,result=result,static_result=static,WG=g,WS=s)
assert results['distinct_word_split']['result']['static_certificate']['decision']=='NET_SPLIT_EQUAL'
assert (results['distinct_word_split']['WG'],results['distinct_word_split']['WS'])==(146,112)
assert results['local_informative']['result']['training_started'] is False
assert results['local_informative']['result']['static_certificate']['selector_work']==12
assert results['unary_global_net']['result']['static_certificate']['decision']=='NET_GLOBAL_COST'
assert (results['unary_global_net']['WG'],results['unary_global_net']['WS'])==(43,60)
assert results['nontrivial_tie']['WG']==results['nontrivial_tie']['WS']==209
assert results['unary_informative']['static_result']['status']=='UNKNOWN'
assert (results['unary_informative']['WG'],results['unary_informative']['WS'])==(316,315)
assert results['unary_informative']['result']['training_started'] is True

new=json.loads((root/'audit_results.json').read_text(encoding='utf8'))
old=json.loads((root/'extension_audit_results.json').read_text(encoding='utf8'))
assert new['status']==old['status']=='passed'
assert new['valid_case_executions']==12866 and old['valid_case_executions']==3119
assert new['old_decisions']['UNKNOWN']-new['new_decisions']['UNKNOWN']==9720
assert new['independent_candidate_checks']+old['independent_candidate_checks']==61534
(root/'worked_examples.json').write_text(json.dumps(results,indent=2,ensure_ascii=False),encoding='utf8')
# Refresh the old search output against the final implementation.
(root/'counterexample_unary_informative_result.json').write_text(
    json.dumps(results['unary_informative'],indent=2,ensure_ascii=False),encoding='utf8')

paths=sorted(p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts
             and p.name not in {'manifest.json','Total_Decision_Research.zip'})
manifest={str(p.relative_to(root)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
(root/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
archive=root/'Total_Decision_Research.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p in paths:z.write(p,p.relative_to(root))
    z.write(root/'manifest.json','manifest.json')
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for name,digest in manifest.items():assert hashlib.sha256(z.read(name)).hexdigest()==digest
print(json.dumps(dict(status='passed',case_executions=15985,independent_candidate_checks=61534,
                      packaged_files=len(paths)+1,archive_bytes=archive.stat().st_size),indent=2))
