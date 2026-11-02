"""Exact finite-sample symbol-ownership inference via canonical block-cover DP.

This returns ownership partitions compatible with the given labeled words,
not a guarantee about the physical generator unless it belongs to the model
class. Standard library only.
"""
from __future__ import annotations
from functools import lru_cache
import math
import time

METHOD = "C009-exact-ownership-dp-v1"


class _Stop(Exception):
    pass


def _check(deadline):
    if deadline is not None and time.perf_counter() >= deadline:
        raise _Stop


def _validate(data, allowed_k_override=None):
    if not isinstance(data, dict): raise ValueError("input must be a JSON object")
    if "k" in data: raise ValueError("use allowed_k:[k], not a separate k field")
    alphabet=data.get("alphabet")
    if (not isinstance(alphabet,list) or not alphabet
            or any(not isinstance(a,str) or len(a)!=1 for a in alphabet)
            or len(alphabet)!=len(set(alphabet))):
        raise ValueError("alphabet must be a nonempty list of distinct one-character strings")
    alphabet=sorted(alphabet); symbols=set(alphabet)
    positives=data.get("positive"); negatives=data.get("negative")
    for label,words in (("positive",positives),("negative",negatives)):
        if not isinstance(words,list) or any(not isinstance(w,str) for w in words):
            raise ValueError(f"{label} must be a list of strings")
        if any(set(w)-symbols for w in words): raise ValueError(f"{label} contains symbols outside alphabet")
    positives=sorted(set(positives)); negatives=sorted(set(negatives))
    if set(positives)&set(negatives): raise ValueError("contradictory_labels")
    raw_k=allowed_k_override if allowed_k_override is not None else data.get("allowed_k")
    if raw_k is None: allowed_k=list(range(1,len(alphabet)+1))
    else:
        if (not isinstance(raw_k,list) or not raw_k
                or any(isinstance(k,bool) or not isinstance(k,int) or not 1<=k<=len(alphabet) for k in raw_k)):
            raise ValueError(f"allowed_k must be a nonempty list of integers in 1..{len(alphabet)}")
        allowed_k=sorted(set(raw_k))
    return alphabet,positives,negatives,allowed_k


def _project(word, block, deadline=None):
    out=[]
    for i,ch in enumerate(word):
        if (i&1023)==0: _check(deadline)
        if ch in block: out.append(ch)
    return "".join(out)


def _mask_symbols(mask, alphabet):
    return [alphabet[i] for i in range(len(alphabet)) if mask>>i&1]


def _render_partition(masks,alphabet):
    return [_mask_symbols(b,alphabet) for b in masks]


def _make_projection_witness(partition,positive,negative,deadline=None):
    blocks=[set(b) for b in partition]
    languages=[{_project(p,b,deadline) for p in positive} for b in blocks]
    neg_records=[]
    for n in negative:
        projections=[_project(n,b,deadline) for b in blocks]
        rejected=[i for i,p in enumerate(projections) if p not in languages[i]]
        if not rejected: raise AssertionError("DP returned an incompatible partition")
        neg_records.append({"word":n,"projections":projections,"rejected_by_blocks":rejected})
    return {"partition":partition,
        "positive_projection_languages":[sorted(x) for x in languages],
        "positive_witnesses":[{"word":p,"projections":[_project(p,b,deadline) for b in blocks]} for p in positive],
        "negative_witnesses":neg_records}


