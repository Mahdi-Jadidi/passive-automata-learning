"""Audit retained rank fixtures against fresh producer output and literal RGS."""
import argparse
from collections import Counter
from pathlib import Path

from p3_frontier_verifier import build_trusted_scope, canonical, need, parse, verify_frontier
from p3_m3_artifact_replay import fingerprint
from p3_rgs12_oracle import oracle


def audit(retained, normal, optimized):
    manifest = parse((retained / "manifest.json").read_bytes(), 2**20)
    for output in (normal, optimized):
        need((output / "manifest.json").read_bytes() ==
             (retained / "manifest.json").read_bytes(), "producer manifest mismatch")
    checkpoints = set()
    count = 0
    for case in ("equality", "strict", "fractional"):
        inputs = []
        for name in ("raw", "journal", "trusted"):
            relative = Path(case) / (name + ".json")
            data = (retained / relative).read_bytes()
            need(data == (normal / relative).read_bytes() ==
                 (optimized / relative).read_bytes(), f"input bytes: {relative}")
            inputs.append(data)
        raw, journal, scope = inputs
        need(canonical(build_trusted_scope(raw, journal)) == scope, "scope mismatch")
        census = oracle(parse(raw, 2**20), seconds=120)
        need(census["status"] == "VERIFIED", str(census))
        truth = census["result"]
        for mode in ("one", "all"):
            for version in (2, 3):
                stem = f"{mode}.v{version}."
                complete = (retained / case / (stem + "complete.json")).read_bytes()
                variants = ["complete", "partial", "resumed"]
                if (retained / case / (stem + "rank-partial.json")).exists():
                    variants += ["rank-partial", "rank-resumed"]
                for variant in variants:
                    path = Path(case) / (stem + variant + ".json")
                    cert = (retained / path).read_bytes()
                    need(cert == (normal / path).read_bytes() ==
                         (optimized / path).read_bytes(), f"certificate bytes: {path}")
                    pin = fingerprint(cert)
                    need(all(manifest[path.as_posix()][key] == value
                             for key, value in pin.items() if key in ("bytes", "sha256")), f"manifest pin: {path}")
                    replay = verify_frontier(raw, journal, scope, cert, sparse_exact=True,
                                             expected_format=f"p3-region-frontier/v{version}",
                                             expected_mode=mode)
                    closures = Counter(node["closure"]["reason"]
                                       for node in parse(cert, 2**20)["nodes"]
                                       if node["kind"] == "LEAF")
                    if "partial" in variant:
                        need(replay["status"] == "INCOMPLETE" and "result" not in replay
                             and replay["reason"] == "unresolved frontier", str(replay))
                        if variant == "rank-partial":
                            need(version == 3 and closures["RANK_COST"] > 0,
                                 "checkpoint lacks checked rank closure")
                            checkpoints.add((case, mode))
                    else:
                        need(cert == complete and replay["status"] == "VERIFIED", str(replay))
                        result = replay["result"]
                        need(result["optimum"] == truth["optimum"] and
                             result["owner"] in truth["optima"] and
                             result["optima"] == (truth["optima"] if mode == "all" else []),
                             f"literal RGS mismatch: {path}")
                    count += 1
                    yield dict(path=path.as_posix(), pin=pin, closures=dict(closures),
                               inputs=[fingerprint(data) for data in inputs], replay=replay)
    need(count == len(manifest) == 40, "retained matrix coverage")
    need(checkpoints == {("equality", "all"), ("strict", "all")},
         "rank-bearing checkpoint coverage")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("retained", "normal", "optimized"):
        parser.add_argument(name, type=Path)
    for record in audit(**vars(parser.parse_args())):
        print(canonical(record).decode("ascii"), flush=True)
