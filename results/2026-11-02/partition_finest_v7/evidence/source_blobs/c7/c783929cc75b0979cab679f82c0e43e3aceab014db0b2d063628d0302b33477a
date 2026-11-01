"""C007 finest sample-compatible partition solver (stdlib only).

Exact labels, known alphabet, unknown k, unrestricted regular factors. The
provider finds the unique finest compatible partition when one exists, or
proves that the meet is incompatible and therefore multiple maximal
refinements exist. It never claims to enumerate those maximal refinements.
"""
from __future__ import annotations
import hashlib
import importlib.util
import math
import time
from pathlib import Path

METHOD = "c007-unknown-k-finest-v3"
PARENT_C006 = (Path(__file__).resolve().parents[3] / "2026-11-01"
               / "partition_identifiability_v6" / "implementation" / "solver_v5.py")
PARENT_C006_SHA256 = "e83c8d13e8eac248415160f6d29fb3309f19b5d447c932e00b69e24e7cb60792"


class _Stop(Exception):
    pass


def _check(deadline):
    if deadline is not None and time.perf_counter() >= deadline:
        raise _Stop


def _load_c006():
    raw = PARENT_C006.read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if got != PARENT_C006_SHA256:
        raise RuntimeError("frozen C006 provider hash mismatch: " + got)
    spec = importlib.util.spec_from_file_location("c007_frozen_c006_solver_v5", PARENT_C006)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen C006 provider")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _validate(data):
    if not isinstance(data, dict):
        raise ValueError("input must be an object")
    if {"k", "q", "local_word_cap"} & set(data):
        raise ValueError("unknown-k C007 input must not contain k, q, or local_word_cap")
    alphabet = data.get("alphabet")
    if (not isinstance(alphabet, list) or not alphabet
            or any(not isinstance(x, str) or len(x) != 1 for x in alphabet)
            or len(set(alphabet)) != len(alphabet)):
        raise ValueError("alphabet must be a nonempty list of distinct one-character strings")
    alphabet = sorted(alphabet)
    sigma = set(alphabet)
    words = []
    for key in ("positive", "negative"):
        value = data.get(key)
        if not isinstance(value, list) or any(not isinstance(w, str) for w in value):
            raise ValueError(key + " must be a list of strings")
        if any(set(w) - sigma for w in value):
            raise ValueError(key + " contains a symbol outside alphabet")
        words.append(sorted(set(value)))
    positive, negative = words
    if set(positive) & set(negative):
        raise ValueError("contradictory labels")
    return alphabet, positive, negative


def _project(word, block, deadline=None):
    out = []
    for i, ch in enumerate(word):
        if i % 256 == 0:
            _check(deadline)
        if ch in block:
            out.append(ch)
    return "".join(out)


def _direct(partition, positive, negative, deadline=None):
    blocks = [set(b) for b in partition]
    languages = [{_project(p, b, deadline) for p in positive} for b in blocks]
    for n in negative:
        _check(deadline)
        projections = [_project(n, b, deadline) for b in blocks]
        unseen = [i for i, proj in enumerate(projections) if proj not in languages[i]]
        if not unseen:
            matches = [next(p for p in positive if _project(p, blocks[i], deadline) == projections[i])
                       for i in range(len(blocks))]
            return None, {"negative":n, "projections":projections,
                          "matching_positive_by_block":matches}
    return {"partition":[sorted(b) for b in blocks],
            "positive_projection_languages":[sorted(x) for x in languages],
            "positive_witnesses":[{"word":p,"projections":[_project(p,b,deadline) for b in blocks]}
                                  for p in positive],
            "negative_witnesses":[{"word":n,
                "projections":[_project(n,b,deadline) for b in blocks],
                "rejected_by_blocks":[i for i,b in enumerate(blocks)
                    if _project(n,b,deadline) not in languages[i]]} for n in negative]}, None


def _canonical_masks(n):
    # First atom is fixed in the left block; omit the all-left mask.
    for tail in range((1 << (n-1))-1):
        yield (tail << 1) | 1


def _cut_blocks(atoms, mask):
    sides = [set(), set()]
    for i, atom in enumerate(atoms):
        sides[0 if mask >> i & 1 else 1].update(atom)
    return [sorted(sides[0]), sorted(sides[1])]


