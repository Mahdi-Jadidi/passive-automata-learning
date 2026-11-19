"""Independent V34-profile mixed-cover certificate checker, standard library."""
import itertools
import json
import sys
if hasattr(sys, 'set_int_max_str_digits'): sys.set_int_max_str_digits(0)

class Invalid(Exception): pass
class Incomplete(Exception): pass

def need(x):
    if not x: raise Invalid()
def object_keys(x, keys): need(type(x) is dict and set(x)==set(keys))
def string(x): return type(x) is str and all(not 0xD800<=ord(c)<=0xDFFF for c in x)
def integer(x): return type(x) is int and x>=0

def validate_value(x):
    if x is None or type(x) in (bool,int): return
    if type(x) is str: need(string(x)); return
    if type(x) is list:
        for v in x: validate_value(v)
        return
    if type(x) is dict:
        for k,v in x.items(): need(string(k)); validate_value(v)
        return
    raise Invalid()

def normalize(x):
    object_keys(x, ('alphabet','positive','negative'))
    a=x['alphabet']; need(type(a) is list and all(string(i) and i for i in a))
    need(len(a)==len(set(a))); aset=set(a); outputs=[]
    for key in ('positive','negative'):
        ws=x[key]; need(type(ws) is list); seen=set(); out=[]
        for w in ws:
            need(type(w) is list and all(string(i) and i in aset for i in w))
            t=tuple(w)
            if t not in seen: seen.add(t); out.append(t)
        outputs.append(out)
    return a,outputs[0],outputs[1]

def coverage(indices, alphabet, positives, negatives):
    symbols={alphabet[i] for i in indices}
    def project(w): return tuple(x for x in w if x in symbols)
    pp={project(p) for p in positives}
    return {i for i,n in enumerate(negatives) if project(n) not in pp}

def verify_inner(r):
    object_keys(r, ('instance','certificate','limits'))
    a,p,n=normalize(r['instance']); m=len(a)
    lim=r['limits']; object_keys(lim,('max_nodes',)); maximum=lim['max_nodes']
    need(maximum is None or integer(maximum))
    c=r['certificate']; object_keys(c,('version','kind','claim','witness','tree'))
    need(c['version']=='v34-cert-r1' and c['kind'] in ('hypergraph','logic'))
    if c['kind']=='logic': raise Incomplete()
    need(c['claim'] in ('OPTIMAL','INFEASIBLE'))
    if c['claim']=='OPTIMAL':
        witness=c['witness']; need(type(witness) is list)
        found=set(); cover=set(); k=len(witness); index={v:i for i,v in enumerate(a)}
        for b in witness:
            need(type(b) is list and len(b)>0 and all(string(x) and x in index for x in b))
            need(len(set(b))==len(b) and not found.intersection(b))
            found.update(b); cover |= coverage([index[x] for x in b],a,p,n)
        need(found==set(a) and cover==set(range(len(n))))
    else:
        need(c['witness'] is None); k=None
    # Iterative preorder; each entry owns its remaining symbols and negatives.
    stack=[(c['tree'],tuple(range(m)),frozenset(range(len(n))),0)]; visits=0
    while stack:
        if maximum is not None and visits>=maximum: raise Incomplete()
        node,S,U,q=stack.pop(); visits+=1
        need(type(node) is dict and 'tag' in node)
        if node['tag']=='bound':
            object_keys(node,('tag',)); need(k is not None and q+len(S)<=k); continue
        if node['tag']=='uncovered':
            object_keys(node,('tag',)); need(not S and bool(U)); continue
        need(bool(S) and node['tag']=='branch'); object_keys(node,('tag','children'))
        children=node['children']; need(type(children) is list)
        # Enumerate numeric incidence vectors with 0 before 1; least S must be 1.
        options=itertools.product((0,1),repeat=len(S)-1)
        expected_count=1 << (len(S)-1); need(len(children)==expected_count)
        scheduled=[]
        for child,bits in zip(children,options):
            block=(S[0],)+tuple(v for v,bit in zip(S[1:],bits) if bit)
            object_keys(child,('block','child')); raw=child['block']
            need(type(raw) is list and all(integer(x) for x in raw) and raw==list(block))
            bset=set(block); remainder=tuple(v for v in S if v not in bset)
            remaining=U-coverage(block,a,p,n)
            scheduled.append((child['child'],remainder,frozenset(remaining),q+1))
        stack.extend(reversed(scheduled))
    return {'status':'ACCEPT'}

def verify(request):
    try:
        validate_value(request); return verify_inner(request)
    except Incomplete: return {'status':'INCOMPLETE'}
    except (MemoryError,RecursionError,TimeoutError,KeyboardInterrupt,OverflowError): return {'status':'INCOMPLETE'}
    except (Invalid,TypeError,ValueError,KeyError,IndexError): return {'status':'REJECT'}

def strict_load(raw):
    def pairs(values):
        result={}
        for k,v in values:
            if k in result: raise Invalid()
            result[k]=v
        return result
    def bad(_): raise Invalid()
    data=raw.decode('utf-8'); need(not data.startswith('\ufeff'))
    return json.loads(data,object_pairs_hook=pairs,parse_float=bad,parse_constant=bad)

def main():
    try: response=verify(strict_load(sys.stdin.buffer.read()))
    except (MemoryError,RecursionError,TimeoutError,KeyboardInterrupt,OverflowError): response={'status':'INCOMPLETE'}
    except (Invalid,UnicodeError,ValueError,TypeError): response={'status':'REJECT'}
    sys.stdout.write(json.dumps(response,separators=(',',':'))+'\n')
if __name__=='__main__': main()
