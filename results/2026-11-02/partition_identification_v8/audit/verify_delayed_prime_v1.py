#!/usr/bin/env python3
"""Exact reachable-product DFA audit for delayed locally-prime ownership ambiguity."""
from __future__ import annotations
import json
import sys
from collections import deque
from pathlib import Path


def make_factor(x,y,M):
    forbidden=x*(2*M)+y*(2*M); L=len(forbidden)
    start=(0,0,0)  # parity x, parity y, matched forbidden-prefix length
    def step(s,ch):
        px,py,j=s
        px ^= (ch==x); py ^= (ch==y)
        if j<0 or j==L: j=-1
        elif ch==forbidden[j]: j+=1
        else: j=-1
        return (int(px),int(py),j)
    states=[start]; seen={start}; queue=deque([start]); trans={}
    for_state={}
    while queue:
        s=queue.popleft(); row={}
        for ch in (x,y):
            t=step(s,ch); row[ch]=t
            if t not in seen: seen.add(t); states.append(t); queue.append(t)
        trans[s]=row
    finals={s for s in states if s[0]==0 and s[1]==0 and s[2]!=L}
    return {"alphabet":(x,y),"states":states,"start":start,"accepting":finals,
            "transitions":trans,"forbidden_word":forbidden,"M":M}


def local_run(dfa,word):
    s=dfa["start"]
    for ch in word:
        if ch not in dfa["alphabet"]: raise ValueError("word outside local alphabet")
        s=dfa["transitions"][s][ch]
    return s in dfa["accepting"]


def build_global(blocks, M):
    factors=[make_factor(*block,M) for block in blocks]
    start=tuple(f["start"] for f in factors)
    def accept(s): return all(q in f["accepting"] for q,f in zip(s,factors))
    def step(s,ch):
        return tuple(f["transitions"][q][ch] if ch in f["alphabet"] else q
                     for q,f in zip(s,factors))
    states=[start]; seen={start}; queue=deque([start]); trans={}
    while queue:
        s=queue.popleft(); row={}
        for ch in "abcd":
            t=step(s,ch); row[ch]=t
            if t not in seen: seen.add(t); states.append(t); queue.append(t)
        trans[s]=row
    finals={s for s in states if accept(s)}
    return {"blocks":blocks,"factors":factors,"states":states,"start":start,
            "accepting":finals,"transitions":trans}


def shortest_difference(left,right):
    start=(left["start"],right["start"]); queue=deque([start]); parent={start:None}; edge={}
    while queue:
        p,q=queue.popleft()
        in_l=p in left["accepting"]; in_r=q in right["accepting"]
        if in_l != in_r:
            out=[]; cur=(p,q)
            while parent[cur] is not None:
                out.append(edge[cur]); cur=parent[cur]
            return {"equivalent":False,"word":"".join(reversed(out)),
                    "accepted_left":in_l,"accepted_right":in_r,
                    "reachable_product_pairs":len(parent)}
        for ch in "abcd":
            nxt=(left["transitions"][p][ch],right["transitions"][q][ch])
            if nxt not in parent: parent[nxt]=(p,q); edge[nxt]=ch; queue.append(nxt)
    return {"equivalent":True,"word":None,"reachable_product_pairs":len(parent)}


def subset_counterexample(source, target):
    start=(source["start"],target["start"]); queue=deque([start]); seen={start}
    while queue:
        p,q=queue.popleft()
        if p in source["accepting"] and q not in target["accepting"]: return False
        for ch in "abcd":
            nxt=(source["transitions"][p][ch],target["transitions"][q][ch])
            if nxt not in seen: seen.add(nxt); queue.append(nxt)
    return True


def all_even_reference():
    start=(0,0,0,0); states=[start]; seen={start}; queue=deque([start]); trans={}
    while queue:
        s=queue.popleft(); row={}
        for i,ch in enumerate("abcd"):
            t=list(s); t[i]^=1; t=tuple(t); row[ch]=t
            if t not in seen: seen.add(t); states.append(t); queue.append(t)
        trans[s]=row
    return {"states":states,"start":start,"transitions":trans,
            "accepting":{s for s in states if not any(s)}}


def check_factor_symbolic(x,y,M,dfa):
    # Finite sanity points support, but do not replace, the algebraic projection proof.
    checks=[]
    for n in range(0,2*M+4):
        ex=local_run(dfa,x*n); ey=local_run(dfa,y*n)
        if ex != (n%2==0) or ey != (n%2==0):
            raise AssertionError(f"unary projection parity mismatch {x,y,M,n}")
        checks.append({"n":n,"x_power_accepted":ex,"y_power_accepted":ey})
    forbidden= x*(2*M)+y*(2*M)
    if local_run(dfa,forbidden): raise AssertionError("forbidden word accepted")
    return {"unary_projection_formula":"{x^(2n):n>=0} and {y^(2n):n>=0}",
            "finite_sanity_checks":checks,"forbidden_word_rejected":forbidden}


