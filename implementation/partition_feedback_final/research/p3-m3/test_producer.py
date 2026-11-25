"""M3 producer, literal region checks, and checkpoint accounting regressions."""
import copy
from itertools import product
from pathlib import Path
import unittest

from selector_v2.edr_bb import RollbackDSU, SearchBudget, SearchCaps
from selector_v2.edr_cross import ALL_PAIRS, CROSS_SUPPORT, CrossPairs, CrossPrefix
from selector_v2.edr_m3 import canonical, load, solve
from selector_v2.edr_search import solve as solve_v1
from test_edr_search import fixture
from p3_frontier_verifier import verify_frontier
from rgs_oracle import oracle


EVIDENCE = Path(__file__).resolve().parent.parent / "p3-m2" / "evidence"


def run(raw, scope, mode="all", **kwargs):
    return solve(raw, scope, mode, split_rule=CROSS_SUPPORT, **kwargs)


class ProducerTests(unittest.TestCase):
    def test_v2_raw_corner_cases(self):
        fixtures = (
            dict(alphabet=list("abcd"), positive=[list("bc"), ["a"], ["a"]],
                 negative=[list("abc"), list("abc")]),
            dict(alphabet=list("ab"), positive=[[]], negative=[[]]),
            dict(alphabet=list("ab"), positive=[], negative=[[]]),
            dict(alphabet=list("ab"), positive=[[]], negative=[]),
            dict(alphabet=[], positive=[], negative=[]),
            dict(alphabet=[], positive=[], negative=[[]]),
            dict(alphabet=[], positive=[[]], negative=[[]]),
        )
        for raw in fixtures:
            journal, scope = fixture(raw)
            expected = oracle(raw)["result"]
            for mode in ("one", "all"):
                cert, _ = run(raw, scope, mode)
                result = verify_frontier(raw, journal, scope, canonical(cert))
                self.assertEqual(result["status"], "VERIFIED", result)
                self.assertEqual(result["result"]["optimum"], expected["optimum"])
                if mode == "all":
                    self.assertEqual(cert["optima"],
                                     sorted([p.index(label) for label in p]
                                            for p in expected["optima"]))

    def test_local_discovery_cap_falls_back(self):
        raw = dict(alphabet=list("abc"), positive=[["a"] * 4100 + ["b"]],
                   negative=[["b"] + ["a"] * 4100])
        journal, scope = fixture(raw)
        cert, stats = run(raw, scope, "one")
        self.assertEqual(stats["witness_local_caps"], 1)
        self.assertEqual(cert["nodes"][0]["rule"], ALL_PAIRS)
        result = verify_frontier(raw, journal, scope, canonical(cert))
        self.assertEqual(result["status"], "VERIFIED", result)
        self.assertEqual(result["result"]["optimum"], 1)

    def test_lazy_family_and_prefixes(self):
        budget = SearchBudget()
        s, t = (0, 3, 6), (1, 2, 5, 7)
        family = CrossPairs.build(s, t, budget)
        pairs = sorted(tuple(sorted(p)) for p in product(s, t))
        self.assertEqual([family.pair_at(j,budget) for j in range(family.count)], pairs)
        dsu = RollbackDSU(8, (0, 0, 2, 3, 3, 3, 0, 3))
        for j, pair in enumerate(pairs):
            self.assertEqual(CrossPrefix(family, pair).violated(dsu, None, budget),
                             any(dsu.find(a) == dsu.find(b) for a,b in pairs[:j]))
        family = CrossPairs.build(tuple(range(0, 100_000, 2)),
                                  tuple(range(1, 100_000, 2)), budget)
        self.assertEqual(family.count, 2_500_000_000)
        self.assertEqual(len(family.rows), 100_000)
        self.assertEqual(family.pair_at(family.count - 1, budget), (99998, 99999))

    def test_mixed_path_and_exhaustive_entry_restart(self):
        raw = dict(alphabet=list("abcde"), positive=[list("abc"), ["d"]], negative=[[]])
        _, scope = fixture(raw)
        complete, _ = run(raw, scope)
        nodes = {q["id"]: q for q in complete["nodes"]}
        self.assertTrue(any(q.get("rule") == CROSS_SUPPORT and
                            nodes[q["parent_id"]]["rule"] == ALL_PAIRS
                            for q in nodes.values() if q["parent_id"]))
        reference = oracle(raw)["result"]
        self.assertEqual(complete["incumbent"]["cost"], reference["optimum"])
        self.assertEqual(complete["optima"],
                         sorted([p.index(label) for label in p] for p in reference["optima"]))
        for cap in range(len(nodes) - 1):
            partial, metrics = run(raw, scope, caps=SearchCaps(entries=cap))
            self.assertEqual(metrics["stop_reason"], "ENTRY_CAP")
            resumed, _ = run(raw, scope, checkpoint=partial)
            self.assertEqual(canonical(resumed), canonical(complete))
        self.assertEqual(next(q for q in complete["nodes"] if q["id"] == "root")["rule"],
                         ALL_PAIRS)

    def test_default_is_pinned_v1(self):
        path = EVIDENCE / "tiny_choice"
        for mode in ("one", "all"):
            raw, scope = load(path/"raw.json"), load(path/"trusted.json")
            cert, _ = solve(raw, scope, mode)
            self.assertEqual(canonical(cert), (path/f"{mode}.cert.json").read_bytes())

    def test_actual_completed_resume_and_cumulative_entries(self):
        for case in ("tiny_choice", "small_choice"):
            path = EVIDENCE / case
            raw, scope = load(path/"raw.json"), load(path/"trusted.json")
            for mode in ("one", "all"):
                fresh, _ = run(raw, scope, mode)
                first, _ = run(raw, scope, mode, caps=SearchCaps(entries=1))
                self.assertEqual(first["declared_status"], "PARTIAL")
                direct, _ = run(raw, scope, mode, caps=SearchCaps(entries=3))
                staged, _ = run(raw, scope, mode, checkpoint=copy.deepcopy(first),
                                caps=SearchCaps(entries=2))
                self.assertEqual(canonical(direct), canonical(staged))
                for _ in range(len(fresh["nodes"])):
                    if first["declared_status"] == "EXHAUSTED":
                        break
                    first, _ = run(raw, scope, mode, checkpoint=first,
                                   caps=SearchCaps(entries=1))
                self.assertEqual(canonical(fresh), canonical(first))

    def test_atomic_work_and_frontier(self):
        path = EVIDENCE / "small_choice"
        raw, scope = load(path/"raw.json"), load(path/"trusted.json")
        first, stats = run(raw, scope, "one", caps=SearchCaps(entries=1))
        residual_payload = stats["frontier_bytes"]
        before, _ = run(raw, scope, "one", caps=SearchCaps(memory_bytes=residual_payload-1))
        self.assertEqual([(n["id"],n["kind"]) for n in before["nodes"]], [("root","OPEN")])
        direct, direct_stats = run(raw, scope, "one", caps=SearchCaps(memory_bytes=5000))
        staged, staged_stats = run(raw, scope, "one", checkpoint=copy.deepcopy(first),
                                   caps=SearchCaps(memory_bytes=5000))
        self.assertEqual(canonical(direct), canonical(staged))
        self.assertEqual(direct_stats["frontier_bytes"], staged_stats["frontier_bytes"])
        self.assertGreater(stats["work"] + staged_stats["work"], direct_stats["work"])
        restarted, _ = run(raw, scope, "one", checkpoint=copy.deepcopy(first),
                           caps=SearchCaps(memory_bytes=residual_payload-1))
        self.assertEqual(restarted, first)
        for work in (0, 25, 250, 1000, 2000):
            partial, _ = run(raw, scope, "one", caps=SearchCaps(work=work))
            complete, _ = run(raw, scope, "one", checkpoint=partial)
            self.assertEqual(complete, run(raw, scope, "one")[0])

    def test_v1_accounting_reproduction(self):
        path = EVIDENCE / "small_choice"
        raw, scope = load(path/"raw.json"), load(path/"trusted.json")
        first, original = solve_v1(raw, scope, caps=SearchCaps(entries=4))
        direct, fresh = solve_v1(raw, scope, caps=SearchCaps(memory_bytes=3072))
        staged, replay = solve_v1(raw, scope, caps=SearchCaps(memory_bytes=3072),
                                  checkpoint=copy.deepcopy(first))
        self.assertNotEqual(canonical(direct), canonical(staged))
        self.assertGreater(replay["nodes"], fresh["nodes"])
        self.assertEqual(replay["frontier_bytes"] + original["frontier_bytes"],
                         solve_v1(raw, scope, caps=SearchCaps(
                             entries=len(staged["nodes"]) - 1))[1]["frontier_bytes"])
        direct, _ = solve_v1(raw, scope, caps=SearchCaps(work=2000))
        staged, _ = solve_v1(raw, scope, checkpoint=copy.deepcopy(first),
                             caps=SearchCaps(work=2000-original["work"]))
        self.assertEqual((len(direct["nodes"]), len(staged["nodes"])), (13, 9))
        renewed, _ = solve_v1(raw, scope, checkpoint=copy.deepcopy(first),
                              caps=SearchCaps(entries=4))
        cumulative, _ = solve_v1(raw, scope, caps=SearchCaps(entries=8))
        self.assertEqual(canonical(renewed), canonical(cumulative))
