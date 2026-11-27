"""Replay retained native producer bytes with independent literal RGS comparison."""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from p3_aefc_verifier import verify_aefc
from p3_frontier_verifier import canonical
from rgs_oracle import compatible, rgs, validate

DATA = Path(__file__).resolve().parents[2] / "research/audit/m5a-native"


def fixture(name):
    return tuple((DATA / name / (label + ".json")).read_bytes()
                 for label in ("raw", "journal", "target", "sidecar", "matrix"))


def literal(raw, owner):
    _, positives, negatives = validate(json.loads(raw))
    return not compatible(owner, positives, negatives)


def containment(journal, owner):
    """Direct zero coverage control over observations checked by the verifier."""
    requests = {}
    zeros = {}
    for event in json.loads(journal)["events"]:
        if event["event"] == "REGISTER":
            request = event["registered"]["request"]
            requests[request["attempt_id"]] = request["owner"]
        elif event["event"] == "OBSERVE" and event["status"] == "PROJECTION_NO":
            source = requests[event["attempt_id"]]
            for row in event["records"][0]["payload"]["feedback"]["tables"]:
                region = {i for i, g in enumerate(source) if g == row["group"]}
                for y in row["anonymous_zeros"] + [z["negative"] for z in row["named_zeros"]]:
                    zeros.setdefault(y, []).append(region)
    blocks = [{i for i, g in enumerate(owner) if g == group} for group in sorted(set(owner))]
    return any(all(any(block <= region for region in regions) for block in blocks)
               for regions in zeros.values())


