"""Certificate consumer: no teacher, native SAT, or projection-store imports.

Pair/count/cut CNF specification is shared trusted code. False-region witnesses
are checked by direct projection of original words; maximality is unnecessary.
"""
from spec import Invalid,Exhausted,budget,normalize,partition_masks,direct_reject,mandatory_groups
from master import Master

def rup(formula,clause,tick):
    values={}
    for literal in clause:
        variable=abs(literal);value=literal<0
        if variable in values and values[variable]!=value:return True
        values[variable]=value
    while True:
        changed=False
        for c in formula:
            tick()
            if any(abs(x) in values and values[abs(x)]==(x>0) for x in c):continue
            free=[x for x in c if abs(x) not in values]
            if not free:return True
            if len(free)==1:values[abs(free[0])]=free[0]>0;changed=True
        if not changed:return False

def check_drup(master,t,proof,tick):
    if type(proof) is not list:return False
    formula=[list(dict.fromkeys(c)) for c in master.threshold(t) if not any(-x in c for x in c)]
    for line in proof:
        tick()
        if type(line) is not str:return False
        words=line.split();delete=bool(words and words[0]=='d')
        if delete:words=words[1:]
        if not words or words[-1]!='0':return False
        clause=[int(x) for x in words[:-1]]
        if any(not x or abs(x)>master.variables for x in clause):return False
        if delete:continue
        if any(-x in clause for x in clause):continue
        clause=list(dict.fromkeys(clause))
        if not rup(formula,clause,tick):return False
        formula.append(clause)
    return rup(formula,[],tick)

def verify_optimal(D,result,limits=None):
    try:
        tick=budget(limits);a,p,n=normalize(D);tick()
        if type(result) is not dict or set(result)!={'status','blocks','max_devices','certificate'}:return {'status':'REJECT'}
        cert=result['certificate']
        if type(cert) is not dict:return {'status':'REJECT'}
        if result['status']=='INFEASIBLE':
            valid=(set(p)&set(n) or (not a and n)) and result['blocks'] is None and result['max_devices'] is None and cert=={'type':'direct_infeasible'}
            return {'status':'ACCEPT' if valid else 'REJECT'}
        if result['status']!='OPTIMAL' or type(result['max_devices']) is not int:return {'status':'REJECT'}
        masks=partition_masks(a,result['blocks']);k=result['max_devices']
        covered=0
        for mask in masks:tick();covered|=direct_reject(a,p,n,mask)
        if covered!=(1<<len(n))-1 or k!=len(masks):return {'status':'REJECT'}
        if cert=={'type':'symbol_bound'}:return {'status':'ACCEPT' if k==len(a) else 'REJECT'}
        groups=mandatory_groups(a,n,lambda mask:direct_reject(a,p,n,mask),tick);q=len(groups)
        if cert=={'type':'atom_bound'}:return {'status':'ACCEPT' if k==q else 'REJECT'}
        if set(cert)!={'type','cuts','proof'} or cert['type']!='teacher_cut_drup' or type(cert['cuts']) is not list:return {'status':'REJECT'}
        master=Master(q,tick)
        for cut in cert['cuts']:
            tick()
            if type(cut) is not dict or set(cut)!={'negative_index','regions','positive_indices'}:return {'status':'REJECT'}
            i=cut['negative_index'];regions=cut['regions'];witnesses=cut['positive_indices']
            if type(i) is not int or not 0<=i<len(n) or type(regions) is not list or not regions or type(witnesses) is not list or len(regions)!=len(witnesses):return {'status':'REJECT'}
            if regions!=sorted(set(regions)):return {'status':'REJECT'}
            for U,j in zip(regions,witnesses):
                if type(U) is not int or not 0<U<(1<<q)-1 or type(j) is not int or not 0<=j<len(p):return {'status':'REJECT'}
                selected={a[x] for t,B in enumerate(groups) if U>>t&1 for x in B}
                if tuple(x for x in n[i] if x in selected)!=tuple(x for x in p[j] if x in selected):return {'status':'REJECT'}
            master.add_cover(regions)
        return {'status':'ACCEPT' if check_drup(master,k+1,cert['proof'],tick) else 'REJECT'}
    except (Exhausted,MemoryError,RecursionError,KeyboardInterrupt):return {'status':'INCOMPLETE'}
    except (Invalid,ValueError,TypeError,KeyError,IndexError):return {'status':'REJECT'}
