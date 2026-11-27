"""Verify native M4 producer bytes offline, without loading producer code."""
import argparse
from pathlib import Path

from p3_frontier_verifier import build_trusted_scope, canonical, need, parse, verify_frontier
from p3_m3_artifact_replay import ORIGINAL_FIXTURES, fingerprint, read
from p3_rgs12_oracle import oracle


CASES = ("tiny_choice", "small_choice", "journal_root", "mixed_path")
ARMS = ("dense", "sparse", "join", "sparse_join")
CAP = 64 * 1024**2


def audit(inputs, normal, optimized):
    for case in CASES:
        source = inputs / case
        raw, journal, scope = [read(source / name, CAP)
                               for name in ("raw.json", "journal.json", "trusted.json")]
        if case in ORIGINAL_FIXTURES:
            need(fingerprint(raw)["sha256"] == ORIGINAL_FIXTURES[case][0], "raw fixture pin")
        derived = build_trusted_scope(raw, journal)
        need(canonical(derived) == scope, "scope byte mismatch")
        if case == "journal_root":
            need(derived["root_owner"] != list(range(len(derived["alphabet"]))),
                 "identity journal root")
        census = oracle(parse(raw, CAP), seconds=120)
        need(census["status"] == "VERIFIED", str(census))
        truth = census["result"]
        for mode in ("one", "all"):
            complete_by_arm = {}
            for arm in ARMS:
                relative = Path(case) / mode / arm
                pins = {}
                for name in ("complete", "partial", "resumed"):
                    path = relative / (name + ".json")
                    cert = read(normal / path, CAP)
                    need(cert == read(optimized / path, CAP), f"interpreter bytes: {path}")
                    pins[name] = fingerprint(cert)
                    answer = verify_frontier(raw, journal, scope, cert, sparse_exact=True,
                                             expected_format="p3-region-frontier/v2",
                                             expected_mode=mode)
                    if name == "partial":
                        need(answer["status"] == "INCOMPLETE" and "result" not in answer
                             and answer["reason"] == "unresolved frontier", str(answer))
                    else:
                        need(answer["status"] == "VERIFIED", str(answer))
                        result = answer["result"]
                        need(result["optimum"] == truth["optimum"] and
                             result["owner"] in truth["optima"] and
                             result["optima"] == (truth["optima"] if mode == "all" else []),
                             f"literal RGS mismatch: {relative}")
                need(pins["complete"] == pins["resumed"], f"resume mismatch: {relative}")
                complete_by_arm[arm] = pins["complete"]
                yield dict(case=case, mode=mode, arm=arm, pins=pins, replay=answer,
                           inputs=dict(raw=fingerprint(raw), journal=fingerprint(journal),
                                       scope=fingerprint(scope)),
                           rgs_visited=census["visited"], rgs_optima=len(truth["optima"]))
            need(complete_by_arm["dense"] == complete_by_arm["sparse"],
                 f"dense/sparse complete mismatch: {case}/{mode}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("inputs", "normal", "optimized"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    for row in audit(args.inputs, args.normal, args.optimized):
        print(canonical(row).decode("ascii"), flush=True)


if __name__ == "__main__":
    main()