def _meet(partition, cut):
    left, right = map(set, cut)
    out = []
    for block in partition:
        b = set(block)
        x, y = sorted(b & left), sorted(b & right)
        if x: out.append(x)
        if y: out.append(y)
    return sorted(out, key=lambda b:b[0])


def _refines_cut(partition, cut):
    owners = {a:i for i,b in enumerate(partition) for a in b}
    return not any(owners[a] == owners[b] for a in cut[0] for b in cut[1])


def _must_link_partition(alphabet, edges):
    parent = {a:a for a in alphabet}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for edge in edges:
        a,b = edge["symbols"]
        ra,rb=find(a),find(b)
        if ra != rb: parent[rb]=ra
    groups={}
    for a in alphabet: groups.setdefault(find(a),[]).append(a)
    return sorted((sorted(g) for g in groups.values()), key=lambda g:g[0])


def _valid_partition(partition, alphabet, block_count=None):
    if not isinstance(partition,list) or not partition or (block_count is not None and len(partition)!=block_count): return False
    if any(not isinstance(b,list) or not b for b in partition): return False
    if any(any(not isinstance(a,str) for a in b) for b in partition): return False
    flat=[a for b in partition for a in b]
    return len(flat)==len(set(flat)) and set(flat)==set(alphabet)


def _replay_edge(edge, positive, negative, alphabet):
    if not isinstance(edge,dict): return False
    pair,w=edge.get("symbols"),edge.get("witness")
    if (not isinstance(pair,list) or len(pair)!=2 or pair[0]==pair[1]
        or any(not isinstance(a,str) or a not in alphabet for a in pair)
        or not isinstance(w,dict) or not isinstance(w.get("negative"),str)):
        return False
    a,b=pair; n=w["negative"]
    if n not in negative or w.get("rule") not in ("adjacent_swap","insertion_rescue"):
        return False
    if w["rule"]=="adjacent_swap":
        p,i=w.get("positive"),w.get("position")
        return (p in positive and isinstance(i,int) and not isinstance(i,bool) and 0<=i<len(p)-1
                and p[i:i+2] in (a+b,b+a) and p[:i]+p[i+1]+p[i]+p[i+2:]==n)
    ps=w.get("positive"); i=w.get("position")
    if not isinstance(ps,list) or len(ps)!=2 or any(p not in positive for p in ps): return False
    if isinstance(i,bool) or not isinstance(i,int) or not 0<=i<len(n): return False
    base,rescue=ps; deleted=n[i]
    if deleted not in pair or n[:i]+n[i+1:]!=base: return False
    inserted=pair[1] if deleted==pair[0] else pair[0]
    return rescue in (n[:i]+inserted+n[i:], n[:i+1]+inserted+n[i+1:])