def solve(data, *, allowed_k=None, deadline=None, enumerate_partitions=False):
    """Compute exact partition count and pairwise ownership relations.

    `deadline` is an absolute `time.perf_counter()` deadline. If any required
    phase stops, the result is incomplete and omits exact counts/relations.
    `enumerate_partitions=True` exports every compatible partition; no silent
    truncation is performed.
    """
    started=time.perf_counter(); preprocessing_start=None; search_start=None
    metrics={"block_masks_precomputed":0,"dp_states":0,"dp_branches":0,
             "enumerated_partitions":0,"witness_search_branches":0,
             "preprocessing_seconds":0.0,"search_seconds":0.0,"provider_seconds":0.0}
    try:
        alphabet,positive,negative,ks=_validate(data,allowed_k)
    except (ValueError,TypeError) as exc:
        return {"method":METHOD,"status":"invalid_input","complete":True,"error":str(exc),"metrics":metrics}
    if deadline is not None and (isinstance(deadline,bool) or not isinstance(deadline,(int,float)) or not math.isfinite(deadline)):
        return {"method":METHOD,"status":"invalid_input","complete":True,
            "error":"deadline must be a finite absolute perf_counter value or None","metrics":metrics}
    if not isinstance(enumerate_partitions,bool):
        return {"method":METHOD,"status":"invalid_input","complete":True,
            "error":"enumerate_partitions must be boolean","metrics":metrics}
    m=len(alphabet); full=(1<<m)-1; neg_full=(1<<len(negative))-1
    pair_list=[(i,j) for i in range(m) for j in range(i+1,m)]
    pair_index={pair:k for k,pair in enumerate(pair_list)}
    pair_n=len(pair_list)
    try:
        _check(deadline)
        preprocessing_start=time.perf_counter()
        # Each block contributes exactly the negatives that its projection rejects.
        reject=[0]*(full+1)
        for blockmask in range(1,full+1):
            _check(deadline)
            block={alphabet[i] for i in range(m) if blockmask>>i&1}
            pos_proj={_project(p,block,deadline) for p in positive}
            mask=0
            for ni,n in enumerate(negative):
                if _project(n,block,deadline) not in pos_proj: mask |= 1<<ni
            reject[blockmask]=mask
            metrics["block_masks_precomputed"]+=1
        metrics["preprocessing_seconds"]=time.perf_counter()-preprocessing_start
        search_start=time.perf_counter()

        zero_pairs=(0,)*pair_n
        @lru_cache(maxsize=None)
        def dp(rem,covered,blocks_left):
            _check(deadline)
            metrics["dp_states"]+=1
            if blocks_left<0 or blocks_left>rem.bit_count(): return (0,zero_pairs)
            if rem==0:
                return (1,zero_pairs) if covered==neg_full and blocks_left==0 else (0,zero_pairs)
            if blocks_left==0: return (0,zero_pairs)
            anchor=rem&-rem
            total=0; same=[0]*pair_n
            sub=rem
            while sub:
                if sub&anchor and (sub&rem)==sub:
                    metrics["dp_branches"]+=1
                    child_count,child_same=dp(rem^sub,covered|reject[sub],blocks_left-1)
                    total+=child_count
                    for pi,value in enumerate(child_same): same[pi]+=value
                    if child_count:
                        for ii in range(m):
                            if sub>>ii&1:
                                for jj in range(ii+1,m):
                                    if sub>>jj&1: same[pair_index[(ii,jj)]]+=child_count
                sub=(sub-1)&rem
            return total,tuple(same)

        total_count=0; total_same=[0]*pair_n; count_by_k={}
        for k in ks:
            count,same=dp(full,0,k); count_by_k[str(k)]=count; total_count+=count
            for pi,value in enumerate(same): total_same[pi]+=value
        metrics["search_seconds"]=time.perf_counter()-search_start
        if total_count==0:
            metrics["provider_seconds"]=time.perf_counter()-started
            return {"method":METHOD,"status":"model_inconsistent","complete":True,
                "allowed_k":ks,"partition_count":0,"partition_count_by_k":count_by_k,
                "pair_relations":None,"representative":None,"enumerated_partitions":None,
                "metrics":metrics}

        def any_suffix(rem,covered,left):
            _check(deadline)
            if rem==0: return [] if covered==neg_full and left==0 else None
            anchor=rem&-rem; sub=rem
            while sub:
                if sub&anchor and (sub&rem)==sub:
                    cnt,_=dp(rem^sub,covered|reject[sub],left-1)
                    if cnt:
                        tail=any_suffix(rem^sub,covered|reject[sub],left-1)
                        if tail is not None: return [sub]+tail
                sub=(sub-1)&rem
            return None

        def relation_suffix(k,i,j,want_same):
            def rec(rem,covered,left,decided):
                _check(deadline)
                if rem==0:
                    return [] if covered==neg_full and left==0 and decided else None
                anchor=rem&-rem; sub=rem
                while sub:
                    if sub&anchor and (sub&rem)==sub:
                        in_i=bool(sub>>i&1); in_j=bool(sub>>j&1)
                        now=decided
                        if not decided:
                            if want_same:
                                if in_i!=in_j: sub=(sub-1)&rem; continue
                                if in_i and in_j: now=True
                            else:
                                if in_i and in_j: sub=(sub-1)&rem; continue
                                if in_i!=in_j: now=True
                        newcovered=covered|reject[sub]; newrem=rem^sub; newleft=left-1
                        cnt,_=dp(newrem,newcovered,newleft)
                        if cnt:
                            if now:
                                tail=any_suffix(newrem,newcovered,newleft)
                            else:
                                tail=rec(newrem,newcovered,newleft,False)
                            if tail is not None: return [sub]+tail
                    sub=(sub-1)&rem
                return None
            return rec(full,0,k,False)

        representative_masks=None
        for k in ks:
            if count_by_k[str(k)]:
                representative_masks=any_suffix(full,0,k); break
        representative=_render_partition(representative_masks,alphabet)
        representative_witness=_make_projection_witness(representative,positive,negative,deadline)
        pairs=[]
        for i,j in pair_list:
            pair=(i,j)
            co=total_same[pair_index[pair]]; separate=total_count-co
            if co==total_count: relation="forced_same"
            elif co==0: relation="forced_different"
            else: relation="ambiguous"
            same_w=None; diff_w=None
            if co:
                for k in ks:
                    if count_by_k[str(k)]:
                        masks=relation_suffix(k,i,j,True)
                        if masks is not None: same_w=_render_partition(masks,alphabet); break
            if separate:
                for k in ks:
                    if count_by_k[str(k)]:
                        masks=relation_suffix(k,i,j,False)
                        if masks is not None: diff_w=_render_partition(masks,alphabet); break
            if (co>0)!=(same_w is not None) or (separate>0)!=(diff_w is not None):
                raise AssertionError("pair-count and witness-search disagreement")
            pairs.append({"symbols":[alphabet[i],alphabet[j]],"relation":relation,
                "same_partition_witness":same_w,"different_partition_witness":diff_w,
                "same_partition_count":co,"different_partition_count":separate})

        enumerated=None
        if enumerate_partitions:
            enumerated=[]
            def enum(rem,covered,left,prefix,k):
                _check(deadline)
                if rem==0:
                    if covered==neg_full and left==0:
                        rendered=_render_partition(prefix,alphabet)
                        enumerated.append(_make_projection_witness(rendered,positive,negative,deadline))
                        metrics["enumerated_partitions"]+=1
                    return
                anchor=rem&-rem; sub=rem
                while sub:
                    if sub&anchor and (sub&rem)==sub:
                        cnt,_=dp(rem^sub,covered|reject[sub],left-1)
                        if cnt: enum(rem^sub,covered|reject[sub],left-1,prefix+[sub],k)
                    sub=(sub-1)&rem
            for k in ks:
                if count_by_k[str(k)]: enum(full,0,k,[],k)
            if len(enumerated)!=total_count: raise AssertionError("enumeration count disagrees with DP")

        metrics["provider_seconds"]=time.perf_counter()-started
        return {"method":METHOD,"status":"identified_unique_partition" if total_count==1 else "partial_ownership_identification",
            "complete":True,"alphabet":alphabet,"allowed_k":ks,"partition_count":total_count,
            "partition_count_by_k":count_by_k,"representative":representative_witness,
            "pair_relations":pairs,"enumerated_partitions":enumerated,
            "model_class":"independent_regular_factors_preserving_local_order",
            "interpretation":"relations range over all sample-compatible partitions with allowed_k; they are not unconditional claims about the hidden physical generator",
            "metrics":metrics}
    except (KeyboardInterrupt,_Stop):
        metrics["provider_seconds"]=time.perf_counter()-started
        if preprocessing_start is not None and search_start is None:
            metrics["preprocessing_seconds"]=time.perf_counter()-preprocessing_start
        if search_start is not None:
            metrics["search_seconds"]=time.perf_counter()-search_start
        return {"method":METHOD,"status":"unknown","complete":False,"reason":"deadline_or_interruption",
            "allowed_k":ks,"partition_count":None,"pair_relations":None,"representative":None,
            "enumerated_partitions":None,"metrics":metrics}

