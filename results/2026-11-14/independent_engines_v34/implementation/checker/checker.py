"""Independent V34 logic certificate verifier; standard library only."""
import itertools
import json
import sys

# The profile requires arbitrary-precision JSON integers. Resource exhaustion
# remains INCOMPLETE rather than misclassifying a valid large integer.
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)

class Invalid(Exception):
    pass
class Incomplete(Exception):
    pass

def require(condition):
    if not condition:
        raise Invalid()

def obj(value, keys):
    require(type(value) is dict and set(value) == set(keys))

def scalar(s):
    return type(s) is str and not any(0xD800 <= ord(c) <= 0xDFFF for c in s)

def integer(x):
    return type(x) is int and x >= 0

def instance(value):
    obj(value, ('alphabet', 'positive', 'negative'))
    a = value['alphabet']; require(type(a) is list)
    require(all(scalar(s) and s for s in a) and len(set(a)) == len(a))
    alphabet = set(a)
    lists = []
    for key in ('positive', 'negative'):
        words = value[key]; require(type(words) is list)
        unique = []; seen = set()
        for word in words:
            require(type(word) is list and all(scalar(x) and x in alphabet for x in word))
            w = tuple(word)
            if w not in seen:
                seen.add(w); unique.append(w)
        lists.append(unique)
    return a, lists[0], lists[1]

def witness_valid(witness, alphabet, positives, negatives):
    require(type(witness) is list)
    available = set(alphabet); found = set(); blocks = []
    for block in witness:
        require(type(block) is list and len(block) > 0)
        require(all(scalar(x) and x in available for x in block))
        require(len(set(block)) == len(block) and not found.intersection(block))
        found.update(block); blocks.append(set(block))
    require(found == available)
    for n in negatives:
        require(any(tuple(x for x in n if x in b) not in
                    {tuple(x for x in p if x in b) for p in positives} for b in blocks))
    return len(blocks)

# Expression trees are ('not',child), ('and',left,right), ('or',left,right).
def conjunction(items):
    if not items: return True
    value = items[0]
    for item in items[1:]: value = ('and', value, item)
    return value

def disjunction(items):
    if not items: return False
    value = items[0]
    for item in items[1:]: value = ('or', value, item)
    return value

def build(alphabet, positives, negatives, threshold):
    m = len(alphabet); idx = {v:i for i,v in enumerate(alphabet)}
    variables = set(); clauses = []
    def y(i, k): return ('Y', i, k)
    for i in range(m):
        for k in range(m): variables.add(y(i,k))
    def clause(literals):
        result = set()
        for var, sign in literals:
            if type(var) is bool:
                if var == sign: return
                continue
            if (var, not sign) in result: return
            result.add((var, sign))
        clauses.append(frozenset(result))
    for i in range(m):
        clause([(y(i,k), True) for k in range(m)])
        for k in range(m):
            for q in range(k): clause([(y(i,k),False),(y(i,q),False)])
        for k in range(1,m):
            clause([(y(i,k),False)] + [(y(j,k-1),True) for j in range(i)])
    def owner_expr(owner, expression):
        def lower(expr, path):
            if type(expr) is bool or (type(expr) is tuple and expr[0] in ('Y','G')):
                return expr
            op = expr[0]; children = [lower(child, path+(i,)) for i,child in enumerate(expr[1:])]
            gate = ('G', owner, path); variables.add(gate)
            distinct = list(dict.fromkeys(v for v in children if type(v) is not bool))
            for vals in itertools.product((False, True), repeat=len(distinct)):
                values = dict(zip(distinct, vals))
                args = [v if type(v) is bool else values[v] for v in children]
                expected = (not args[0]) if op == 'not' else ((args[0] and args[1]) if op == 'and' else (args[0] or args[1]))
                # Exclude inputs plus the incorrect output valuation.
                clause([(v, not b) for v,b in zip(distinct,vals)] + [(gate, expected)])
            return gate
        return lower(expression, ())
    active = []
    for k in range(m):
        active.append(owner_expr(('A',k),disjunction([y(i,k) for i in range(m)])))
    eq = {}
    for ni,n in enumerate(negatives):
        for pi,p in enumerate(positives):
            for k in range(m):
                for i in range(len(n)+1):
                    for j in range(len(p)+1):
                        key = (ni,pi,k,i,j)
                        if i == 0 and j == 0: expression = True
                        elif j == 0: expression = conjunction([eq[ni,pi,k,i-1,0], ('not',y(idx[n[i-1]],k))])
                        elif i == 0: expression = conjunction([eq[ni,pi,k,0,j-1], ('not',y(idx[p[j-1]],k))])
                        else:
                            x = y(idx[n[i-1]],k); z = y(idx[p[j-1]],k)
                            expression = disjunction([
                                conjunction([('not',x),eq[ni,pi,k,i-1,j]]),
                                conjunction([x,('not',z),eq[ni,pi,k,i,j-1]]),
                                conjunction([x,z,n[i-1]==p[j-1],eq[ni,pi,k,i-1,j-1]])])
                        eq[key] = owner_expr(('E',)+key, expression)
    for ni,n in enumerate(negatives):
        parts = []
        for k in range(m):
            comparisons = [('not',eq[ni,pi,k,len(n),len(p)]) for pi,p in enumerate(positives)]
            parts.append(conjunction([active[k],conjunction(comparisons)]))
        root = owner_expr(('C',ni),disjunction(parts))
        clause([(root,True)])
    if threshold > m: clause([])
    elif threshold > 0:
        for subset in itertools.combinations(range(m),m-threshold+1):
            clause([(active[k],True) for k in subset])
    return variables, clauses

