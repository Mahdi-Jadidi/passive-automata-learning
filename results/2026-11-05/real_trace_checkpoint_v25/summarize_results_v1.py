"""Aggregate preserved audit outputs without running inference."""
from collections import Counter
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main():
    arms = []
    statuses = Counter()
    for path in sorted((HERE / "audit").glob("ACTUAL_*_V1.json")):
        data = read(path)
        if not isinstance(data, dict) or "rows" not in data:
            continue
        rows = []
        for item in data["rows"]:
            statuses[item["status"]] += 1
            alternatives = []
            for blocks in item["heldout_alternatives"]:
                counts = Counter()
                for block in blocks:
                    counts.update({k: block.get(k, 0) for k in
                                   ("labelled", "known_context", "opposite_conflicts", "abstention")})
                alternatives.append(dict(counts))
            rows.append(dict(depth=item["depth"], status=item["status"],
                             family_count=item["independent_family_count"], heldout=alternatives,
                             block_checks=item["result"]["metrics"]["block_masks_computed"]))
        arms.append(dict(arm=data["rows"][0]["arm"], coverage=data["coverage"],
                         selected=data["selected"], results=rows,
                         source=str(path.relative_to(HERE)),
                         source_sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    out = dict(scope="Manager aggregation of preserved independent audit outputs; no new inference",
               status_counts=dict(statuses), cells=sum(statuses.values()), arms=arms)
    (HERE / "RESULTS_SUMMARY_V1.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
