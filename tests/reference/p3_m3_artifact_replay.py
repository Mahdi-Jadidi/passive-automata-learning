"""Offline proof-only gate for exact native v2 artifact files."""
import argparse
import hashlib
from pathlib import Path
import sys

from p3_frontier_verifier import (
    ALL_PAIRS, CROSS_SUPPORT, Incomplete, build_trusted_scope, canonical, need, parse,
    verify_frontier,
)
from p3_rgs12_oracle import oracle


ORIGINAL_FIXTURES = {
    "tiny_choice": ("1c064aa4c7ce111ec8c403e8b6a05b64de5acdec2ef564861f06c2e2e2e42f23", 203, 2, 4),
    "small_choice": ("10b0c3534ddf42369db003bca6b323c9fdaa33cd36aa15031360c3428949931b", 4213597, 4, 16),
}


def read(path, limit):
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise Incomplete(f"{path.name} byte cap")
    return data


def fingerprint(data):
    blob = hashlib.sha1()
    blob.update(f"blob {len(data)}\0".encode("ascii"))
    blob.update(data)
    return dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                git_blob_calculated=blob.hexdigest())


def replay(case, mode, paths, *, proof_cap=64*1024**2, seconds=30):
    inputs = {key: read(paths[key], 64*1024**2) for key in ("raw", "journal", "scope")}
    pins = {key: fingerprint(data) for key, data in inputs.items()}
    expected = ORIGINAL_FIXTURES.get(case)
    if expected is not None:
        need(pins["raw"]["sha256"] == expected[0], "original fixture byte mismatch")

    budgets = dict(seconds=seconds, max_proof_bytes=proof_cap, max_work=4_000_000_000,
                   max_nodes=6_000_001, max_exact_checks=200_000_000, max_entries=6_000_001)
    raw, journal, scope_bytes = (inputs[key] for key in ("raw", "journal", "scope"))
    scope = build_trusted_scope(raw, journal, budgets=budgets)
    need(canonical(scope) == scope_bytes, "trusted scope byte mismatch")
    if case == "nonempty_journal":
        events = parse(journal, 64*1024**2)["events"]
        need(events and scope["root_owner"] != list(range(len(scope["alphabet"]))),
             "nonempty journal must prove a nonidentity root")

    def verify(data, **overrides):
        return verify_frontier(raw, journal, scope_bytes, data,
                               expected_format="p3-region-frontier/v2", expected_mode=mode,
                               budgets=dict(budgets, **overrides))

    normal = read(paths["normal"], proof_cap)
    pins["normal"] = fingerprint(normal)
    variants = ("optimized", "resumed") if "resumed" in paths else ("optimized",)
    for variant in variants:
        # An explicitly provided alias may reference the same retained payload.
        with paths[variant].open("rb") as stream:
            view = memoryview(normal)
            for start in range(0, len(normal), 1024*1024):
                part = view[start:start + 1024*1024]
                need(stream.read(len(part)) == part, f"{variant} proof bytes differ")
            need(stream.read(1) == b"", f"{variant} proof bytes differ")
        pins[variant] = pins["normal"]

    complete = verify(normal)
    if complete["status"] == "INCOMPLETE":
        raise Incomplete(f"complete proof replay: {complete}")
    need(complete["status"] == "VERIFIED", f"complete proof replay: {complete}")
    if case == "mixed_path":
        splits = {q["id"]: q for q in parse(normal, proof_cap)["nodes"] if q["kind"] == "SPLIT"}
        mixed = any(q["parent_id"] in splits and
                    {q["rule"], splits[q["parent_id"]]["rule"]} == {ALL_PAIRS, CROSS_SUPPORT}
                    for q in splits.values())
        need(mixed, "mixed fixture must contain a mixed ancestor path")
    checkpoint = read(paths["checkpoint"], min(proof_cap, 16*1024**2))
    pins["checkpoint"] = fingerprint(checkpoint)
    partial = verify(checkpoint)
    need(partial["reason"] == "unresolved frontier", f"checkpoint frontier: {partial}")
    forged = parse(checkpoint, proof_cap)
    forged["declared_status"] = "EXHAUSTED"
    controls = {"checkpoint": partial, "false_exhausted": verify(forged),
                "byte_cap": verify(normal, max_proof_bytes=1)}
    for scenario, status in (("checkpoint", "INCOMPLETE"), ("false_exhausted", "INVALID"),
                             ("byte_cap", "INCOMPLETE")):
        outcome = controls[scenario]
        need(outcome["status"] == status and "result" not in outcome, f"{scenario}: {outcome}")
    del normal

    census = oracle(parse(raw, 64*1024**2), seconds=seconds)
    if census["status"] == "INCOMPLETE":
        raise Incomplete(f"literal RGS census: {census}")
    need(census["status"] == "VERIFIED", f"literal RGS census: {census}")
    answer, truth = complete["result"], census["result"]
    need(answer["optimum"] == truth["optimum"], "literal RGS cost mismatch")
    need(answer["owner"] in (truth["optima"] or [None]), "literal RGS incumbent mismatch")
    need(answer["optima"] == (truth["optima"] if mode == "all" else []),
         "literal RGS optimum set mismatch")
    if expected is not None:
        need((census["visited"], truth["optimum"], len(truth["optima"])) == expected[1:],
             "literal RGS census mismatch")
    return dict(status="VERIFIED", operational_status="INCOMPLETE", case=case, mode=mode,
                byte_pins=pins, limits=budgets, complete=complete, controls=controls,
                root_owner=scope["root_owner"], census=census,
                completed_resume_status="VERIFIED" if "resumed" in pins else "NOT RUN")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=(*ORIGINAL_FIXTURES, "nonempty_journal", "mixed_path"),
                        required=True)
    parser.add_argument("--mode", choices=("one", "all"), required=True)
    parser.add_argument("--proof-cap", type=int, default=64*1024**2)
    parser.add_argument("--seconds", type=float, default=30)
    keys = ("raw", "journal", "scope", "normal", "optimized", "checkpoint")
    for key in keys:
        parser.add_argument("--" + key, required=True, type=Path)
    resume = parser.add_mutually_exclusive_group(required=True)
    resume.add_argument("--resumed", type=Path)
    resume.add_argument("--resume-unavailable", action="store_true")
    args = parser.parse_args()
    try:
        need(args.proof_cap >= 0, "negative proof byte cap")
        paths = {key: getattr(args, key) for key in keys}
        if args.resumed is not None:
            paths["resumed"] = args.resumed
        out = replay(args.case, args.mode, paths, proof_cap=args.proof_cap, seconds=args.seconds)
    except (Incomplete, MemoryError, TimeoutError, OSError) as exc:
        out = dict(status="INCOMPLETE", operational_status="INCOMPLETE", reason=str(exc))
    except (ValueError, TypeError, OverflowError) as exc:
        out = dict(status="INVALID", operational_status="INCOMPLETE", reason=str(exc))
    print(canonical(out).decode("ascii"))
    return {"VERIFIED": 0, "INVALID": 1, "INCOMPLETE": 2}[out["status"]]


if __name__ == "__main__":
    sys.exit(main())
