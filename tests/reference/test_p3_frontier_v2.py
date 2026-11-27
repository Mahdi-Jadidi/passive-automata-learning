"""Literal RGS region tests and wire mutations. No producer dependency."""
from copy import deepcopy
from itertools import combinations, product
from pathlib import Path
from random import Random
from tempfile import TemporaryDirectory
import unittest

from independent_replay import sample_data
from p3_frontier_verifier import (
    ALL_PAIRS, CROSS_SUPPORT, Budget, CrossFamily, Invalid, canonical, path_state,
    build_trusted_scope, scope_digest, verify_frontier,
)
from p3_m3_artifact_replay import replay
from rgs_oracle import compatible, rgs
from test_p3_frontier_verifier import fixture, minimum_owner
from test_production_replay import build as journal_records


def split(node, rule, pairs, witness=None, cursor=None):
    ident = node["id"]
    count = len(pairs)
    cursor = count if cursor is None else cursor
    log = [
        {"from": j, "to": j + 1, "child_id": ident + "/c" + str(j), "pair": list(pair)}
        for j, pair in enumerate(pairs[:cursor])
    ]
    node.update(kind="SPLIT", rule=rule, alternative_count=count, cursor=cursor,
                children=[row["child_id"] for row in log], cursor_log=log,
                residual_id=ident + "/r",
                suffix=dict(rule="FIRST_TRUE_SUFFIX_V1", start=cursor, stop=count))
    if witness is not None:
        node["witness"] = witness


def header(scope, mode, optima):
    return dict(format="p3-region-frontier/v2", mode=mode,
                scope_digest=scope_digest(scope), root_owner=scope["root_owner"],
                declared_status="EXHAUSTED", nodes=[],
                incumbent=dict(owner=list(optima[0]), cost=len(optima[0])-len(set(optima[0])))
                if optima else None, optima=[list(q) for q in optima] if mode == "all" else [])


def literal_witness(p, X, Y):
    reps = sorted(set(p))
    supports = [(a,) for a in reps] + list(combinations(reps, 2))
    for i, y in enumerate(Y):
        hits = {}
        for support in supports:
            kept = tuple(a for a in y if p[a] not in support)
            for j, x in enumerate(X):
                if tuple(a for a in x if p[a] not in support) == kept:
                    hits[support] = j
                    break
        for s, t in combinations(sorted(hits), 2):
            if not set(s).intersection(t):
                return dict(negative_id=f"N{i}", positive_s_id=f"P{hits[s]}",
                            positive_t_id=f"P{hits[t]}", support_s=list(s), support_t=list(t))
    return None


def literal_proof(test, raw, scope, mode, cross_at_root):
    n, X, Y, _ = sample_data(raw)
    root = tuple(scope["root_owner"])
    partitions = [minimum_owner(q) for q in rgs(n)]
    feasible = [q for q in partitions if compatible(q, X, Y)]
    test.assertTrue(all(all(q[i] == q[a] for i, a in enumerate(root)) for q in feasible))
    best = min((n-len(set(q)) for q in feasible), default=None)
    optima = sorted(q for q in feasible if n-len(set(q)) == best)
    cert = header(scope, mode, optima)
    mixed = set()
    region_count = 0

    def visit(ident, parent, edge, p, constraints, members, rules):
        nonlocal region_count
        region_count += 1
        node = dict(id=ident, parent_id=parent, edge=edge, kind="LEAF")
        cert["nodes"].append(node)
        test.assertEqual(
            members,
            [q for q in partitions if all(q[i] == q[a] for i, a in enumerate(p))
             and all(q[a] != q[c] for a, c in constraints)],
        )
        cost = n-len(set(p))
        if edge["kind"] == "RESIDUAL" and rules[-1] == CROSS_SUPPORT:
            test.assertFalse(any(compatible(q, X, Y) for q in members))
            reason = "CONFLICT_RESIDUAL"
        elif not members:
            reason = "EMPTY"
        elif compatible(p, X, Y):
            reason = "FEASIBLE_MIN"
        elif best is not None and (cost > best or (mode == "one" and cost == best)):
            reason = "COST"
        elif len(members) == 1:
            reason = "EXACT_NO"
        else:
            choose_cross = cross_at_root != bool(len(rules) % 2)
            witness = literal_witness(p, X, Y) if choose_cross else None
            if witness:
                pairs = sorted(tuple(sorted(pair)) for pair in
                               product(witness["support_s"], witness["support_t"]))
                rule = CROSS_SUPPORT
            else:
                pairs = list(combinations(sorted(set(p)), 2))
                rule = ALL_PAIRS
            split(node, rule, pairs, witness)
            if rules and rules[-1] != rule:
                mixed.add((rules[-1], rule))
            bins = [[] for _ in range(len(pairs)+1)]
            for q in members:
                hits = [j for j, (a, c) in enumerate(pairs) if q[a] == q[c]]
                bins[min(hits, default=len(pairs))].append(q)
            for j, (a, c) in enumerate(pairs):
                visit(node["children"][j], ident, dict(kind="CHILD", index=j, pair=[a, c]),
                      tuple(a if v == c else v for v in p), constraints + pairs[:j],
                      bins[j], rules + (rule,))
            visit(node["residual_id"], ident, dict(kind="RESIDUAL"), p, constraints+pairs,
                  bins[-1], rules + (rule,))
            return
        node["closure"] = dict(reason=reason)

    members = [q for q in partitions if all(q[i] == q[a] for i, a in enumerate(root))]
    visit("root", None, dict(kind="ROOT"), root, [], members, ())
    cert["nodes"].sort(key=lambda q: q["id"])
    return cert, best, optima, len(partitions), region_count, mixed


