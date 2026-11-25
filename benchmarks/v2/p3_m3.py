"""Run the M3 pair or its prerequisite M2 audit on standard Linux profiles."""
import argparse
import json
from pathlib import Path

from p3_harness import load_manifest
from p3_native import CONFIG, MANIFEST, run_case

JOURNAL_CASE = "nonempty_root"
JOURNAL_RAW = {
    "alphabet": ["a", "b", "c", "d"],
    "positive": [["a", "b"], ["c", "d"]],
    "negative": [["b", "a"], ["a", "b", "c"]],
}
JOURNAL_CODE = """
import json
from pathlib import Path
import sys

sys.path.insert(0, sys.argv[1])
from independent_replay import sample_data
from p3_frontier_verifier import canonical

raw = json.loads(Path(sys.argv[2]).read_bytes())
n, positives, negatives, digest = sample_data(raw)
identity = list(range(n))
owner = identity[:]
facts, edges = [], []
for i, negative in enumerate(negatives):
    hits = []
    for g in identity:
        target = tuple(a for a in negative if a != g)
        for j, positive in enumerate(positives):
            if tuple(a for a in positive if a != g) == target:
                hits.append((g, j))
                facts.append(dict(negative=i, group=g, positive=j))
                break
    if hits:
        a, j = hits[0]
        for b, k in hits[1:]:
            if owner[a] != owner[b]:
                lo, hi = sorted((owner[a], owner[b]))
                owner = [lo if g == hi else g for g in owner]
                edges.append(dict(negative=i, a=a, positive_a=j, b=b, positive_b=k))
record = dict(version="selector-v2/1", sample_digest=digest, origin="RAW",
              kind="COMPONENT_EPOCH", payload=dict(epoch=0, owner=identity,
              facts=facts, edges=edges, result_owner=owner, state="EXHAUSTED", cursor=None))
journal = dict(version="selector-v2-journal/2", sample_digest=digest,
               events=[dict(event="RAW", records=[record])])
Path(sys.argv[3]).write_bytes(canonical(journal))
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", required=True, choices=(*load_manifest(MANIFEST), JOURNAL_CASE))
    parser.add_argument("--memory-mib", required=True, type=int, choices=(512, 1536))
    parser.add_argument("--producer-root", type=Path, required=True)
    parser.add_argument("--verifier-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--m3-config", type=Path)
    parser.add_argument("--m3-producer-root", type=Path)
    parser.add_argument("--m3-verifier-root", type=Path)
    parser.add_argument("--audit", action="store_true")
    args = parser.parse_args()
    m3 = (args.m3_config, args.m3_producer_root, args.m3_verifier_root)
    if any(m3) and not all(m3):
        parser.error("the M3 config and both source checkouts must be supplied together")
    if bool(args.m3_config) == args.audit:
        parser.error("select either the M2 cumulative audit or paired M3")
    if args.m3_config:
        base = json.loads(CONFIG.read_bytes())
        candidate = json.loads(args.m3_config.read_bytes())
        if any(candidate[key] != base[key] for key in ("limits", "verifier", "scope")):
            parser.error("paired runs require the frozen M2 budgets and verifier/scope interface")
        old_flags, new_flags = base["producer"], candidate["producer"]
        if new_flags[:len(old_flags)] != old_flags or len(new_flags) <= len(old_flags):
            parser.error("M3 must append its documented opt-in flags to the M2 command")
    args.experiment = True
    output = args.output.resolve()
    if args.case == JOURNAL_CASE:
        output.mkdir(parents=True)
        args.fixture = output / "journal-input.json"
        args.fixture.write_bytes(json.dumps(JOURNAL_RAW, separators=(",", ":")).encode())
        args.journal_code = JOURNAL_CODE
        args.audit = False
    args.output, args.config = output / "m2", CONFIG
    baseline = run_case(args)
    candidate = None
    if args.m3_config:
        args.output, args.config = output / "m3", args.m3_config
        args.producer_root, args.verifier_root = args.m3_producer_root, args.m3_verifier_root
        candidate = run_case(args)
        for name in ("raw", "journal", "scope"):
            if baseline[name] != candidate[name]:
                raise ValueError(f"paired {name} differs")
        for run in candidate["runs"]:
            proof = run["phases"]["producer-1"]
            if proof.get("certificate") and proof["proof_format"] != "p3-region-frontier/v2":
                raise ValueError("M3 did not produce the opt-in wire format")
    for result in (baseline, candidate):
        if result is None:
            continue
        if len(result["runs"]) != 4 or any(
            phase["status"] == "INVALID" for run in result["runs"] for phase in run["phases"].values()
        ):
            raise ValueError("missing variants or independently rejected evidence")
        if args.case == JOURNAL_CASE and any(
            run["status"] != "VERIFIED" or run["normal_optimized_parity"] != "MATCH" or
            run["checkpoint_resume"] not in ("MATCH", "NOT NEEDED")
            for run in result["runs"]
        ):
            raise ValueError("nonempty journal experiment requires verified completion and parity")


if __name__ == "__main__":
    main()
