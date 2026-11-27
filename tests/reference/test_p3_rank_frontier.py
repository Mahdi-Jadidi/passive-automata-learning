"""Independent v3 coverage and wire mutation tests."""
import copy
import unittest
from unittest.mock import patch

from p3_frontier_verifier import V3, canonical, verify_frontier
from rgs_oracle import oracle
from test_p3_frontier_verifier import certificate, fixture, minimum_owner


def rank_closure():
    return dict(reason="RANK_COST", version="p3-rank-cost/v1", packings=[
        dict(negative_id="N0", weight=[1, 1], deletions=[
            dict(positive_id="P1", support=[0]),
            dict(positive_id="P0", support=[1]),
        ]),
    ])


def close(cert, path):
    nodes = [node for node in cert["nodes"] if not node["id"].startswith(path + "/")]
    node = next(node for node in nodes if node["id"] == path)
    edge = {key: node[key] for key in ("id", "parent_id", "edge")}
    node.clear()
    node.update(edge, kind="LEAF", closure=rank_closure())
    cert["nodes"] = nodes
    return node["closure"]


class RankFrontierTests(unittest.TestCase):
    def setup_case(self, n, mode):
        alphabet = [str(i) for i in range(n)]
        raw = dict(alphabet=alphabet, positive=[["0"], ["1"]], negative=[["0", "1"]])
        journal, scope = fixture(raw)
        cert = certificate(raw, scope, mode, prune=True)
        cert["format"] = V3
        return raw, journal, scope, cert

    def replay(self, case, *, wire=None, **kw):
        raw, journal, scope, cert = case
        return verify_frontier(raw, journal, scope, canonical(cert) if wire is None else wire,
                               **dict(dict(expected_format=V3, expected_mode=cert["mode"]), **kw))

    def test_exhaustive_rgs_with_rank(self):
        for n in range(3, 9):
            for mode in ("one", "all"):
                with self.subTest(n=n, mode=mode):
                    case = self.setup_case(n, mode)
                    raw, _, _, c = case
                    if mode == "one":
                        close(c, "root")
                    else:
                        close(c, "root/c1")
                        close(c, "root/c" + str(n - 1))
                    truth = oracle(raw)["result"]
                    winners = sorted(list(minimum_owner(p)) for p in truth["optima"])
                    for sparse in (False, True):
                        out = self.replay(case, sparse_exact=sparse)
                        self.assertEqual(out["status"], "VERIFIED", out)
                        self.assertEqual(out["result"]["optimum"], truth["optimum"])
                        self.assertIn(out["result"]["owner"], winners)
                        self.assertEqual(out["result"]["optima"], winners if mode == "all" else [])

    def test_adversarial_witnesses(self):
        mutations = (
            lambda c, w, d: d[1].update(support=[0]),  # Overlap.
            lambda c, w, d: d[0].update(support=[2]),  # Stale after 0 == 2.
            lambda c, w, d: d[0].update(support=[True]),
            lambda c, w, d: d[0].update(support=[0, 0]),
            lambda c, w, d: d[0].update(support=[]),
            lambda c, w, d: d[0].update(positive_id="P0"),
            lambda c, w, d: w.update(negative_id="N00"),
            lambda c, w, d: w.update(weight=[2, 2]),
            lambda c, w, d: w.update(weight=[1, 2**32]),
            lambda c, w, d: w.update(weight=[1, 0]),
            lambda c, w, d: w.update(weight=[0, 2]),
            lambda c, w, d: w.update(weight=[True, 1]),
            lambda c, w, d: w.update(weight=[0, 1]),  # Valid weight, insufficient floor.
            lambda c, w, d: c.update(incumbent=None),
            lambda c, w, d: c["incumbent"].update(cost=2),
            lambda c, w, d: c["incumbent"].update(owner=[0, 0, 0]),
            lambda c, w, d: c["incumbent"].update(owner=[0, 1, 0]),  # Incompatible.
            lambda c, w, d: c["nodes"][-1].update(closure={"reason": "UNKNOWN"}),
        )
        for mutate in mutations:
            with self.subTest(mutation=mutate.__code__.co_firstlineno):
                case = self.setup_case(3, "all")
                closure = close(case[3], "root/c1")
                row = closure["packings"][0]
                mutate(case[3], row, row["deletions"])
                out = self.replay(case)
                self.assertEqual(out["status"], "INVALID", out)
                self.assertNotIn("result", out)

    def test_binding_rationals_and_partial(self):
        case = self.setup_case(3, "one")
        cert = case[3]
        closure = close(cert, "root")
        row = closure["packings"][0]
        row["weight"] = [1, 3]
        closure["packings"].append(copy.deepcopy(row))
        self.assertEqual(self.replay(case)["status"], "VERIFIED")  # ceil(2/3) == 1.
        self.assertEqual(self.replay(case, expected_mode="all")["status"], "INVALID")
        for binding in ({"expected_format": None}, {"expected_mode": None}):
            self.assertEqual(self.replay(case, **binding)["status"], "INVALID")
        cert["mode"] = "all"
        self.assertEqual(self.replay(case)["reason"], "invalid rank cutoff")
        cert["mode"] = "one"
        closure["packings"].extend([copy.deepcopy(row), copy.deepcopy(row)])
        self.assertEqual(self.replay(case)["reason"], "rank capacity exceeded")
        closure["packings"] = [row]
        wire = canonical(cert).replace(b'"weight":[1,3]', b'"weight":[1,' + b'9'*10000 + b']')
        self.assertEqual(self.replay(case, wire=wire)["reason"], "oversized v3 integer")
        for version in ("p3-region-frontier/v1", "p3-region-frontier/v2"):
            cert["format"] = version
            self.assertEqual(self.replay(case, expected_format=version)["status"], "INVALID")
        case = self.setup_case(3, "all")
        close(case[3], "root/c1")
        case[3]["nodes"][-1]["closure"] = {"reason": "UNKNOWN"}
        case[3].update(declared_status="PARTIAL", optima=[])
        self.assertEqual(self.replay(case)["reason"], "unresolved frontier")

    def test_deletes_whole_class_and_preserves_token_order(self):
        raw = dict(alphabet=["0", "1", "2"],
                   positive=[["0", "2"], ["1"]], negative=[["0", "2", "1"]])
        journal, scope = fixture(raw)
        cert = certificate(raw, scope, "all", prune=True)
        cert["format"] = V3
        close(cert, "root/c1")
        case = raw, journal, scope, cert
        out = self.replay(case)
        self.assertEqual(out["status"], "VERIFIED", out)
        truth = oracle(raw)["result"]
        self.assertEqual(out["result"]["optima"],
                         sorted(list(minimum_owner(p)) for p in truth["optima"]))
        # The retained symbols have equal counts but different original order.
        raw["negative"] = [["2", "0", "1"]]
        journal, scope = fixture(raw)
        cert = certificate(raw, scope, "one", prune=True)
        cert["format"] = V3
        out = self.replay((raw, journal, scope, cert))
        self.assertEqual(out["status"], "VERIFIED", out)
        close(cert, "root")
        out = self.replay((raw, journal, scope, cert))
        self.assertEqual(out["reason"], "false rank deletion residue")

    def test_cumulative_limits(self):
        case = self.setup_case(3, "all")
        first = close(case[3], "root/c1")
        close(case[3], "root/c2")
        self.assertEqual(self.replay(case)["status"], "VERIFIED")
        for target, limit, reason in (
            ("RANK_ENTRY_LIMIT", 7, "rank structural entry limit"),
            ("RANK_BYTE_LIMIT", len(canonical(first))*2 - 1, "rank structural byte limit"),
        ):
            with patch("p3_frontier_verifier." + target, limit):
                self.assertEqual(self.replay(case)["reason"], reason)
        capped = self.replay(case, max_entries=7)
        self.assertEqual(capped["status"], "INCOMPLETE", capped)
        self.assertEqual(capped["reason"], "entry cap")
        self.assertNotIn("result", capped)
