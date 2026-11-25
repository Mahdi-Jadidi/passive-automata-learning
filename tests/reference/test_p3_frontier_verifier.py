"""Independent adversarial tests for the P3 region/frontier verifier."""
import copy
import hashlib
import json
import unittest

from selector_v2.schema import canonical
from independent_replay import sample_data
import rgs_oracle
import p3_frontier_verifier as verifier


def scope(raw=None):
    if raw is None:
        raw = {"alphabet": ["a", "b"], "positive": [], "negative": []}
    n, positive_words, negative_words, sample_digest = sample_data(raw)
    selector_scope = {"version": "selector-v2/1", "sample_digest": sample_digest,
                      "regime": "UNRESTRICTED", "family": "ALL_PARTITIONS", "capacity_digest": None}
    journal = {"version": "selector-v2-journal/2", "sample_digest": sample_digest, "events": []}
    journal_bytes = canonical(journal)
    root_owner = list(range(n))
    root_equalities = [[i, j] for i in range(n) for j in range(i + 1, n)
                       if root_owner[i] == root_owner[j]]
    trusted = {
        "format": "p3-trusted-scope/v1",
        "selector_scope": selector_scope,
        "journal2_digest": hashlib.sha256(journal_bytes).hexdigest(),
        "alphabet": list(raw["alphabet"]),
        "positive": [{"id": "P" + str(i), "tokens": list(tokens)}
                     for i, tokens in enumerate(positive_words)],
        "negative": [{"id": "N" + str(i), "tokens": list(tokens)}
                     for i, tokens in enumerate(negative_words)],
        "root_equalities": root_equalities,
        "root_owner": root_owner,
    }
    return raw, journal_bytes, trusted


def leaf(node_id, owner, disequalities=(), via=None, reason="EXACT_FEASIBLE"):
    if reason == "EXACT_FEASIBLE":
        closure = {"reason": reason, "owner": list(owner), "cost": 2 - len(set(owner))}
    else:
        closure = {"reason": reason}
    node = {"id": node_id, "owner": list(owner), "disequalities": [list(x) for x in disequalities],
            "kind": "LEAF", "closure": closure}
    if via is not None:
        node["via"] = list(via)
    return node


def complete_proof(trusted, mode="all"):
    owner = [0, 1]
    alternatives = [[0, 1]]
    digest = hashlib.sha256(json.dumps(alternatives, sort_keys=True, separators=(",", ":"),
                                       ensure_ascii=False).encode()).hexdigest()
    root = {
        "id": "root", "owner": owner, "disequalities": [], "kind": "SPLIT",
        "rule": "ALL_PAIRS_LEX_V1", "cursor": 1,
        "suffix": {"rule": "FIRST_TRUE_SUFFIX_V1", "start": 1, "stop": 1,
                   "alternatives_sha256": digest},
        "cursor_log": [{"from": 0, "to": 1, "child_id": "root/c0", "pair": [0, 1]}],
        "children": [leaf("root/c0", [0, 0], via=[0, 1])],
        "residual": leaf("root/r", [0, 1], [(0, 1)]),
    }
    return {
        "format": "p3-region-frontier/v1",
        "scope_digest": verifier.scope_digest(trusted),
        "mode": mode,
        "declared_status": "EXHAUSTED",
        "root_owner": owner,
        "incumbent": {"owner": owner, "cost": 0},
        "optima": [owner] if mode == "all" else [],
        "root": root,
    }


