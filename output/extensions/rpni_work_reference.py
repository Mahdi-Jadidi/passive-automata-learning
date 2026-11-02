"""Fixed RPNI reference. W is specified loop work, NOT CPU instructions or time.

Charged events: word, symbol, state/edge creation, fringe state/edge visits,
candidate, fold state/edge visits, negative word/symbol visits, red remapping.
Library sorting, hashing, integer arithmetic and return conventions are not charged.
All dictionaries are sparse; unused alphabet symbols do not affect learner W.
"""
from collections import Counter

def shortlex(w): return len(w),w

def run(pos,neg,observer=None):
    pos,neg=set(pos),set(neg)
    assert not pos&neg
    c=Counter(); states={''}; edges={}; finals=set(pos)
    c['state_create']+=1
    for w in sorted(pos,key=shortlex):
        c['positive_word']+=1;q=''
        for a in w:
            c['positive_symbol']+=1;t=q+a
            if t not in states:
                states.add(t);edges[q,a]=t
                c['state_create']+=1;c['edge_create']+=1
            q=t
    initial_n=len(states);initial_e=len(edges);red={''};attempts=0;iterations=0
    fold_records=[]
    while True:
        # Two explicitly counted state passes: red ordering and blue ordering.
        ordered_red=[]
        for q in sorted(states,key=shortlex):
            c['fringe_state']+=1
            if q in red:ordered_red.append(q)
        blue=set()
        for (q,a),t in edges.items():
            c['fringe_edge']+=1
            if q in red and t not in red:blue.add(t)
        ordered_blue=[]
        for q in sorted(states,key=shortlex):
            c['fringe_state']+=1
            if q in blue:ordered_blue.append(q)
        if not ordered_blue:break
        iterations+=1;b=ordered_blue[0]
        for r in ordered_red:
            attempts+=1;c['candidate']+=1;before=sum(c.values())
            current=sorted(states,key=shortlex);parent={}
            for q in current:c['fold_state']+=1;parent[q]=q
            unions=0
            def union(x,y):
                nonlocal unions
                lo,hi=sorted((parent[x],parent[y]),key=shortlex)
                if lo==hi:return False
                unions+=1
                for q in current:
                    c['fold_state']+=1
                    if parent[q]==hi:parent[q]=lo
                return True
            union(r,b);passes=0
            while True:
                passes+=1;changed=False;seen={}
                for (q,a),t in sorted(edges.items(),key=lambda z:(shortlex(z[0][0]),z[0][1])):
                    c['fold_edge']+=1;key=parent[q],a
                    if key in seen:changed=union(seen[key],t) or changed
                    else:seen[key]=t
                if not changed:break
            new_states=set();new_finals=set()
            for q in current:
                c['fold_state']+=1;new_states.add(parent[q])
                if q in finals:new_finals.add(parent[q])
            new_edges={}
            for (q,a),t in edges.items():
                c['fold_edge']+=1;new_edges[parent[q],a]=parent[t]
            fold_work=sum(c.values())-before
            fold_records.append({'n':len(states),'e':len(edges),'work':fold_work,'passes':passes,'unions':unions})
            ok=True
            for w in sorted(neg,key=shortlex):
                c['negative_word']+=1;q=parent[''];defined=True
                for a in w:
                    c['negative_symbol']+=1
                    if (q,a) not in new_edges:defined=False;break
                    q=new_edges[q,a]
                if defined and q in new_finals:ok=False;break
            if observer is not None:
                observer((set(states),dict(edges),set(finals),''),r,b,
                         (set(new_states),dict(new_edges),set(new_finals),parent['']),ok,neg)
            if ok:
                states,edges,finals=new_states,new_edges,new_finals
                new_red=set()
                for q in red:c['red_remap']+=1;new_red.add(parent[q])
                red=new_red;break
        else:red.add(b)
    model=(states,edges,finals,'')
    assert all(accepts(model,w) for w in pos)
    assert all(not accepts(model,w) for w in neg)
    return {'W':sum(c.values()),'events':dict(c),'N':initial_n,'E':initial_e,
            'A':attempts,'iterations':iterations,'folds':fold_records,'model':model}

def accepts(model,w):
    _,edges,finals,q=model
    for a in w:
        if (q,a) not in edges:return False
        q=edges[q,a]
    return q in finals

def project(w,B):return ''.join(a for a in w if a in B)

def split_run(pos,neg,blocks):
    # Slot events include per-word projection handling; negative attribution gets
    # a second complete slot pass. The policy is the highest available witness.
    # This fixed alphabet lookup is configuration, outside per-sample W.
    owner={a:i for i,B in enumerate(blocks) for a in B}
    ps=[set() for B in blocks];ns=[set() for B in blocks];pending=[];prep=0
    for positive,words in ((True,pos),(False,neg)):
        for w in words:
            buckets={};images=[]
            for a in w:
                prep+=1;buckets.setdefault(owner[a],[]).append(a)
            for i in range(len(blocks)):
                prep+=1;v=''.join(buckets.get(i,[]))
                if positive:ps[i].add(v)
                else:images.append(v)
            if not positive:pending.append(images)
    for images in pending:
        selected=None
        for i,v in enumerate(images):
            prep+=1
            if v not in ps[i]:selected=i
        if selected is None:raise ValueError('Infeasible partition')
        ns[selected].add(images[selected])
    assert prep==sum(map(len,pos))+sum(map(len,neg))+len(blocks)*(len(pos)+2*len(neg))
    runs=[run(p,n) for p,n in zip(ps,ns)]
    return {'W':prep+sum(r['W'] for r in runs),'projection_work':prep,'runs':runs}
