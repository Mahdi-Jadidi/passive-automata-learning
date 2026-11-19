"""V35 mixed-cover full-output engine; standard library, no old solver imports."""
class Invalid(ValueError):
    pass


def blank(status, reason=None):
    r = dict(status=status, compatible_count=None, optimal_count=None, max_blocks=None,
             recommendation=None, optimal_unique=None, compatible_witnesses=None, optimal_witnesses=None)
    if reason is not None: r['reason'] = reason
    return r


def normalize(data):
    if not isinstance(data, dict) or set(data) != {'alphabet','positive','negative'}:
        raise Invalid('expected exactly alphabet, positive, negative')
    a = data['alphabet']
    if not isinstance(a, list): raise Invalid('alphabet must be an array')
    if any(not isinstance(x, str) or not x for x in a): raise Invalid('alphabet IDs must be nonempty strings')
    if len(set(a)) != len(a): raise Invalid('alphabet IDs must be distinct')
    allowed = set(a); out = []
    for key in ('positive','negative'):
        words = data[key]
        if not isinstance(words, list): raise Invalid(key + ' must be an array')
        seen = set(); unique = []
        for w in words:
            if not isinstance(w, list): raise Invalid('each word must be an array')
            if any(not isinstance(x,str) or x not in allowed for x in w):
                raise Invalid('word contains invalid or unknown symbol')
            v = tuple(w)
            if v not in seen: seen.add(v); unique.append(v)
        out.append(unique)
    return tuple(a), out[0], out[1]


def bell_exceeds(m, cap):
    # Bell triangle; every entry and its first value are nondecreasing.
    row = [1]
    for _ in range(m):
        nxt = [row[-1]]
        for x in row: nxt.append(nxt[-1] + x)
        row = nxt
        if row[0] > cap: return True
    return row[0] > cap


def rows(a, p, n):
    m = len(a); masks = {}
    for b in range(1, 1 << m):
        s = {a[i] for i in range(m) if b & (1 << i)}
        h = {tuple(x for x in w if x in s) for w in p}
        reject = 0
        for j,w in enumerate(n):
            if tuple(x for x in w if x in s) not in h: reject |= 1 << j
        masks[b] = reject
    return masks


def iterate(m, n_count, tags):
    allmask=(1 << m)-1
    def go(s,u,selected):
        if not s:
            if not u: yield tuple(selected)
            return
        bit=s & -s
        b=s
        while b:
            if b & bit:
                selected.append(b)
                yield from go(s ^ b, u & ~tags[b], selected)
                selected.pop()
            b=(b-1)&s
    yield from go(allmask, (1 << n_count)-1, [])


def canonical(a, selection):
    ordered = sorted(selection, key=lambda b: (b & -b).bit_length())
    owner = {i:k for k,b in enumerate(ordered) for i in range(len(a)) if b & (1<<i)}
    return tuple(owner[i] for i in range(len(a)))


def witness(a,p,n,rgs):
    count=max(rgs)+1 if rgs else 0
    blocks=[[] for _ in range(count)]
    for symbol,k in zip(a,rgs): blocks[k].append(symbol)
    factors=[]; groups=[]
    for block in blocks:
        s=set(block); groups.append(s); seen=set(); f=[]
        for w in p:
            v=tuple(x for x in w if x in s)
            if v not in seen: seen.add(v); f.append(list(v))
        factors.append(f)
    rejected=[]
    for w in n:
        k=next((i for i,s in enumerate(groups) if tuple(x for x in w if x in s) not in {tuple(z) for z in factors[i]}),None)
        if k is None: return None
        rejected.append(k)
    return dict(rgs=list(rgs),blocks=blocks,factors=factors,negative_rejected_by=rejected)


def solve(data, *, max_candidates=None):
    try:
        if max_candidates is not None and (type(max_candidates) is not int or max_candidates < 0):
            return blank('INVALID_INPUT','max_candidates must be a nonnegative integer or None')
        try: a,p,n=normalize(data)
        except Invalid as e: return blank('INVALID_INPUT',str(e))
        if set(p)&set(n):
            r=blank('INCOMPATIBLE'); r.update(compatible_count=0,optimal_count=0,compatible_witnesses=[],optimal_witnesses=[]); return r
        if max_candidates is not None and bell_exceeds(len(a),max_candidates):
            return blank('INCOMPLETE','candidate budget exhausted')
        tags=rows(a,p,n); total=0; best=None; numbest=0; first=[]; top=[]
        for part in iterate(len(a),len(n),tags):
            total+=1; rgs=canonical(a,part); k=len(part)
            first=sorted(first+[rgs])[:2]
            if best is None or k>best: best=k; numbest=1; top=[rgs]
            elif k==best: numbest+=1; top=sorted(top+[rgs])[:2]
        if not total:
            r=blank('INCOMPATIBLE'); r.update(compatible_count=0,optimal_count=0,compatible_witnesses=[],optimal_witnesses=[]); return r
        compatible=[witness(a,p,n,x) for x in first]; optimal=[witness(a,p,n,x) for x in top]
        if any(w is None for w in compatible+optimal): return blank('ERROR','witness replay failed')
        return dict(status='UNIQUE_COMPATIBLE' if total==1 else 'AMBIGUOUS',compatible_count=total,
                    optimal_count=numbest,max_blocks=best,recommendation=optimal[0],optimal_unique=numbest==1,
                    compatible_witnesses=compatible,optimal_witnesses=optimal)
    except (KeyboardInterrupt,MemoryError): return blank('INCOMPLETE','execution interrupted or resources exhausted')
