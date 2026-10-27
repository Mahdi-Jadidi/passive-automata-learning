"""Serial hard-capped performance suite from the frozen plan."""
import gzip, hashlib, json, os, sys
from pathlib import Path

from capture import capture

ROOT=Path(__file__).resolve().parents[4]
C003=ROOT/"results/2026-10-26/partition_discovery_v3"
AUDIT=C003/"audit"
C002=ROOT/"results/2026-10-26/partition_constraints_v2"
PLAN=AUDIT/"plans/plan_v2"
INPUTS=C002/"audit/corpus/frozen_v1/solver_inputs/performance_100.jsonl"
BASELINE=C002/"audit/correctness_runs/20261026T125503.860658Z_805e5494/baseline.jsonl.gz"
RUNTIME=json.loads((C003/"coordination/runtime_manifest.json").read_text(encoding="utf-8"))
PY=sys.executable

def sha(b): return hashlib.sha256(b).hexdigest()
def append(path,row):
    with path.open("ab",buffering=0) as f:
        f.write((json.dumps(row,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n").encode("utf-8")); os.fsync(f.fileno())
def main():
    run=AUDIT/"performance_adopted/runs/serial_v1"
    run.mkdir(parents=True,exist_ok=False)
    inp_dir=run/"inputs"; inp_dir.mkdir()
    rows=[json.loads(s) for s in INPUTS.read_text(encoding="utf-8").splitlines() if s]
    data_by_id={r["case_id"]:r["input"] for r in rows}
    for cid,data in data_by_id.items():
        path=inp_dir/(cid+".json")
        path.write_text(json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    truth={}
    with gzip.open(BASELINE,"rt",encoding="utf-8") as handle:
        for s in handle:
            row=json.loads(s)
            if row.get("case_id") in data_by_id: truth[row["case_id"]]=row["result"]
    if set(truth)!=set(data_by_id): raise RuntimeError("saved C002 F2 coverage mismatch")
    (run/"input_manifest.json").write_text(json.dumps({"input_source_sha256":sha(INPUTS.read_bytes()),
        "baseline_f2_sha256":sha(BASELINE.read_bytes()),"cases":len(data_by_id),
        "case_ids":list(data_by_id)},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (run/"baseline_f2.json").write_text(json.dumps(truth,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")

    cases_by_size={}
    for row in rows:
        m=len(row["input"]["alphabet"])
        if m in (4,6,8,10): cases_by_size.setdefault(m,[]).append(row["case_id"])
    if any(len(cases_by_size.get(m,[]))!=25 for m in (4,6,8,10)):
        raise RuntimeError(f"performance strata invalid: { {m:len(v) for m,v in cases_by_size.items()} }")
    perf_cases=[cid for m in (4,6,8,10) for cid in cases_by_size[m]]
    fixed_rows=[json.loads(s) for s in (AUDIT/"corpus/frozen_c003_v1/fixed_word_inputs.jsonl").read_text(encoding="utf-8").splitlines() if s]
    fixed_cases=[]
    for m in (2,8,16,32,64,128):
        group=[r for r in fixed_rows if len(r["input"]["alphabet"])==m]
        fixed_cases.extend(group[i]["case_id"] for i in sorted({0,(len(group)-1)//2,len(group)-1}))
    suite={"general":[],"fair-reference":[],"fixed-word":[]}
    for method in ("general","fair-reference"):
        for cid in perf_cases:
            for limit in (1,2):
                for rep in (1,2,3): suite[method].append((cid,limit,"timing",rep))
                suite[method].append((cid,limit,"memory",1))
    for cid in fixed_cases:
        for limit in (1,2):
            for rep in (1,2,3): suite["fixed-word"].append((cid,limit,"timing",rep))
            suite["fixed-word"].append((cid,limit,"memory",1))
    expected_total=sum(map(len,suite.values()))
    ledger=run/"ledger.jsonl"
    spent={k:0.0 for k in suite}
    attempted=skipped=0
    base_sources=[C003/"solver.py",C003/"coordination/runtime_manifest.json",Path(__file__),
                  AUDIT/"profile_one.py"]+[C003/r["path"] for r in RUNTIME["files"]]
    for method in ("general","fair-reference","fixed-word"):
        for cid,limit,mode,rep in suite[method]:
            job_id=f"{method}:{cid}:limit{limit}:{mode}:{rep}"
            if spent[method]>=900:
                append(ledger,{"job_id":job_id,"method":method,"case_id":cid,"limit":limit,
                               "mode":mode,"replicate":rep,"execution_status":"budget_skipped",
                               "budget_seconds_used":spent[method]})
                skipped+=1; continue
            if method=="fixed-word":
                input_obj=next(r["input"] for r in fixed_rows if r["case_id"]==cid)
                ip=inp_dir/(cid+".json")
                if not ip.exists(): ip.write_text(json.dumps(input_obj,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
            else: ip=inp_dir/(cid+".json")
            command=([PY,"-B","-X","utf8",str(C003/"solver.py"),str(ip),"--method",method,
                     "--max-solutions",str(limit),"--timeout-seconds","30"] if mode=="timing" else
                    [PY,"-B","-X","utf8",str(AUDIT/"profile_one.py"),str(ip),"--method",method,
                     "--max-solutions",str(limit)])
            hard_timeout=max(0.001,min(30.0,900.0-spent[method]))
            record=capture(f"C003_PERF_{method}_{mode}_{cid}_l{limit}_r{rep}",command,
                           cwd=ROOT,timeout_seconds=hard_timeout,source_paths=base_sources+[ip,INPUTS,BASELINE])
            record.update({"job_id":job_id,"method":method,"case_id":cid,"max_solutions":limit,
                           "mode":mode,"replicate":rep})
            append(ledger,record)
            attempted+=1
            spent[method]+=float(record.get("subprocess_seconds",0.0))
    summary={"suite_id":"C003-performance-serial-v1","planned_jobs":expected_total,
             "attempted_jobs":attempted,"budget_skipped":skipped,"by_method":{
                 m:{"planned":len(suite[m]),"subprocess_seconds":spent[m]} for m in suite},
             "performance_case_count":len(perf_cases),"fixed_word_case_count":len(fixed_cases),
             "performance_case_ids":perf_cases,"fixed_word_case_ids":fixed_cases,
             "timing_policy":"capture subprocess_seconds; three fresh-process reps per timing job",
             "memory_policy":"isolated profile_one.py run; tracemalloc peak, separate from timing",
             "hard_timeout_seconds":30,"method_budget_seconds":900,"serial":True,
             "corpus_manifest_sha256":sha((AUDIT/"corpus/frozen_c003_v1/freeze_manifest.json").read_bytes()),
             "runtime_manifest_sha256":sha((C003/"coordination/runtime_manifest.json").read_bytes()),
             "ledger_sha256":sha(ledger.read_bytes()) if ledger.exists() else sha(b"")}
    (run/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