class V2Tests(unittest.TestCase):
    def setUp(self):
        self.raw = dict(alphabet=list("abcd"), positive=[list("ab"), ["c"]],
                        negative=[[]])
        self.journal, self.scope = fixture(self.raw)
        self.cert, *_ = literal_proof(self, self.raw, self.scope, "all", True)

    def check_proof(self, proof, status, **budgets):
        out = verify_frontier(self.raw, self.journal, self.scope, proof, **budgets)
        self.assertEqual(out["status"], status, out)
        self.assertEqual(out["operational_status"], "INCOMPLETE")
        self.assertEqual("result" in out, status == "VERIFIED")
        return out

    def test_regions_to_eight(self):
        visited = regions = 0
        mixed = set()
        for n in range(9):
            alphabet = [str(i) for i in range(n)]
            for extra_negative in (False, True):
                raw = dict(alphabet=alphabet,
                           positive=[alphabet[:2], alphabet[2:3]] if n >= 3 else [],
                           negative=[[]] + ([alphabet[:2][::-1]] if extra_negative else []))
                j, scope = fixture(raw)
                for cross_first, mode in product((False, True), ("one", "all")):
                    c, best, winners, count, steps, transitions = literal_proof(
                        self, raw, scope, mode, cross_first)
                    out = verify_frontier(raw, j, scope, canonical(c))
                    self.assertEqual(out["status"], "VERIFIED", out)
                    self.assertEqual(out["result"]["optimum"], best)
                    self.assertIn(out["result"]["owner"], [list(q) for q in winners] or [None])
                    self.assertEqual(out["result"]["optima"],
                                     [list(q) for q in winners] if mode == "all" else [])
                    visited += count
                    regions += steps
                    mixed.update(transitions)
        self.assertEqual(mixed, {(ALL_PAIRS, CROSS_SUPPORT), (CROSS_SUPPORT, ALL_PAIRS)})
        print(f"literal RGS partitions across configurations={visited} regions={regions}")

    def test_minima_against_literal_prefixes(self):
        rng = Random(703)
        count = 0
        budget = Budget()
        for n in range(2, 9):
            cases = {(tuple(range(0, n, 2)), tuple(range(1, n, 2)))}
            for _ in range(6):
                tags = [rng.randrange(3) for _ in range(n)]
                s, t = [tuple(i for i, k in enumerate(tags) if k == a) for a in (0, 1)]
                if s and t:
                    cases.add(tuple(sorted((s, t))))
            for s, t in sorted(cases):
                pairs = sorted(tuple(sorted(pair)) for pair in product(s, t))
                family = CrossFamily(s, t, budget)
                self.assertEqual([family.pair(j, budget) for j in range(family.count)], pairs)
                for q in rgs(n):
                    p = minimum_owner(q)
                    for stop in range(len(pairs)+1):
                        self.assertEqual(family.conflicts(p, stop, budget),
                                         any(p[a] == p[c] for a, c in pairs[:stop]))
                        count += 1
        print(f"seeded minima-prefix comparisons={count}")

    def test_prefixes_keep_original_endpoints(self):
        # The later merge puts earlier cross endpoints 1 and 3 together;
        # neither remains a representative. A lower unrelated pair stays legal.
        b = Budget()
        family = CrossFamily((1, 2), (3,), b)
        table = {
            "root": {"id": "root", "cursor_log": []},
            "root/c1": dict(id="root/c1", parent_id="root",
                            edge=dict(kind="CHILD", pair=[2, 3], index=1), cursor_log=[]),
        }
        earlier = table["root/c1"]
        next_node = dict(id="root/c1/c0", parent_id=earlier["id"],
                         edge=dict(kind="CHILD", pair=[0, 2], index=0))
        table[next_node["id"]] = next_node
        families = {"root": family}
        self.assertFalse(path_state(next_node, table, tuple(range(4)), b,
                                    cross_families=families)[2])
        descendant = dict(id=next_node["id"]+"/c0", parent_id=next_node["id"],
                          edge=dict(kind="CHILD", pair=[0, 1], index=0))
        table[next_node["id"]]["cursor_log"] = []
        self.assertTrue(path_state(descendant, table, tuple(range(4)), b,
                                   cross_families=families)[2])

    def test_mutations_and_partial(self):
        self.check_proof(self.cert, "VERIFIED")
        witness_changes = [
            dict(negative_id="N1"), dict(negative_id="P0"), dict(negative_id="N00"),
            dict(positive_s_id="P1"), dict(positive_t_id="P0"), dict(positive_t_id="P01"),
            dict(support_s=[1, 0]), dict(support_s=[0, 0, 1]), dict(support_s=[False, 1]),
            dict(support_s=[0]), dict(support_t=[]), dict(support_t=[2, 4]),
            dict(support_t=[1, 2]), dict(support_s=[2], support_t=[0, 1],
                                         positive_s_id="P1", positive_t_id="P0"),
            dict(extra=True),
        ]
        for change in witness_changes:
            c = deepcopy(self.cert)
            c["nodes"][0]["witness"].update(change)
            self.check_proof(c, "INVALID")
        for mutate in (
            lambda c: c.update(format="p3-region-frontier/v1"),
            lambda c: c.update(format="p3-region-frontier/v3"),
            lambda c: c["nodes"][0].update(alternative_count=1),
            lambda c: c["nodes"][0]["cursor_log"][1].update(pair=[0, 2]),
            lambda c: c["nodes"][1]["edge"].update(pair=[1, 2]),
            lambda c: c["nodes"][1].update(closure=dict(reason="CONFLICT_RESIDUAL")),
            lambda c: c["nodes"][-1].update(closure=dict(reason="EXACT_NO")),
            lambda c: c["nodes"][-1]["closure"].update(extra=0),
            lambda c: c["nodes"].pop(),
        ):
            c = deepcopy(self.cert)
            mutate(c)
            self.check_proof(c, "INVALID")
        for cursor in (0, 1):
            c = deepcopy(self.cert)
            root = c["nodes"][0]
            split(root, CROSS_SUPPORT, [(0, 2), (1, 2)], root["witness"], cursor)
            c["nodes"] = [q for q in c["nodes"] if q["id"] in
                          ("root", "root/r", *root["children"])]
            c.update(declared_status="PARTIAL", optima=[])
            self.check_proof(c, "INCOMPLETE")
            bad = deepcopy(c)
            bad["nodes"][0]["suffix"]["start"] += 1
            self.check_proof(bad, "INVALID")
            self.check_proof(dict(c, declared_status="EXHAUSTED"), "INVALID")
        for budget in (dict(seconds=0), dict(max_work=0), dict(max_nodes=0),
                       dict(max_entries=0), dict(max_proof_bytes=1),
                       dict(max_journal_bytes=1), dict(max_exact_checks=0)):
            self.check_proof(self.cert, "INCOMPLETE", **budget)

    def test_order_repetitions_and_common_positive(self):
        self.raw = dict(alphabet=list("abc"), positive=[list("aabc"), list("aabc")],
                        negative=[list("abac"), list("baac")])
        self.journal, self.scope = fixture(self.raw)
        c, *_ = literal_proof(self, self.raw, self.scope, "all", True)
        self.assertEqual(c["nodes"][0]["witness"]["positive_t_id"], "P0")
        self.check_proof(c, "VERIFIED")
        c["nodes"][0]["witness"].update(support_s=[0], support_t=[2])
        # Dropping c gives identical multisets but different ordered sequences.
        out = self.check_proof(c, "INVALID")
        self.assertEqual(out["reason"], "false ordered deletion witness")

    def test_nonempty_journal_root_and_representatives(self):
        self.raw = dict(alphabet=list("abcd"), positive=[list("ab"), ["c"]],
                        negative=[list("ba"), list("abc")])
        records = journal_records(self.raw)["records"][:1]
        self.journal = canonical(dict(version="selector-v2-journal/2",
                                      sample_digest=sample_data(self.raw)[3],
                                      events=[dict(event="RAW", records=records)]))
        self.scope = build_trusted_scope(self.raw, self.journal)
        self.assertEqual(self.scope["root_owner"], [0, 0, 2, 3])
        c, *_ = literal_proof(self, self.raw, self.scope, "all", True)
        self.assertEqual(c["nodes"][0]["rule"], CROSS_SUPPORT)
        self.check_proof(c, "VERIFIED")
        bad = deepcopy(c)
        bad["nodes"][0]["witness"]["support_s"][0] = 1
        self.check_proof(bad, "INVALID")
        self.check_proof(dict(c, root_owner=list(range(4))), "INVALID")
        journal, self.journal = self.journal, self.journal + b"\n"
        self.check_proof(c, "INVALID")
        self.journal = journal

        checkpoint = deepcopy(c)
        root = checkpoint["nodes"][0]
        split(root, CROSS_SUPPORT, [(0, 2)], root["witness"], cursor=0)
        checkpoint.update(declared_status="PARTIAL", optima=[],
                          nodes=[root, checkpoint["nodes"][-1]])
        with TemporaryDirectory() as d:
            data = dict(raw=canonical(self.raw), journal=self.journal, scope=canonical(self.scope),
                        normal=canonical(c), optimized=canonical(c), resumed=canonical(c),
                        checkpoint=canonical(checkpoint))
            paths = {key: Path(d) / (key + ".json") for key in data}
            for key, path in paths.items():
                path.write_bytes(data[key])
            report = replay("nonempty_journal", "all", paths)
            self.assertEqual(report["census"]["visited"], 15)
            self.assertEqual(report["census"]["result"]["optimum"], 2)
            self.assertEqual(report["root_owner"], [0, 0, 2, 3])
            paths["resumed"].write_bytes(data["resumed"] + b" ")
            with self.assertRaisesRegex(Invalid, "resumed proof bytes differ"):
                replay("nonempty_journal", "all", paths)
            paths["resumed"].write_bytes(data["resumed"])
            with self.assertRaisesRegex(Invalid, "unexpected mode"):
                replay("nonempty_journal", "one", paths)

    def test_large_symbolic_cross_residual_and_caps(self):
        k = 10_000
        alphabet = [str(i) for i in range(2*k)]
        self.raw = dict(alphabet=alphabet, positive=[alphabet[::2], alphabet[1::2]],
                        negative=[[]])
        self.journal, self.scope = fixture(self.raw)
        c = header(self.scope, "one", [])
        root = dict(id="root", parent_id=None, edge=dict(kind="ROOT"), kind="SPLIT",
                    rule=CROSS_SUPPORT, alternative_count=k*k, cursor=1, children=["root/c0"],
                    cursor_log=[{"from": 0, "to": 1, "child_id": "root/c0", "pair": [0, 1]}],
                    residual_id="root/r", suffix=dict(rule="FIRST_TRUE_SUFFIX_V1", start=1, stop=k*k),
                    witness=dict(negative_id="N0", positive_s_id="P0", positive_t_id="P1",
                                 support_s=list(range(0, 2*k, 2)), support_t=list(range(1, 2*k, 2))))
        c.update(declared_status="PARTIAL", nodes=[
            root,
            dict(id="root/c0", parent_id="root", edge=dict(kind="CHILD", index=0, pair=[0, 1]),
                 kind="OPEN", reason="WORK_CAP"),
            dict(id="root/r", parent_id="root", edge=dict(kind="RESIDUAL"),
                 kind="LEAF", closure=dict(reason="CONFLICT_RESIDUAL")),
        ])
        out = self.check_proof(c, "INCOMPLETE", max_work=10_000_000)
        self.assertEqual(out["nodes_checked"], 3, out)
        self.assertEqual(out["exact_checks"], 2, out)
        capped = self.check_proof(c, "INCOMPLETE", max_exact_checks=1)
        self.assertEqual(capped["reason"], "exact projection cap")
        family = CrossFamily(tuple(root["witness"]["support_s"]),
                             tuple(root["witness"]["support_t"]), Budget())
        self.assertEqual(family.pair(k*k-1, Budget()), (2*k-2, 2*k-1))
        self.assertLessEqual(len(family.rows), 2*k)
        print(f"cross symbolic alternatives={k*k} nodes={out['nodes_checked']} work={out['work_units']}")
