#!/usr/bin/env python3
"""Create provider-only JSON files from the already frozen scale JSONL."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SCALE = HERE / "scale_v1"
SOURCE = SCALE / "inputs.jsonl"
OUT = SCALE / "cli_inputs"


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = [json.loads(line) for line in SOURCE.read_text(encoding="utf-8").splitlines() if line]
    files = {}
    for row in rows:
        data = row["input"]
        encoded = (json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
        path = OUT / (row["case_id"] + ".json")
        if path.exists():
            raise FileExistsError(f"refusing to overwrite scale CLI input: {path}")
        path.write_bytes(encoded)
        files[row["case_id"]] = {"path": str(path.relative_to(SCALE)).replace("\\", "/"),
                                 "bytes": len(encoded), "sha256": sha256(encoded),
                                 "solver_fields": sorted(data)}
    manifest = {
        "schema_version": 1,
        "derivation": "jsonl row input only; case_id and all sidecar data excluded",
        "source_inputs_sha256": sha256(SOURCE.read_bytes()),
        "files": files,
    }
    output = SCALE / "cli_input_manifest_v1.json"
    if output.exists():
        raise FileExistsError(f"refusing to overwrite CLI input manifest: {output}")
    output.write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                      encoding="utf-8", newline="\n")
    print(json.dumps({"derived_inputs": len(files),
                      "manifest_sha256": sha256(output.read_bytes()),
                      "source_inputs_sha256": manifest["source_inputs_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
