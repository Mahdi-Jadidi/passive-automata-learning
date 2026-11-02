"""Complete pre-training lookup on an explicitly compiled finite vocabulary.
No learner is imported or executed here. Offline/setup costs are separate.
"""
from pathlib import Path
import json,hashlib,sys


def validate_domain(vocabulary,blocks):
    words=list(vocabulary);blocks=[set(B) for B in blocks];work=0;owner={}
    if not blocks:raise ValueError('Empty partition')
    for i,B in enumerate(blocks):
        work+=1
        if not B:raise ValueError('Empty block')
        for a in B:
            work+=1
            if not isinstance(a,str) or len(a)!=1:raise ValueError('Non-character symbol')
            if a in owner:raise ValueError('Overlapping blocks')
            owner[a]=i
    if len(set(words))!=len(words):raise ValueError('Duplicate vocabulary word')
    for w in words:
        work+=1
        if not isinstance(w,str):raise ValueError('Non-string word')
        for a in w:
            work+=1
            if a not in owner:raise ValueError('Out-of-alphabet vocabulary')
    return sorted(words,key=lambda w:(len(w),w)),[sorted(B) for B in blocks],owner,work


def entries_digest(entries):
    data=json.dumps(entries,sort_keys=True,separators=(',',':')).encode('utf8')
    return hashlib.sha256(data).hexdigest()


class CompiledSelector:
    def __init__(self,path):
        self.data=json.loads(Path(path).read_text(encoding='utf8'))
        if self.data['schema']!='rpni-compiled-v1':raise ValueError('Wrong schema')
        words,blocks,owner,setup=validate_domain(self.data['vocabulary'],self.data['blocks'])
        if words!=self.data['vocabulary']:raise ValueError('Vocabulary order')
        self.index={};self.powers=[]
        for i,w in enumerate(words):
            setup+=1;self.index[w]=i;self.powers.append(3**i)
        self.entries=self.data['entries']
        if len(self.entries)!=3**len(words):raise ValueError('Incomplete table')
        for e in self.entries:
            setup+=1
            g,s=e['global_work'],e['split_work'];status=e['status']
            if type(g) is not int or g<3:raise ValueError('Invalid Global cost')
            if status=='GLOBAL_ONLY':
                if s is not None:raise ValueError('Infeasible row has Split cost')
            else:
                if type(s) is not int or s<3:raise ValueError('Invalid Split cost')
                expected='GLOBAL' if g<s else 'SPLIT' if s<g else 'TIE'
                if status!=expected:raise ValueError('Cost/sign mismatch')
        if entries_digest(self.entries)!=self.data['entries_sha256']:raise ValueError('Table digest mismatch')
        self.setup_work=setup

    def query(self,positive,negative):
        work=1;key=0
        try:
            if isinstance(positive,str) or isinstance(negative,str):raise ValueError('Expected word collections')
            P,Q=set(positive),set(negative)
            if P&Q:raise ValueError('Contradictory labels')
            for label,words in ((1,P),(2,Q)):
                for w in words:
                    work+=1
                    if not isinstance(w,str):raise ValueError('Non-string word')
                    if w not in self.index:
                        return dict(status='OUT_OF_DOMAIN',word=w,query_work=work,training_started=False)
                    key+=label*self.powers[self.index[w]]
        except (TypeError,ValueError) as exc:
            return dict(status='INVALID',reason=str(exc),query_work=work,training_started=False)
        e=self.entries[key];g,s=e['global_work'],e['split_work']
        chosen=g if s is None else min(g,s)
        return dict(e,method='COMPILED_LOOKUP',training_started=False,query_work=work,
                    chosen_pipeline_work=chosen,
                    per_query_net_excludes_offline_and_setup=(None if s is None else work+chosen<max(g,s)),
                    offline_work=self.data['offline_work'],setup_work=self.setup_work,
                    saving_vs_global_before_overhead=g-chosen,
                    scope='All consistent labeled subsets of the fixed compiled vocabulary; W_ref only')


if __name__=='__main__':
    selector=CompiledSelector(sys.argv[1])
    x=json.loads(Path(sys.argv[2]).read_text(encoding='utf8'))
    if 'blocks' in x and [sorted(set(B)) for B in x['blocks']]!=selector.data['blocks']:
        raise ValueError('Query partition differs from compiled partition')
    print(json.dumps(selector.query(x['positive'],x['negative']),indent=2,ensure_ascii=False))
