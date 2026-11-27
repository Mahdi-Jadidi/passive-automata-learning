"""Replay native M4 certificates at the frozen Review08 verifier pin."""
import argparse
from hashlib import sha256
from pathlib import Path
import sys

from p3_frontier_verifier import build_trusted_scope, verify_frontier
from p3_rgs12_oracle import oracle
from selector_v2.edr_bb import SearchCaps
from selector_v2.edr_m3 import CROSS_SUPPORT, FORMAT_V2, canonical, load, solve as frozen
from selector_v2.edr_m4 import solve


M3 = Path(__file__).resolve().parent.parent / "p3-m3" / "evidence" / "normal"
ARMS = {"dense": {}, "sparse": {"sparse": True}, "join": {"join": True},
        "sparse_join": {"sparse": True, "join": True}}


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def write(path, data):
    path.write_bytes(canonical(data))


def replay(raw, journal, scope, cert, mode):
    return verify_frontier(raw, journal, scope, cert, expected_format=FORMAT_V2,
                           expected_mode=mode, max_work=200_000_000)


def native(output):
    for case in ("tiny_choice", "small_choice", "journal_root", "mixed_path"):
        source = M3 / case
        raw = load(source / "raw.json")
        journal = (source / "journal.json").read_bytes()
        scope = build_trusted_scope(raw, journal)
        reference = oracle(raw, seconds=120)
        require(reference["status"] == "VERIFIED", f"{case} oracle")
        result = reference["result"]
        for mode in ("one", "all"):
            baseline, _ = frozen(raw, scope, mode, split_rule=CROSS_SUPPORT)
            baseline_bytes = canonical(baseline)
            require(baseline_bytes == (source / f"{mode}.cert.json").read_bytes(),
                    f"{case}/{mode} frozen certificate")
            for arm, flags in ARMS.items():
                name = f"{case}/{mode}/{arm}"
                path = output / name
                path.mkdir(parents=True, exist_ok=True)
                complete, stats = solve(raw, scope, mode, caps=SearchCaps(seconds=30), **flags)
                complete_bytes = canonical(complete)
                if not flags.get("join"):
                    require(complete_bytes == baseline_bytes, f"{name} certificate bytes")
                require(complete["declared_status"] == "EXHAUSTED", f"{name} exhausted")
                require(complete["incumbent"]["cost"] == result["optimum"], f"{name} oracle cost")
                require(complete["incumbent"]["owner"] in result["optima"], f"{name} incumbent")
                if mode == "all":
                    require(complete["optima"] == sorted(result["optima"]), f"{name} oracle optima")
                (path / "complete.json").write_bytes(complete_bytes)
                pending, partial_stats = solve(raw, scope, mode, caps=SearchCaps(entries=1), **flags)
                write(path / "partial.json", pending)
                resumed, resume_stats = solve(raw, scope, mode, checkpoint=load(path / "partial.json"),
                                              caps=SearchCaps(seconds=30), **flags)
                write(path / "resumed.json", resumed)
                require((path / "resumed.json").read_bytes() == complete_bytes, f"{name} resume bytes")
                verified = replay(raw, journal, scope, complete_bytes, mode)
                partial = replay(raw, journal, scope, (path / "partial.json").read_bytes(), mode)
                false_complete = replay(raw, journal, scope,
                                        canonical(dict(pending, declared_status="EXHAUSTED")), mode)
                require(verified["status"] == "VERIFIED", f"{name} complete replay {verified}")
                require(partial["status"] == "INCOMPLETE" and "result" not in partial,
                        f"{name} partial replay {partial}")
                require(false_complete["status"] == "INVALID", f"{name} false exhaustion")
                if flags.get("sparse"):
                    capped, cap_stats = solve(raw, scope, mode, index_bytes=0, **flags)
                    require(capped["declared_status"] == "PARTIAL" and cap_stats["exact_checks"] == 1
                            and cap_stats["closed"] == 0, f"{name} scratch cap")
                    recovered, _ = solve(raw, scope, mode, checkpoint=capped, **flags)
                    require(canonical(recovered) == complete_bytes, f"{name} scratch resume")
                if flags.get("join"):
                    fallback, fallback_stats = solve(raw, scope, mode, join_work=0, **flags)
                    require(canonical(fallback) == baseline_bytes and fallback_stats["join_local_caps"],
                            f"{name} join local fallback")
                write(path / "metrics.json", dict(complete=stats, partial=partial_stats,
                                                 resumed=resume_stats, verified=verified))
                print(name, sha256(complete_bytes).hexdigest(), len(complete_bytes), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--memory-mib", type=int)
    args = parser.parse_args()
    require(sys.version_info[:3] == (3, 13, 5), "Python 3.13.5 required")
    if args.memory_mib is not None:
        import resource

        limit = args.memory_mib * 1024**2
        resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    native(args.output)


if __name__ == "__main__":
    main()
