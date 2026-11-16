"""Independent proof checking; shared deterministic encoding is trusted.
Does not import the optimizer or SAT library. DRUP deletions safely ignored.
"""
import encoding as E
from itertools import combinations

class RupDatabase:
    """Indexed unit propagation, no external solver or persistent assignments."""
    def __init__(self,clauses,tick):
        self.clauses=[];self.occurrences={};self.lengths=[];self.units=[];self.empty=False;self.tick=tick
        for clause in clauses:self.add(clause)

    def add(self,clause):
        self.tick();unique=set(clause)
        if any(-literal in unique for literal in unique):return
        item=tuple(sorted(unique));index=len(self.clauses)
        self.clauses.append(item);self.lengths.append(len(item))
        if not item:self.empty=True
        if len(item)==1:self.units.append(item[0])
        for literal in item:self.occurrences.setdefault(literal,[]).append(index)

    def check(self,clause):
        if self.empty:return True
        remaining=self.lengths[:];values={};queue=self.units[:]+[-literal for literal in clause];head=0
        while head<len(queue):
            self.tick();literal=queue[head];head+=1;variable=abs(literal);value=literal>0
            if variable in values:
                if values[variable]!=value:return True
                continue
            values[variable]=value
            for index in self.occurrences.get(-literal,()):
                self.tick();item=self.clauses[index]
                if any(abs(x) in values and values[abs(x)]==(x>0) for x in item):continue
                remaining[index]-=1
                if remaining[index]==0:return True
                if remaining[index]==1:
                    unassigned=next(x for x in item if abs(x) not in values)
                    queue.append(unassigned)
        return False
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

def check_drup(enc,k,proof,tick):
    if type(proof) is not list:return False
    database=RupDatabase(E.threshold(enc,k+1),tick)
    for line in proof:
        tick()
        if type(line) is not str:return False
        parts=line.split();deletion=bool(parts and parts[0]=='d')
        if deletion:parts=parts[1:]
        if not parts or parts[-1]!='0':return False
        lits=[int(x) for x in parts[:-1]]
        if any(not x or abs(x)>enc['variables'] for x in lits):return False
        if deletion:continue
        if not database.check(lits):return False
        database.add(lits)
    return database.check([])
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
        if cert=={'type':'single_negative_bound'}:
            if len(n)!=1:return {'status':'REJECT'}
            prepared=E.Prepared(a,p,n,tick);groups=prepared.prepare_atoms();q=len(groups);d=q-k+1
            if not 1<=d<=q:return {'status':'REJECT'}
            for size in range(1,d):
                for subset in combinations(range(q),size):
                    if prepared.atom_rejects(sum(1<<i for i in subset),0):return {'status':'REJECT'}
            return {'status':'ACCEPT'}
        if cert=={'type':'edge_size_bound'}:
            enc=E.build(a,p,n,tick)
            return {'status':'ACCEPT' if k==enc['upper'] else 'REJECT'}
        if set(cert)!={'type','proof'} or cert['type']!='drup' or type(cert['proof']) is not list:return {'status':'REJECT'}
        enc=E.build(a,p,n,tick)
        return {'status':'ACCEPT' if check_drup(enc,k,cert['proof'],tick) else 'REJECT'}
    except (E.Exhausted,MemoryError,RecursionError,KeyboardInterrupt):return {'status':'INCOMPLETE'}
    except (E.Invalid,ValueError,TypeError,KeyError,IndexError):return {'status':'REJECT'}