def verify_result(data, result):
    """Replay finality/ambiguity proof; never calls the search procedure."""
    try: alphabet,positive,negative=_validate(data)
    except (ValueError,TypeError): return {"valid":False,"reason":"invalid_input"}
    if not isinstance(result,dict) or result.get("complete") is not True:
        return {"valid":False,"reason":"result_not_complete"}
    if result.get("status")=="finest_unique":
        witness=result.get("finest_witness")
        if not isinstance(witness,dict): return {"valid":False,"reason":"missing_finest_witness"}
        direct,collision=_direct(witness.get("partition",[]),positive,negative)
        if direct is None: return {"valid":False,"reason":"finest_partition_incompatible","collision":collision}
        if direct!=witness: return {"valid":False,"reason":"finest_witness_mismatch"}
        cert=result.get("finality_certificate")
        if not isinstance(cert,dict): return {"valid":False,"reason":"missing_finality_certificate"}
        if cert.get("kind")=="must_link_components_compatible":
            edges=cert.get("must_link_edges")
            if not isinstance(edges,list) or any(not _replay_edge(e,positive,negative,set(alphabet)) for e in edges):
                return {"valid":False,"reason":"invalid_must_link_edge"}
            atoms=_must_link_partition(alphabet,edges)
            if cert.get("components")!=atoms or witness.get("partition")!=atoms:
                return {"valid":False,"reason":"must_link_components_mismatch"}
            return {"valid":True,"kind":"must_link_components_compatible"}
        nosep=_verify_no_separator(data,cert)
        if nosep.get("valid") and witness.get("partition")!=cert.get("meet_partition"):
            return {"valid":False,"reason":"finest_partition_does_not_match_meet"}
        return nosep
    if result.get("status")=="multiple_maximal_exist":
        cert=result.get("finality_certificate")
        if isinstance(cert,dict) and cert.get("kind")=="early_infeasible_meet":
            nosep=_verify_early_ambiguity(data,cert,result.get("partial_meet"),result.get("meet_collision"))
        else:
            nosep=_verify_no_separator(data,cert)
        if not nosep.get("valid"): return nosep
        meet=result.get("partial_meet") if cert.get("kind")=="early_infeasible_meet" else result.get("meet_partition")
        if not _valid_partition(meet,alphabet): return {"valid":False,"reason":"invalid_meet_partition"}
        direct,collision=_direct(meet,positive,negative)
        if direct is not None: return {"valid":False,"reason":"meet_is_compatible"}
        if collision!=result.get("meet_collision"):
            return {"valid":False,"reason":"meet_collision_mismatch"}
        return {"valid":True,"kind":"multiple_maximal_exist","meet_collision":collision}
    if result.get("status")=="one_block_only":
        cert=result.get("finality_certificate")
        if isinstance(cert,dict) and cert.get("kind")=="must_link_components_compatible":
            edges=cert.get("must_link_edges")
            if not isinstance(edges,list) or any(not _replay_edge(e,positive,negative,set(alphabet)) for e in edges):
                return {"valid":False,"reason":"invalid_must_link_edge"}
            atoms=_must_link_partition(alphabet,edges)
            if cert.get("components")!=[alphabet] or atoms!=[alphabet]:
                return {"valid":False,"reason":"one_block_not_forced_by_components"}
            nosep={"valid":True}
        else:
            nosep=_verify_no_separator(data,cert)
            if not nosep.get("valid"): return nosep
        if result.get("meet_partition")!=[alphabet] or cert.get("meet_partition")!=[alphabet]:
            if cert.get("kind")!="must_link_components_compatible" or result.get("meet_partition")!=[alphabet]:
                return {"valid":False,"reason":"wrong_one_block_meet"}
        direct,collision=_direct([alphabet],positive,negative)
        if direct is None:
            return {"valid":False,"reason":"one_block_incompatible"}
        if result.get("finest_witness") is not None and result["finest_witness"]!=direct:
            return {"valid":False,"reason":"one_block_witness_mismatch"}
        return {"valid":True,"kind":"one_block_only"}
    return {"valid":False,"reason":"unsupported_status"}


