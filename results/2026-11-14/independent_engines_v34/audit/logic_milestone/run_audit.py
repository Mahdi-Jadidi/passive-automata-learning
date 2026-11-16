"""Bounded subprocess audit; invoke only on frozen, hash-recorded sources."""
import copy, hashlib, json, pathlib, subprocess, sys
from oracle import corpus, optimum, witness_valid

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOLVER = ROOT / 'implementation' / 'logic' / 'solver.py'
CHECKER = ROOT / 'implementation' / 'checker' / 'checker.py'
OUT = pathlib.Path(__file__).with_name('audit_raw.jsonl')

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest().upper()

def invoke(path, value=None, raw=None, timeout=10):
    payload = raw if raw is not None else json.dumps(value, ensure_ascii=True).encode()
    try:
        p = subprocess.run([sys.executable, str(path)], input=payload, capture_output=True, timeout=timeout)
        try: response = json.loads(p.stdout)
        except Exception: response = None
        return {'exit':p.returncode, 'response':response, 'stdout':p.stdout.decode('utf-8','replace'), 'stderr':p.stderr.decode('utf-8','replace')}
    except subprocess.TimeoutExpired:
        return {'timeout':True}

def nodes(tree):
    return 1 if tree['tag']=='conflict' else 1+nodes(tree['zero'])+nodes(tree['one'])

def main():
    with OUT.open('w',encoding='utf-8') as log:
        def record(name, passed, **data):
            log.write(json.dumps({'case':name,'pass':passed,**data},ensure_ascii=True)+'\n'); log.flush()
        record('sources', True, solver_sha256=digest(SOLVER),checker_sha256=digest(CHECKER),oracle_sha256=digest(pathlib.Path(__file__).with_name('oracle.py')),harness_sha256=digest(pathlib.Path(__file__)))
        captured = []
        for name, inst in corpus():
            expected = optimum(inst)
            result = invoke(SOLVER, {'instance':inst,'kind':'logic','limits':{'max_nodes':None}})
            response = result.get('response') or {}
            status = 'INFEASIBLE' if expected is None else 'OPTIMAL'
            cert = response.get('certificate')
            good = result.get('exit') == 0 and response.get('status') == status and isinstance(cert,dict)
            if good and expected is not None:
                good = witness_valid(inst,cert.get('witness')) and len(cert['witness']) == expected
            record('solver_'+name,good,expected=status,expected_k=expected,result=result)
            if not good: continue
            checked=invoke(CHECKER,{'instance':inst,'certificate':cert,'limits':{'max_nodes':None}})
            record('checker_'+name,checked.get('exit')==0 and checked.get('response')=={'status':'ACCEPT'},result=checked)
            captured.append((name,inst,cert))
        if captured:
            name,inst,cert = next((x for x in captured if x[2]['claim']=='OPTIMAL' and len(x[1]['alphabet'])>0 and nodes(x[2]['tree'])>1),captured[0])
            req={'instance':inst,'certificate':cert,'limits':{'max_nodes':None}}
            count=nodes(cert['tree'])
            for cap, status in [(0,'INCOMPLETE'),(count-1,'INCOMPLETE'),(count,'ACCEPT')]:
                r=copy.deepcopy(req); r['limits']['max_nodes']=cap; out=invoke(CHECKER,r)
                record('checker_cap_'+str(cap),out.get('response')=={'status':status},result=out,proof_nodes=count)
            corrupt=copy.deepcopy(req); corrupt['certificate']['tree']={'tag':'conflict','extra':1}
            out=invoke(CHECKER,corrupt); record('tamper_tree',out.get('response')=={'status':'REJECT'},result=out)
            corrupt=copy.deepcopy(req); corrupt['certificate']['witness']=[['not_declared']]
            out=invoke(CHECKER,corrupt); record('tamper_witness',out.get('response')=={'status':'REJECT'},result=out)
            valid_wire=json.dumps(req,ensure_ascii=True,separators=(',',':')).encode()
            duplicate_wire=valid_wire.replace(b'"version":"v34-cert-r1"',b'"version":"v34-cert-r1","version":"v34-cert-r1"',1)
            out=invoke(CHECKER,raw=duplicate_wire); record('checker_duplicate_valid_envelope',out.get('response')=={'status':'REJECT'},result=out)
            for spelling in ('true','1e0'):
                wire=valid_wire.replace(b'"max_nodes":null',('"max_nodes":'+spelling).encode(),1)
                out=invoke(CHECKER,raw=wire); record('checker_limit_'+spelling,out.get('response')=={'status':'REJECT'},result=out)
            # A contradiction makes this OPTIMAL certificate invalid, regardless of its original witness.
            corrupt=copy.deepcopy(req); corrupt['instance']['positive']=[[]]; corrupt['instance']['negative']=[[]]
            out=invoke(CHECKER,corrupt); record('instance_rebinding',out.get('response')=={'status':'REJECT'},result=out)
        valid={'instance':{'alphabet':['a'],'positive':[],'negative':[]},'kind':'logic','limits':{'max_nodes':0}}
        out=invoke(SOLVER,valid); record('solver_cap_zero',out.get('response')=={'status':'INCOMPLETE','certificate':None},result=out)
        wire=json.dumps(valid,separators=(',',':')).replace('"kind":"logic"','"kind":"logic","kind":"logic"').encode()
        out=invoke(SOLVER,raw=wire); record('solver_duplicate_valid_envelope',(out.get('response') or {}).get('status')=='INVALID_INPUT',result=out)
        invalid={'instance':{'alphabet':['a'],'positive':[[],['z']],'negative':[[]]},'kind':'logic','limits':{'max_nodes':None}}
        out=invoke(SOLVER,invalid); record('validation_before_contradiction',out.get('response')=={'status':'INVALID_INPUT','certificate':None},result=out)
        for name, token in [('bool','true'),('exponent','1e0'),('huge','1'+'0'*4400)]:
            raw=('{"instance":{"alphabet":[],"positive":[],"negative":[]},"kind":"logic","limits":{"max_nodes":'+token+'}}').encode()
            out=invoke(SOLVER,raw=raw); expected=['INCOMPLETE','OPTIMAL'] if name=='huge' else ['INVALID_INPUT']
            record('solver_limit_'+name,(out.get('response') or {}).get('status') in expected,result=out)
        deep = ('['*10000 + '0' + ']'*10000).encode()
        for path in (SOLVER,CHECKER):
            out=invoke(path,raw=deep); record(path.stem+'_deep_resource', (out.get('response') or {}).get('status')=='INCOMPLETE',result=out)
        for name, raw in [('duplicate',b'{"instance":{},"instance":{},"kind":"logic","limits":{"max_nodes":null}}'),('trailing',b'{} {}')]:
            for path,status in [(SOLVER,'INVALID_INPUT'),(CHECKER,'REJECT')]:
                out=invoke(path,raw=raw); record(path.stem+'_raw_'+name,(out.get('response') or {}).get('status')==status,result=out)
    print('Audit records:',OUT)

if __name__ == '__main__': main()



