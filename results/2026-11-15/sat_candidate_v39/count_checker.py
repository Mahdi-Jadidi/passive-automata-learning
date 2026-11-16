"""Exhaustive independent checker of a completed full partition result.

This checker re-solves by set insertion. It is exponential, not a succinct
proof format, and imports neither the candidate nor the historical solver.
"""
class Invalid(Exception): pass
class Interrupted(Exception): pass

def same(actual, expected):
    if type(actual) is not type(expected): return False
    if isinstance(expected,dict):
        return actual.keys()==expected.keys() and all(same(actual[k],v) for k,v in expected.items())
    if isinstance(expected,list):
        return len(actual)==len(expected) and all(same(a,b) for a,b in zip(actual,expected))
    return actual==expected

def check(data, result, *, max_partitions=None):
    try:
        if max_partitions is not None and (type(max_partitions) is not int or max_partitions < 0):
            raise Invalid()
        if not isinstance(data,dict) or set(data)!={'alphabet','positive','negative'}: raise Invalid()
        a=data['alphabet']
        if not isinstance(a,list) or any(not isinstance(s,str) or not s for s in a) or len(set(a))!=len(a): raise Invalid()
        permitted=set(a); labels=[]
        for key in ('positive','negative'):
            source=data[key]
            if not isinstance(source,list): raise Invalid()
            normalized=[]; seen=set()
            for word in source:
                if not isinstance(word,list) or any(not isinstance(x,str) or x not in permitted for x in word): raise Invalid()
                w=tuple(word)
                if w not in seen: normalized.append(w); seen.add(w)
            labels.append(normalized)
        positives,negatives=labels
        count=0; optimum_count=0; best=None; first=[]; best_first=[]; inspected=0
        def scan(blocks):
            nonlocal count,optimum_count,best,first,best_first,inspected
            if max_partitions is not None and inspected>=max_partitions: raise Interrupted()
            inspected+=1
            factors=[]; groups=[]
            for block in blocks:
                group={a[i] for i in block}; groups.append(group)
                seen=set(); projected=[]
                for word in positives:
                    w=tuple(x for x in word if x in group)
                    if w not in seen: seen.add(w); projected.append(list(w))
                factors.append(projected)
            rejection=[]
            for word in negatives:
                found=next((i for i,group in enumerate(groups) if list(x for x in word if x in group) not in factors[i]),None)
                if found is None: return
                rejection.append(found)
            rgs=tuple(next(j for j,block in enumerate(blocks) if i in block) for i in range(len(a)))
            witness={'rgs':list(rgs),'blocks':[[a[i] for i in b] for b in blocks],'factors':factors,'negative_rejected_by':rejection}
            count+=1; first=sorted(first+[(rgs,witness)],key=lambda item:item[0])[:2]
            k=len(blocks)
            if best is None or k>best: best=k; optimum_count=1; best_first=[(rgs,witness)]
            elif k==best: optimum_count+=1; best_first=sorted(best_first+[(rgs,witness)],key=lambda item:item[0])[:2]
        def visit(i,blocks):
            if i==len(a): scan(blocks); return
            for j in range(len(blocks)):
                next_blocks=[b[:] for b in blocks]; next_blocks[j].append(i); visit(i+1,next_blocks)
            visit(i+1,blocks+[[i]])
        visit(0,[])
        if count==0:
            expected={'status':'INCOMPATIBLE','compatible_count':0,'optimal_count':0,'max_blocks':None,'recommendation':None,'optimal_unique':None,'compatible_witnesses':[],'optimal_witnesses':[]}
        else:
            fw=[x[1] for x in first]; bw=[x[1] for x in best_first]
            expected={'status':'UNIQUE_COMPATIBLE' if count==1 else 'AMBIGUOUS','compatible_count':count,'optimal_count':optimum_count,'max_blocks':best,'recommendation':bw[0],'optimal_unique':optimum_count==1,'compatible_witnesses':fw,'optimal_witnesses':bw}
        return {'status':'ACCEPT' if same(result,expected) else 'REJECT'}
    except (Interrupted,KeyboardInterrupt,MemoryError,RecursionError,OverflowError): return {'status':'INCOMPLETE'}
    except (Invalid,TypeError,ValueError,KeyError): return {'status':'REJECT'}
