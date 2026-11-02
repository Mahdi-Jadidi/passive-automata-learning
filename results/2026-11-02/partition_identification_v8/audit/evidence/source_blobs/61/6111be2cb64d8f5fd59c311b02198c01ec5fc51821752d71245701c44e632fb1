#!/usr/bin/env python3
"""Exact DFA-product audit for same-k, different ownership maps (stdlib only)."""
from __future__ import annotations
import json
import sys
from collections import deque
from pathlib import Path


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def validate_model(model, alphabet):
    factors=model.get("factors")
    blocks=model.get("ownership_partition")
    if not isinstance(factors,list) or not factors or not isinstance(blocks,list):
        raise ValueError(f"{model.get('id')}: missing factors/partition")
    if model.get("k") != len(factors) or len(blocks) != len(factors):
        raise ValueError(f"{model.get('id')}: k/factor/partition mismatch")
    normalized=sorted(tuple(sorted(b)) for b in blocks)
    factor_blocks=sorted(tuple(sorted(f.get("alphabet",[]))) for f in factors)
    if normalized != factor_blocks:
        raise ValueError(f"{model.get('id')}: factor alphabets differ from ownership blocks")
    flattened=[x for b in normalized for x in b]
    if sorted(flattened) != sorted(alphabet) or len(set(flattened)) != len(alphabet):
        raise ValueError(f"{model.get('id')}: blocks must partition the alphabet exactly")
    for f in factors:
        states=f.get("states"); alpha=f.get("alphabet"); trans=f.get("transitions")
        if not isinstance(states,list) or not states or len(states)!=len(set(states)):
            raise ValueError(f"{f.get('id')}: malformed states")
        if f.get("start") not in states or not set(f.get("accepting",[])) <= set(states):
            raise ValueError(f"{f.get('id')}: bad initial/final states")
        if set(trans or {}) != set(states): raise ValueError(f"{f.get('id')}: transition rows incomplete")
        for q in states:
            if set(trans[q]) != set(alpha) or any(v not in states for v in trans[q].values()):
                raise ValueError(f"{f.get('id')}: transition function not total")
        reached={f["start"]}; queue=deque(reached)
        while queue:
            q=queue.popleft()
            for a in alpha:
                t=trans[q][a]
                if t not in reached: reached.add(t); queue.append(t)
        if reached != set(states): raise ValueError(f"{f.get('id')}: unreachable states")
        for i,q in enumerate(states):
            for r in states[i+1:]:
                suffix=distinguishing_suffix(f,q,r)
                if suffix is None: raise ValueError(f"{f.get('id')}: states {q}/{r} equivalent; DFA not minimal")
    if any(len(block)<2 for block in normalized):
        raise ValueError(f"{model.get('id')}: each device must own at least two symbols")


def distinguishing_suffix(dfa, left, right):
    alpha=dfa["alphabet"]; trans=dfa["transitions"]; finals=set(dfa["accepting"])
    queue=deque([(left,right,"")]); seen={(left,right)}
    while queue:
        p,q,w=queue.popleft()
        if (p in finals)!=(q in finals): return w
        for a in alpha:
            x,y=trans[p][a],trans[q][a]
            if (x,y) not in seen: seen.add((x,y)); queue.append((x,y,w+a))
    return None


def build_global(model, alphabet):
    factors=model["factors"]
    start=tuple(f["start"] for f in factors)
    def step(state, symbol):
        return tuple(f["transitions"][q][symbol] if symbol in f["alphabet"] else q
                     for f,q in zip(factors,state))
    def accepting(state):
        return all(q in set(f["accepting"]) for f,q in zip(factors,state))
    states=[start]; ids={start:"g00"}; queue=deque([start]); transitions={}
    while queue:
        s=queue.popleft(); sid=ids[s]; row={}
        for a in alphabet:
            t=step(s,a)
            if t not in ids:
                ids[t]=f"g{len(ids):02d}"; states.append(t); queue.append(t)
            row[a]=ids[t]
        transitions[sid]=row
    table=[]
    for s in states:
        sid=ids[s]
        table.append({"id":sid,"factor_states":list(s),"accepting":accepting(s),"transitions":transitions[sid]})
    return {"alphabet":alphabet,"start":"g00","states":table,
            "state_count":len(states),"accepting_state_count":sum(r["accepting"] for r in table)}


def machine_index(machine):
    rows=machine["states"]
    return {r["id"]:r for r in rows}


