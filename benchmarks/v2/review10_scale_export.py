"""Summarize the pinned Agent #6 native compact CI artifacts."""
import argparse
import csv
from hashlib import sha256
import json
from pathlib import Path


def read(path):
    return json.loads(path.read_bytes())


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifacts", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    manifest = read(Path(__file__).parent / "review03/p3/input-manifest.json")
    raw_hashes = {item["case"]: item["input_sha256"] for item in manifest}
    rows = []
    for memory in (512, 1536):
        for case in ("native", "medium_choice", "huge_choice_active"):
            artifact = args.artifacts / f"native-scale-{memory}-{case}"
            for runtime in ("normal", "optimized"):
                directory = artifact / runtime
                measurements = sorted(directory.rglob("metrics.json"))
                if len(measurements) != (50 if case == "native" else 4):
                    raise ValueError(f"incomplete artifact: {directory}")
                for path in measurements:
                    record = read(path)
                    relative = path.parent.relative_to(directory).parts
                    if case == "native":
                        fixture, mode, arm = relative
                        inputs = directory / fixture
                        proof = path.with_name("complete.json")
                        replay = record["replay"]
                        root_metrics = None
                    else:
                        fixture, mode, arm = case, "one", relative[0]
                        inputs = path.parent
                        proof = path.with_name("certificate.json")
                        verdict = path.with_name("replay.json")
                        replay = read(verdict) if verdict.exists() else {"status": "INCOMPLETE"}
                        root_metrics = read(path.with_name("root-metrics.json"))
                    rows.append(dict(case=fixture, memory_mib=memory, runtime=runtime,
                                     mode=mode, arm=arm, status=replay["status"],
                                     search=record["search"], replay=replay,
                                     wall_seconds=record.get("wall_seconds"),
                                     peak_rss_kib=record.get("peak_rss_kib"),
                                     root_preparation=root_metrics, root_check=record["search"].get("root_check"),
                                     raw_sha256=digest(inputs / "raw.json") if case == "native" else raw_hashes[case],
                                     scope_sha256=digest(inputs / "scope.json"),
                                     journal_sha256=digest(inputs / "journal.json"),
                                     certificate_bytes=proof.stat().st_size if proof.exists() else None,
                                     certificate_sha256=digest(proof) if proof.exists() else None))
    args.output.mkdir(parents=True, exist_ok=True)
    pins = dict(ci_run=46021645996, scale_commit="23883be28cbde727443d8d3c5d2a723d924e3aec",
                proof_commit="98e913a7e15d32638319832fc69edb36edb2f505",
                interface_commit="122844ee5668f1c898f85b08133a562f31719718",
                fixtures_commit="8484b8bff5b93e1be3a7924697161efc34e481d8",
                retained_commit="444cea666816a4faaf875a831ec4a3949c673a4b")
    (args.output / "scale.json").write_bytes(
        (json.dumps(dict(pins=pins, routes=rows), indent=2, sort_keys=True) + "\n").encode())
    columns = ("case", "memory_mib", "runtime", "mode", "arm", "status", "wall_seconds",
               "peak_rss_kib", "scope_sha256", "journal_sha256", "certificate_bytes",
               "certificate_sha256")
    with (args.output / "scale-search.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    with (args.output / "scale-roots.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(("case", "memory_mib", "runtime", "arm", "root_check_json", "root_preparation_json"))
        for row in rows:
            if row["root_preparation"] is not None:
                writer.writerow([row[key] for key in ("case", "memory_mib", "runtime", "arm")]
                                + [json.dumps(row[key], sort_keys=True) for key in ("root_check", "root_preparation")])


if __name__ == "__main__":
    main()
