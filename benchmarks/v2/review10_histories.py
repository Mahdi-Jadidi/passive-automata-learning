"""Build and independently replay frozen Review 10 offline benchmark histories."""
import argparse
import csv
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from time import perf_counter

PIN = "be52e6aa51dcbc6a7cc37d84608df97cfffd1f43"
AB, AC, BC = (0, 0, 2, 3), (0, 1, 0, 3), (0, 1, 1, 3)
CASES = {
    "named": (["abcd"], ["abdc"], [(owner, 0, 0) for owner in (AB, AC, BC)]),
    "cross_id": (["ab", "abcd"], ["abdc", "abdc", "a", "ad"],
                 [(AB, 0, 0), (AB, 1, 0), (AB, 1, 1), (AC, 0, 0), (BC, 0, 0)]),
    "repeated_order": (["aabcd", "aabcd"], ["aabdc"],
                       [(owner, 0, 0) for owner in (AB, AC, BC)]),
}


def owners(n):
    def extend(prefix):
        if len(prefix) == n:
            yield prefix
            return
        for group in sorted(set(prefix) | {len(prefix)}):
            yield from extend(prefix + [group])
    return extend([])


def projections(raw, owner):
    index = dict(zip(raw["alphabet"], owner))
    for group in sorted(set(owner)):
        yield group, [
            [tuple(symbol for symbol in word if index[symbol] == group)
             for word in raw[label]]
            for label in ("positive", "negative")
        ]


def simulate(raw, request, negative_choice, witness_choice):
    tables = []
    for group, (positive, negative) in projections(raw, request["owner"]):
        zeros, free = [], {}
        for i, word in enumerate(negative):
            matches = [j for j, candidate in enumerate(positive) if candidate == word]
            if matches:
                witness = matches[witness_choice % len(matches)] if i == negative_choice else None
                zeros.append(dict(negative=i, positive=witness))
            else:
                free.setdefault(word, []).append(i)
        if not any(z["negative"] == negative_choice for z in zeros):
            raise ValueError("offline response policy selected a non-failing negative")
        tables.append(dict(block=group, kind="UNRESTRICTED_BASE", complete=True,
                           zeros=zeros, free=list(free.values())))
    return dict(version=request["version"], request=request, origin="SIMULATOR",
                status="PROJECTION_NO", complete=True, receipt=request["attempt_id"],
                failed=negative_choice, tables=tables)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = args.source.resolve()
    directories = ("implementation/partition_feedback_final/selector_v2",
                   "research/interface/p2", "tests/reference")

    def git(*argv):
        return subprocess.check_output(["git", "-C", str(source), *argv]).decode().strip()

    if git("rev-parse", "HEAD") != PIN or git(
        "status", "--porcelain", "--untracked-files=all", "--", *directories
    ):
        raise ValueError("expected clean pinned staging source")
    sys.path[:0] = [str((source / directories[0]).parent),
                    *(str(source / path) for path in directories[1:])]
    from adapter import canonical
    from gateway import open_gateway
    from p3_frontier_verifier import build_trusted_scope

    args.output.mkdir(parents=True)
    results = []
    for name, (positive, negative, queries) in CASES.items():
        directory = args.output / name
        directory.mkdir()
        hashes = {}

        def save(filename, data):
            (directory / filename).write_bytes(data)
            hashes[filename] = dict(sha256=sha256(data).hexdigest(), bytes=len(data))

        raw = dict(alphabet=list("abcd"), positive=list(map(list, positive)),
                   negative=list(map(list, negative)))
        ledger = open_gateway(raw)
        for i, (owner, failing, witness) in enumerate(queries):
            request_id, attempt_id = f"q{i}", f"a{i}"
            request = ledger.register(list(owner), request_id, attempt_id)
            reply = canonical(simulate(raw, request, failing, witness))
            if ledger.ingest(request_id, attempt_id, reply) != "PROJECTION_NO":
                raise ValueError(f"{name}: adapter rejected {attempt_id}")
        journal = ledger.export()
        start = perf_counter()
        scope = build_trusted_scope(raw, journal)
        replay_seconds = perf_counter() - start
        targets = list(owners(len(raw["alphabet"])))
        save("raw.json", canonical(raw))
        save("journal.json", journal)
        save("scope.json", canonical(scope))
        save("targets.json", canonical(targets))
        results.append(dict(case=name, offline_queries=len(queries), external_calls=0,
                            targets=len(targets), snapshot_exports=1,
                            replay_seconds=replay_seconds, files=hashes))
    summary = dict(source_commit=PIN, source_trees={path: git("rev-parse", PIN + ":" + path)
                                                  for path in directories}, cases=results)
    (args.output / "summary.json").write_bytes(canonical(summary))
    with (args.output / "summary.csv").open("w", newline="", encoding="utf-8") as stream:
        columns = [key for key in results[0] if key != "files"]
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    main()
