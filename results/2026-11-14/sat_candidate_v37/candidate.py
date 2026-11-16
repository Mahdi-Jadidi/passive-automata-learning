"""V35 standalone full-output SAT candidate; see README for scope and limits."""
import itertools

class Limited(Exception): pass
class InvalidInput(ValueError): pass
MAX_VARIABLES = 2000
MAX_CLAUSES = 200000
MAX_SEARCH_NODES = 200000
MAX_MODELS = 100000
def neg(x): return ['not', x]
def group(op, xs):
    if not xs: return op == 'and'
    acc = xs[0]
    for x in xs[1:]: acc = [op, acc, x]
    return acc


def build(a, p, n, threshold):
    m = len(a); index = {v:i for i,v in enumerate(a)}
    clauses = []; names = set()
    def add(lits):
        # Signed literal is (variable, Boolean positive).
        d = {}
        for var, sign in lits:
            if var in d and d[var] != sign: return
            d[var] = sign
        clauses.append(tuple(d.items()))
        if len(clauses) > MAX_CLAUSES: raise Limited()
    def var(name):
        names.add(name)
        if len(names) > MAX_VARIABLES: raise Limited()
        return name
    y = [[var(('Y', i, k)) for k in range(m)] for i in range(m)]
    for i in range(m):
        add([(y[i][k], True) for k in range(m)])
        for k in range(m):
            for j in range(k): add([(y[i][k], False), (y[i][j], False)])
            if k: add([(y[i][k], False)] + [(y[j][k-1], True) for j in range(i)])
    gate_cache = {}
    def compile_expr(owner, expr, path=()):
        if not isinstance(expr, list): return expr
        op = expr[0]
        first = compile_expr(owner, expr[1], path+(0,))
        if op == 'and' and first is False: return False
        if op == 'or' and first is True: return True
        children = [first]
        if len(expr) == 3:
            children.append(compile_expr(owner, expr[2], path+(1,)))
        # These identities preserve each gate's Boolean function exactly.
        # Retain all emitted full-equivalence clauses; no one-way gates.
        if op == 'not' and type(children[0]) is bool:
            return not children[0]
        if op == 'and':
            if any(x is False for x in children): return False
            if children[0] is True: return children[1]
            if children[1] is True or children[0] == children[1]: return children[0]
        if op == 'or':
            if any(x is True for x in children): return True
            if children[0] is False: return children[1]
            if children[1] is False or children[0] == children[1]: return children[0]
        key = (op, tuple(children))
        if key in gate_cache: return gate_cache[key]
        g = var(('G', owner, path))
        gate_cache[key] = g
        inputs = []
        for c in children:
            if type(c) is not bool and c not in inputs: inputs.append(c)
        for values in itertools.product((False, True), repeat=len(inputs)):
            val = dict(zip(inputs, values))
            args = [c if type(c) is bool else val[c] for c in children]
            out = (not args[0]) if op == 'not' else ((args[0] and args[1]) if op == 'and' else (args[0] or args[1]))
            bad = not out
            add([(v, not value) for v,value in zip(inputs,values)] + [(g, not bad)])
        return g
    active = []
    for k in range(m): active.append(compile_expr(('A', k), group('or', [y[i][k] for i in range(m)])))
    eq = {}
    for ni,u in enumerate(n):
        for pi,v in enumerate(p):
            for k in range(m):
                for i in range(len(u)+1):
                    for j in range(len(v)+1):
                        owner = ('E', ni, pi, k, i, j)
                        if i == 0 and j == 0: expr = True
                        elif j == 0: expr = group('and', [eq[ni,pi,k,i-1,0], neg(y[index[u[i-1]]][k])])
                        elif i == 0: expr = group('and', [eq[ni,pi,k,0,j-1], neg(y[index[v[j-1]]][k])])
                        else:
                            x,z = y[index[u[i-1]]][k],y[index[v[j-1]]][k]
                            expr = group('or', [group('and',[neg(x),eq[ni,pi,k,i-1,j]]), group('and',[x,neg(z),eq[ni,pi,k,i,j-1]]), group('and',[x,z,u[i-1]==v[j-1],eq[ni,pi,k,i-1,j-1]])])
                        eq[ni,pi,k,i,j] = compile_expr(owner, expr)
    for ni,u in enumerate(n):
        terms = []
        for k in range(m):
            terms.append(group('and', [active[k],group('and',[neg(eq[ni,pi,k,len(u),len(v)]) for pi,v in enumerate(p)])]))
        c = compile_expr(('C', ni), group('or', terms))
        if c is False: add([])
        elif c is not True: add([(c, True)])
    if threshold > m: add([])
    elif threshold > 0:
        for subset in itertools.combinations(active, m-threshold+1):
            if True in subset: continue
            add([(x, True) for x in subset if x is not False])
    return clauses, names



def blank(status, reason=None):
    result = {'status': status, 'compatible_count': None, 'optimal_count': None,
              'max_blocks': None, 'recommendation': None, 'optimal_unique': None,
              'compatible_witnesses': None, 'optimal_witnesses': None}
    if reason is not None: result['reason'] = reason
    return result