class AefcTests(unittest.TestCase):
    def test_native_matrix(self):
        for case, expected in (("named", (15, 10, 4, 5)), ("cross-id", (52, 37, 9, 10))):
            with self.subTest(case=case):
                raw, journal, target, sidecar, matrix = fixture(case)
                target = json.loads(target)
                self.assertFalse(containment(journal, target))
                self.assertTrue(literal(raw, target))
                result = verify_aefc(raw, journal, sidecar)
                self.assertEqual(result, dict(status="VERIFIED", result=dict(
                    verdict="STRUCTURAL_NO", owner=target, negative_id="N0")))
                proof = json.loads(sidecar)
                self.assertEqual(proof["blocks"][0]["kind"], "ATOM_MATCH")
                if case == "cross-id":
                    self.assertEqual([e["to"] for e in proof["blocks"][0]["paths"][3]["edges"]],
                                     ["N1", "P0"])
                n, _, _ = validate(json.loads(raw))
                remaining = {tuple(labels.index(label) for label in labels) for labels in rgs(n)}
                counts = Counter()
                for row in json.loads(matrix):
                    owner = row["owner"]
                    remaining.remove(tuple(owner))
                    no = literal(raw, owner)
                    direct = containment(journal, owner)
                    self.assertEqual(row["containment"], "PROVEN_NO" if direct else "UNKNOWN")
                    counts.update(targets=1, literal_no=no, containment=direct)
                    if row["status"] == "PROVEN_NO":
                        proposed = bytes.fromhex(row["sidecar_hex"])
                        replay = verify_aefc(raw, journal, proposed)
                        self.assertEqual(replay["status"], "VERIFIED", replay)
                        self.assertEqual(replay["result"]["owner"], owner)
                        self.assertTrue(no)
                        if owner == target:
                            self.assertEqual(proposed, sidecar)
                        counts.update(named=1)
                    else:
                        self.assertEqual(row["status"], "UNKNOWN")
                        self.assertIsNone(row["sidecar_hex"])
                        self.assertFalse(direct)
                self.assertFalse(remaining)
                self.assertEqual(tuple(counts[k] for k in
                                 ("targets", "literal_no", "containment", "named")), expected)

    def check_status(self, status, raw, journal, proof, **limits):
        result = verify_aefc(raw, journal, proof, **limits)
        self.assertEqual(result["status"], status, result)
        self.assertNotIn("result", result)

    def test_hostile_sidecars(self):
        raw, journal, _, sidecar, _ = fixture("cross-id")
        original = json.loads(sidecar)
        for name, mutate in (
            ("format", lambda p, b, a, e: p.update(format="feedback-aefc-named/v2")),
            ("sample", lambda p, b, a, e: p.update(sample_digest="0" * 64)),
            ("journal", lambda p, b, a, e: p.update(journal_sha256="0" * 64)),
            ("owner", lambda p, b, a, e: p["owner"].__setitem__(1, True)),
            ("empty block list", lambda p, b, a, e: p["blocks"].clear()),
            ("missing block", lambda p, b, a, e: p["blocks"].pop()),
            ("block order", lambda p, b, a, e: p["blocks"].reverse()),
            ("wrong group", lambda p, b, a, e: b.update(group=False)),
            ("missing atom", lambda p, b, a, e: b["paths"].pop(3)),
            ("atom order", lambda p, b, a, e: b["paths"].reverse()),
            ("wrong atom", lambda p, b, a, e: a.update(atom=[1, 0])),
            ("extra atom", lambda p, b, a, e: b["paths"].append(a)),
            ("empty path", lambda p, b, a, e: a["edges"].clear()),
            ("register cited", lambda p, b, a, e: e.update(event=0)),
            ("Boolean index", lambda p, b, a, e: e.update(event=True)),
            ("missing source group", lambda p, b, a, e: e.update(group=1)),
            ("source lacks atom", lambda p, b, a, e: e.update(group=2)),
            ("wrong positive", lambda p, b, a, e: b.update(positive_id="P1")),
            ("mixed negative", lambda p, b, a, e: p.update(negative_id="N1")),
            ("noncanonical ID", lambda p, b, a, e: e.update(to="N01")),
            ("unlicensed duplicate-word equality", lambda p, b, a, e: e.update(event=1)),
            ("broken chain", lambda p, b, a, e: a["edges"][1].update({"from": "N0"})),
            ("repeated vertex", lambda p, b, a, e: a["edges"].insert(1, {
                "event": 7, "group": 0, "from": "N1", "to": "N0"})),
            ("anonymous guessed positive", lambda p, b, a, e: a.update(edges=[
                {"event": 1, "group": 0, "from": "N0", "to": "P0"}])),
            ("containment lacks target", lambda p, b, a, e: p["blocks"][1].update(source_group=0)),
            ("unknown field", lambda p, b, a, e: e.update(label=0)),
        ):
            with self.subTest(name=name):
                proof = deepcopy(original)
                block = proof["blocks"][0]
                path = block["paths"][3]
                mutate(proof, block, path, path["edges"][0])
                self.check_status("INVALID", raw, journal, canonical(proof))
        for mutated in (sidecar + b" ", b'{"format":0,' + sidecar[1:], b'{"x":NaN}',
                        b'{"x":1e999}', b"\xff", b"[]"):
            self.check_status("INVALID", raw, journal, mutated)

    def test_native_bounded_and_mixed_controls(self):
        for case, owner, references in (
            ("bounded", [0, 0], [(0, 3, 0)]),
            ("mixed", [0, 0, 2, 2], [(0, 1, 0), (2, 3, 2)]),
        ):
            with self.subTest(case=case):
                raw, journal = [(DATA / case / (label + ".json")).read_bytes()
                                for label in ("raw", "journal")]
                self.assertFalse(literal(raw, owner))
                self.assertFalse(containment(journal, owner))
                for negative in range(len(json.loads(raw)["negative"])):
                    proof = dict(format="feedback-aefc-named/v1",
                                 sample_digest=json.loads(journal)["sample_digest"],
                                 journal_sha256=sha256(journal).hexdigest(),
                                 owner=owner, negative_id=f"N{negative}", blocks=[
                                     dict(group=group, kind="ZERO_CONTAINMENT", event=event,
                                          source_group=source)
                                     for group, event, source in references])
                    result = verify_aefc(raw, journal, canonical(proof))
                    self.assertEqual(result, dict(status="INVALID", reason={
                        "bounded": "source is not a projection NO observation",
                        "mixed": "unlicensed zero containment",
                    }[case]))

    def test_forged_journal_and_caps(self):
        raw, journal, _, sidecar, _ = fixture("named")
        corrupt = json.loads(journal)
        corrupt["events"][1]["wire_sha256"] = "0" * 64
        forged_journal = canonical(corrupt)
        forged = json.loads(sidecar)
        forged["journal_sha256"] = sha256(forged_journal).hexdigest()
        self.check_status("INVALID", raw, forged_journal, canonical(forged))
        for label in ("max_work", "seconds", "max_entries", "max_depth", "max_exact_checks",
                      "max_proof_bytes", "max_raw_bytes", "max_journal_bytes"):
            with self.subTest(label=label):
                self.check_status("INCOMPLETE", raw, journal, sidecar, budgets={label: 0})
        self.check_status("INCOMPLETE", raw, journal, sidecar, max_index_entries=0)
        for label, limit in (("MAX_BYTES", len(sidecar) - 1), ("MAX_BLOCKS", 1),
                             ("MAX_PATHS", 5), ("MAX_EDGES", 5)):
            with self.subTest(label=label), patch("p3_aefc_verifier." + label, limit):
                self.check_status("INVALID", raw, journal, sidecar)


if __name__ == "__main__":
    unittest.main()
