"""Standalone V34 Boolean milestone. No external dependencies."""
import itertools
import json
import sys

class Invalid(Exception): pass
class Limited(Exception): pass

if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)

MAX_BYTES = 8_000_000
MAX_VARIABLES = 2000
MAX_CLAUSES = 200_000
MAX_SEARCH_NODES = 200_000
MAX_OUTPUT_BYTES = 8_000_000


def scalar(s):
    return isinstance(s, str) and all(not 0xD800 <= ord(c) <= 0xDFFF for c in s)


def unique_object(pairs):
    d = {}
    for k, v in pairs:
        if k in d: raise Invalid()
        d[k] = v
    return d


def parse_json(raw):
    if len(raw) > MAX_BYTES: raise Limited()
    try:
        s = raw.decode('utf-8')
        if s.startswith('\ufeff'): raise Invalid()
        def invalid_number(_): raise Invalid()
        return json.loads(s, object_pairs_hook=unique_object, parse_float=invalid_number,
                          parse_constant=invalid_number)
    except (UnicodeError, ValueError, RecursionError) as e:
        raise Invalid() from e


def validate(req):
    if not isinstance(req, dict) or set(req) != {'instance', 'kind', 'limits'}: raise Invalid()
    if req['kind'] not in ('logic', 'hypergraph'): raise Invalid()
    lim = req['limits']
    if not isinstance(lim, dict) or set(lim) != {'max_nodes'}: raise Invalid()
    cap = lim['max_nodes']
    if cap is not None and (type(cap) is not int or cap < 0): raise Invalid()
    ins = req['instance']
    if not isinstance(ins, dict) or set(ins) != {'alphabet', 'positive', 'negative'}: raise Invalid()
    a, p, n = ins['alphabet'], ins['positive'], ins['negative']
    if not isinstance(a, list) or any(not scalar(x) or not x for x in a) or len(set(a)) != len(a): raise Invalid()
    allowed = set(a)
    def words(w):
        if not isinstance(w, list): raise Invalid()
        out, seen = [], set()
        for row in w:
            if not isinstance(row, list) or any(not scalar(x) or x not in allowed for x in row): raise Invalid()
            t = tuple(row)
            if t not in seen: out.append(t); seen.add(t)
        return out
    return a, words(p), words(n), cap


def projection(word, block): return tuple(x for x in word if x in block)

def witness_ok(a, p, n, blocks):
    try:
        flat = [x for b in blocks for x in b]
        if any(not b for b in blocks) or len(flat) != len(a) or set(flat) != set(a) or len(set(flat)) != len(flat): return False
        for word in n:
            if not any(projection(word, set(b)) not in {projection(w, set(b)) for w in p} for b in blocks): return False
        return True
    except (TypeError, ValueError): return False

# Expression leaves are booleans or variable-name tuples; operation nodes are lists.
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
    def compile_expr(owner, expr, path=()):
        if not isinstance(expr, list): return expr
        op = expr[0]
        children = [compile_expr(owner, child, path+(i,)) for i,child in enumerate(expr[1:])]
        g = var(('G', owner, path))
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


def wire(v):
    if v[0] == 'Y': return list(v)
    return ['G', list(v[1]), list(v[2])]


def search(clauses, cap):
    visits = 0
    def go(assignment):
        nonlocal visits
        if visits >= MAX_SEARCH_NODES or (cap is not None and visits >= cap): raise Limited()
        visits += 1
        choice = None
        for clause in clauses:
            satisfied = False; unassigned = []
            for v, sign in clause:
                if v not in assignment: unassigned.append(v)
                elif assignment[v] == sign: satisfied = True; break
            if satisfied: continue
            if not unassigned: return None, {'tag':'conflict'}
            if choice is None: choice = unassigned[0]
        if choice is None: return assignment, None
        left = dict(assignment); left[choice] = False
        model, zero = go(left)
        if model is not None: return model, None
        right = dict(assignment); right[choice] = True
        model, one = go(right)
        if model is not None: return model, None
        return None, {'tag':'split', 'v':wire(choice), 'zero':zero, 'one':one}
    return go({})


def check_tree(clauses, names, tree, cap):
    count = 0
    def go(node, assignment):
        nonlocal count
        if cap is not None and count >= cap: raise Limited()
        count += 1
        if not isinstance(node, dict): return False
        if node.get('tag') == 'conflict' and set(node) == {'tag'}:
            return any(all(v in assignment and assignment[v] != sign for v,sign in clause) for clause in clauses)
        if node.get('tag') != 'split' or set(node) != {'tag','v','zero','one'}: return False
        w = node['v']
        try:
            if w[0] == 'Y' and len(w) == 3: v = tuple(w)
            elif w[0] == 'G' and len(w) == 3: v = ('G',tuple(w[1]),tuple(w[2]))
            else: return False
            if v not in names or v in assignment: return False
        except (TypeError, IndexError): return False
        assignment[v] = False
        ok = go(node['zero'],assignment)
        assignment[v] = True
        ok = ok and go(node['one'],assignment)
        del assignment[v]
        return ok
    return go(tree,{})


def solve(req):
    try:
        a,p,n,cap = validate(req)
        if req['kind'] != 'logic': return {'status':'INCOMPLETE','certificate':None}
        if cap == 0: raise Limited()
        # Discover optimum by descending thresholds, retaining the adjacent refutation.
        upper_tree = None
        for threshold in range(len(a), -1, -1):
            clauses,names = build(a,p,n,threshold)
            model,tree = search(clauses, cap)
            if model is None:
                upper_tree = (clauses,names,tree)
                continue
            blocks = [[] for _ in range(len(a))]
            for i,symbol in enumerate(a):
                slots = [k for k in range(len(a)) if model.get(('Y',i,k),False)]
                if len(slots) != 1: raise Limited()
                blocks[slots[0]].append(symbol)
            blocks = [b for b in blocks if b]
            if not witness_ok(a,p,n,blocks): raise Limited()
            k = len(blocks)
            if k != threshold: raise Limited()
            if upper_tree is None: upper_tree = (*build(a,p,n,k+1), {'tag':'conflict'})
            proof_clauses,proof_names,proof = upper_tree
            if not check_tree(proof_clauses,proof_names,proof,cap): raise Limited()
            cert = {'version':'v34-cert-r1','kind':'logic','claim':'OPTIMAL','witness':blocks,'tree':proof}
            return {'status':'OPTIMAL','certificate':cert}
        if upper_tree is None: raise Limited()
        proof_clauses,proof_names,proof = upper_tree
        if not check_tree(proof_clauses,proof_names,proof,cap): raise Limited()
        return {'status':'INFEASIBLE','certificate':{'version':'v34-cert-r1','kind':'logic','claim':'INFEASIBLE','witness':None,'tree':proof}}
    except Invalid:
        return {'status':'INVALID_INPUT','certificate':None}
    except (Limited, MemoryError, RecursionError, OverflowError):
        return {'status':'INCOMPLETE','certificate':None}


def main():
    try:
        raw = sys.stdin.buffer.read(MAX_BYTES+1)
        req = parse_json(raw)
        response = solve(req)
        data = json.dumps(response, ensure_ascii=True, separators=(',',':')).encode('utf-8')
        if len(data) > MAX_OUTPUT_BYTES: data = b'{"status":"INCOMPLETE","certificate":null}'
    except Invalid: data = b'{"status":"INVALID_INPUT","certificate":null}'
    except (Limited, MemoryError, RecursionError, OverflowError): data = b'{"status":"INCOMPLETE","certificate":null}'
    sys.stdout.buffer.write(data+b'\n')

if __name__ == '__main__': main()


