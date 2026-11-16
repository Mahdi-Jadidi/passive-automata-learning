"""Bounded read-only archived observations; no artifact execution or AND conversion."""
import ast
from collections import Counter
import hashlib,json,platform,sys,time,zipfile
from pathlib import Path
import yaml

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
OUT=HERE.parent/'inventory/prepared_v1'
ARCHIVE=ROOT/'.cache/lancer/cas-artifact-cav2026_20261103T211638Z.zip'
EXPECTED='06039a2cb4c8a5e2230aa7681f2b7e09914ce7ce44a7721b272a437ce2daef76'
POOLS={
 'cage2_raw':('artifact/data/cage2/cage2_raw_traces/','.yaml'),
 'baby_random15':('artifact/data/one_host_network_validity_only/trial_1/random_15steps/training_traces/','.txt'),
 'baby_heuristic15':('artifact/data/one_host_network_validity_only/trial_1/heuristic_15steps/training_traces/','.txt')}
def digest(raw):return hashlib.sha256(raw).hexdigest()
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def filehash(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def literal(raw):
    tree=ast.parse(raw.decode('utf-8'),mode='eval');todo=[(tree,0)];count=0
    while todo:
        node,depth=todo.pop();count+=1
        if count>200000 or depth>50:raise ValueError('literal structural budget')
        if not isinstance(node,(ast.Expression,ast.List,ast.Tuple,ast.Dict,ast.Constant,ast.Load)):
            raise ValueError('unsupported literal node')
        todo.extend((c,depth+1) for c in ast.iter_child_nodes(node))
    return ast.literal_eval(tree)
def label(code,present,raw):
    if raw:
        if present and type(code) is int and code==1:return True,'known_success'
        if present and type(code) is int and code==3:return False,'known_failure'
        return None,('unknown' if type(code) is int and code==2 else 'missing_or_unsupported')
    if present and code=='TRUE':return True,'published_success'
    if present and code=='FALSE':return False,'published_failure'
    return None,'missing_or_unsupported'

def main():
    OUT.mkdir(parents=True,exist_ok=False);started=time.perf_counter()
    report=dict(status='started',command='py -3.14 results/2026-11-05/real_trace_checkpoint_v25/implementation/prepare_recorded_v1.py',
                python=sys.version,platform=platform.platform(),yaml_version=yaml.__version__,archive=str(ARCHIVE),
                original_artifact_executed=False,solver_runs=0,errors=[],sources=[])
    try:
        before=ARCHIVE.stat();sha=filehash(ARCHIVE)
        if sha!=EXPECTED:raise ValueError('archive checksum mismatch')
        report.update(archive_sha256=sha,archive_bytes=before.st_size)
        vocab={};key_ids={};traces=[];faithful=[];exclusions=[]
        target_vocab={};target_traces=[];aliases={}
        with zipfile.ZipFile(ARCHIVE) as z:
            names=[i.filename for i in z.infolist()];counts=Counter(names)
            report['zip_members']=len(names)
            for scenario,(prefix,suffix) in POOLS.items():
                pool=sorted(n for n in names if n.startswith(prefix) and n.endswith(suffix))
                selected=pool[:6]
                if len(selected)!=6:raise ValueError('not six available sources')
                exclusions.extend(dict(scenario=scenario,archive_member=n,reason='outside_fixed_first_six_lexicographic_subset') for n in pool[6:])
                source=dict(scenario=scenario,pool_files=len(pool),selection='first six full archive paths sorted lexicographically; not numeric',
                            provenance='recorded simulator-generated cybersecurity benchmark, not production telemetry',files=[])
                for member in selected:
                    if counts[member]!=1:raise ValueError('duplicate archive member')
                    info=z.getinfo(member)
                    if info.file_size>2*1024*1024:raise ValueError('member >2MiB')
                    raw=z.read(member);data=yaml.safe_load(raw.decode('utf-8')) if scenario=='cage2_raw' else literal(raw)
                    if not isinstance(data,list):raise ValueError('expected list root')
                    file_id=len(report['sources'])*6+len(source['files'])+1
                    item=dict(file_id=file_id,archive_member=member,sha256=digest(raw),bytes=len(raw),zip_crc32=f'{info.CRC:08x}',
                              format='safe YAML' if scenario=='cage2_raw' else 'bounded Python literal',episodes=[],outcomes={})
                    outcomes=Counter()
                    episodes=[data] if scenario=='cage2_raw' else data
                    for ei,episode in enumerate(episodes):
                        if not isinstance(episode,list):raise ValueError('episode not list')
                        events=[];target_events=[];local=[]
                        for si,step in enumerate(episode):
                            if scenario=='cage2_raw':
                                if not isinstance(step,dict):raise ValueError('raw step not dict')
                                pairs=[(actor,step[actor]) for actor in ('Blue','Red')]
                            else:
                                if not isinstance(step,list) or len(step)!=2 or [x.get('agent') for x in step]!=['Blue','Red']:
                                    raise ValueError('processed Blue/Red pair schema')
                                if step[0].get('episode')!=step[1].get('episode') or step[0].get('step')!=step[1].get('step'):
                                    raise ValueError('processed pair boundary disagreement')
                                pairs=list(zip(('Blue','Red'),step))
                            for actor,event in pairs:
                                action=event['action'] if scenario=='cage2_raw' else {k:v for k,v in event.items() if k not in ('episode','step','agent','success')}
                                if not isinstance(action,dict):raise ValueError('action must be dictionary')
                                name=action.get('type') if scenario=='cage2_raw' else action.get('action')
                                if not isinstance(name,str) or not name:raise ValueError('action name not nonempty string')
                                # Explicit action-only abstraction: identity is withheld, not inferred.
                                description={'action':name}
                                for field in ('exploit_class','exploit_port'):
                                    if field in action and action[field] is not None:description[field]=action[field]
                                key=canonical(description);opaque='e'+digest(key.encode())
                                if opaque in key_ids and key_ids[opaque]!=key:raise ValueError('token digest collision')
                                key_ids[opaque]=key;vocab[opaque]=description
                                target={k:action[k] for k in ('hostname','ip_address','subnet','subnetname') if k in action}
                                qualified={**description,'observed_target_fields':target}
                                target_key=canonical(qualified);target_id='q'+digest(target_key.encode())
                                if target_id in target_vocab and target_vocab[target_id]!=qualified:raise ValueError('qualified collision')
                                target_vocab[target_id]=qualified
                                aliases.setdefault(opaque,set()).add(canonical(target))
                                if scenario=='cage2_raw':
                                    next_obs=episode[si+1][actor]['obs'] if si+1<len(episode) else {}
                                    present='prev_action_status' in next_obs;code=next_obs.get('prev_action_status')
                                    y,reason=label(code,present,True)
                                    if si+1==len(episode):reason='final_action_no_next_observation'
                                    loc={'step_index':si,'actor':actor,'outcome_step_index':si+1 if si+1<len(episode) else None}
                                    boundary={'raw_step':step.get('step'),'episode_value':None,'episode_boundary_evidence':'file only; reset unverified'}
                                else:
                                    present='success' in event;code=event.get('success');y,reason=label(code,present,False)
                                    loc={'episode_index':ei,'step_index':si,'actor':actor}
                                    boundary={'raw_step':event.get('step'),'episode_value':event.get('episode'),'episode_boundary_evidence':'explicit outer container'}
                                outcomes[reason]+=1
                                events.append({'id':opaque,'outcome':y})
                                target_events.append({'id':target_id,'outcome':y})
                                local.append(dict(event_index=len(events)-1,location=loc,boundary=boundary,raw_action=action,
                                                  raw_processed_event=event if scenario!='cage2_raw' else None,
                                                  raw_outcome=code,raw_outcome_present=present,outcome=y,outcome_reason=reason,
                                                  token_id=opaque,target_qualified_token_id=target_id,excluded_action_fields={k:v for k,v in action.items() if k not in description and k not in ('action','type')},
                                                  raw_true_state_read_for_tokenization=False))
                        trace_id=len(traces)+1
                        traces.append(dict(file_id=trace_id,events=events))
                        target_traces.append(dict(file_id=trace_id,events=target_events))
                        faithful.append(dict(trace_id=trace_id,source_file_id=file_id,scenario=scenario,archive_member=member,source_sha256=item['sha256'],
                                             episode_container_index=ei,events=local))
                        item['episodes'].append(dict(episode_index=ei,trace_id=trace_id,steps=len(episode),events=len(events)))
                    item['outcomes']=dict(outcomes);source['files'].append(item)
                report['sources'].append(source)
            report['out_of_scope_zip_entries']=len(names)-sum(s['pool_files'] for s in report['sources'])
        after=ARCHIVE.stat()
        if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):raise ValueError('archive changed during reading')
        write(OUT/'observations.json',dict(alphabet=sorted(vocab),traces=traces))
        write(OUT/'token_dictionary.json',vocab)
        write(OUT/'observations_target_qualified.json',dict(alphabet=sorted(target_vocab),traces=target_traces))
        write(OUT/'target_qualified_dictionary_metadata.json',dict(warning='NEW target-qualified abstraction deliberately uses observed target fields; not blind host recovery and not original learner token stream',dictionary=target_vocab))
        write(OUT/'aliasing_diagnostics.json',dict(action_only_token_count=len(vocab),target_qualified_token_count=len(target_vocab),
              action_types_with_multiple_observed_targets=sum(len(x)>1 for x in aliases.values()),
              observed_targets_per_action_token={k:sorted(v) for k,v in aliases.items()},
              interpretation='Action-only IDs can alias events addressing different hosts; multiple observed targets are not proof of distinct physical owners. Neither IDs nor target fields imply disjoint ownership.'))
        write(OUT/'faithful_records_and_metadata.json',dict(warning='not solver input; contains host/IP/actor/boundary provenance',traces=faithful))
        write(OUT/'excluded_source_files.json',exclusions)
        report.update(status='prepared_observations_only',vocabulary=len(vocab),traces=len(traces),events=sum(len(t['events']) for t in traces),
                      excluded_events=0,unknown_events_retained=True,and_input_created=False,
                      outside_pool_policy='all other ZIP entries unselected by declared scope; archive directory represented by authenticated C016 inventory',
                      archive_unchanged_size_mtime=True)
        report['output_hashes']={p.name:digest(p.read_bytes()) for p in OUT.iterdir() if p.is_file()}
    except Exception as exc:
        report.update(status='failed_preserved');report['errors'].append(repr(exc))
    report['script_sha256']=digest(Path(__file__).read_bytes());report['wall_seconds']=time.perf_counter()-started
    write(OUT/'manifest.json',report)
    print(json.dumps({k:report.get(k) for k in ('status','events','vocabulary','traces','errors')}))
    return 0 if not report['errors'] else 1
if __name__=='__main__':raise SystemExit(main())
