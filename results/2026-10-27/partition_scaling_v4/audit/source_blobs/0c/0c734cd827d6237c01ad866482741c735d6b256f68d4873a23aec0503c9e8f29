"""Hash the exact C004 stage-1 corpus and its deterministic builder."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE / "corpora" / "stage1_v4"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest_path = ROOT / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = [manifest_path]
    for row in manifest["cases"]:
        files.append(ROOT / row["input"])
        if row.get("truth"):
            files.append(ROOT / row["truth"])
    entries = []
    for path in sorted(set(files), key=lambda p: p.as_posix()):
        entries.append({"path": path.relative_to(ROOT).as_posix(),
                        "sha256": digest(path), "bytes": path.stat().st_size})
    builder = HERE / "build_corpus_v4.py"
    freeze = {"schema": "c004-stage1-corpus-freeze-v1",
              "manifest_sha256": digest(manifest_path),
              "builder_path": str(builder), "builder_sha256": digest(builder),
              "capture_path": str(HERE / "capture.py"),
              "capture_sha256": digest(HERE / "capture.py"),
              "case_count": manifest["case_count"], "file_count": len(entries),
              "truth_separated_from_inputs": True,
              "files": entries}
    out = ROOT / "corpus_freeze_v2.json"
    if out.exists():
        raise FileExistsError(f"refusing to replace frozen record: {out}")
    out.write_text(json.dumps(freeze, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8", newline="\n")
    print(json.dumps({"case_count": freeze["case_count"],
                      "file_count": freeze["file_count"],
                      "manifest_sha256": freeze["manifest_sha256"],
                      "freeze": str(out)}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

