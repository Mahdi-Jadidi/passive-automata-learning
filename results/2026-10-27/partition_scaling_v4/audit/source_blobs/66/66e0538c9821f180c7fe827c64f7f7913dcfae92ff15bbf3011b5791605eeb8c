"""Run a child through the immutable C004 audit capture module."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpora" / "stage1_v4"


def main():
    raw = sys.argv[1:]
    if "--" not in raw:
        raise SystemExit("usage: run_captured_v2.py LABEL SECONDS [OPTIONS] -- COMMAND [ARG ...]")
    cut = raw.index("--")
    option_args, command = raw[:cut], raw[cut + 1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("label")
    parser.add_argument("timeout", type=float)
    parser.add_argument("--source", action="append", default=[])
    parser.add_argument("--include-corpus", action="store_true")
    args = parser.parse_args(option_args)
    if not command:
        parser.error("a command is required after --")
    command = list(command)
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
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from capture import capture
    result = capture(args.label, command, cwd=HERE,
                     timeout_seconds=args.timeout, source_paths=sources)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return {"success": 0, "program_error": 1, "timed_out": 3,
            "environment_error": 4, "capture_error": 5,
            "interrupted": 130}[result["execution_status"]]


if __name__ == "__main__":
    raise SystemExit(main())