class FrontierVerifierTests(unittest.TestCase):
    def test_independent_rgs_oracle_bell_counts_labels_and_region_coverage(self):
        # Includes Bell(0..8), independent label enumeration (0..5), and
        # exhaustive first-true/residual region-membership checks on n=4.
        rgs_oracle.self_test()
        expected = [1, 1, 2, 5, 15, 52, 203, 877, 4140]
        self.assertEqual([sum(1 for _ in rgs_oracle.rgs(n)) for n in range(9)], expected)

    def test_complete_frontier_one_and_all_optima(self):
        raw, journal, trusted = scope()
        all_result = verifier.verify_frontier(raw, journal, trusted, complete_proof(trusted, "all"))
        self.assertEqual(all_result["status"], "VERIFIED")
        self.assertEqual(all_result["result"]["optimum"], 0)
        self.assertEqual(all_result["result"]["optima"], [[0, 1]])
        one_result = verifier.verify_frontier(raw, journal, trusted, complete_proof(trusted, "one"))
        self.assertEqual(one_result["status"], "VERIFIED")
        self.assertEqual(one_result["result"]["optima"], [])

    def test_first_true_children_and_residual_are_literal_partition(self):
        raw, journal, trusted = scope()
        proof = complete_proof(trusted)
        alternatives = verifier._alternatives((0, 1))
        partitions = list(rgs_oracle.rgs(2))
        for partition in partitions:
            in_parent = rgs_oracle.region(partition, (), ())
            in_child = rgs_oracle.region(partition, ((0, 1),), ())
            in_residual = rgs_oracle.region(partition, (), ((0, 1),))
            self.assertEqual(int(in_child) + int(in_residual), int(in_parent))
        self.assertEqual(alternatives, ((0, 1),))
        self.assertEqual(proof["root"]["cursor"], 1)

    def test_root_e0_and_scope_binding_are_independently_enforced(self):
        raw, journal, trusted = scope()
        bad_scope = copy.deepcopy(trusted)
        bad_scope["root_owner"] = [0, 0]
        bad_scope["root_equalities"] = [[0, 1]]
        proof = complete_proof(bad_scope)
        self.assertEqual(verifier.verify_frontier(raw, journal, bad_scope, proof)["status"], "INVALID")
        proof = complete_proof(trusted)
        proof["scope_digest"] = "b" * 64
        self.assertEqual(verifier.verify_frontier(raw, journal, trusted, proof)["status"], "INVALID")

    def test_selector_scope_sample_identity_and_exact_journal_bytes_are_bound(self):
        raw, journal, trusted = scope()
        bad_scope = copy.deepcopy(trusted)
        bad_scope["selector_scope"]["sample_digest"] = "b" * 64
        self.assertEqual(verifier.verify_frontier(raw, journal, bad_scope,
                                                  complete_proof(bad_scope))["status"], "INVALID")
        bad_scope = copy.deepcopy(trusted)
        bad_scope["journal2_digest"] = "b" * 64
        self.assertEqual(verifier.verify_frontier(raw, journal, bad_scope,
                                                  complete_proof(bad_scope))["status"], "INVALID")
        # A semantically equivalent JSON spelling is not the exact journal byte stream.
        changed_bytes = journal + b"\n"
        changed_scope = copy.deepcopy(trusted)
        changed_scope["journal2_digest"] = hashlib.sha256(changed_bytes).hexdigest()
        self.assertEqual(verifier.verify_frontier(raw, changed_bytes, changed_scope,
                                                  complete_proof(changed_scope))["status"], "INVALID")
        self.assertEqual(verifier.verify_frontier(raw, journal, trusted, complete_proof(trusted),
                                                  max_journal_bytes=1)["status"], "INCOMPLETE")

    def test_missing_duplicate_and_reordered_children_are_invalid(self):
        raw, journal, trusted = scope()
        proof = complete_proof(trusted)
        proof["root"]["children"] = []
        self.assertEqual(verifier.verify_frontier(raw, journal, trusted, proof)["status"], "INVALID")
        proof = complete_proof(trusted)
        proof["root"]["children"].append(copy.deepcopy(proof["root"]["children"][0]))
        self.assertEqual(verifier.verify_frontier(raw, journal, trusted, proof)["status"], "INVALID")
        proof = complete_proof(trusted)
        proof["root"]["children"][0]["via"] = [1, 0]
        self.assertEqual(verifier.verify_frontier(raw, journal, trusted, proof)["status"], "INVALID")

    def test_cursor_suffix_and_residual_transition_are_checked(self):
        raw, journal, trusted = scope()
        proof = complete_proof(trusted)
        proof["root"]["cursor_log"][0]["to"] = 0
        self.assertEqual(verifier.verify_frontier(raw, journal, trusted, proof)["status"], "INVALID")
        proof = complete_proof(trusted)
        proof["root"]["suffix"]["stop"] = 0
        self.assertEqual(verifier.verify_frontier(raw, journal, trusted, proof)["status"], "INVALID")
        proof = complete_proof(trusted)
        proof["root"]["residual"]["disequalities"] = []
        self.assertEqual(verifier.verify_frontier(raw, journal, trusted, proof)["status"], "INVALID")

    def test_forged_witness_and_all_optima_claim_are_invalid(self):
        raw, journal, trusted = scope()
        proof = complete_proof(trusted)
        proof["root"]["residual"]["closure"]["owner"] = [0, 0]
        self.assertEqual(verifier.verify_frontier(raw, journal, trusted, proof)["status"], "INVALID")
        proof = complete_proof(trusted)
        proof["optima"] = []
        self.assertEqual(verifier.verify_frontier(raw, journal, trusted, proof)["status"], "INVALID")
        proof = complete_proof(trusted, "one")
        proof["optima"] = [[0, 1]]
        self.assertEqual(verifier.verify_frontier(raw, journal, trusted, proof)["status"], "INVALID")

    def test_unknown_open_and_resource_caps_never_verify(self):
        raw, journal, trusted = scope()
        proof = complete_proof(trusted)
        proof["declared_status"] = "PARTIAL"
        proof["root"] = {"id": "root", "owner": [0, 1], "disequalities": [], "kind": "OPEN"}
        self.assertEqual(verifier.verify_frontier(raw, journal, trusted, proof)["status"], "INCOMPLETE")
        proof["declared_status"] = "EXHAUSTED"
        self.assertEqual(verifier.verify_frontier(raw, journal, trusted, proof)["status"], "INVALID")
        proof = complete_proof(trusted)
        self.assertEqual(verifier.verify_frontier(raw, journal, trusted, proof, max_nodes=1)["status"], "INCOMPLETE")

    def test_equality_class_lower_bound_cutoff_is_strict_for_all_optima(self):
        raw, journal, trusted = scope()
        proof = complete_proof(trusted, "one")
        proof["root"] = leaf("root", [0, 1], reason="COST")
        self.assertEqual(verifier.verify_frontier(raw, journal, trusted, proof)["status"], "VERIFIED")
        proof["mode"] = "all"
        proof["optima"] = [[0, 1]]
        self.assertEqual(verifier.verify_frontier(raw, journal, trusted, proof)["status"], "INVALID")

    def test_original_trace_ids_and_raw_label_conflict_witness(self):
        raw = {"alphabet": ["a", "b"], "positive": [["a"]], "negative": [["a"]]}
        raw, journal, trusted = scope(raw)
        proof = {
            "format": "p3-region-frontier/v1", "scope_digest": verifier.scope_digest(trusted),
            "mode": "one", "declared_status": "EXHAUSTED", "root_owner": [0, 1],
            "incumbent": None, "optima": [],
            "root": {"id": "root", "owner": [0, 1], "disequalities": [], "kind": "LEAF",
                     "closure": {"reason": "RAW_LABEL_CONFLICT", "positive_id": "P0",
                                 "negative_id": "N0"}},
        }
        self.assertEqual(verifier.verify_frontier(raw, journal, trusted, proof)["status"], "VERIFIED")
        proof["root"]["closure"]["positive_id"] = "invented-id"
        self.assertEqual(verifier.verify_frontier(raw, journal, trusted, proof)["status"], "INVALID")


if __name__ == "__main__":
    unittest.main(verbosity=2)
