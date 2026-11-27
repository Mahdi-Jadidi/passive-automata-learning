"""Producer-only fixture export. Run in a separate process at the documented pins."""
import argparse
from pathlib import Path

from selector_v2.feedback_aefc import prepare
from selector_v2.integration.test_feedback_aefc import CROSS, NAMED, STITCH, history, owners
from selector_v2.integration.test_roundtrip import response
from selector_v2.schema import canonical


def export(directory):
    export_controls(directory)
    cases = (
        ("named", NAMED, [(q, 0) for q in STITCH], [0, 0, 0, 3]),
        ("cross-id", CROSS, [(STITCH[0] + [4], 1), (STITCH[1] + [4], 0),
                            (STITCH[2] + [4], 0), ([0, 0, 2, 3, 0], 2)], [0, 0, 0, 3, 4]),
    )
    for name, raw, queries, target in cases:
        journal = history(raw, queries).export()
        status, snapshot = prepare(raw, journal)
        if status != "READY":
            raise RuntimeError((name, status))
        path = directory / name
        path.mkdir(parents=True, exist_ok=True)
        proofs = []
        for owner in owners(len(raw["alphabet"])):
            direct, _ = snapshot.prove(owner, containment_only=True)
            verdict, proof = snapshot.prove(owner)
            if direct not in ("UNKNOWN", "PROVEN_NO") or verdict not in ("UNKNOWN", "PROVEN_NO"):
                raise RuntimeError((name, owner, direct, verdict))
            proofs.append(dict(owner=owner, containment=direct, status=verdict,
                               sidecar_hex=proof.hex() if proof is not None else None))
        verdict, sidecar = snapshot.prove(target)
        if verdict != "PROVEN_NO":
            raise RuntimeError((name, target, verdict))
        artifacts = {"raw": canonical(raw), "journal": journal, "target": canonical(target),
                     "sidecar": sidecar, "matrix": canonical(proofs)}
        for label, content in artifacts.items():
            (path / (label + ".json")).write_bytes(content)


def export_controls(directory):
    bounded_raw = dict(alphabet=list("ab"), positive=[list("aba")], negative=[list("aab")])
    bounded = history(bounded_raw, [([0, 1], 0)])
    request = bounded.register([0, 0], "bounded", "bounded", capacities=[1])
    wire = canonical(response(request, "BOUNDED_NO", "bounded", exact=True))
    if bounded.ingest("bounded", "bounded", wire) != "BOUNDED_NO":
        raise RuntimeError("bounded control rejected")
    mixed_raw = dict(alphabet=list("abcd"), positive=[list("abcd")],
                     negative=list(map(list, ("bacd", "abdc"))))
    mixed = history(mixed_raw, [([0, 0, 2, 3], 1), ([0, 1, 2, 2], 0)])
    for name, raw, ledger in (("bounded", bounded_raw, bounded), ("mixed", mixed_raw, mixed)):
        path = directory / name
        path.mkdir(parents=True, exist_ok=True)
        (path / "raw.json").write_bytes(canonical(raw))
        (path / "journal.json").write_bytes(ledger.export())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    export(parser.parse_args().directory)
