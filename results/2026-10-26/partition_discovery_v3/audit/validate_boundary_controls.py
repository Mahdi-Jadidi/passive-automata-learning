"""Check captured boundary outputs against the immutable C002 exact baseline."""
import argparse
import hashlib
import json
from pathlib import Path


def signature(record):
    return tuple(sorted(tuple(sorted(block)) for block in record["blocks"]))


def result_set(result):
    return {signature(row) for row in result["solutions"]}


def verify_witnesses(data, result):
    for solution in result["solutions"]:
        blocks = [set(block) for block in solution["blocks"]]
        languages = [{"".join(a for a in word if a in block)
                      for word in data["positive"]} for block in blocks]
        for witness in solution["negative_witnesses"]:
            negative = witness["negative"]
            projection = "".join(a for a in negative if a in blocks[witness["block_index"]])
            assert projection not in languages[witness["block_index"]]
            assert witness["projection"] == projection


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stream", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.stream.read_text(encoding="utf-8").splitlines() if line]
    assert len(rows) == 9, len(rows)
    summary = {}
    for row in rows:
        name = row["control"]
        if name == "deadline_expired":
            for method in ("general", "fair_reference"):
                result = row[method]
                assert result["status"] == "incomplete"
                assert not result["search_exhausted"] and not result["decision_complete"]
                assert result["uniqueness"] == "unknown"
            summary[name] = "both providers return incomplete/unknown without claiming exhaustion"
            continue
        general, fair, baseline = row["general"], row["fair_reference"], row["baseline"]
        expected = {signature(item) for item in baseline["feasible_partitions"]}
        assert result_set(general) == expected, name
        assert result_set(fair) == expected, name
        assert general["solutions"] == fair["solutions"], name
        for result in (general, fair):
            assert result["search_exhausted"] and result["decision_complete"]
            verify_witnesses(row["input"], result)
        summary[name] = {"exact_partition_set_size": len(expected),
                         "status": general["status"], "witnesses_checked": sum(
                             len(s["negative_witnesses"]) for s in general["solutions"])}
    raw, clean = next(r for r in rows if r["control"] == "duplicates_permuted"), \
                 next(r for r in rows if r["control"] == "permutation_deduplicated")
    assert result_set(raw["general"]) == result_set(clean["general"])
    assert raw["general"]["solutions"] == clean["general"]["solutions"]
    assert raw["fair_reference"]["solutions"] == clean["fair_reference"]["solutions"]
    report = {"status": "accepted", "cases": len(rows), "controls": summary,
              "general_and_fair_match_immutable_baseline": True,
              "all_full_results_exhausted": True,
              "permutation_duplicate_normalization_invariant": True,
              "expired_deadline_classification": "incomplete, no exhaustion or uniqueness claim",
              "raw_stream_sha256": hashlib.sha256(args.stream.read_bytes()).hexdigest()}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
