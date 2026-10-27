"""Validate and write a corrected, non-mutating C003 execution plan."""
import hashlib, json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus/frozen_c003_v1"
EXT = HERE / "corpus/correctness_extension_v1"
C002 = Path(__file__).resolve().parents[4] / "results/2026-10-26/partition_constraints_v2/audit/corpus/frozen_v1"
OUT = HERE / "plans/plan_v2"

def sha(raw): return hashlib.sha256(raw).hexdigest()
def read_jsonl(path): return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x]
def dump(path, rows): path.write_bytes(b"".join((json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",", ":"))+"\n").encode() for x in rows))

def main():
    OUT.mkdir(parents=True, exist_ok=False)
    old = read_jsonl(CORPUS / "job_list.jsonl")
    counts = Counter(x["job_id"] for x in old)
    duplicates = sorted((key, n) for key, n in counts.items() if n > 1)
    old_review = {"artifact": "frozen_c003_v1/job_list.jsonl", "sha256": sha((CORPUS/"job_list.jsonl").read_bytes()),
                  "rows": len(old), "unique_job_ids": len(counts), "duplicate_ids": duplicates,
                  "decision": "rejected_before_provider_run; immutable frozen corpus retained"}
    (OUT / "rejected_frozen_job_list_review.json").write_text(json.dumps(old_review, indent=2)+"\n", encoding="utf-8")

    plans = []
    for row in read_jsonl(EXT / "inputs.jsonl"):
        for method in ("general", "fair-reference"):
            plans.append({"job_id": f"oldfull:{method}:{row['case_id']}", "mode": "correctness_all",
                          "method": method, "case_id": row["case_id"], "dataset": row["dataset"],
                          "input_file": "correctness_extension_v1/inputs.jsonl", "max_solutions": "all",
                          "deadline_seconds": 30})
    for name in ("c002_regression_inputs.jsonl", "random_dfa_inputs.jsonl", "fixed_word_inputs.jsonl"):
        rows = read_jsonl(CORPUS / name)
        for row in rows:
            method_list = (("general", "fair-reference") if name != "fixed_word_inputs.jsonl" else ("fixed-word",))
            for method in method_list:
                limit = ("all" if name != "random_dfa_inputs.jsonl" or len(row["input"]["alphabet"]) <= 10 else 1)
                plans.append({"job_id": f"generated:{method}:{row['case_id']}", "mode": "correctness",
                              "method": method, "case_id": row["case_id"], "dataset": row.get("dataset", name),
                              "input_file": name, "max_solutions": limit, "deadline_seconds": 30})

    perf_manifest = json.loads((C002 / "manifest.json").read_text(encoding="utf-8"))
    perf_ids = [x["case_id"] for x in perf_manifest["datasets"]["performance_100"]["case_input_hashes"]]
    for case_id in perf_ids:
        for method in ("general", "fair-reference"):
            for limit in (1, 2):
                for rep in range(1, 4):
                    plans.append({"job_id": f"perf:{method}:{case_id}:limit{limit}:time{rep}", "mode": "timing",
                                  "method": method, "case_id": case_id, "dataset": "performance_100",
                                  "max_solutions": limit, "replicate": rep, "deadline_seconds": 30})
                plans.append({"job_id": f"perf:{method}:{case_id}:limit{limit}:memory", "mode": "memory",
                              "method": method, "case_id": case_id, "dataset": "performance_100",
                              "max_solutions": limit, "replicate": 1, "deadline_seconds": 30})
    fixed_rows = read_jsonl(CORPUS / "fixed_word_inputs.jsonl")
    chosen = []
    for m in (2, 8, 16, 32, 64, 128):
        group = [r for r in fixed_rows if len(r["input"]["alphabet"]) == m]
        for index in sorted({0, (len(group)-1)//2, len(group)-1}):
            chosen.append(group[index])
    for row in chosen:
        for limit in (1, 2):
            for rep in range(1, 4):
                plans.append({"job_id": f"perf:fixed-word:{row['case_id']}:limit{limit}:time{rep}", "mode": "timing",
                              "method": "fixed-word", "case_id": row["case_id"], "dataset": "fixed_word_constructive",
                              "max_solutions": limit, "replicate": rep, "deadline_seconds": 30})
            plans.append({"job_id": f"perf:fixed-word:{row['case_id']}:limit{limit}:memory", "mode": "memory",
                          "method": "fixed-word", "case_id": row["case_id"], "dataset": "fixed_word_constructive",
                          "max_solutions": limit, "replicate": 1, "deadline_seconds": 30})
    unique = {row["job_id"] for row in plans}
    if len(unique) != len(plans): raise RuntimeError("corrected plan has duplicate IDs")
    dump(OUT / "jobs.jsonl", plans)
    summary = {"plan_id": "C003-audit-plan-v2", "frozen_corpus_manifest_sha256": sha((CORPUS/"freeze_manifest.json").read_bytes()),
               "correctness_extension_manifest_sha256": sha((EXT/"manifest.json").read_bytes()),
               "rejected_plan": old_review, "planned_jobs": len(plans),
               "unique_job_ids": len(unique), "by_method_mode": {},
               "performance_protocol": {"general_reference_cases": len(perf_ids),
                   "tasks": [1,2], "fresh_process_timing_reps": 3, "separate_memory_runs": 1,
                   "fixed_word_cases": len(chosen), "per_job_timeout_seconds": 30,
                   "per_method_total_budget_seconds": 900, "serial": True},
               "rules": ["No providers run before this plan is frozen.",
                         "Captured raw JSONL is written before independent comparison.",
                         "The C003 frozen_v1 corpus and flawed job_list are immutable.",
                         "Timing is never inferred from correctness runs; budget skips are explicit."]}
    for row in plans:
        key = f"{row['method']}:{row['mode']}"
        summary["by_method_mode"][key] = summary["by_method_mode"].get(key, 0) + 1
    raw = (json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2)+"\n").encode()
    (OUT / "manifest.json").write_bytes(raw)
    print(json.dumps({"manifest": str(OUT/"manifest.json"), "sha256": sha(raw),
                      "planned_jobs": len(plans), "unique_job_ids": len(unique),
                      "by_method_mode": summary["by_method_mode"], "rejected_plan": old_review},
                     ensure_ascii=False, indent=2))

if __name__ == "__main__": main()
