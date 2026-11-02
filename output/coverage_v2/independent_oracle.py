from collections import deque

def key(w):return len(w),w

def independent_accept(model,word):
    states,edges,finals,q=model
    for a in word:
        q=edges.get((q,a),None)
        if q is None:return False
    return q in finals

def oracle_fold(model,r,b):
    states,edges,finals,start=model
    parts=[{r,b}]+[{q} for q in states if q not in (r,b)]
    while True:
        block={q:i for i,C in enumerate(parts) for q in C}
        obligations={}
        for (q,a),t in edges.items():obligations.setdefault((block[q],a),set()).add(block[t])
        conflict=next((targets for targets in obligations.values() if len(targets)>1),None)
        if conflict is None:break
        merged=set().union(*(parts[i] for i in conflict))
        parts=[C for i,C in enumerate(parts) if i not in conflict]+[merged]
    names={q:min(C,key=key) for C in parts for q in C}
    return (set(names.values()),{(names[q],a):names[t] for (q,a),t in edges.items()},
            {names[q] for q in finals},names[start])

def oracle_learner(pos,neg):
    states={''}|{w[:j] for w in pos for j in range(1,len(w)+1)}
    model=(states,{(w[:-1],w[-1]):w for w in states if w},set(pos),'')
    red={''};attempts=0
    while True:
        blue={t for (q,a),t in model[1].items() if q in red and t not in red}
        if not blue:return model,attempts
        b=min(blue,key=key)
        for r in sorted(red,key=key):
            attempts+=1;candidate=oracle_fold(model,r,b)
            if all(not independent_accept(candidate,w) for w in neg):
                # A former red state maps to the canonical member of its class.
                # Recover the partition from canonical quotient paths.
                newred=set()
                for old in red:
                    q=candidate[3]
                    for a in old:q=candidate[1][q,a]
                    newred.add(q)
                model,red=candidate,newred
                break
        else:red.add(b)

def exact_equivalent(global_model,local_models,blocks):
    """BFS on completed synchronous product, including implicit rejecting sinks."""
    alphabet=sorted(set().union(*map(set,blocks)))
    initial=(global_model[3],)+tuple(m[3] for m in local_models)
    todo=deque([(initial,'')]);seen={initial}
    while todo:
        qs,w=todo.popleft()
        left=qs[0] in global_model[2]
        right=all(q in m[2] for q,m in zip(qs[1:],local_models))
        if left!=right:return False,w
        for a in alphabet:
            nxt=(global_model[1].get((qs[0],a)),)+tuple(
                m[1].get((q,a)) if a in B else q
                for q,m,B in zip(qs[1:],local_models,blocks))
            if nxt not in seen:seen.add(nxt);todo.append((nxt,w+a))
    return True,None
