"""Independent full-history oracle and direct certificate replay; no provider imports.
Not executed in preparation. Last-event runs await reviewed ingestion/solver contract.
"""
from context_oracle_c017_v3 import partitions,block_conflicts

def validate_traces(traces,alphabet):
 assert isinstance(traces,list) and alphabet and len(set(alphabet))==len(alphabet)
 for trace in traces:
  assert isinstance(trace,list)
  for e in trace:
   assert set(e)=={'symbol','label'} and e['symbol'] in alphabet
   assert e['label'] is None or type(e['label']) is bool

def full_family(traces,alphabet,known_k=None):
 validate_traces(traces,alphabet);assert len(alphabet)<=8
 assert known_k is None or type(known_k)is int and 1<=known_k<=len(alphabet)
 return tuple(p for p in partitions(sorted(alphabet)) if (known_k is None or len(p)==known_k) and all(not block_conflicts(traces,b,'full') for b in p))

def local_word(traces,ref,block):
 ti,ei=ref;assert type(ti)is int and type(ei)is int and 0<=ti<len(traces) and 0<=ei<len(traces[ti]);trace=traces[ti]
 assert trace[ei]['symbol'] in block
 return tuple(e['symbol'] for e in trace[:ei+1] if e['symbol'] in block),trace[ei]['label']

def replay_conflict(traces,block,left,right):
 w,y=local_word(traces,left,block);v,z=local_word(traces,right,block)
 assert w==v and type(y)is bool and type(z)is bool and y!=z
 return True

def replay_partition(traces,alphabet,partition,known_k=None):
 flat=[x for b in partition for x in b];assert all(partition) and len(flat)==len(set(flat)) and set(flat)==set(alphabet)
 assert known_k is None or len(partition)==known_k
 for block in partition:assert not block_conflicts(traces,block,'full')
 return True

def and_conflict_evidence(positive,negative,partition):
 # Negative word has a matching positive projection in EACH block. This refutes
 # AND acceptance only; it says nothing about selected active-owner output.
 for block in partition:
  project=lambda w:tuple(x for x in w if x in block)
  assert any(project(negative)==project(p) for p in positive)
 return True

def self_check():
 # Prepared synthetic contract gate; manager authorization needed before call.
 for n,bell in enumerate([1,1,2,5,15,52,203,877,4140]):assert sum(1 for _ in partitions(tuple(map(str,range(n)))))==bell
 and_conflict_evidence([['y'],['y','x','y']],['y','x'],[('x',),('y',)])
 e=lambda a,y:{'symbol':a,'label':y}
 contradiction=[[e('x',False)],[e('x',True)]];assert not full_family(contradiction,['x'])
 unknown=[[e('x',False)],[e('x',None),e('x',True)]];assert len(full_family(unknown,['x']))==1
 ambiguous=[[e('x',False)],[e('y',True)]];assert len(full_family(ambiguous,['x','y']))==2 and len(full_family(ambiguous,['x','y'],2))==1
 finite=[[e('y',False),e('x',False)],[e('x',False),e('y',False),e('x',True)]]
 assert all(not block_conflicts(finite,b,1) for b in [('x',),('y',)]) and block_conflicts(finite,('x','y'),1)
 assert not block_conflicts(finite,('x','y'),'full')
 return {'status':'passed','scope':'constructed oracle gate only; not artifact benchmark'}
