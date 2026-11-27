"""Exhaustive Review10 comparison on frozen offline snapshots."""
import argparse
import csv
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from time import perf_counter

from review10_histories import owners

CORE = "3fcb278d6562b76e5c75936425b39c57d02f2409"
PROOF = "b8676e30917b8df4ca07086c54a9d38d09330abd"
PACKAGE = "implementation/partition_feedback_final"
CORE_CASE = Path(PACKAGE) / "research/p3-m5/aefc/cross-id"


def literal(raw, owner):
    # Relabel once and slice each word by group, preserving order and repeats.
    group_for = dict(zip(raw["alphabet"], owner))
    groups = sorted(set(owner))
    work = 0

    def signatures(words):
        nonlocal work
        for word in words:
            blocks = {group: [] for group in groups}
            for symbol in word:
                blocks[group_for[symbol]].append(symbol)
                work += 1
            yield tuple(tuple(blocks[group]) for group in groups)

    positive = list(signatures(raw["positive"]))
    seen = [set(column) for column in zip(*positive)] if positive else [set() for _ in groups]
    for word in signatures(raw["negative"]):
        for projection, matches in zip(word, seen):
            work += 1
            if projection not in matches:
                break
        else:
            return "NO", work
    return "COMPATIBLE", work


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ("core", "proof", "output"):
        parser.add_argument("--" + flag, type=Path, required=True)
    parser.add_argument("--arm", choices=("containment", "named", "literal"), required=True)
    args = parser.parse_args()
    for source, commit in ((args.core, CORE), (args.proof, PROOF)):
        def git(*command):
            return subprocess.check_output(["git", "-C", str(source), *command]).decode().strip()
        if git("rev-parse", "HEAD") != commit or git("status", "--porcelain", "--untracked-files=all"):
            raise ValueError(f"expected clean checkout of {commit}")

    fixtures = Path(__file__).parent / "results/review10"
    expected = {row["case"]: row for row in json.loads(
        (fixtures / "summary.json").read_bytes())["cases"]}
    cases = {name: fixtures / name for name in expected}
    cases["free_group_cross_id"] = args.core / CORE_CASE

    if args.arm != "literal":
        sys.path[:0] = [str((args.core / PACKAGE).resolve()),
                        str((args.proof / "tests/reference").resolve())]
        from selector_v2 import feedback_aefc as aefc
        from p3_aefc_verifier import verify_aefc

        budgets = []

        class MeasuredBudget(aefc._Budget):
            def __init__(self, limits):
                super().__init__(limits)
                self.initial_work = self.work
                budgets.append(self)

        aefc._Budget = MeasuredBudget

        def measured_work():
            budget, = budgets
            budgets.clear()
            return budget.initial_work - budget.work

    args.output.mkdir(parents=True)
    rows, summaries = [], []
    for name, fixture in cases.items():
        files = {key: (fixture / (key + ".json")).read_bytes() for key in ("raw", "journal")}
        if name in expected:
            files["targets"] = (fixture / "targets.json").read_bytes()
        raw, journal = json.loads(files["raw"]), files["journal"]
        targets = list(owners(len(raw["alphabet"])))
        if "targets" in files and [list(owner) for owner in targets] != json.loads(files["targets"]):
            raise ValueError("target list mismatch")
        hashes = {key: sha256(data).hexdigest() for key, data in files.items()}
        if name in expected and any(
            expected[name]["files"][key + ".json"]["sha256"] != value
            for key, value in hashes.items()
        ):
            raise ValueError("frozen fixture hash mismatch")
        summary = dict(case=name, files=hashes, targets=len(targets), index_builds=0,
                       index_reuses=0, external_calls=0,
                       offline_queries=sum(event["event"] == "REGISTER"
                                           for event in json.loads(journal)["events"]))
        if args.arm != "literal":
            started = perf_counter()
            status, snapshot = aefc.prepare(raw, journal)
            summary.update(prepare_seconds=perf_counter()-started, prepare_work=measured_work(),
                           index_builds=1, index_reuses=len(targets)-1)
            if status != "READY":
                raise ValueError((name, status))
        case_rows = []
        for owner in targets:
            row = dict(case=name, owner=list(owner), proof_bytes=0, proof_sha256=None,
                       replay_seconds=None)
            started = perf_counter()
            if args.arm == "literal":
                status, work = literal(raw, owner)
                row.update(status=status, work=work, seconds=perf_counter()-started)
            else:
                status, proof = snapshot.prove(list(owner), containment_only=args.arm == "containment")
                row.update(status=status, seconds=perf_counter()-started, work=measured_work())
                if status == "PROVEN_NO":
                    started = perf_counter()
                    verdict = verify_aefc(raw, journal, proof)
                    row["replay_seconds"] = perf_counter()-started
                    if verdict["status"] != "VERIFIED" or verdict["result"]["owner"] != list(owner):
                        raise ValueError((name, owner, verdict))
                    path = args.output / name
                    path.mkdir(exist_ok=True)
                    (path / ("-".join(map(str, owner)) + ".json")).write_bytes(proof)
                    row.update(status="VERIFIED_NO", proof_bytes=len(proof),
                               proof_sha256=sha256(proof).hexdigest())
                elif status != "UNKNOWN":
                    raise ValueError((name, owner, status))
            case_rows.append(row)
        summary["counts"] = {status: sum(row["status"] == status for row in case_rows)
                             for status in sorted({row["status"] for row in case_rows})}
        rows.extend(case_rows)
        summaries.append(summary)

    try:
        import resource
        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    except ImportError:
        rss = None
    report = dict(core=CORE, proof=PROOF, arm=args.arm, runtime=sys.flags.optimize,
                  peak_process_rss_kib=rss, cases=summaries, routes=rows)
    (args.output / "results.json").write_bytes((json.dumps(report, indent=2) + "\n").encode())
    with (args.output / "results.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
