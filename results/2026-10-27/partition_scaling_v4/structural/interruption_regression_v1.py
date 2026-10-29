"""Targeted control-flow audit: one KeyboardInterrupt during preprocessing."""
import json
import singleton_solver_v1 as base
import singleton_solver_v3 as candidate

data={'alphabet':list('abcd'),'positive':['abcd','cdab'],'negative':['bacd','abdc']}
original=base.check
calls=0
def interrupt_once(deadline):
    global calls
    calls+=1
    if calls==1:raise KeyboardInterrupt()
    return original(deadline)
base.check=interrupt_once
try:
    value=candidate.solve(data,infer_k=True)
    record={'result':value,'exception':None,'calls':calls}
except BaseException as error:
    record={'result':None,'exception':{'type':type(error).__name__,'message':str(error)},'calls':calls}
finally:
    base.check=original
print(json.dumps({'input':data,'observed':record,'expected':'incomplete without propagated exception'}),flush=True)
assert record['exception'] is None and record['result']['status']=='incomplete'
