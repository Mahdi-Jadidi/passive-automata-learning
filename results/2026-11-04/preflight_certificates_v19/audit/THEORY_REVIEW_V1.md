# C019 independent final theory review

Reviewed once after the two saved tiny enumeration runs: theory/PREFLIGHT_PROOFS_FA_v1.md, GRAPH_CERTIFICATE_LIMITS_v1.md, MATCHED_SUMMARY_COUNTEREXAMPLE_v1.md and CLAIM_LEDGER_v1.json. Exact bytes are hash-bound in FINAL_HANDOFF_V1.json. No further runtime test was required or run.

Scientific decision: **accepted under stated finite-sample independent-disjoint regular-language assumptions and externally trusted exact K**. No blocking mathematical error found.

- Projection criterion has the correct quantifier order: for each negative, one block separates it from ALL positives. Reverse-label r=K counterexample independently confirms why per-positive block choice is unsound.
- The arbitrary-cardinality even/odd a-count construction proves absence of a universal minimum-count/minimum-length guarantee. The proof, not the four finite computational instances alone, supports arbitrary sizes. This does not establish a probabilistic lower bound or exclude statements for a fixed finite bounded word universe.
- One-positive construction is valid for any desired K-partition after arranging each block contiguously. Each internal adjacent unequal swap forces its edge; its changed local projection supplies compatibility. Our20computed instances use one canonical chain-plus-singletons partition per(m,K), not an exhaustive search over all desired partitions or all datasets. The universal construction is accepted by direct proof review.
- m-K is forest rank/independent merge count only. The |P||N| capacity bound is necessary only for obtaining r=K by this adjacent-swap graph route. It is not a necessary bound on negative examples for arbitrary uniqueness: K1 or Km already demonstrate why such a global interpretation would be wrong. Duplicate pairs, repeated edges and cycles need not improve rank.
- If atoms fit the sample, all and only their coarsenings fit, so family cardinality is exactly S(r,K). If r=K but atoms do not fit, there is no legal K-model; if r>K and atoms fail, this graph certificate alone is inconclusive. No missing-edge heuristic may emit ambiguity. K1/invalid-schema/contradictory-label precedence is kept separate.
- The matched-summary unique/ambiguous examples have exactly the same P/N cardinalities, lengths and per-word symbol counts. Their exact K2 families were independently enumerated and agree with the supplementary proof.
- Empty-graph doubled-pair example and the infinite even-parity language example are mathematically sound; the latter shows observational equivalence of alternative K2 decompositions without a prime-factor assumption. It is not evidence that prime models are unidentifiable.

Boundary: an arbitrary swapped observation cannot be labeled negative automatically in passive data. The construction is a possible informative labeled sample, not an acquisition guarantee. Preflight soundness does not promise universal cheapness, universal sample threshold, general hardness classification, or recovery of physical hosts under invalid assumptions. No solver, performance benchmark, real data or paused paper task was resumed.

All prior enumeration versions remain unchanged. A literal commentary correction (a-count1, not0, in abcd) is documented in the audit report; it did not affect input strings or theory final proofs. No failed executable attempt occurred in this scope.