def read_name(value):
    require(type(value) is list and len(value) >= 1 and type(value[0]) is str)
    if value[0] == 'Y':
        require(len(value)==3 and integer(value[1]) and integer(value[2]))
        return ('Y',value[1],value[2])
    require(value[0]=='G' and len(value)==3 and type(value[1]) is list and type(value[2]) is list)
    owner=value[1]; path=value[2]
    require(owner and owner[0] in ('A','E','C'))
    require(len(owner)=={'A':2,'E':6,'C':2}[owner[0]] and all(integer(x) for x in owner[1:]))
    require(all(integer(x) for x in path))
    return ('G',tuple(owner),tuple(path))

def verify_inner(request):
    obj(request,('instance','certificate','limits'))
    alphabet, positives, negatives = instance(request['instance'])
    limits=request['limits']; obj(limits,('max_nodes',)); limit=limits['max_nodes']
    require(limit is None or integer(limit))
    cert=request['certificate']; obj(cert,('version','kind','claim','witness','tree'))
    require(cert['version']=='v34-cert-r1' and cert['kind'] in ('logic','hypergraph'))
    if cert['kind']=='hypergraph': raise Incomplete()
    require(cert['claim'] in ('OPTIMAL','INFEASIBLE'))
    if cert['claim']=='OPTIMAL':
        k=witness_valid(cert['witness'],alphabet,positives,negatives); threshold=k+1
    else:
        require(cert['witness'] is None); threshold=0
    variables, clauses = build(alphabet,positives,negatives,threshold)
    stack=[(cert['tree'],{})]; visited=0
    while stack:
        if limit is not None and visited >= limit: raise Incomplete()
        node, assignment = stack.pop(); visited += 1
        require(type(node) is dict and 'tag' in node)
        if node['tag']=='conflict':
            obj(node,('tag',))
            require(any(all(var in assignment and assignment[var] != sign for var,sign in c) for c in clauses))
        elif node['tag']=='split':
            obj(node,('tag','v','zero','one'))
            name=read_name(node['v']); require(name in variables and name not in assignment)
            left=assignment.copy(); left[name]=False
            right=assignment.copy(); right[name]=True
            stack.append((node['one'],right)); stack.append((node['zero'],left))
        else: raise Invalid()
    return {'status':'ACCEPT'}

def validate_json(value):
    if value is None or type(value) is bool or type(value) is int: return
    if type(value) is str:
        require(scalar(value)); return
    if type(value) is list:
        for item in value: validate_json(item)
        return
    if type(value) is dict:
        for key, item in value.items():
            require(scalar(key)); validate_json(item)
        return
    raise Invalid()

def verify(request):
    try:
        validate_json(request)
        return verify_inner(request)
    except Incomplete:
        return {'status':'INCOMPLETE'}
    except (MemoryError, RecursionError, TimeoutError, KeyboardInterrupt):
        return {'status':'INCOMPLETE'}
    except (Invalid, TypeError, ValueError, KeyError, IndexError):
        return {'status':'REJECT'}

def strict_load(raw):
    def pairs(items):
        out={}
        for key,value in items:
            if key in out: raise Invalid()
            out[key]=value
        return out
    def reject_number(_): raise Invalid()
    text=raw.decode('utf-8')
    require(not text.startswith('\ufeff'))
    return json.loads(text, object_pairs_hook=pairs, parse_float=reject_number,
                      parse_constant=reject_number)

def main():
    try:
        request=strict_load(sys.stdin.buffer.read())
        result=verify(request)
    except (MemoryError, RecursionError, TimeoutError, KeyboardInterrupt): result={'status':'INCOMPLETE'}
    except (Invalid, UnicodeError, ValueError, TypeError): result={'status':'REJECT'}
    sys.stdout.write(json.dumps(result, separators=(',',':'))+'\n')

if __name__ == '__main__': main()
