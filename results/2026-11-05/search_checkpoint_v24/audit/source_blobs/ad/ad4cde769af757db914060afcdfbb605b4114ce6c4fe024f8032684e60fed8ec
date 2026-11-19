"""Bounded reproducible audit launcher. Explicit launch flag is required for timing."""
import argparse,hashlib,json,statistics,sys,time
from pathlib import Path
import capture
from certificate_replay_c015_v2 import verify,analytic_obstruction
A=Path(__file__).resolve().parent;ROOT=A.parents[3]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['correctness','timing']);ap.add_argument('--providers',type=Path,required=True);ap.add_argument('--run-id',required=True);ap.add_argument('--manager-launch',action='store_true');args=ap.parse_args()
 if args.mode=='timing':assert args.manager_launch,'Manager source review and explicit launch instruction required'
 providers=read(args.providers)['providers'];run=A/'runs'/args.run_id;run.mkdir(parents=True,exist_ok=False);ledger=[];spent={p['id']:0. for p in providers}
 sources=[args.providers,*A.glob('*.py'),A/'TIMING_PLAN_B_V1.json',A/'CASE_MANIFEST_B_V1.json',A/'ORACLES_B_V1.json']
 for p in providers:
  for field in ['solver','cli']:assert Path(p[field]).is_file();sources.append(Path(p[field]))
 save(run/'SOURCE_FREEZE.json',[{'path':str(p.resolve()),'sha256':sha(p)} for p in sources])
 def append(row):
  ledger.append(row)
  with (run/'ledger.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(row,ensure_ascii=False)+'\n')
 def launch(p,label,cmd,ip,budget,outer=25):
  if spent[p['id']]+outer>budget:return {'execution_status':'budget_unstarted'}
  cap=capture.capture(label,cmd,cwd=ROOT,timeout_seconds=outer,source_paths=sources+[ip]);spent[p['id']]+=cap['subprocess_seconds'];return cap
 if args.mode=='correctness':
  jobs=read(A/'CASE_MANIFEST_B_V1.json')['jobs'];lookup={j['job_id']:j for j in jobs};oracles={o['job_id']:o for o in read(A/'ORACLES_B_V1.json')['jobs']};rows=[]
  # Small bounded chunks preserve partial records if a provider stalls.
  for p in providers:
   for start in range(0,len(jobs),100):
    chunk=jobs[start:start+100];cp=run/f'chunk_{start:04}.json';save(cp,chunk)
    cap=launch(p,f"{args.run_id}_{p['id']}_c{start}",[sys.executable,'-B','-X','utf8',str(A/'provider_batch_v1.py'),p['solver'],str(cp)],cp,175,25);append({'provider':p['id'],'chunk':start,**cap})
    records=[]
    if 'attempt_dir' in cap:
     for line in (Path(cap['attempt_dir'])/'stdout.bin').read_bytes().splitlines():
      try:records.append(json.loads(line))
      except Exception as e:rows.append({'provider':p['id'],'failure_id':f"{p['id']}-chunk{start}-parse",'error':repr(e)})
    seen=set()
    for rec in records:
     jid=rec.get('job_id');seen.add(jid)
     try:
      assert not rec.get('error') and not rec.get('unstarted'),rec
      decision=verify(lookup[jid],rec['result'],oracles.get(jid));assert decision!='unresolved' or lookup[jid]['expectation']=='timeout'
      rows.append({'provider':p['id'],'job_id':jid,'decision':decision})
     except Exception as e:rows.append({'provider':p['id'],'job_id':jid,'failure_id':f"{p['id']}-{jid}",'error':repr(e)})
    for j in chunk:
     if j['job_id'] not in seen:rows.append({'provider':p['id'],'job_id':j['job_id'],'failure_id':f"{p['id']}-{j['job_id']}",'error':'unstarted_or_missing_record'})
  save(run/'correctness_report.json',{'rows':rows,'errors':sum('error' in r for r in rows),'provider_process_seconds':spent,'unique_inputs':len({j['input_sha256'] for j in jobs}),'planned_calls_per_provider':len(jobs)})
 else:
  plan=read(A/'TIMING_PLAN_B_V1.json')
  for ci,c in enumerate(plan['cells']):
   ip=Path(c['input']);assert sha(ip)==c['input_sha256']
   for rep in range(1,6):
    offset=(ci+rep-1)%len(providers);order=providers[offset:]+providers[:offset]
    for p in order:
     cmd=[sys.executable,'-B','-X','utf8',p['cli'],str(ip),'--seconds','20']
     if c['known_k'] is not None:cmd+=['--known-k',str(c['known_k'])]
     cap=launch(p,f"{args.run_id}_{c['cell_id']}_{p['id']}_r{rep}",cmd,ip,600);append({'provider':p['id'],'cell_id':c['cell_id'],'rep':rep,'input_sha256':sha(ip),**cap})
  # Distributions retain timeouts as censored outcomes; no speed ratio computed here.
  groups=[]
  for c in plan['cells']:
   for p in providers:
    rr=[r for r in ledger if r['provider']==p['id'] and r['cell_id']==c['cell_id']];times=[r['subprocess_seconds'] for r in rr if r['execution_status'] in ['success','program_error']]
    groups.append({'cell_id':c['cell_id'],'provider':p['id'],'all_records':rr,'uncensored_process_median':statistics.median(times) if times else None})
  save(run/'distributions.json',groups)
 save(run/'closure.json',{'mode':args.mode,'provider_process_seconds':spent,'records':len(ledger),'independent_replay_in_solver_timing':False})
 print(str(run))
if __name__=='__main__':main()