def _verify_no_separator(data, cert):
    try: alphabet,positive,negative=_validate(data)
    except (ValueError,TypeError): return {"valid":False,"reason":"invalid_input"}
    if not isinstance(cert,dict) or cert.get("kind")!="complete_separator_cover":
        return {"valid":False,"reason":"missing_complete_separator_cover"}
    edges=cert.get("must_link_edges")
    if not isinstance(edges,list) or any(not _replay_edge(e,positive,negative,set(alphabet)) for e in edges):
        return {"valid":False,"reason":"invalid_must_link_edge"}
    atoms=_must_link_partition(alphabet,edges)
    meet=cert.get("meet_partition")
    if not _valid_partition(meet,alphabet): return {"valid":False,"reason":"invalid_meet_partition"}
    if cert.get("components")!=atoms: return {"valid":False,"reason":"component_mismatch"}
    records=cert.get("cut_records")
    if not isinstance(records,list): return {"valid":False,"reason":"missing_cut_records"}
    count=(1 << (len(atoms)-1))-1
    bymask={}
    for r in records:
        m=r.get("mask") if isinstance(r,dict) else None
        if isinstance(m,bool) or not isinstance(m,int) or m in bymask: return {"valid":False,"reason":"bad_or_duplicate_mask"}
        bymask[m]=r
    if len(bymask)!=count: return {"valid":False,"reason":"incomplete_cut_cover","expected":count,"actual":len(bymask)}
    feasible_cuts=[]
    for tail in range(count):
        mask=(tail<<1)|1
        if mask not in bymask: return {"valid":False,"reason":"incomplete_cut_cover"}
        r=bymask[mask]; cut=_cut_blocks(atoms,mask)
        if r.get("kind")=="incompatible":
            c=r.get("collision")
            if not isinstance(c,dict) or c.get("negative") not in negative:
                return {"valid":False,"reason":"invalid_cut_collision","mask":mask}
            n=c["negative"]; ps=c.get("matching_positive_by_block")
            if not isinstance(ps,list) or len(ps)!=2:
                return {"valid":False,"reason":"missing_side_positive","mask":mask}
            for i,p in enumerate(ps):
                if p not in positive or _project(p,set(cut[i]))!=_project(n,set(cut[i])):
                    return {"valid":False,"reason":"bad_cut_collision","mask":mask}
        elif r.get("kind")=="compatible_nonseparator":
            sol=r.get("witness")
            if not isinstance(sol,dict): return {"valid":False,"reason":"missing_nonsplit_witness","mask":mask}
            direct,collision=_direct(cut,positive,negative)
            if direct is None or direct!=sol: return {"valid":False,"reason":"bad_nonsplit_witness","mask":mask}
            if not _refines_cut(meet,cut): return {"valid":False,"reason":"cut_splits_claimed_meet","mask":mask}
            feasible_cuts.append((cut,sol))
        else: return {"valid":False,"reason":"unknown_cut_record_kind","mask":mask}
    # Reconstruct the meet of successful compatible separators. Each history
    # entry must be a compatible cut that strictly splits the previous meet.
    computed=[list(alphabet)]
    history=cert.get("successful_separators",[])
    if not isinstance(history,list): return {"valid":False,"reason":"bad_separator_history"}
    for step in history:
        if not isinstance(step,dict): return {"valid":False,"reason":"bad_separator_history"}
        cut=step.get("cut"); witness=step.get("witness")
        if not _valid_partition(cut,alphabet,2): return {"valid":False,"reason":"bad_separator_history"}
        direct,collision=_direct(cut,positive,negative)
        if direct is None or direct!=witness: return {"valid":False,"reason":"incompatible_separator_history"}
        if _refines_cut(computed,cut): return {"valid":False,"reason":"separator_did_not_split_meet"}
        computed=_meet(computed,cut)
    for cut,witness in feasible_cuts:
        computed=_meet(computed,cut)
    if sorted(map(tuple,computed))!=sorted(tuple(b) for b in meet):
        return {"valid":False,"reason":"meet_mismatch","computed":computed}
    return {"valid":True,"kind":"complete_separator_cover","checked_cuts":count}


def solve(data, *, deadline=None, mode="adaptive", max_solutions=None):
    """Return finest_unique, multiple_maximal_exist, one_block_only, or incomplete.

    mode='adaptive' refines a current meet with compatible separating cuts.
    mode='reference' enumerates all compatible bipartitions and computes their
    meet. max_solutions applies only to reference mode; any truncation is
    incomplete and cannot prove finality.
    """
    start=time.perf_counter()
    if mode not in ("adaptive","reference"): raise ValueError("mode must be adaptive or reference")
    if max_solutions is not None and (isinstance(max_solutions,bool) or not isinstance(max_solutions,int) or max_solutions<1):
        raise ValueError("max_solutions must be a positive integer or None")
    if deadline is not None and (isinstance(deadline,bool) or not isinstance(deadline,(int,float)) or not math.isfinite(deadline)):
        raise ValueError("deadline must be finite absolute perf_counter value or None")
    metrics={"binary_cuts_checked":0,"separator_rounds":0,"successful_refinements":0,
             "must_link_edges":0,"must_link_components":None,"oracle_calls":0}
    try: alphabet,positive,negative=_validate(data)
    except (ValueError,TypeError) as exc:
        return {"method":METHOD,"status":"invalid_input","complete":True,"error":str(exc),
                "solutions":[],"metrics":metrics}
    try:
        _check(deadline); c006=_load_c006()
        components,raw_edges=c006._load_parent_helper()._components(alphabet,positive,negative,deadline)
    except KeyboardInterrupt:
        return _incomplete(metrics,start,[],None,"interrupted")
    except Exception as exc:
        if exc.__class__.__name__ in ("_Stop","_Deadline"):
            return _incomplete(metrics,start,[],None,"deadline_or_interruption")
        return {"method":METHOD,"status":"runtime_error","complete":False,"error":repr(exc),"solutions":[],"metrics":metrics}
    atoms=sorted((sorted(x) for x in components),key=lambda x:x[0])
    edges=[{"symbols":sorted(e["symbols"]),"witness":e["witness"]} for e in raw_edges]
    metrics.update(must_link_edges=len(edges),must_link_components=len(atoms))
    current=[list(b) for b in atoms]
    if mode=="reference":
        return _solve_reference(alphabet,positive,negative,atoms,edges,metrics,start,deadline,max_solutions)
    try:
        direct,collision=_direct(current,positive,negative,deadline)
    except (KeyboardInterrupt,_Stop):
        return _incomplete(metrics,start,[],None,"deadline_or_interruption")
    metrics["oracle_calls"]+=1
    if direct is not None:
        cert={"kind":"must_link_components_compatible","components":atoms,"must_link_edges":edges}
        if len(current)==1:
            return _result("one_block_only",True,metrics,start,meet_partition=current,
                           finest_witness=direct,finality_certificate=cert,
                           existence_status="not_decomposable")
        return _result("finest_unique",True,metrics,start,finest_witness=direct,
                       finality_certificate=cert,existence_status="nontrivial_exists")
    # The atom partition is only a forced-coownership bound, not a meet of
    # found feasible cuts. Adaptive state starts at the empty meet: one block.
    return _solve_adaptive(alphabet,positive,negative,atoms,edges,[list(alphabet)],metrics,start,deadline)


