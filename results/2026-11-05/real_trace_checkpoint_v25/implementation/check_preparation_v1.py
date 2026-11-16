"""Adapter structural/replay checks and C017 helper unit controls, no real-data inference."""
import hashlib,json,py_compile,sys,zipfile
from pathlib import Path
import prepare_recorded_v1 as adapter
import contexts_c017_copy_v1 as contexts
HERE=Path(__file__).resolve().parent;OUT=HERE.parent/'inventory/prepared_v1'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(name):return json.loads((OUT/name).read_text(encoding='utf-8'))
def main():
    for p in HERE.glob('*.py'):py_compile.compile(str(p),doraise=True)
    assert adapter.label(2,True,True)==(None,'unknown')
    assert adapter.label(True,True,True)[0] is None
    assert adapter.label(3,True,True)[0] is False
    assert adapter.label(None,False,True)[0] is None
    try:adapter.literal(b'__import__("os")')
    except ValueError:pass
    else:raise AssertionError('executable expression accepted')
    toy={'alphabet':['x','u'],'traces':[{'file_id':1,'events':[{'id':'x','outcome':True},{'id':'u','outcome':None},{'id':'x','outcome':False}]}]}
    assert not contexts.evaluate_block(toy,['x','u'],0)['consistent']
    assert contexts.evaluate_block(toy,['x','u'],1)['consistent']
    assert contexts.evaluate_block(toy,['x','u'],'full')['consistent']
    reset={'alphabet':['x'],'traces':[{'file_id':1,'events':[{'id':'x','outcome':True}]},{'file_id':2,'events':[{'id':'x','outcome':False}]}]}
    assert not contexts.evaluate_block(reset,['x'],'full')['consistent']
    manifest=read('manifest.json');assert manifest['status']=='prepared_observations_only'
    for name,sha in manifest['output_hashes'].items():assert digest(OUT/name)==sha
    observations=read('observations.json');qualified=read('observations_target_qualified.json')
    contexts.validate(observations);contexts.validate(qualified)
    faithful=read('faithful_records_and_metadata.json')['traces'];dictionary=read('token_dictionary.json')
    qualified_dict=read('target_qualified_dictionary_metadata.json')['dictionary']
    assert len(observations['traces'])==len(qualified['traces'])==len(faithful)
    unknown=0;total=0;final=0
    for trace,qtrace,raw in zip(observations['traces'],qualified['traces'],faithful):
        assert trace['file_id']==qtrace['file_id']==raw['trace_id']
        assert len(trace['events'])==len(qtrace['events'])==len(raw['events'])
        for index,(event,qevent,record) in enumerate(zip(trace['events'],qtrace['events'],raw['events'])):
            assert set(event)=={'id','outcome'} and event['outcome']==qevent['outcome']==record['outcome']
            assert event['id']==record['token_id'] and qevent['id']==record['target_qualified_token_id']
            assert record['event_index']==index
            assert set(dictionary[event['id']])<= {'action','exploit_class','exploit_port'}
            assert record['raw_true_state_read_for_tokenization'] is False
            assert qualified_dict[qevent['id']]['action']==dictionary[event['id']]['action']
            total+=1;unknown+=event['outcome'] is None;final+=record['outcome_reason']=='final_action_no_next_observation'
    with zipfile.ZipFile(adapter.ARCHIVE) as z:
        for source in manifest['sources']:
            pool=sorted(n for n in z.namelist() if n.startswith(adapter.POOLS[source['scenario']][0]) and n.endswith(adapter.POOLS[source['scenario']][1]))
            assert [f['archive_member'] for f in source['files']]==pool[:6]
            for f in source['files']:assert hashlib.sha256(z.read(f['archive_member'])).hexdigest()==f['sha256']
    result=dict(passed=True,scope='structural checks, authenticated byte replay, label policy and toy helper unit controls only; no real-data context or solver runs',
                events=total,unlabelled_events=unknown,retained_final_cage_events=final,python=sys.version,
                adapter_sha256=digest(HERE/'prepare_recorded_v1.py'),c017_copy_sha256=digest(HERE/'contexts_c017_copy_v1.py'))
    (HERE/'checks_v1.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
if __name__=='__main__':main()
