"""Public BGL sample adapter: EventId inputs and current-message alert tags."""
import csv,hashlib,io,json,platform,sys
from collections import Counter,defaultdict
from pathlib import Path
HERE=Path(__file__).resolve().parent;SOURCE=HERE.parent/'external/loghub_bgl_v1';OUT=HERE.parent/'inventory/bgl_v1'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def write(name,x):(OUT/name).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def main():
    OUT.mkdir(parents=True,exist_ok=False)
    report=dict(status='started',python=sys.version,platform=platform.platform(),errors=[],original_artifact_code_executed=False,solver_runs=0,
                command='py -3.14 results/2026-11-05/real_trace_checkpoint_v25/implementation/prepare_bgl_v1.py')
    try:
        acquisition=json.loads((SOURCE/'ACQUISITION_V1.json').read_text(encoding='utf-8'))
        for item in acquisition['files']:
            raw=(SOURCE/item['local']).read_bytes()
            if sha(raw)!=item['sha256'] or len(raw)!=item['bytes']:raise ValueError('acquisition hash mismatch: '+item['local'])
        raw_csv=(SOURCE/'BGL_2k.log_structured.csv').read_bytes();raw_log=(SOURCE/'BGL_2k.log').read_bytes()
        rows=list(csv.DictReader(io.StringIO(raw_csv.decode('utf-8-sig'),newline='')))
        lines=raw_log.decode('utf-8').splitlines()
        if len(rows)!=2000 or len(lines)!=len(rows):raise ValueError('expected 2000 paired rows/lines')
        fields=['Label','Timestamp','Date','Node','Time','NodeRepeat','Type','Component','Level','Content']
        events=[];metadata=[];frequencies=Counter();labels=Counter();nodes=defaultdict(set);templates=defaultdict(set);times=[]
        for index,(row,line) in enumerate(zip(rows,lines),1):
            parsed=line.split(None,9)
            if len(parsed)!=10:raise ValueError(f'raw grammar mismatch row{index}')
            if row['LineId']!=str(index):raise ValueError('non-sequential source LineId')
            if any(row[field]!=value for field,value in zip(fields,parsed)):
                raise ValueError(f'raw/CSV field disagreement row{index}')
            event=row['EventId']
            if not event or not row['Label']:raise ValueError('missing ID/label')
            outcome=row['Label']=='-'
            events.append(dict(id=event,outcome=outcome))
            metadata.append(dict(event_index=index-1,source_line_1based=index,csv_row=row,raw_line_sha256=sha(line.encode('utf-8'))))
            frequencies[event]+=1;labels[row['Label']]+=1;nodes[event].add(row['Node']);templates[event].add(row['EventTemplate']);times.append(int(row['Timestamp']))
        observations=dict(alphabet=sorted(frequencies),traces=[dict(file_id=1,events=events)])
        write('observations.json',observations)
        write('faithful_rows_and_metadata.json',dict(warning='Not inference input: original tags, node, level, message and template provenance only',records=metadata))
        write('eventid_dictionary_metadata.json',dict(warning='EventId is the pre-existing upstream template ID, no reparsing or label-based remapping',
              dictionary={e:sorted(v) for e,v in templates.items()}))
        top=sorted(frequencies,key=lambda e:(-frequencies[e],e))[:8]
        write('mechanical_top8_selection.json',dict(event_ids=top,rule='descending whole-public-sample EventId frequency then lexicographic EventId',
              selection_scope='transductive diagnostic selection, no held-out evaluation',full_stream_retained=True,
              events_in_selected_types=sum(frequencies[e] for e in top),events_outside_selected_types=sum(frequencies[e] for e in frequencies if e not in top),
              interpretation='Future small exact-cover compatibility controls only; no physical recovery or chosen memory-depth validity implied'))
        write('sharing_diagnostics.json',dict(nodes_per_eventid={e:sorted(v) for e,v in nodes.items()},
              eventids_shared_across_nodes=sum(len(v)>1 for v in nodes.values()),total_nodes=len(set().union(*nodes.values())),
              interpretation='Same upstream EventId can occur on multiple nodes. A disjoint symbol-owner model does not follow from node identities. Node is metadata, never a primary input.'))
        report.update(status='prepared_observations_only',repository=acquisition['repository'],commit=acquisition['commit'],
                      source_hashes={p.name:sha(p.read_bytes()) for p in SOURCE.iterdir() if p.is_file()},
                      events=len(events),vocabulary=len(frequencies),true_non_alert=sum(e['outcome'] for e in events),false_alert=sum(not e['outcome'] for e in events),
                      original_label_counts=dict(labels),event_frequencies=dict(frequencies),excluded_records=[],raw_csv_alignment_checks=len(rows),
                      timestamp_decreases=sum(a>b for a,b in zip(times,times[1:])),
                      boundary_policy='one observed sample stream in provided row order; no sessions invented; completeness, temporal contiguity and physical reset unverified',
                      output_semantics='current-message non-alert indicator, not action success or full-session/full-word validity',
                      primary_input_fields=['EventId'],forbidden_primary_fields=['Label','Level','Content','Node','EventTemplate'],and_input_created=False)
        report['output_hashes']={p.name:sha(p.read_bytes()) for p in OUT.iterdir() if p.is_file()}
    except Exception as exc:report.update(status='failed_preserved');report['errors'].append(repr(exc))
    report['script_sha256']=sha(Path(__file__).read_bytes());write('manifest.json',report)
    print(json.dumps({k:report.get(k) for k in ['status','events','vocabulary','true_non_alert','false_alert','timestamp_decreases','errors']}))
    return 0 if not report['errors'] else 1
if __name__=='__main__':raise SystemExit(main())
