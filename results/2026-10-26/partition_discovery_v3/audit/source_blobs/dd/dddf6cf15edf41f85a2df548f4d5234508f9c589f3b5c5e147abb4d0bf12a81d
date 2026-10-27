"""Freeze the full small-alphabet C002 correctness regression extension."""
import gzip
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[4]
frozen = root / "results/2026-10-26/partition_constraints_v2/audit/corpus/frozen_v1"
run = root / "results/2026-10-26/partition_constraints_v2/audit/correctness_runs/20261026T125503.860658Z_805e5494"
out = Path(__file__).resolve().parent / "corpus/correctness_extension_v1"
datasets = {"prior_binary_2187", "prior_abc_81", "prior_theory_4",
            "targeted_controls", "random_ternary_5000"}

def sha(b): return hashlib.sha256(b).hexdigest()
def line(obj): return (json.dumps(obj, ensure_ascii=False, sort_keys=True,
                                  separators=(",", ":")) + "\n").encode("utf-8")

manifest = json.loads((frozen / "manifest.json").read_text(encoding="utf-8"))
reference = {}
with gzip.open(run / "baseline.jsonl.gz", "rt", encoding="utf-8") as handle:
    for raw in handle:
        row = json.loads(raw)
        if row.get("dataset") in datasets:
            reference[row["case_id"]] = row
inputs = []
refs = []
for dataset in sorted(datasets):
    ids = [x["case_id"] for x in manifest["datasets"][dataset]["case_input_hashes"]]
    for index, case_id in enumerate(ids):
        row = reference[case_id]
        if not row["result"].get("complete"):
            raise RuntimeError(f"incomplete saved F2 reference: {case_id}")
        inputs.append({"case_id": case_id, "dataset": dataset,
                       "input": row["input"], "input_sha256": row["input_sha256"]})
        refs.append({"case_id": case_id, "dataset": dataset,
                     "selected_index": index, "baseline_f2": row["result"]})
out.mkdir(parents=True, exist_ok=False)
files = {}
for name, rows in (("inputs.jsonl", inputs), ("baseline_f2.jsonl", refs)):
    raw = b"".join(line(x) for x in rows)
    (out / name).write_bytes(raw)
    files[name] = {"bytes": len(raw), "sha256": sha(raw)}
meta = {"corpus_id": "C003-correctness-extension-v1", "dataset_counts": {
            key: len(manifest["datasets"][key]["case_input_hashes"]) for key in sorted(datasets)},
        "case_count": len(inputs), "jobs": ["general:max_solutions=all", "fair-reference:max_solutions=all"],
        "deadline_seconds_per_case": 30,
        "reference_manifest_sha256": sha((frozen / "manifest.json").read_bytes()),
        "reference_stream_sha256": sha((run / "baseline.jsonl.gz").read_bytes()),
        "source_run": "20261026T125503.860658Z_805e5494", "files": files}
raw = line(meta)
(out / "manifest.json").write_bytes(raw)
print(json.dumps({"directory": str(out), "case_count": len(inputs),
                  "manifest_sha256": sha(raw), "files": files,
                  "dataset_counts": meta["dataset_counts"]}, ensure_ascii=False, indent=2))