def equivalent(left, right, alphabet):
    li,ri=machine_index(left),machine_index(right)
    start=(left["start"],right["start"])
    queue=deque([start]); parent={start:None}; parent_edge={}
    while queue:
        p,q=queue.popleft()
        if li[p]["accepting"] != ri[q]["accepting"]:
            word=[]; cur=(p,q)
            while parent[cur] is not None:
                word.append(parent_edge[cur]); cur=parent[cur]
            return {"equivalent":False,"shortest_counterexample":"".join(reversed(word)),
                    "reachable_product_pairs":len(parent)}
        for a in alphabet:
            nxt=(li[p]["transitions"][a],ri[q]["transitions"][a])
            if nxt not in parent:
                parent[nxt]=(p,q); parent_edge[nxt]=a; queue.append(nxt)
    return {"equivalent":True,"shortest_counterexample":None,
            "reachable_product_pairs":len(parent)}


def parity_reference(alphabet):
    start="0"*len(alphabet); states=[]; ids={start:"r00"}; queue=deque([start]); rows=[]
    while queue:
        s=queue.popleft(); row={}
        for i,a in enumerate(alphabet):
            t=s[:i]+("1" if s[i]=="0" else "0")+s[i+1:]
            if t not in ids: ids[t]=f"r{len(ids):02d}"; queue.append(t)
            row[a]=ids[t]
        rows.append({"id":ids[s],"parities":s,"accepting":s==start,"transitions":row})
    return {"alphabet":alphabet,"start":"r00","states":rows,
            "state_count":len(rows),"accepting_state_count":1}


def main(models_path, mutants_path):
    data=load_json(models_path); variants=load_json(mutants_path)
    alphabet=data["alphabet"]
    if alphabet != ["a","b","c","d"]: raise ValueError("frozen alphabet must be [a,b,c,d]")
    if len(data["models"]) != 2: raise ValueError("expected exactly two ownership models")
    a,b=data["models"]
    validate_model(a,alphabet); validate_model(b,alphabet)
    if a["k"] != b["k"] or a["ownership_partition"] == b["ownership_partition"]:
        raise ValueError("counterexample requires same k and distinct partitions")
    ga,gb=build_global(a,alphabet),build_global(b,alphabet)
    target=parity_reference(alphabet)
    eq_ab=equivalent(ga,gb,alphabet)
    eq_a=equivalent(ga,target,alphabet); eq_b=equivalent(gb,target,alphabet)
    if not (eq_ab["equivalent"] and eq_a["equivalent"] and eq_b["equivalent"]):
        raise AssertionError({"between_models":eq_ab,"model_a_to_target":eq_a,"model_b_to_target":eq_b})
    symbols={}
    for i,ch in enumerate(alphabet):
        single=ch; double=ch+ch
        # Directly run the global DFA for the stated all-even membership checks.
        for name,m in (("A",ga),("B",gb)):
            idx=machine_index(m); q=m["start"]
            for x in single: q=idx[q]["transitions"][x]
            single_accept=idx[q]["accepting"]
            q=m["start"]
            for x in double: q=idx[q]["transitions"][x]
            double_accept=idx[q]["accepting"]
            if single_accept or not double_accept: raise AssertionError(f"symbol {ch} is not essential in {name}")
        symbols[ch]={"single_rejected":True,"double_occurrence_accepted":True}
    mutant_results=[]
    ref_model=next(m for m in data["models"] if m["id"]==variants["reference_model_id"])
    gref=build_global(ref_model,alphabet)
    for mutant in variants["mutants"]:
        validate_model(mutant,alphabet)
        gm=build_global(mutant,alphabet)
        result=equivalent(gref,gm,alphabet)
        if result["equivalent"]: raise AssertionError(f"mutant unexpectedly equivalent: {mutant['id']}")
        mutant_results.append({"id":mutant["id"],**result,"global_dfa":gm})
    result={"audit":"C008 exact ownership nonidentifiability DFA product BFS",
        "scientific_status":"counterexample_verified_exactly",
        "proof_kind":"reachable_product_equivalence_BFS_no_finite_length_cutoff",
        "assumptions":{"alphabet":alphabet,"same_k":2,"nontrivial_blocks":True,
            "independent_factors":True,"interleaving_preserves_local_order":True,
            "exact_complete_word_language_observed":True},
        "ownership_partitions":[a["ownership_partition"],b["ownership_partition"]],
        "local_factor_minimality":"all states reachable and every state pair has a distinguishing suffix",
        "global_language":"each symbol occurs an even number of times",
        "global_language_infinite":True,"global_language_universal":False,
        "symbol_essentiality":symbols,
        "equivalence":{"A_vs_B":eq_ab,"A_vs_all_even_reference":eq_a,"B_vs_all_even_reference":eq_b},
        "global_dfa_A":ga,"global_dfa_B":gb,"canonical_all_even_dfa":target,
        "mutant_counterexamples":mutant_results,
        "scope_caveat":"Each two-letter even/even local factor itself decomposes into two one-letter even-count languages; this counterexample does not refute a prime-factor assumption."}
    print(json.dumps(result,ensure_ascii=False,sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=3: raise SystemExit("usage: verify_ownership_equivalence_v1.py MODELS.json MUTANTS.json")
    main(sys.argv[1],sys.argv[2])
