"""Independent proof checking; shared deterministic encoding is trusted.
Does not import the optimizer or SAT library. DRUP deletions safely ignored.
"""
import encoding as E
def rup(clauses,clause,tick):
    values={}
    for literal in clause:
        v=abs(literal); value=literal<0
        if v in values and values[v]!=value:return True
        values[v]=value
    while True:
        changed=False
        for c in clauses:
            tick(); free=[]
            if any(abs(x) in values and values[abs(x)]==(x>0) for x in c):continue
            free=[x for x in c if abs(x) not in values]
            if not free:return True
            if len(free)==1: values[abs(free[0])]=free[0]>0;changed=True
        if not changed:return False
def verify_optimal(instance,result,limits=None):
    try:
        tick=E.budget(limits);a,p,n=E.normalize(instance);tick()
        if type(result) is not dict or set(result)!={'status','blocks','max_devices','certificate'}:return {'status':'REJECT'}
        cert=result['certificate']
        if type(cert) is not dict:return {'status':'REJECT'}
        if result['status']=='INFEASIBLE':
            valid=result['blocks'] is None and result['max_devices'] is None and (bool(set(p)&set(n)) or (not a and bool(n)))
            return {'status':'ACCEPT' if valid and cert=={'type':'direct_infeasible'} else 'REJECT'}
        if result['status']!='OPTIMAL' or type(result['max_devices']) is not int:return {'status':'REJECT'}
        k=result['max_devices'];blocks=result['blocks']
        if not E.feasible(a,p,n,blocks) or k!=len(blocks):return {'status':'REJECT'}
        if cert=={'type':'symbol_bound'}:return {'status':'ACCEPT' if k==len(a) else 'REJECT'}
        if cert=={'type':'atom_bound'}:
            return {'status':'ACCEPT' if k==len(E.atoms(a,p,n,tick)) else 'REJECT'}
        if set(cert)!={'type','proof'} or cert['type']!='drup' or type(cert['proof']) is not list:return {'status':'REJECT'}
        enc=E.build(a,p,n,tick);clauses=E.threshold(enc,k+1)
        for line in cert['proof']:
            tick()
            if type(line) is not str:return {'status':'REJECT'}
            parts=line.split(); deletion=bool(parts and parts[0]=='d')
            if deletion:parts=parts[1:]
            if not parts or parts[-1]!='0':return {'status':'REJECT'}
            lits=[int(x) for x in parts[:-1]]
            if any(not x or abs(x)>enc['variables'] for x in lits):return {'status':'REJECT'}
            if deletion:continue
            if not rup(clauses,lits,tick):return {'status':'REJECT'}
            clauses.append(lits)
        return {'status':'ACCEPT' if rup(clauses,[],tick) else 'REJECT'}
    except (E.Exhausted,MemoryError,RecursionError,KeyboardInterrupt):return {'status':'INCOMPLETE'}
    except (E.Invalid,ValueError,TypeError,KeyError,IndexError):return {'status':'REJECT'}
