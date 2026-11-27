"""Independent extended literal oracle, only for n<=12; no producer imports.
Precompute exact separating-negative masks per nonempty alphabet subset, then
visit every RGS partition (no branch-and-bound, no omitted partitions).
The existing n<=8 oracle remains unchanged; parity is tested separately.
"""
import argparse
import json
import math
import time
from pathlib import Path


class Limit(Exception):
    pass


def need(ok, msg):
    if not ok:
        raise ValueError(msg)


def exhaustive(raw, *, max_partitions=4213597, max_work=100_000_000, seconds=30):
    visited=work=0
    try:
        need(type(max_partitions) is int and max_partitions>=0 and type(max_work) is int
             and max_work>=0 and type(seconds) in (int,float) and math.isfinite(seconds)
             and 0<=seconds<=60, 'budget')
        deadline=time.monotonic()+seconds
        def debit(k=1):
            nonlocal work
            work+=k
            if work>max_work or time.monotonic()>=deadline:
                raise Limit('work/time cap')
        need(type(raw) is dict and set(raw)=={'alphabet','positive','negative'}, 'raw fields')
        alphabet=raw['alphabet']
        need(type(alphabet) is list and all(type(a) is str and a for a in alphabet)
             and len(set(alphabet))==len(alphabet), 'alphabet')
        n=len(alphabet)
        if n>12: raise Limit('alphabet cap 12')
        ids={a:i for i,a in enumerate(alphabet)}
        def words(key):
            need(type(raw[key]) is list, 'trace array')
            out=[]
            for w in raw[key]:
                need(type(w) is list, 'trace')
                v=[]
                for a in w:
                    debit()
                    need(type(a) is str and a in ids, 'token')
                    v.append(ids[a])
                out.append(tuple(v))
            return out
        X,Y=words('positive'),words('negative')
        target=(1<<len(Y))-1
        good=[0]*(1<<n)
        def project(w,mask):
            out=[]
            for a in w:
                debit()
                if mask&(1<<a): out.append(a)
            return tuple(out)
        for mask in range(1,1<<n):
            debit()
            positives={project(w,mask) for w in X}
            for j,y in enumerate(Y):
                debit()
                if project(y,mask) not in positives: good[mask]|=1<<j
        blocks=[];best=None;winners=[]
        def visit(i):
            nonlocal visited,work,best,winners
            if i==n:
                if visited>=max_partitions: raise Limit('partition cap')
                visited+=1
                work+=1+len(blocks)
                if work>max_work or (visited&1023)==0 and time.monotonic()>=deadline:
                    raise Limit('work/time cap')
                cover=0
                for b in blocks: cover|=good[b]
                if cover!=target:return
                cost=n-len(blocks)
                if best is not None and cost>best:return
                p=[-1]*n
                for b in blocks:
                    representative=(b&-b).bit_length()-1
                    for a in range(n):
                        if b&(1<<a):p[a]=representative
                if best is None or cost<best:best=cost;winners=[]
                winners.append(p)
                return
            bit=1<<i
            for j in range(len(blocks)):
                blocks[j]|=bit
                visit(i+1)
                blocks[j]^=bit
            blocks.append(bit)
            visit(i+1)
            blocks.pop()
        debit(0);visit(0);debit(0)
        return dict(status='VERIFIED',operational_status='INCOMPLETE',visited=visited,work_units=work,
                    result=dict(optimum=best,optima=sorted(winners)))
    except (Limit,MemoryError,RecursionError,TimeoutError) as e:
        return dict(status='INCOMPLETE',operational_status='INCOMPLETE',reason=str(e),visited=visited,work_units=work)
    except (ValueError,TypeError,KeyError) as e:
        return dict(status='INVALID',operational_status='INCOMPLETE',reason=str(e),visited=visited,work_units=work)


def self_test():
    from rgs_oracle import oracle
    cases=0
    for n in range(9):
        a=[str(i) for i in range(n)]
        W=[[]]+[[x] for x in a]+([a[:2],a[:2][::-1]] if n>=2 else [])
        # Exhaustive single-positive/single-negative label choices through n=5,
        # representative multi-label and empty-label cases through n=8.
        pairs=[([x],[y]) for x in W for y in W] if n<=5 else [([W[0]],[W[-1]])]
        pairs += [([],[]),([],W),(W,[]),(W[::2],W[1::2]),(W,W)]
        for X,Y in pairs:
            raw=dict(alphabet=a,positive=X,negative=Y)
            expected=oracle(raw)
            actual=exhaustive(raw)
            need(expected['status']==actual['status']=='VERIFIED','oracle status parity')
            truth=expected['result']
            need(actual['visited']==truth['visited'],'partition count parity')
            need(actual['result']==dict(optimum=truth['optimum'],
                optima=sorted([p.index(g) for g in p] for p in truth['optima'])),'oracle result parity')
            cases+=1
    raw=dict(alphabet=['a','b'],positive=[],negative=[])
    for kw in (dict(max_partitions=1),dict(max_work=0),dict(seconds=0)):
        result=exhaustive(raw,**kw)
        need(result['status']=='INCOMPLETE' and 'result' not in result,'cap result')
    print('literal RGS parity cases:',cases)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--raw');p.add_argument('--self-test',action='store_true')
    p.add_argument('--seconds',type=float,default=30)
    p.add_argument('--max-partitions',type=int,default=4213597)
    p.add_argument('--max-work',type=int,default=100_000_000)
    a=p.parse_args()
    if a.self_test:self_test();return 0
    def pairs(items):
        d={}
        for k,v in items:need(k not in d,'duplicate key');d[k]=v
        return d
    try:
        with open(a.raw,'rb') as f:buf=f.read(64*1024*1024+1)
        if len(buf)>64*1024*1024:raise Limit('raw byte cap')
        raw=json.loads(buf,object_pairs_hook=pairs,parse_constant=lambda s:need(False,'nonfinite'))
        out=exhaustive(raw,max_partitions=a.max_partitions,max_work=a.max_work,seconds=a.seconds)
    except (Limit,MemoryError,RecursionError) as e:
        out=dict(status='INCOMPLETE',operational_status='INCOMPLETE',reason=str(e))
    except (ValueError,TypeError,OSError) as e:
        out=dict(status='INVALID',operational_status='INCOMPLETE',reason=str(e))
    print(json.dumps(out,sort_keys=True,separators=(',',':')))
    return {'VERIFIED':0,'INVALID':1,'INCOMPLETE':2}[out['status']]


if __name__=='__main__':
    raise SystemExit(main())
