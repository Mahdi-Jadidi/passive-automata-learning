"""Independent C003 generated-corpus, selected-regression and witness audit."""
import json, hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus/frozen_c003_v1"
OUT = HERE / "validation/generated_v1"
RUNS = {
    "selected_general": HERE / "attempts/20261026T193117.638592Z_85534ddd1d/stdout.bin",
    "selected_fair": HERE / "attempts/20261026T193123.761411Z_25cf45f3e8/stdout.bin",
    "dfa_general": HERE / "attempts/20261026T193140.989070Z_26908bb50e/stdout.bin",
    "dfa_fair": HERE / "attempts/20261026T193156.823230Z_ac355f2832/stdout.bin",
    "fixed_word": HERE / "attempts/20261026T193208.243374Z_d30ec97983/stdout.bin",
}

def sha(raw): return hashlib.sha256(raw).hexdigest()
def canon(blocks): return tuple(sorted(tuple(sorted(b)) for b in blocks))
def project(word, block):
    members = set(block)
    return "".join(a for a in word if a in members)
def jsonl(path): return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x]
def exact_f2(data):
    alphabet = sorted(data["alphabet"])
    positives, negatives = sorted(set(data["positive"])), sorted(set(data["negative"]))
    out = set()
    for mask in range(1, (1 << (len(alphabet)-1))):
        b1 = {alphabet[i+1] for i in range(len(alphabet)-1) if mask & (1 << i)}
        b0 = set(alphabet) - b1
        blocks = [sorted(b0), sorted(b1)]
        langs = [{project(p,b) for p in positives} for b in blocks]
        if all(any(project(n,b) not in langs[i] for i,b in enumerate(blocks)) for n in negatives):
            out.add(canon(blocks))
    return out

def feasible(data, blocks):
    positives=sorted(set(data["positive"])); negatives=sorted(set(data["negative"]))
    langs=[{project(p,b) for p in positives} for b in blocks]
    return all(any(project(n,b) not in langs[i] for i,b in enumerate(blocks))
               for n in negatives)

def verify_solution(data, solution):
    errors=[]
    blocks=solution.get("blocks",[])
    if len(blocks)!=2 or not all(blocks) or set(blocks[0])&set(blocks[1]) or set(blocks[0])|set(blocks[1])!=set(data["alphabet"]):
        return ["invalid partition"]
    pos=sorted(set(data["positive"])); neg=sorted(set(data["negative"]))
    langs=[sorted({project(p,b) for p in pos}) for b in blocks]
    if solution.get("positive_projection_languages")!=langs: errors.append("positive projection languages mismatch")
    witness={w.get("negative"):w for w in solution.get("negative_witnesses",[])}
    if set(witness)!=set(neg): errors.append("negative witness coverage mismatch")
    for n in neg:
        w=witness.get(n)
        if w is None: continue
        i=w.get("block_index")
        if i not in (0,1) or w.get("projection")!=project(n,blocks[i]) or w.get("projection") in langs[i]:
            errors.append(f"bad negative witness: {n}")
    return errors

def map_results(path):
    rows=jsonl(path)
    result={}
    for row in rows:
        if row["case_id"] in result: raise ValueError(f"duplicate result {row['case_id']} in {path}")
        result[row["case_id"]]=row
    return result

