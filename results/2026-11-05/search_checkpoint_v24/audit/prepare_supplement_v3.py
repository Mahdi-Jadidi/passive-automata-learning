"""Prepare supplemental controls without changing V1 evidence."""
import json,hashlib
from pathlib import Path
from oracle_data_v1 import full_family
A=Path(__file__).resolve().parent
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 jobs=[];oracles=[]
 def add(cid,d,k=None,expect=None,api=False):
  p=A/'fixtures'/f'{cid}.json';save(p,d);h=hashlib.sha256(p.read_bytes()).hexdigest();fam=[] if expect=='invalid' else full_family(d)
  if expect is None:
   fam=[x for x in fam if k is None or max(x)+1==k];expect='unique' if len(fam)==1 else 'ambiguous' if fam else 'incompatible'
  j={'job_id':cid,'case_id':cid,'input':str(p),'input_sha256':h,'allowed_k':None if api or k is None else [k],'expectation':expect}
  if api:j['api_known_k']=k
  jobs.append(j);oracles.append({'job_id':cid,'compatible_rgs':fam})
 d={'alphabet':['a','b','c'],'positive':['ab'],'negative':['ba']}
 for tag,k in [('zero',0),('too_large',4),('boolean',True),('float',1.5),('string','2'),('negative',-1)]:add('supp_badK_'+tag,d,k,'invalid',True)
 add('supp_unobserved_symbol',{'alphabet':['a','b','z'],'positive':['a'],'negative':['aa']})
 # 65,536 boundary, astral Unicode, and collision after a long common prefix.
 prefix='🙂'*65536
 for suffix in ['', '中']:
  add('supp_long_unicode_'+('boundary' if not suffix else 'after_boundary'),{'alphabet':['🙂','α','中'],'positive':[prefix+'α'+suffix],'negative':[prefix+suffix+'α']},None)
 # Long invalid character occurs beyond 64KiB and mixed observed/absent alphabet.
 add('supp_late_unicode_invalid',{'alphabet':['🙂','α'],'positive':[prefix+'α','🙂'*65537+'中'],'negative':[]},None,'invalid')
 save(A/'SUPPLEMENT_MANIFEST_V2.json',{'jobs':jobs,'unique_input_count':len({j['input_sha256'] for j in jobs}),'call_count':len(jobs)})
 save(A/'SUPPLEMENT_ORACLES_V2.json',{'jobs':oracles});print({'supplement_calls':len(jobs)})
if __name__=='__main__':main()
