"""Resume missing benchmark cases, with each case's variants run serially."""
import argparse
from concurrent.futures import ProcessPoolExecutor
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from reproduce import HERE, METHODS, benchmark, fixtures, summarize


def run_case(task):
    path, case = task
    benchmark(path, [case])
    return path.read_text(encoding="utf-8")


def finish(output, workers):
    raw = output / "trials.jsonl"
    recovered = output / "serial-prefix.jsonl"
    if raw.exists() and not recovered.exists():
        raw.replace(recovered)
    prior = {}
    if recovered.exists():
        for line in recovered.read_text(encoding="utf-8").splitlines():
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            case = row["case"]
            prior.setdefault(case, set()).add((row["method"], row["budget"], row["repeat"], line))
    cases = list(fixtures())
    expected = len(METHODS)*6
    retained = {name for name, rows in prior.items() if len(rows) == expected}
    pending = [case for case in cases if case[1] not in retained]
    inputs = output / "inputs.json"
    inputs.write_text(json.dumps(cases, indent=2), encoding="utf-8")
    manifest_path = output / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["source"] = {p.name: sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.glob("*.py"))}
    manifest["inputs_sha256"] = sha256(inputs.read_bytes()).hexdigest()
    manifest["case_workers"] = workers
    manifest["serial_cases"] = sorted(retained)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    with TemporaryDirectory() as temp, raw.open("w", encoding="utf-8") as stream:
        for name in sorted(retained):
            for _, _, _, line in sorted(prior[name]):
                stream.write(line + "\n")
        stream.flush()
        with ProcessPoolExecutor(max_workers=workers) as pool:
            tasks = [(Path(temp) / f"case-{i}.jsonl", case) for i, case in enumerate(pending)]
            for lines in pool.map(run_case, tasks):
                stream.write(lines)
                stream.flush()
    summarize(raw, output / "table.md")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("evidence"))
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    finish(args.output, args.workers)