def main():
    errors=[]; summary={}
    selected_inputs={r["case_id"]:r for r in jsonl(CORPUS/"c002_regression_inputs.jsonl")}
    selected_refs={r["case_id"]:r["baseline_f2"] for r in jsonl(CORPUS/"c002_regression_f2.jsonl")}
    for key in ("selected_general","selected_fair"):
        rows=map_results(RUNS[key]); per={"rows":len(rows),"exact_f2":0,"witnesses":0}
        if set(rows)!=set(selected_inputs): errors.append({"run":key,"error":"selected regression coverage mismatch"})
        for cid,row in rows.items():
            inp=selected_inputs[cid]["input"]; res=row.get("result")
            if row.get("runner_error") or not res: errors.append({"run":key,"case_id":cid,"error":row.get("runner_error")}); continue
            expected={canon(x["blocks"]) for x in selected_refs[cid].get("feasible_partitions",[])}
            actual={canon(x["blocks"]) for x in res.get("solutions",[])}
            if not res.get("search_exhausted") or actual!=expected:
                errors.append({"run":key,"case_id":cid,"error":"selected exact F2 mismatch","expected":len(expected),"actual":len(actual),"exhausted":res.get("search_exhausted")})
            else: per["exact_f2"]+=1
            for sol in res.get("solutions",[]):
                se=verify_solution(inp,sol)
                if se: errors.append({"run":key,"case_id":cid,"errors":se})
                else: per["witnesses"]+=len(inp["negative"])
        summary[key]=per

    dfa_inputs={r["case_id"]:r["input"] for r in jsonl(CORPUS/"random_dfa_inputs.jsonl")}
    dfa_truth={r["case_id"]:r for r in jsonl(CORPUS/"random_dfa_truth.jsonl")}
    for key in ("dfa_general","dfa_fair"):
        rows=map_results(RUNS[key]); per={"rows":len(rows),"oracle_cases":0,"oracle_exact":0,"planted_feasible":0,"high_m_found":0,"witnesses":0,"by_m":{}}
        if set(rows)!=set(dfa_inputs): errors.append({"run":key,"error":"DFA coverage mismatch"})
        for cid,row in rows.items():
            data=dfa_inputs[cid]; truth=dfa_truth[cid]; res=row.get("result")
            m=len(data["alphabet"]); per["by_m"][str(m)]=per["by_m"].get(str(m),0)+1
            if row.get("runner_error") or not res: errors.append({"run":key,"case_id":cid,"error":row.get("runner_error")}); continue
            blocks=truth["blocks"]
            def accepts(dfa,word,local):
                ix={a:i for i,a in enumerate(local)}; q=dfa["start"]
                for a in word: q=dfa["transitions"][q][ix[a]]
                return q in dfa["accepting"]
            for label in ("positive","negative"):
                for w in data[label]:
                    actual=(accepts(truth["dfa_left"],project(w,blocks[0]),blocks[0]) and
                            accepts(truth["dfa_right"],project(w,blocks[1]),blocks[1]))
                    if actual != (label=="positive"):
                        errors.append({"run":key,"case_id":cid,"error":"hidden DFA labeling mismatch","label":label,"word":w})
            if feasible(data, blocks): per["planted_feasible"]+=1
            else: errors.append({"run":key,"case_id":cid,"error":"planted partition not in independent F2"})
            for sol in res.get("solutions",[]):
                se=verify_solution(data,sol)
                if se: errors.append({"run":key,"case_id":cid,"errors":se})
                else: per["witnesses"]+=len(data["negative"])
            if m<=10:
                expected=exact_f2(data)
                per["oracle_cases"]+=1
                actual={canon(s["blocks"]) for s in res.get("solutions",[])}
                if res.get("search_exhausted") and actual==expected: per["oracle_exact"]+=1
                else: errors.append({"run":key,"case_id":cid,"error":"small-DFA exact F2 mismatch","expected":len(expected),"actual":len(actual),"exhausted":res.get("search_exhausted")})
            else:
                if res.get("status")=="found" and res.get("solutions"):
                    per["high_m_found"]+=1
                else: errors.append({"run":key,"case_id":cid,"error":"high-alphabet run failed to find a compatible partition"})
        summary[key]=per

    fixed_inputs={r["case_id"]:r["input"] for r in jsonl(CORPUS/"fixed_word_inputs.jsonl")}
    fixed_truth={r["case_id"]:r for r in jsonl(CORPUS/"fixed_word_truth.jsonl")}
    rows=map_results(RUNS["fixed_word"]); per={"rows":len(rows),"unique_recoveries":0,"true_targets_recovered":0,"witnesses":0,"by_m":{}}
    if set(rows)!=set(fixed_inputs): errors.append({"run":"fixed_word","error":"constructive coverage mismatch"})
    for cid,row in rows.items():
        data=fixed_inputs[cid]; truth=fixed_truth[cid]; res=row.get("result"); m=len(data["alphabet"])
        per["by_m"][str(m)]=per["by_m"].get(str(m),0)+1
        if row.get("runner_error") or not res: errors.append({"run":"fixed_word","case_id":cid,"error":row.get("runner_error")}); continue
        if (res.get("status")!="found" or res.get("uniqueness")!="unique" or
                not res.get("search_exhausted") or len(res.get("solutions",[]))!=1 or
                "fixed_word_product_class" not in res.get("uniqueness_scope","")):
            errors.append({"run":"fixed_word","case_id":cid,"error":"no fixed-word class uniqueness certificate","status":res.get("status")})
            continue
        per["unique_recoveries"]+=1
        sol=res["solutions"][0]; se=verify_solution(data,sol)
        if se: errors.append({"run":"fixed_word","case_id":cid,"errors":se})
        else: per["witnesses"]+=len(data["negative"])
        if canon(sol["blocks"])==canon(truth["blocks"]): per["true_targets_recovered"]+=1
        else: errors.append({"run":"fixed_word","case_id":cid,"error":"unique fixed-word answer differs from planted partition"})
        expected_local=sorted(["".join(a for a in data["positive"][0] if a in set(b)) for b in sol["blocks"]])
        if sorted(sol.get("local_words",[]))!=expected_local:
            errors.append({"run":"fixed_word","case_id":cid,"error":"local word certificate mismatch"})
    summary["fixed_word"]=per
    report={"validation_id":"C003-GENERATED-AND-REGRESSION-AUDIT-v1","corpus_manifest_sha256":sha((CORPUS/"freeze_manifest.json").read_bytes()),
            "runs":{k:{"stdout_sha256":sha(p.read_bytes()),"path":str(p)} for k,p in RUNS.items()},
            "summary":summary,"errors":errors,"accepted":not errors}
    OUT.mkdir(parents=True,exist_ok=False)
    raw=(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n").encode()
    (OUT/"report.json").write_bytes(raw)
    print(json.dumps({"accepted":not errors,"error_count":len(errors),"summary":summary,
                      "report":str(OUT/"report.json"),"report_sha256":sha(raw),
                      "first_errors":errors[:5]},ensure_ascii=False,indent=2))

if __name__=="__main__": main()
