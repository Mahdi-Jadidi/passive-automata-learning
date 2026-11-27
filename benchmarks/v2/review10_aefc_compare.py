"""Compare independently measured AEFC arms against literal verdicts."""
import argparse
from collections import Counter
import csv
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    data = {}
    for runtime in ("normal", "optimized"):
        for arm in ("containment", "named", "literal"):
            report = json.loads((args.directory / runtime / arm / "results.json").read_bytes())
            data[runtime, arm] = {(row["case"], tuple(row["owner"])): row
                                  for row in report["routes"]}
    counts = {}
    normal = data["normal", "literal"]
    for key, reference in normal.items():
        verdicts = {}
        for arm in ("containment", "named", "literal"):
            rows = [data[runtime, arm][key] for runtime in ("normal", "optimized")]
            fields = ("status", "work", "proof_bytes", "proof_sha256")
            if any(rows[0][field] != rows[1][field] for field in fields):
                raise ValueError((key, arm, "interpreter parity"))
            verdicts[arm] = rows[0]["status"]
            if verdicts[arm] == "VERIFIED_NO" and reference["status"] != "NO":
                raise ValueError((key, arm, "false NO"))
        if verdicts["containment"] == "VERIFIED_NO" and verdicts["named"] != "VERIFIED_NO":
            raise ValueError((key, "lost containment coverage"))
        if key in (("named", (0, 0, 0, 3)), ("free_group_cross_id", (0, 0, 0, 3, 4))):
            if verdicts != dict(containment="UNKNOWN", named="VERIFIED_NO", literal="NO"):
                raise ValueError((key, verdicts))
        for arm, status in verdicts.items():
            counts.setdefault((key[0], arm), Counter())[status] += 1
    if any(routes.keys() != normal.keys() for routes in data.values()):
        raise ValueError("arm target sets differ")
    summary = [dict(case=case, arm=arm, **counter) for (case, arm), counter in counts.items()]
    (args.directory / "comparison.json").write_bytes((json.dumps(summary, indent=2) + "\n").encode())
    columns = ("case", "arm", "VERIFIED_NO", "UNKNOWN", "NO", "COMPATIBLE")
    with (args.directory / "comparison.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(summary)


if __name__ == "__main__":
    main()
