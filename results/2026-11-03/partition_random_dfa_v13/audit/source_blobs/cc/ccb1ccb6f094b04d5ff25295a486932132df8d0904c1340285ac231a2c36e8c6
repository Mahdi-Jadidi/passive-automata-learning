"""Independent one-pass-per-word projection and feasibility replay."""
import time
deadline=None
characters_routed=0
def poll():
    if deadline is not None and time.perf_counter()>=deadline:raise TimeoutError('independent validation time budget exhausted')
def projected(word,owner,count):
    global characters_routed
    out=[[] for _ in range(count)]
    for i,ch in enumerate(word):
        if i%4096==0:poll()
        out[owner[ch]].append(ch)
    characters_routed+=len(word)
    return [''.join(x) for x in out]
def evaluate(data,partition,witness=None):
    owner={ch:i for i,block in enumerate(partition) for ch in block};n=len(partition)
    assert n and all(partition) and len(owner)==sum(map(len,partition)) and set(owner)==set(data['alphabet'])
    languages=[set() for _ in range(n)]
    for word in data['positive']:
        for i,value in enumerate(projected(word,owner,n)):languages[i].add(value)
    feasible=True;negative_records=[]
    for word in data['negative']:
        values=projected(word,owner,n);rejected=[i for i,v in enumerate(values) if v not in languages[i]]
        feasible=feasible and bool(rejected)
        if witness is not None:negative_records.append({'word':word,'projections':values,'rejected_by_blocks':rejected})
    if witness is not None:
        assert feasible and witness['positive_projection_languages']==[sorted(x) for x in languages] and witness['negative_witnesses']==negative_records
    return feasible
