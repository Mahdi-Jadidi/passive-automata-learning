"""Independent exact deletion enumeration with resource caps.
Fingerprints filter candidates only; equality is checked on ordered original IDs.
Caps cover enumeration (not JSON parsing, sample encoding, or all proof work).
"""
from array import array
from collections import defaultdict
from time import monotonic
from independent_replay import require


class ReplayIncomplete(Exception):
    """No verified result when an enumeration budget is exhausted."""


class DeletionBudget:
    def __init__(self, *, work=200_000_000, entries=2_000_000, word_length=2_000_000, seconds=30):
        for x in (work,entries,word_length):
            if type(x) is not int or x < 0: raise ValueError('nonnegative integer budget required')
        if seconds is not None and (type(seconds) not in (int,float) or not 0 <= seconds < float('inf')): raise ValueError('invalid seconds')
        self.work, self.entries, self.word_length = work, entries, word_length
        self.deadline = None if seconds is None else monotonic()+seconds
        self.used=0; self.peak_entries=0; self.exact_checks=0
    def debit(self,k=1):
        self.used+=k
        if self.used>self.work or (self.deadline is not None and monotonic()>=self.deadline):
            raise ReplayIncomplete('deletion work/deadline cap')
    def index_size(self,k):
        self.peak_entries=max(self.peak_entries,k)
        if k>self.entries: raise ReplayIncomplete('deletion index entry cap')


def check_exhaustion(X,Y,p,claimed,budget,*,hash_bits=64):
    """Check exactly all (negative ID, deleted canonical group) keys.
    No remainder tuple index. O(Lmax + distinct touched positive groups +
    max touched groups in one trace) auxiliary entries; no hard byte guarantee.
    """
    if type(hash_bits) is not int or not 0<=hash_bits<=64: raise ValueError('hash bits')
    budget.debit(1+len(X)+len(Y))
    longest=max((len(w) for words in (X,Y) for w in words),default=0)
    if longest>budget.word_length: raise ReplayIncomplete('deletion word length cap')
    budget.debit(longest)
    mask=(1<<hash_bits)-1; base=0x9e3779b185ebca87
    powers=array('Q',[1 & mask]);
    for i in range(longest):
        if i%4096==0: budget.debit(0)
        powers.append((powers[-1]*base)&mask)
    def signatures(word):
        budget.debit(1+2*len(word))
        h=0; states={}
        for i,a in enumerate(word):
            if i%4096==0: budget.debit(0)
            g=p[a]; acc,prev,hprev,count=states.get(g,(0,0,0,0))
            factor=powers[i-prev]; acc=(acc*factor+h-hprev*factor)&mask
            h=(h*base+a+1)&mask
            states[g]=(acc,i+1,h,count+1)
        m=len(word)
        for g,(acc,prev,hprev,count) in states.items():
            factor=powers[m-prev]
            states[g]=(m-count,(acc*factor+h-hprev*factor)&mask)
        return (m,h),states
    # Full literal duplicates are disallowed before ordinary deletion enumeration.
    full_words=set()
    for x in X:
        budget.debit(1+len(x)); full_words.add(x)
    for y in Y:
        budget.debit(1+len(y)); require(y not in full_words,'duplicate conflict precludes exhausted pass')
    buckets=defaultdict(list); count=0; seen=set()
    for j,x in enumerate(X):
        budget.debit(1+len(x))
        if x in seen: continue
        seen.add(x)
        sig,groups=signatures(x)
        count+=1+len(groups);budget.index_size(count)
        buckets[sig].append((-1,j))
        for g,key in groups.items(): buckets[key].append((g,j))
    def equal(x,y,g):
        budget.exact_checks+=1;budget.debit(1+len(x)+len(y))
        # Linear temporary space only, not retained across comparisons. Tuples
        # use fast C equality; generation still checks exact original order.
        return tuple(a for a in x if p[a]!=g)==tuple(a for a in y if p[a]!=g)
    found_count=0
    for i,y in enumerate(Y):
        sig,groups=signatures(y);found=set()
        for g,key in groups.items():
            for h,j in buckets.get(key,()):
                budget.debit()
                if (h==-1 or h==g) and equal(X[j],y,g):
                    require((i,g) in claimed,'missing exhausted deletion fact');found.add(g);break
        for g,j in buckets.get(sig,()):
            budget.debit()
            if g!=-1 and g not in groups and g not in found and equal(X[j],y,g):
                require((i,g) in claimed,'missing exhausted deletion fact');found.add(g)
        found_count+=len(found)
    budget.debit(0)
    require(found_count==len(claimed),'extra exhausted deletion fact')