def main(path):
    spec=json.loads(Path(path).read_text(encoding="utf-8-sig"))
    Ms=spec["parameter_values"]
    if Ms != [1,2,3]: raise ValueError("frozen M list must be [1,2,3]")
    Ablocks=spec["ownership_partitions"]["A"]
    Bblocks=spec["ownership_partitions"]["B"]
    if Ablocks==Bblocks or len(Ablocks)!=2 or len(Bblocks)!=2: raise ValueError("need distinct k=2 partitions")
    ref=all_even_reference(); results=[]
    for M in Ms:
        A=build_global(Ablocks,M); B=build_global(Bblocks,M)
        diff=shortest_difference(A,B)
        expected=4*M; word="a"*(2*M)+"b"*(2*M)
        if diff["equivalent"] or len(diff["word"])!=expected:
            raise AssertionError({"M":M,"difference":diff,"expected_length":expected})
        def run(g,w):
            s=g["start"]
            for ch in w: s=g["transitions"][s][ch]
            return s in g["accepting"]
        if run(A,word) or not run(B,word): raise AssertionError(f"expected witness orientation failed at M={M}")
        if not subset_counterexample(A,ref) or not subset_counterexample(B,ref):
            raise AssertionError("a model accepted a word outside all-even language")
        symbol_checks={}
        for ch in "abcd":
            if run(A,ch) or run(B,ch) or not run(A,ch*2) or not run(B,ch*2):
                raise AssertionError(f"symbol relevance check failed: {ch}")
            symbol_checks[ch]={"single_rejected":True,"double_accepted":True}
        if run(A,"a") or run(B,"a"): raise AssertionError("language unexpectedly universal")
        if not all(run(A,"a"*(2*n)) for n in range(0,2*M+3)):
            raise AssertionError("expected infinite unary family sanity failed")
        factors=[]
        for (x,y),f in zip(Ablocks,A["factors"]):
            factors.append({"pair":[x,y],"dfa_states":len(f["states"]),
                            "symbolic_projection_check":check_factor_symbolic(x,y,M,f)})
        for (x,y),f in zip(Bblocks,B["factors"]):
            factors.append({"pair":[x,y],"dfa_states":len(f["states"]),
                            "symbolic_projection_check":check_factor_symbolic(x,y,M,f)})
        results.append({"M":M,"expected_shortest_length":expected,
            "bfs_shortest_difference":diff,"claimed_word":word,
            "global_dfa_reachable_states":{"A":len(A["states"]),"B":len(B["states"]),"all_even_reference":len(ref["states"])},
            "both_languages_subset_of_all_even":True,"nonuniversal_witness":"a",
            "symbol_relevance":symbol_checks,
            "infinite_family":"a^(2n), n>=0 (finite checked range plus symbolic argument)",
            "factors":factors})
    output={"audit":"C008 delayed finite-prefix ambiguity with local symbol-prime factors",
        "scientific_status":"exact_bounded_instances_verified_symbolic_all_M_proof_separate",
        "method":"complete DFA construction plus reachable product BFS for shortest symmetric difference",
        "M_results":results,
        "symbolic_proof_summary":{
            "local_projection":"For all n>=0, x^(2n),y^(2n) are in F_xy(M); parity excludes odd powers.",
            "local_prime":"Any independent singleton-symbol factorization must use those exact unary projections, whose shuffle is E_xy; F_xy(M) omits x^(2M)y^(2M).",
            "prefix_equality":"Any difference requires a factor projection equal to x^(2M)y^(2M), length at least 4M.",
            "difference_witness":"a^(2M)b^(2M) is rejected by A's ab factor and accepted by B's ac and bd factors; hence shortest difference length is 4M.",
            "finite_data_implication":"For any finite maximum trace length L, choose M with 4M>L. These two admissible same-k systems agree on every observed word of length <=L, so no algorithm can guarantee the true ownership on every allowed finite dataset under this unrestricted class.",
            "not_claimed":"This does not say every finite dataset is ambiguous; known state bounds or a different prime-factor model are outside this construction."},
        "scope":"C008 audit folder only; does not feed the solver and does not reveal generator metadata to any solver input"}
    print(json.dumps(output,ensure_ascii=False,sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=2: raise SystemExit("usage: verify_delayed_prime_v1.py delayed_prime_models_v1.json")
    main(sys.argv[1])
