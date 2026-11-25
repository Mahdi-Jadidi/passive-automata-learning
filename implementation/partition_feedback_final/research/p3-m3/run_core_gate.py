"""Generate native M3 certificate artifacts and compare with the pinned RGS oracle."""
import argparse
from hashlib import sha256
from pathlib import Path
import sys

from journal_v2_replay import verify_journal
from p3_frontier_verifier import build_trusted_scope, verify_frontier
from p3_rgs12_oracle import oracle
from selector_v2.component_closure import component_closure
from selector_v2.core import Sample
from selector_v2.edr_bb import SearchCaps
from selector_v2.edr_m3 import CROSS_SUPPORT, canonical, load, solve, write_atomic


M2 = Path(__file__).resolve().parent.parent / "p3-m2" / "evidence"


def inputs(case):
    if case == "journal_root":
        raw = dict(alphabet=list("abcdef"), positive=[["a"], ["b"], list("cde")],
                   negative=[list("ab"), list("ecd")])
        sample = Sample.from_input(raw)
        closure = component_closure(sample)
        journal = canonical(dict(version="selector-v2-journal/2", sample_digest=sample.sample_digest,
                                 events=[dict(event="RAW", records=closure["records"])]))
    elif case == "mixed_path":
        raw = dict(alphabet=list("abcde"), positive=[list("abc"), ["d"]], negative=[[]])
        sample = Sample.from_input(raw)
        journal = canonical(dict(version="selector-v2-journal/2", sample_digest=sample.sample_digest,
                                 events=[]))
    else:
        raw_file = M2 / case / "raw.json"
        return raw_file.read_bytes(), (M2 / case / "journal.json").read_bytes()
    return canonical(raw), journal


def require(predicate, message):
    if not predicate:
        raise RuntimeError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--memory-mib", type=int)
    args = parser.parse_args()
    if args.memory_mib is not None:
        import resource
        limit = args.memory_mib * 1024**2
        resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    require(sys.version_info[:3] == (3, 13, 5), "Python 3.13.5 required")
    manifest = dict(python=sys.version.split()[0], optimized=not __debug__,
                    producer_seconds_cap=30, process_address_space_mib=args.memory_mib, cases={})
    for case in ("tiny_choice", "small_choice", "journal_root", "mixed_path"):
        path = args.output / case
        path.mkdir(parents=True, exist_ok=True)
        raw_bytes, journal = inputs(case)
        (path/"raw.json").write_bytes(raw_bytes)
        (path/"journal.json").write_bytes(journal)
        raw = load(path/"raw.json")
        scope = build_trusted_scope(raw, journal)
        write_atomic(path/"trusted.json", scope)
        replay = verify_journal(raw, scope["selector_scope"], journal)
        require(replay["status"] == "VERIFIED", f"{case} journal replay")
        if case == "journal_root":
            require(scope["root_owner"] == [0, 0, 2, 3, 4, 5], "expected checked contraction")
        reference = oracle(raw, seconds=120)
        require(reference["status"] == "VERIFIED", f"{case} RGS oracle")
        write_atomic(path/"rgs.json", reference)
        report = dict(journal_status=replay["status"], root_owner=scope["root_owner"], modes={})
        manifest["cases"][case] = report
        for mode in ("one", "all"):
            kwargs = dict(split_rule=CROSS_SUPPORT, mode=mode)
            complete, stats = solve(raw, scope, caps=SearchCaps(seconds=30), **kwargs)
            pending, partial_stats = solve(raw, scope, caps=SearchCaps(entries=1), **kwargs)
            require(pending["declared_status"] == "PARTIAL", f"{case} one-entry checkpoint")
            write_atomic(path/f"{mode}.partial.json", pending)
            resumed, resume_stats = solve(raw, scope, checkpoint=load(path/f"{mode}.partial.json"),
                                          caps=SearchCaps(seconds=30), **kwargs)
            require(canonical(complete) == canonical(resumed), f"{case}/{mode} resume differs")
            require(complete["declared_status"] == "EXHAUSTED", f"{case}/{mode} not exhausted")
            result = reference["result"]
            require(complete["incumbent"]["cost"] == result["optimum"], f"{case}/{mode} cost")
            require(complete["incumbent"]["owner"] in result["optima"], f"{case}/{mode} owner")
            if mode == "all":
                require(complete["optima"] == sorted(result["optima"]), f"{case} optimum set")
            write_atomic(path/f"{mode}.cert.json", complete)
            proof = (path/f"{mode}.cert.json").read_bytes()
            partial = (path/f"{mode}.partial.json").read_bytes()
            verdicts = dict(
                complete=verify_frontier(raw, journal, scope, proof),
                partial=verify_frontier(raw, journal, scope, partial),
                false_exhausted=verify_frontier(
                    raw, journal, scope, canonical(dict(load(path/f"{mode}.partial.json"),
                                                       declared_status="EXHAUSTED"))),
                byte_cap=verify_frontier(raw, journal, scope, proof, max_proof_bytes=1),
            )
            require(verdicts["complete"]["status"] == "VERIFIED",
                    f"{case}/{mode} certificate: {verdicts['complete']}")
            require(verdicts["complete"]["result"]["optimum"] == result["optimum"],
                    f"{case}/{mode} verifier cost")
            require(verdicts["partial"]["status"] == verdicts["byte_cap"]["status"] == "INCOMPLETE"
                    and verdicts["false_exhausted"]["status"] == "INVALID",
                    f"{case}/{mode} partial semantics: {verdicts}")
            require(all("result" not in verdict for name, verdict in verdicts.items()
                        if name != "complete"), f"{case}/{mode} unresolved result leaked")
            write_atomic(path/f"{mode}.verification.json", verdicts)
            report["modes"][mode] = dict(complete=stats, partial=partial_stats, resumed=resume_stats)
        report["files"] = {file.name: dict(bytes=file.stat().st_size,
                                          sha256=sha256(file.read_bytes()).hexdigest())
                           for file in sorted(path.iterdir())}
        print(case, {mode: data["complete"]["nodes"] for mode, data in report["modes"].items()},
              "RGS partitions", reference["visited"], flush=True)
    write_atomic(args.output/"manifest.json", manifest)


if __name__ == "__main__":
    main()