def _verify_early_ambiguity(data,cert,claimed_meet,claimed_collision):
    try: alphabet,positive,negative=_validate(data)
    except (ValueError,TypeError): return {"valid":False,"reason":"invalid_input"}
    if not isinstance(cert,dict) or cert.get("kind")!="early_infeasible_meet":
        return {"valid":False,"reason":"wrong_early_ambiguity_kind"}
    edges=cert.get("must_link_edges")
    if not isinstance(edges,list) or any(not _replay_edge(e,positive,negative,set(alphabet)) for e in edges):
        return {"valid":False,"reason":"invalid_must_link_edge"}
    atoms=_must_link_partition(alphabet,edges)
    if cert.get("components")!=atoms: return {"valid":False,"reason":"component_mismatch"}
    history=cert.get("successful_separators")
    if not isinstance(history,list) or len(history)<2:
        return {"valid":False,"reason":"early_ambiguity_needs_two_feasible_cuts"}
    computed=[list(alphabet)]
    for step in history:
        if not isinstance(step,dict) or not _valid_partition(step.get("cut"),alphabet,2):
            return {"valid":False,"reason":"malformed_separator_history"}
        cut=step["cut"]; witness,collision=_direct(cut,positive,negative)
        if witness is None or witness!=step.get("witness"):
            return {"valid":False,"reason":"history_cut_not_compatible"}
        if _refines_cut(computed,cut):
            return {"valid":False,"reason":"history_cut_did_not_refine"}
        # No valid cut may split a replayed must-link component.
        atom_owner={a:i for i,b in enumerate(atoms) for a in b}
        if any((a in cut[0]) != (b in cut[0]) for b0 in atoms for a in b0 for b in b0):
            return {"valid":False,"reason":"history_cut_splits_must_link_component"}
        computed=_meet(computed,cut)
    if computed!=claimed_meet: return {"valid":False,"reason":"partial_meet_mismatch"}
    direct,collision=_direct(computed,positive,negative)
    if direct is not None: return {"valid":False,"reason":"partial_meet_is_compatible"}
    if collision!=claimed_collision: return {"valid":False,"reason":"partial_meet_collision_mismatch"}
    return {"valid":True,"kind":"early_infeasible_meet","meet_is_final":False}


def _solve_reference(alphabet,positive,negative,atoms,edges,metrics,start,deadline,max_solutions):
    feasible=[]; records=[]; total=(1 << (len(atoms)-1))-1
    try:
        for mask in _canonical_masks(len(atoms)):
            _check(deadline); metrics["binary_cuts_checked"]+=1
            cut=_cut_blocks(atoms,mask); witness,collision=_direct(cut,positive,negative,deadline); metrics["oracle_calls"]+=1
            if witness is not None:
                feasible.append(cut); records.append({"mask":mask,"kind":"compatible_nonseparator","witness":witness})
                if max_solutions is not None and len(feasible)>=max_solutions and metrics["binary_cuts_checked"]<total:
                    return _incomplete(metrics,start,[],{"partial_compatible_bipartitions":feasible},"reference_truncated")
            else: records.append({"mask":mask,"kind":"incompatible","collision":collision})
        meet=[list(alphabet)]
        for cut in feasible: meet=_meet(meet,cut)
        cert={"kind":"complete_separator_cover","components":atoms,"must_link_edges":edges,
              "meet_partition":meet,"cut_records":records,"successful_separators":[]}
        return _finish_from_meet(alphabet,positive,negative,meet,cert,metrics,start,
                                 reference_bipartitions=feasible,deadline=deadline)
    except (KeyboardInterrupt,_Stop): return _incomplete(metrics,start,[],None,"deadline_or_interruption")


