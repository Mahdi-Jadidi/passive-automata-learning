"""Run a child through the immutable C004 audit capture module."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAPTURE = HERE / "capture.py"
CORPUS = HERE / "corpora" / "stage1_v4"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("label")
    parser.add_argument("timeout", type=float)
    parser.add_argument("--source", action="append", default=[])
    parser.add_argument("--include-corpus", action="store_true")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        parser.error("a command is required after --")
    if not Path(command[0]).is_absolute():
        command[0] = str((Path.cwd() / command[0]).resolve())
    sources = [Path(__file__).resolve(), *[Path(s) for s in args.source]]
    if args.include_corpus:
        manifest_path = CORPUS / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        sources.append(manifest_path)
        for row in manifest["cases"]:
            sources.append(CORPUS / row["input"])
            if row.get("truth"):
                sources.append(CORPUS / row["truth"])
    # capture.py is explicitly imported here and snapshots itself automatically.
    sys.path.insert(0, str(HERE))
    from capture import capture
    result = capture(args.label, command, cwd=HERE,
                     timeout_seconds=args.timeout, source_paths=sources)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return {"success": 0, "program_error": 1, "timed_out": 3,
            "environment_error": 4, "capture_error": 5,
            "interrupted": 130}[result["execution_status"]]


if __name__ == "__main__":
    raise SystemExit(main())
