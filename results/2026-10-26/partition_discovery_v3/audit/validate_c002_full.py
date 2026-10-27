"""Independent exact-set and witness audit for captured C003 full C002 runs."""
import json, hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXT = HERE / "corpus/correctness_extension_v1"
RUNS = {"general": HERE / "attempts/20261026T192820.106900Z_b9d9227a8b/stdout.bin",
        "fair-reference": HERE / "attempts/20261026T192913.329298Z_e29b25c46f/stdout.bin"}
OUT = HERE / "validation/c002_full_v1"

def canon(blocks): return tuple(sorted(tuple(sorted(block)) for block in blocks))
def project(word, block): return "".join(a for a in word if a in set(block))
def sha(raw): return hashlib.sha256(raw).hexdigest()

def main():
    inputs = {r["case_id"]: r for r in (json.loads(x) for x in (EXT/"inputs.jsonl").read_text(encoding="utf-8").splitlines())}
    refs = {r["case_id"]: r for r in (json.loads(x) for x in (EXT/"baseline_f2.jsonl").read_text(encoding="utf-8").splitlines())}
    all_rows, errors, summary = [], [], {}
    for method, path in RUNS.items():
        rows = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x]
        per = {"rows": len(rows), "complete": 0, "incomplete": 0, "provider_errors": 0,
               "full_set_matches": 0, "witnesses_checked": 0, "cases_by_dataset": {}}
        seen = set()
        for row in rows:
            cid = row.get("case_id")
            if cid in seen: errors.append({"method": method,"case_id":cid,"error":"duplicate result row"}); continue
            seen.add(cid)
            if row.get("runner_error") or row.get("result") is None:
                per["provider_errors"] += 1
                errors.append({"method":method,"case_id":cid,"error":row.get("runner_error") or "missing result"}); continue
            inp, ref = inputs[cid]["input"], refs[cid]["baseline_f2"]
            result = row["result"]
            dataset = inputs[cid]["dataset"]
            per["cases_by_dataset"][dataset] = per["cases_by_dataset"].get(dataset, 0) + 1
            if not result.get("search_exhausted"):
                per["incomplete"] += 1
                errors.append({"method":method,"case_id":cid,"error":"full-enumeration request did not exhaust","status":result.get("status")})
                continue
            per["complete"] += 1
            expected = {canon(p["blocks"]) for p in ref.get("feasible_partitions", [])}
            actual = {canon(s["blocks"]) for s in result.get("solutions", [])}
            if actual != expected:
                errors.append({"method":method,"case_id":cid,"error":"exact F2 mismatch",
                               "expected_count":len(expected),"actual_count":len(actual),
                               "missing":[[list(b) for b in p] for p in sorted(expected-actual)],
                               "extra":[[list(b) for b in p] for p in sorted(actual-expected)]})
            else: per["full_set_matches"] += 1
            if (not expected and (result.get("status") != "infeasible" or result.get("decision_complete") is not True)):
                errors.append({"method":method,"case_id":cid,"error":"empty F2 lacks complete infeasible status"})
            if expected and result.get("status") != "found":
                errors.append({"method":method,"case_id":cid,"error":"nonempty F2 lacks found status"})
            positives = sorted(set(inp["positive"]))
            negatives = sorted(set(inp["negative"]))
            for solution in result.get("solutions", []):
                blocks = solution["blocks"]
                if len(blocks) != 2 or not all(blocks) or set(blocks[0]) & set(blocks[1]) or set(blocks[0]) | set(blocks[1]) != set(inp["alphabet"]):
                    errors.append({"method":method,"case_id":cid,"error":"invalid partition blocks"}); continue
                expected_languages = [sorted({project(p,b) for p in positives}) for b in blocks]
                if solution.get("positive_projection_languages") != expected_languages:
                    errors.append({"method":method,"case_id":cid,"error":"positive projection language mismatch"})
                witness_by_negative = {w.get("negative"): w for w in solution.get("negative_witnesses", [])}
                if set(witness_by_negative) != set(negatives):
                    errors.append({"method":method,"case_id":cid,"error":"negative witness coverage mismatch",
                                   "expected":len(negatives),"actual":len(witness_by_negative)})
                for n in negatives:
                    w = witness_by_negative.get(n)
                    if w is None: continue
                    idx = w.get("block_index")
                    if idx not in (0,1) or w.get("projection") != project(n, blocks[idx]) or w.get("projection") in expected_languages[idx]:
                        errors.append({"method":method,"case_id":cid,"negative":n,"error":"invalid negative rejection witness"})
                    else: per["witnesses_checked"] += 1
        missing = set(inputs) - seen
        if missing: errors.append({"method":method,"error":"missing cases","count":len(missing),"first":sorted(missing)[:10]})
        summary[method] = per
        all_rows.append({"method":method,"stdout_path":str(path),"stdout_sha256":sha(path.read_bytes()),"summary":per})
    report = {"validation_id":"C003-C002-FULL-AUDIT-v1", "source_corpus_manifest_sha256":sha((EXT/"manifest.json").read_bytes()),
              "runs":all_rows,"errors":errors,"accepted":not errors}
    OUT.mkdir(parents=True, exist_ok=False)
    raw=(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n").encode()
    (OUT/"report.json").write_bytes(raw)
    print(json.dumps({"accepted":not errors,"errors":len(errors),"summary":summary,
                      "report":str(OUT/"report.json"),"report_sha256":sha(raw)},ensure_ascii=False,indent=2))

if __name__ == "__main__": main()
