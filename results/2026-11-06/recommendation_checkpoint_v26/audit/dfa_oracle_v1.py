"""Independent finite-language equivalence check using projected epsilon NFAs."""
from itertools import product
from collections import deque
from oracle_v1 import partitions

def accepts(delta, finals, word, alphabet):
    q=0
    for a in word:q=delta[q][alphabet.index(a)]
    return q in finals

def cut_counterexample(delta, finals, alphabet, blocks):
    """Return shortest w in intersection pi_B^-1(pi_B(L)) minus L, or None."""
    def close(states,b):
        states=set(states);todo=list(states)
        while todo:
            q=todo.pop()
            for j,a in enumerate(alphabet):
                v=delta[q][j]
                if a not in b and v not in states:states.add(v);todo.append(v)
        return frozenset(states)
    initial=(0,tuple(close({0},b) for b in blocks))
    todo=deque([(initial,'')]);seen={initial}
    while todo:
        (q,subsets),w=todo.popleft()
        if q not in finals and all(s & finals for s in subsets):return w
        for j,a in enumerate(alphabet):
            updated=tuple(close({delta[v][j] for v in s},b) if a in b else s for b,s in zip(blocks,subsets))
            nxt=(delta[q][j],updated)
            if nxt not in seen:seen.add(nxt);todo.append((nxt,w+a))
    return None

def all_small_dfas():
    for qcount in (1,2):
        for m in (2,3):
            a=list('abc'[:m])
            for flat in product(range(qcount),repeat=qcount*m):
                delta=[flat[i*m:(i+1)*m] for i in range(qcount)]
                for bits in product((False,True),repeat=qcount):
                    finals=frozenset(i for i,b in enumerate(bits) if b)
                    if not finals:continue
                    # Nonempty language requires reachable final, not merely nonempty F.
                    reach={0}
                    while True:
                        new=reach|{delta[q][j] for q in reach for j in range(m)}
                        if new==reach:break
                        reach=new
                    if reach & finals:yield a,delta,finals

def selftest():
    count=cuts=0
    for a,d,f in all_small_dfas():
        count+=1
        assert cut_counterexample(d,f,a,[a]) is None
        for p in partitions(a):
            w=cut_counterexample(d,f,a,p);cuts+=1
            if w is not None:assert not accepts(d,f,w,a)
    return dict(status='passed',total_complete_transition_final_choices=324,empty_language_filtered=324-count,nonempty_dfas=count,partition_checks=cuts)

if __name__=='__main__':
    import json
    print(json.dumps(selftest()))
