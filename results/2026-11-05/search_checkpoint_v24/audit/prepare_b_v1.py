"""Separate B preregistration; never alters A manifests or source freeze."""
import hashlib,json
from pathlib import Path
from oracle_data_v1 import full_family
from certificate_replay_c015_v2 import analytic_obstruction
A=Path(__file__).resolve().parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 old=read(A/'CASE_MANIFEST_V1.json')['jobs'];seen=set();jobs=[]
 for j in old:
  if j['job_id'] not in seen:jobs.append(j);seen.add(j['job_id'])
 jobs+=read(A/'SUPPLEMENT_MANIFEST_V2.json')['jobs'];oracles=read(A/'ORACLES_V1.json')['jobs']+read(A/'SUPPLEMENT_ORACLES_V2.json')['jobs']
 for cid,d,k in [('unsafe_current_prune',{'alphabet':list('abc'),'positive':['aaccbb'],'negative':['ccaabb']},2),('quantifier_all_positives',{'alphabet':list('ab'),'positive':['a','b'],'negative':['ab']},2)]:
  p=A/'fixtures'/f'B_{cid}.json';save(p,d);f=[x for x in full_family(d) if max(x)+1==k];e='unique' if len(f)==1 else 'ambiguous' if f else 'incompatible';jid='B_'+cid;jobs.append({'job_id':jid,'case_id':cid,'input':str(p),'input_sha256':sha(p),'allowed_k':[k],'expectation':e});oracles.append({'job_id':jid,'compatible_rgs':f})
 save(A/'CASE_MANIFEST_B_V1.json',{'jobs':jobs,'unique_input_count':len({j['input_sha256'] for j in jobs}),'call_count':len(jobs),'distinct_job_ids':len({j['job_id'] for j in jobs})});save(A/'ORACLES_B_V1.json',{'jobs':oracles})
 acells={c['cell_id']:c for c in read(A/'TIMING_PLAN_V1.json')['cells']};cells=[acells['D_K4']]
 for m in [8,12]:cells.append({**acells[f'obstruction_m{m}_noK'],'cell_id':f'obstruction_m{m}_K4','known_k':4,'compatible_rgs':[]})
 j=jobs[-2];cells.append({**{k:j[k] for k in ['input','input_sha256','case_id']},'cell_id':'unsafe_K2','known_k':2,'oracle_method':'full RGS'})
 cells.append({**acells['ambiguous_noK'],'cell_id':'ambiguous_K3','known_k':3,'compatible_rgs':[x for x in full_family(read(acells['ambiguous_noK']['input'])) if max(x)+1==3]});cells.append(acells['A_K4'])
 save(A/'TIMING_PLAN_B_V1.json',{'cells':cells,'repeats':5,'cooperative_seconds':20,'outer_seconds':25,'provider_total_process_seconds':600,'rotating_order':True})
 f=read(A/'PROVIDERS_V1.json');d=A.parent/'implementation/candidate_c024b_v1';assert sha(d/'gate_v1.py')=='4e5a8e39528efadf3d2eeaab2dfa02a0d77711d7028005737fe78a42b38cb9a3';f['providers'][1]={'id':'C024_B','solver':str(d/'gate_v1.py'),'cli':str(d/'partition_gate_v1.py')};save(A/'PROVIDERS_B_V1.json',f)
 assert 'no blocking correctness issue' in (A.parent/'theory/SOURCE_REVIEW_B_V1.md').read_text(encoding='utf-8-sig')
 files=[A/'TIMING_PLAN_B_V1.json',A/'CASE_MANIFEST_B_V1.json',A/'ORACLES_B_V1.json',A/'PROTOCOL_B_V1.md',A/'run_audit_b_v1.py',A/'validate_timing_b_v1.py',A.parent/'theory/SOURCE_REVIEW_B_V1.md']+[Path(p[k]) for p in f['providers'] for k in ['solver','cli']]
 save(A/'LAUNCH_FREEZE_B_V1.json',[{'path':str(p),'sha256':sha(p)} for p in files]);print({'B_correctness_calls':len(jobs),'unique_inputs':len({j['input_sha256'] for j in jobs}),'cells':len(cells)})
if __name__=='__main__':main()