def normalize(data):
    if not isinstance(data,dict) or set(data) != {'alphabet','positive','negative'}:
        raise InvalidInput('expected exactly alphabet, positive, negative')
    a=data['alphabet']
    if not isinstance(a,list): raise InvalidInput('alphabet must be an array')
    if any(not isinstance(x,str) or not x for x in a): raise InvalidInput('alphabet IDs must be nonempty strings')
    if len(set(a)) != len(a): raise InvalidInput('alphabet IDs must be distinct')
    allowed=set(a); result=[]
    for key in ('positive','negative'):
        words=data[key]
        if not isinstance(words,list): raise InvalidInput(key+' must be an array')
        seen=set(); out=[]
        for word in words:
            if not isinstance(word,list): raise InvalidInput('each word must be an array')
            if any(not isinstance(x,str) or x not in allowed for x in word): raise InvalidInput('word contains invalid or unknown symbol')
            t=tuple(word)
            if t not in seen: seen.add(t); out.append(t)
        result.append(out)
    return tuple(a),result[0],result[1]


def bell_exceeds(m, cap):
    # Compute Bell numbers by Bell triangle, stopping as soon as threshold exceeded.
    row=[1]
    if cap < 1: return True
    for _ in range(m):
        nextrow=[row[-1]]
        for x in row: nextrow.append(nextrow[-1]+x)
        row=nextrow
        if row[0]>cap: return True
    return False


def sat(clauses):
    visited=0
    def go(assign):
        nonlocal visited
        visited+=1
        if visited>MAX_SEARCH_NODES: raise Limited()
        while True:
            unit=None; pick=None
            for clause in clauses:
                unassigned=[]; satisfied=False
                for var,sign in clause:
                    if var not in assign: unassigned.append((var,sign))
                    elif assign[var]==sign: satisfied=True; break
                if satisfied: continue
                if not unassigned: return None
                if len(unassigned)==1:
                    unit=unassigned[0]; break
                if pick is None: pick=unassigned[0][0]
            if unit is None: break
            assign[unit[0]]=unit[1]
        if pick is None: return assign
        for value in (False,True):
            branch=assign.copy(); branch[pick]=value
            found=go(branch)
            if found is not None: return found
        return None
    return go({})


def witness(a,p,n,r):
    k=max(r)+1 if r else 0
    blocks=[[] for _ in range(k)]
    for x,i in zip(a,r): blocks[i].append(x)
    factors=[]; sets=[]
    for b in blocks:
        members=set(b); seen=set(); local=[]
        for word in p:
            projection=tuple(x for x in word if x in members)
            if projection not in seen: seen.add(projection); local.append(list(projection))
        factors.append(local); sets.append(seen)
    rejected=[]
    for word in n:
        first=next((i for i,b in enumerate(blocks) if tuple(x for x in word if x in set(b)) not in sets[i]),None)
        if first is None: return None
        rejected.append(first)
    return {'rgs':list(r),'blocks':blocks,'factors':factors,'negative_rejected_by':rejected}


def solve(data, *, max_candidates=None):
    try:
        if max_candidates is not None and (type(max_candidates) is not int or max_candidates<0):
            return blank('INVALID_INPUT','max_candidates must be a nonnegative integer or None')
        try: a,p,n=normalize(data)
        except InvalidInput as exc: return blank('INVALID_INPUT',str(exc))
        if set(p)&set(n):
            result=blank('INCOMPATIBLE'); result.update(compatible_count=0,optimal_count=0,compatible_witnesses=[],optimal_witnesses=[]); return result
        m=len(a)
        if max_candidates is not None and bell_exceeds(m,max_candidates): return blank('INCOMPLETE','candidate budget exhausted')
        clauses,_=build(a,p,n,0)
        count=0; optimum=0; best=None; all_first=[]; best_first=[]; seen=set()
        while True:
            model=sat(clauses)
            if model is None: break
            labels=[]
            for i in range(m):
                owners=[k for k in range(m) if model.get(('Y',i,k),False)]
                if len(owners)!=1: return blank('ERROR','witness replay failed')
                labels.append(owners[0])
            r=tuple(labels)
            if r in seen or witness(a,p,n,r) is None: return blank('ERROR','witness replay failed')
            seen.add(r); count+=1
            if count>MAX_MODELS: raise Limited()
            all_first=sorted(all_first+[r])[:2]
            k=max(r)+1 if r else 0
            if best is None or k>best: best=k; optimum=1; best_first=[r]
            elif k==best: optimum+=1; best_first=sorted(best_first+[r])[:2]
            clauses.append(tuple((('Y',i,label),False) for i,label in enumerate(r)))
            if len(clauses)>MAX_CLAUSES: raise Limited()
        if not count:
            result=blank('INCOMPATIBLE'); result.update(compatible_count=0,optimal_count=0,compatible_witnesses=[],optimal_witnesses=[]); return result
        aw=[witness(a,p,n,r) for r in all_first]; bw=[witness(a,p,n,r) for r in best_first]
        if any(w is None for w in aw+bw): return blank('ERROR','witness replay failed')
        return {'status':'UNIQUE_COMPATIBLE' if count==1 else 'AMBIGUOUS', 'compatible_count':count,
                'optimal_count':optimum,'max_blocks':best,'recommendation':bw[0], 'optimal_unique':optimum==1,
                'compatible_witnesses':aw,'optimal_witnesses':bw}
    except (KeyboardInterrupt,MemoryError,RecursionError,OverflowError,Limited):
        return blank('INCOMPLETE','execution interrupted or resources exhausted')
