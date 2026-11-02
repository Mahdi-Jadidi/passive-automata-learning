"""Offline exhaustive compilation. Learners DO run in this phase.
python -B compile_domain.py domain.json table.json [--max-entries N]
"""
from pathlib import Path
from itertools import product
from collections import Counter
import json,sys,argparse,hashlib
from compiled_selector import validate_domain,entries_digest
from rpni_work_reference import run


def prepare(P,Q,blocks,owner):
    ps=[set() for B in blocks];ns=[set() for B in blocks];pending=[];work=0
    for positive,words in ((True,P),(False,Q)):
        for w in words:
            buckets={};images=[]
            for a in w:work+=1;buckets.setdefault(owner[a],[]).append(a)
            for i in range(len(blocks)):
                work+=1;v=''.join(buckets.get(i,[]))
                if positive:ps[i].add(v)
                else:images.append(v)
            if not positive:pending.append(images)
    feasible=True
    for images in pending:
        witness=None
        for i,v in enumerate(images):
            work+=1
            if v not in ps[i]:witness=i
        if witness is None:feasible=False
        else:ns[witness].add(images[witness])
    expected=sum(map(len,P))+sum(map(len,Q))+len(blocks)*(len(P)+2*len(Q))
    assert work==expected
    return ps,ns,feasible,work


def compile_table(vocabulary,blocks,max_entries=100000):
    words,blocks,owner,configuration=validate_domain(vocabulary,blocks)
    size=3**len(words)
    if size>max_entries:raise ValueError(f'{size} entries exceed resource limit {max_entries}; no partial table emitted')
    events=Counter(domain_validation=configuration)
    powers=[]
    for i in range(len(words)):events['vocabulary_index']+=1;powers.append(3**i)
    entries=[None]*size;statuses=Counter()
    for labels in product(range(3),repeat=len(words)):
        P,Q=set(),set();key=0
        for i,(w,label) in enumerate(zip(words,labels)):
            events['label_record']+=1;key+=label*powers[i]
            if label==1:P.add(w)
            elif label==2:Q.add(w)
        ps,ns,feasible,prep=prepare(P,Q,blocks,owner)
        events['preparation']+=prep
        g=run(P,Q)['W'];events['global_learning']+=g
        s=None
        if feasible:
            s=prep
            for p,n in zip(ps,ns):
                events['local_dispatch']+=1
                value=run(p,n)['W'];events['local_learning']+=value;s+=value
            status='GLOBAL' if g<s else 'SPLIT' if s<g else 'TIE'
        else:status='GLOBAL_ONLY'
        events['entry_emit']+=1;statuses[status]+=1
        entries[key]=dict(status=status,global_work=g,split_work=s)
    assert all(e is not None for e in entries)
    return dict(schema='rpni-compiled-v1',vocabulary=words,blocks=blocks,
                entries=entries,entries_sha256=entries_digest(entries),
                offline_work=sum(events.values()),offline_events=dict(events),counts=dict(statuses),
                reference_sha256=hashlib.sha256((Path(__file__).parent/'rpni_work_reference.py').read_bytes()).hexdigest(),
                metric='Declared loop events; library internals, allocation, hashing, sorting, serialization and bit arithmetic excluded',
                warning='Compilation executes learners exhaustively. Query-time lookup does not. Offline and setup costs must be amortized explicitly.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('domain');parser.add_argument('output')
    parser.add_argument('--max-entries',type=int,default=100000);args=parser.parse_args()
    x=json.loads(Path(args.domain).read_text(encoding='utf8'))
    data=compile_table(x['vocabulary'],x['blocks'],args.max_entries)
    Path(args.output).write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf8')
    print(json.dumps({k:data[k] for k in ('counts','offline_work','offline_events')},indent=2))
