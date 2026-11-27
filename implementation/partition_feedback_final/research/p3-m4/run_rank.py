"""Generate rank-on/off native artifacts and compare with the literal RGS oracle."""

import argparse
from fractions import Fraction
from hashlib import sha256
from math import ceil
from pathlib import Path

from p3_frontier_verifier import build_trusted_scope, verify_frontier
from p3_rgs12_oracle import oracle

from selector_v2.core import Sample
from selector_v2.edr_bb import SearchCaps
from selector_v2.edr_m4 import solve
from selector_v2.edr_search import canonical, load

HERE = Path(__file__).resolve().parent
M3 = HERE.parent / "p3-m3/evidence/normal"
CASES = ("tiny_choice", "small_choice", "cover", "mixed_path", "journal_root",
         "equality", "strict", "fractional")


def require(ok, label):
    if not ok:
        raise RuntimeError(label)


def inputs(case):
    if case in ("tiny_choice", "small_choice", "journal_root", "mixed_path"):
        return load(M3 / case / "raw.json"), (M3 / case / "journal.json").read_bytes()
    if case == "cover":
        raw = load(HERE.parent.parent / "evidence/cover_path_8.json")["input"]
    else:
        raw = load(HERE / "rank-inputs" / f"{case}.json")
    journal = canonical(dict(events=[], version="selector-v2-journal/2",
                             sample_digest=Sample.from_input(raw).sample_digest))
    return raw, journal


def check_active(case, mode, cert):
    # Each /c edge in these identity-root paths merges two distinct classes.
    checks = {("equality", "one"): (True, False), ("strict", "all"): (False, False),
              ("fractional", "one"): (True, True)}
    target = checks.get((case, mode))
    if target is None:
        return
    found = set()
    for node in cert["nodes"]:
        rows = node.get("closure", {}).get("packings")
        if rows:
            score = sum(Fraction(*row["weight"]) * (len(row["deletions"]) - 1)
                        for row in rows)
            floor = node["id"].count("/c") + ceil(score)
            require(floor >= cert["incumbent"]["cost"], (case, mode, "rank floor"))
            found.add((floor == cert["incumbent"]["cost"],
                       any(row["weight"][1] > 1 for row in rows)))
    require(target in found, (case, mode, found))


def native(out, cases):
    manifest = {}
    for case in cases:
        raw, journal = inputs(case)
        scope = build_trusted_scope(raw, journal)
        result = None
        if len(raw["alphabet"]) <= 12:
            reference = oracle(raw, seconds=120)
            require(reference["status"] == "VERIFIED", (case, reference))
            result = reference["result"]
        path = out / case
        path.mkdir(parents=True, exist_ok=True)
        for label, data in (("raw", canonical(raw)), ("journal", journal),
                            ("trusted", canonical(scope))):
            (path / f"{label}.json").write_bytes(data)
        for mode in ("one", "all"):
            for rank in (False, True):
                name = f"{mode}.v{3 if rank else 2}"
                flags = dict(mode=mode, sparse=True, rank=rank)
                cert, stats = solve(raw, scope, caps=SearchCaps(seconds=30), **flags)
                encoded = canonical(cert)
                require(cert["declared_status"] == "EXHAUSTED", (case, name, stats))
                if not rank:
                    baseline = cert
                if result is not None:
                    require(cert["incumbent"]["cost"] == result["optimum"], (case, name))
                    require(cert["incumbent"]["owner"] in result["optima"], (case, name))
                    if mode == "all":
                        require(cert["optima"] == sorted(result["optima"]), (case, name))
                else:
                    require(cert["incumbent"]["cost"] == baseline["incumbent"]["cost"], (case, name))
                    require(cert["optima"] == baseline["optima"], (case, name))
                if rank:
                    check_active(case, mode, cert)
                elif (M3 / case / f"{mode}.cert.json").exists():
                    require(encoded == (M3 / case / f"{mode}.cert.json").read_bytes(),
                            (case, name, "frozen v2 bytes"))

                replay_options = dict(expected_format=cert["format"], expected_mode=mode,
                                      sparse_exact=True)
                replay = verify_frontier(raw, journal, scope, encoded, **replay_options)
                require(replay["status"] == "VERIFIED", (case, name, replay))
                variants = [("complete", encoded)]
                cap_cases = (
                    ("entries", SearchCaps(entries=1), None),
                    ("work", SearchCaps(work=0), None),
                    ("time", SearchCaps(seconds=0), None),
                    ("frontier", SearchCaps(memory_bytes=0), None),
                    ("index", SearchCaps(), 0),
                )
                for label, caps, index in (cap_cases[:1] if case == "cover" else cap_cases):
                    extra = {} if index is None else dict(index_bytes=index)
                    partial, _ = solve(raw, scope, caps=caps, **flags, **extra)
                    require(partial["declared_status"] == "PARTIAL", (case, name, label))
                    partial_bytes = canonical(partial)
                    resumed, _ = solve(raw, scope, checkpoint=load_checkpoint(path, partial_bytes),
                                       caps=SearchCaps(seconds=30), **flags)
                    require(canonical(resumed) == encoded, (case, name, label, "resume"))
                    if label == "entries":
                        variants.extend([("partial", partial_bytes), ("resumed", canonical(resumed))])
                if rank and case in ("equality", "strict", "fractional") and stats["rank_leaves"]:
                    for limit in range(2, stats["entries"]):
                        partial, partial_stats = solve(raw, scope, caps=SearchCaps(entries=limit),
                                                       **flags)
                        if partial_stats["rank_leaves"] and partial["declared_status"] == "PARTIAL":
                            encoded_partial = canonical(partial)
                            resumed, _ = solve(raw, scope,
                                               checkpoint=load_checkpoint(path, encoded_partial),
                                               **flags)
                            require(canonical(resumed) == encoded, (case, name, "rank resume"))
                            variants.extend([("rank-partial", encoded_partial),
                                             ("rank-resumed", canonical(resumed))])
                            break
                for label, data in variants:
                    if "partial" in label or "resumed" in label:
                        checked = verify_frontier(raw, journal, scope, data, **replay_options)
                        expected = "INCOMPLETE" if "partial" in label else "VERIFIED"
                        require(checked["status"] == expected, (case, name, label, checked))
                        if expected == "INCOMPLETE":
                            require("result" not in checked, (case, name, label, checked))
                    file = path / f"{name}.{label}.json"
                    file.write_bytes(data)
                    manifest[str(file.relative_to(out).as_posix())] = dict(
                        bytes=len(data), sha256=sha256(data).hexdigest(),
                        rank_leaves=stats.get("rank_leaves", 0) if label == "complete" else None)
    (out / "manifest.json").write_bytes(canonical(manifest))


def load_checkpoint(path, data):
    checkpoint = path / "checkpoint.tmp"
    checkpoint.write_bytes(data)
    try:
        return load(checkpoint)
    finally:
        checkpoint.unlink()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--memory-mib", type=int)
    parser.add_argument("--case", action="append", choices=CASES)
    args = parser.parse_args()
    if args.memory_mib is not None:
        import resource

        limit = args.memory_mib * 1024**2
        resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    native(args.output, args.case or CASES)
