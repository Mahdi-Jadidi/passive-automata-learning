"""Produce and independently replay native v2 certificates and capped scale runs."""
import argparse
import gzip
from hashlib import sha256
from pathlib import Path
from time import monotonic

from p3_frontier_verifier import build_trusted_scope, verify_frontier
from p3_rgs12_oracle import oracle
from profile_pipeline import phase
from profile_raw import FIXTURES
from run_native import M3, replay, require, write
from selector_v2.core import Sample
from selector_v2.edr_bb import SearchCaps
from selector_v2.edr_m3 import FORMAT_V2, canonical, load
from selector_v2.edr_m4 import solve as baseline
from selector_v2.scale_search import solve


ARMS = {
    "dense": {},
    "sparse": {"sparse": True},
    "compact": {"compact": True},
    "compact-target": {"compact": True, "targeted": True},
    "dense-target": {"targeted": True},
}
CAPS = SearchCaps(25, 10_000_000, 2_000_000, 67_108_864)


def native(fixtures, output):
    for case in ("tiny_choice", "small_choice", "mixed_path", "journal_root", "cover_path_8"):
        if case == "cover_path_8":
            raw = load(fixtures / (case + ".json"))
            journal = canonical(dict(version="selector-v2-journal/2",
                                     sample_digest=Sample.from_input(raw).sample_digest, events=[]))
            reference = None
        else:
            source = M3 / case
            raw = load(source / "raw.json")
            journal = (source / "journal.json").read_bytes()
            # The pinned RGS12 result enumerated all 4,213,597 partitions.
            # Reuse it for small_choice to keep this producer gate bounded.
            reference = load(source / "rgs.json") if case == "small_choice" else oracle(raw)
            require(reference["status"] == "VERIFIED", case)
        scope = build_trusted_scope(raw, journal)
        inputs = output / case
        inputs.mkdir(parents=True)
        write(inputs / "raw.json", raw)
        (inputs / "journal.json").write_bytes(journal)
        write(inputs / "scope.json", scope)
        for mode in ("one", "all"):
            frozen, _ = baseline(raw, scope, mode, caps=CAPS)
            for arm, flags in ARMS.items():
                name = f"{case}/{mode}/{arm}"
                path = output / name
                path.mkdir(parents=True)
                cert, stats = solve(raw, scope, mode, caps=CAPS, **flags)
                require(cert["declared_status"] == "EXHAUSTED", f"{name}: {stats}")
                if not flags.get("targeted"):
                    require(canonical(cert) == canonical(frozen), name + " frozen parity")
                if reference is not None:
                    result = reference["result"]
                    require(cert["incumbent"]["cost"] == result["optimum"], name)
                    require(cert["incumbent"]["owner"] in result["optima"], name)
                    if mode == "all":
                        require(cert["optima"] == sorted(result["optima"]), name)
                require(cert["incumbent"]["cost"] == frozen["incumbent"]["cost"], name)
                if mode == "all":
                    require(cert["optima"] == frozen["optima"], name + " all optima")
                write(path / "complete.json", cert)
                emitted = (path / "complete.json").read_bytes()
                verified = replay(raw, journal, scope, emitted, mode)
                require(verified["status"] == "VERIFIED", f"{name}: {verified}")
                for entries in (1, 5):
                    pending, _ = solve(raw, scope, mode, caps=SearchCaps(entries=entries), **flags)
                    if pending["declared_status"] == "EXHAUSTED":
                        require(canonical(pending) == emitted, name)
                        continue
                    partial = path / f"partial-{entries}.json"
                    write(partial, pending)
                    verdict = replay(raw, journal, scope, partial.read_bytes(), mode)
                    require(verdict["status"] == "INCOMPLETE", f"{name}: {verdict}")
                    resumed, _ = solve(raw, scope, mode, checkpoint=load(partial), caps=CAPS, **flags)
                    write(path / f"resumed-{entries}.json", resumed)
                    require((path / f"resumed-{entries}.json").read_bytes() == emitted, name)
                write(path / "metrics.json", dict(search=stats, replay=verified))
                print(name, sha256(emitted).hexdigest(), len(emitted), flush=True)


def contracted(source, retained, output, arm, mode, stage):
    import resource

    case = source.stem
    if stage == "prepare":
        output.mkdir(parents=True)
        require(sha256(source.read_bytes()).hexdigest() == FIXTURES[case], "raw pin")
        raw = load(source)
        raw_stats = phase("raw", source, output, mode)
        journal = (output / "journal.json").read_bytes()
        expected_journal, = retained.glob(case + "-journal-*.json.gz")
        expected_scope, = retained.glob(case + "-scope-*.json.gz")
        require(journal == gzip.decompress(expected_journal.read_bytes()), "journal parity")
        scope = build_trusted_scope(raw, journal, budgets=dict(seconds=25, max_work=200_000_000))
        require(canonical(scope) == gzip.decompress(expected_scope.read_bytes()), "scope parity")
        require(len(set(scope["root_owner"])) == len(raw["alphabet"]) - 1, "expected contraction")
        write(output / "scope.json", scope)
        write(output / "root-metrics.json", raw_stats)
        return
    raw = load(source)
    scope = load(output / "scope.json")
    if stage == "replay":
        proof = (output / "certificate.json").read_bytes()
        verdict = verify_frontier(raw, (output / "journal.json").read_bytes(), scope, proof,
                                  expected_format=FORMAT_V2, expected_mode=mode,
                                  seconds=25, max_work=200_000_000)
        write(output / "replay.json", verdict)
        require(verdict["status"] in ("INCOMPLETE", "VERIFIED"), verdict)
        return
    started = monotonic()
    try:
        cert, stats = solve(raw, scope, mode, caps=CAPS, **ARMS[arm])
    except MemoryError:
        cert, stats = None, dict(status="INCOMPLETE", stop_reason="MEMORY_ERROR")
    wall = monotonic() - started
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    metrics = dict(search=stats, wall_seconds=wall, peak_rss_kib=rss)
    if cert is not None:
        write(output / "certificate.json", cert)
        blob = (output / "certificate.json").read_bytes()
        metrics.update(certificate_sha256=sha256(blob).hexdigest(), certificate_bytes=len(blob))
    write(output / "metrics.json", metrics)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", type=Path, required=True)
    parser.add_argument("--retained", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--memory-mib", type=int)
    parser.add_argument("--case")
    parser.add_argument("--mode", choices=("one", "all"), default="one")
    parser.add_argument("--arm", choices=ARMS, default="compact")
    parser.add_argument("--stage", choices=("prepare", "search", "replay"))
    args = parser.parse_args()
    if args.memory_mib is not None:
        import resource

        limit = args.memory_mib * 1024**2
        resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    if args.case:
        contracted(args.fixtures / (args.case + ".json"), args.retained, args.output,
                   args.arm, args.mode, args.stage)
    else:
        native(args.fixtures, args.output)


if __name__ == "__main__":
    main()
