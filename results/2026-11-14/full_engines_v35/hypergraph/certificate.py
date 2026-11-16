"""V34-profile hypergraph optimum/infeasibility proof producer."""
import json
import sys
import candidate

if hasattr(sys,'set_int_max_str_digits'): sys.set_int_max_str_digits(0)
MAX_BYTES=8_000_000
class Invalid(Exception): pass
class Limited(Exception): pass


def scalar(x): return type(x) is str and all(not 0xD800<=ord(c)<=0xDFFF for c in x)
def validate(value):
    if type(value) is not dict or set(value)!={'instance','kind','limits'} or value['kind']!='hypergraph': raise Invalid()
    lim=value['limits']
    if type(lim) is not dict or set(lim)!={'max_nodes'}: raise Invalid()
    cap=lim['max_nodes']
    if cap is not None and (type(cap) is not int or cap<0): raise Invalid()
    d=value['instance']
    if type(d) is not dict or set(d)!={'alphabet','positive','negative'}: raise Invalid()
    if type(d['alphabet']) is not list or any(not scalar(x) or not x for x in d['alphabet']): raise Invalid()
    for label in ('positive','negative'):
        if type(d[label]) is not list: raise Invalid()
        for w in d[label]:
            if type(w) is not list or any(not scalar(x) for x in w): raise Invalid()
    try: a,p,n=candidate.normalize(d)
    except candidate.Invalid: raise Invalid()
    return a,p,n,cap


def subsets(s,m):
    a=s&-s
    found=[]; b=s
    while b:
        if b&a: found.append(b)
        b=(b-1)&s
    found.sort(key=lambda b: tuple(bool(b&(1<<i)) for i in range(m)))
    return found


def certify(request):
    try:
        a,p,n,cap=validate(request)
        result=candidate.solve(request['instance'])
        if result['status']=='INCOMPLETE': raise Limited()
        if result['status'] not in ('INCOMPATIBLE','AMBIGUOUS','UNIQUE_COMPATIBLE'): raise Limited()
        optimal=result['status']!='INCOMPATIBLE'; k=result['max_blocks'] if optimal else None
        tags=candidate.rows(a,p,n); count=0; m=len(a)
        def build(s,u,q):
            nonlocal count
            if cap is not None and count>=cap: raise Limited()
            count+=1
            if optimal and q+s.bit_count()<=k: return {'tag':'bound'}
            if not s:
                if u: return {'tag':'uncovered'}
                raise Limited()
            return {'tag':'branch','children':[{'block':[i for i in range(m) if b&(1<<i)],
                       'child':build(s^b,u&~tags[b],q+1)} for b in subsets(s,m)]}
        tree=build((1<<m)-1,(1<<len(n))-1,0)
        # Local replay reconstructs row tags and checks branch completeness, bound and witness.
        reconstructed=candidate.rows(a,p,n)
        def check(node,s,u,q):
            tag=node.get('tag')
            if tag=='bound': return optimal and q+s.bit_count()<=k and set(node)=={'tag'}
            if tag=='uncovered': return not s and bool(u) and set(node)=={'tag'}
            if tag!='branch' or not s or set(node)!={'tag','children'}: return False
            children=node['children']; expected=subsets(s,m)
            if len(children)!=len(expected): return False
            for entry,b in zip(children,expected):
                if set(entry)!={'block','child'} or entry['block']!=[i for i in range(m) if b&(1<<i)]: return False
                if not check(entry['child'],s^b,u&~reconstructed[b],q+1): return False
            return True
        blocks=result['recommendation']['blocks'] if optimal else None
        if optimal:
            flat=[x for b in blocks for x in b]
            if len(flat)!=m or len(set(flat))!=m or set(flat)!=set(a) or any(not b for b in blocks): raise Limited()
            for w in n:
                if not any(tuple(x for x in w if x in set(b)) not in {tuple(x for x in z if x in set(b)) for z in p} for b in blocks): raise Limited()
        if not check(tree,(1<<m)-1,(1<<len(n))-1,0): raise Limited()
        claim='OPTIMAL' if optimal else 'INFEASIBLE'
        return {'status':claim,'certificate':{'version':'v34-cert-r1','kind':'hypergraph','claim':claim,'witness':blocks,'tree':tree}}
    except Invalid: return {'status':'INVALID_INPUT','certificate':None}
    except (Limited,MemoryError,RecursionError,OverflowError,KeyboardInterrupt): return {'status':'INCOMPLETE','certificate':None}


def strict_load(raw):
    if len(raw)>MAX_BYTES: raise Limited()
    def pairs(xs):
        d={}
        for k,v in xs:
            if k in d: raise Invalid()
            d[k]=v
        return d
    def bad(_): raise Invalid()
    try:
        text=raw.decode('utf-8')
        if text.startswith('\ufeff'): raise Invalid()
        obj=json.loads(text,object_pairs_hook=pairs,parse_float=bad,parse_constant=bad)
    except (UnicodeError,ValueError): raise Invalid()
    def check(x):
        if x is None or type(x) in (bool,int): return
        if type(x) is str:
            if not scalar(x): raise Invalid()
        elif type(x) is list:
            for z in x: check(z)
        elif type(x) is dict:
            for k,v in x.items(): check(k); check(v)
        else: raise Invalid()
    check(obj); return obj


def main():
    try: response=certify(strict_load(sys.stdin.buffer.read(MAX_BYTES+1)))
    except Invalid: response={'status':'INVALID_INPUT','certificate':None}
    except (Limited,MemoryError,RecursionError,OverflowError,KeyboardInterrupt): response={'status':'INCOMPLETE','certificate':None}
    try: out=json.dumps(response,ensure_ascii=True,separators=(',',':'))
    except (MemoryError,RecursionError,OverflowError): out='{"status":"INCOMPLETE","certificate":null}'
    sys.stdout.write(out+'\n')

if __name__=='__main__': main()