def _solve_adaptive(alphabet,positive,negative,atoms,edges,current,metrics,start,deadline):
    history=[]
    while True:
        metrics["separator_rounds"]+=1; records=[]; found=None
        try:
            for mask in _canonical_masks(len(atoms)):
                _check(deadline); metrics["binary_cuts_checked"]+=1
                cut=_cut_blocks(atoms,mask); witness,collision=_direct(cut,positive,negative,deadline); metrics["oracle_calls"]+=1
                if witness is None: records.append({"mask":mask,"kind":"incompatible","collision":collision})
                elif _refines_cut(current,cut): records.append({"mask":mask,"kind":"compatible_nonseparator","witness":witness})
                else:
                    found=(cut,witness,mask); break
            if found is not None:
                cut,witness,mask=found
                history.append({"cut":cut,"witness":witness,"mask":mask})
                current=_meet(current,cut)
                metrics["successful_refinements"]+=1
                direct,collision=_direct(current,positive,negative,deadline); metrics["oracle_calls"]+=1
                if direct is None:
                    cert={"kind":"early_infeasible_meet","components":atoms,"must_link_edges":edges,
                          "successful_separators":history}
                    return _result("multiple_maximal_exist",True,metrics,start,
                                   partial_meet=current,meet_collision=collision,
                                   finality_certificate=cert,meet_is_final=False,
                                   existence_status="nontrivial_exists")
                continue
            cert={"kind":"complete_separator_cover","components":atoms,"must_link_edges":edges,
                  "meet_partition":current,"cut_records":records,"successful_separators":history}
            if not history:
                current=[list(alphabet)]
                cert["meet_partition"]=current
            return _finish_from_meet(alphabet,positive,negative,current,cert,metrics,start,deadline=deadline)
        except (KeyboardInterrupt,_Stop): return _incomplete(metrics,start,current,history,"deadline_or_interruption")


def _finish_from_meet(alphabet,positive,negative,meet,cert,metrics,start,
                      reference_bipartitions=None,deadline=None):
    witness,collision=_direct(meet,positive,negative,deadline); metrics["oracle_calls"]+=1
    if len(meet)==1:
        status="one_block_only"; extra={"meet_partition":meet,"finest_witness":witness,
                                        "existence_status":"not_decomposable"}
    elif witness is not None:
        status="finest_unique"; extra={"finest_witness":witness,"existence_status":("one_block_only" if len(meet)==1 else "nontrivial_exists")}
    else:
        status="multiple_maximal_exist"; extra={"meet_partition":meet,"meet_collision":collision,
                                                  "existence_status":"nontrivial_exists"}
    if reference_bipartitions is not None: extra["reference_bipartitions"]=reference_bipartitions
    return _result(status,True,metrics,start,finality_certificate=cert,**extra)


def _result(status,complete,metrics,start,**extra):
    return {"method":METHOD,"model_class":"general_regular_product",
            "status":status,"complete":complete,"decision_complete":complete,
            "maximal_refinements_enumerated":False,"solutions":[],
            "uniqueness_scope":"finest_sample_compatible_partition_not_hidden_architecture",
            "assumptions":["exact complete-word labels","known alphabet","unknown k",
                           "unrestricted regular factors"],
            "metrics":dict(metrics,provider_seconds=time.perf_counter()-start),**extra}


def _incomplete(metrics,start,meet,history,reason):
    return {"method":METHOD,"status":"incomplete","complete":False,"decision_complete":False,
            "reason":reason,"partial_meet":meet,"successful_separators":history,"solutions":[],
            "maximal_refinements_enumerated":False,
            "metrics":dict(metrics,provider_seconds=time.perf_counter()-start)}

