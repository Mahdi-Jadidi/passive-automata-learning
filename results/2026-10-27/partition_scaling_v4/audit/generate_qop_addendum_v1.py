"""Freeze the master-provided tiny QOP CLI example as an auditor input."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
SOURCE = PROJECT / "examples" / "two_word_positive_only_certificate.json"
ROOT = HERE / "corpora" / "stage2_qop_addendum_v1"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if ROOT.exists():
        raise FileExistsError(f"refusing to overwrite frozen addendum: {ROOT}")
    data = json.loads(SOURCE.read_text(encoding="utf-8-sig"))
    input_path = ROOT / "inputs" / "qop_positive_only_tiny.json"
    truth_path = ROOT / "hidden_truth" / "qop_positive_only_tiny.json"
    input_path.parent.mkdir(parents=True)
    truth_path.parent.mkdir(parents=True)
    input_path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    truth = {"k": 2, "q": 2, "target_blocks": [["a", "b"], ["c", "d"]],
             "expected_unrestricted_partition_count": 7,
             "expected_q2_partition_count": 1,
             "expected_q1_partition_count": 0}
    truth_path.write_text(json.dumps(truth, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    manifest = {"schema": "C004-stage2-qop-addendum-manifest-v1",
                "id": "qop_positive_only_tiny", "family": "q2_positive_only_constructive",
                "input": "inputs/qop_positive_only_tiny.json",
                "input_sha256": sha(input_path), "input_bytes": input_path.stat().st_size,
                "truth": "hidden_truth/qop_positive_only_tiny.json",
                "truth_sha256": sha(truth_path), "truth_bytes": truth_path.stat().st_size,
                "public_source": str(SOURCE), "public_source_sha256": sha(SOURCE),
                "alphabet_size": len(data["alphabet"]), "k_input": data.get("k"),
                "positive_count": len(data["positive"]), "negative_count": len(data["negative"]),
                "positive_lengths": sorted({len(x) for x in data["positive"]}),
                "negative_lengths": [], "truth_hidden_from_solver": True}
    manifest_path = ROOT / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    freeze = {"schema": "C004-stage2-qop-addendum-freeze-v1",
              "manifest_sha256": sha(manifest_path), "generator_sha256": sha(Path(__file__)),
              "public_source_sha256": sha(SOURCE), "case_count": 1}
    freeze_path = ROOT / "freeze_v1.json"
    freeze_path.write_text(json.dumps(freeze, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"manifest_sha256": sha(manifest_path),
                      "freeze_sha256": sha(freeze_path), "input_sha256": sha(input_path),
                      "truth_sha256": sha(truth_path)}, separators=(",", ":")))


if __name__ == "__main__":
    main()
