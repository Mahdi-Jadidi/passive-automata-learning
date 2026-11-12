# Independent review of V33 subset-DP candidate

**Verdict: PASS for the reviewed mathematical formulation and full-output source, conditional on sufficient resources and the exact reference dependency.** This is source/proof review plus finite differential checks, not human peer review, a proof assistant, official audit, or a timing result.

Reviewed byte hashes:

- `candidate_dp/candidate.py`: SHA-256 `8EC5B68A08D9EC430C0BF5F10D86024408C3BB9408A4045F7EFB41EED6E5F86F`.
- `candidate_dp/PROOF.md`: SHA-256 `37E99838EE8B869ACDE908191819DD31B3B173E5024A0017B0EB1CB7E0A80623`.
- The candidate checks C028 reference bytes against SHA-256 `5f60b27447b37ec07f1fd6bce75be6199b898573d4b32e90413e900e3a615a94` when imported. That external local file is an execution dependency; missing or changed reference causes import failure, not a C028 status. This is an environment/deployment limitation and should be included in any reproducibility package, not confused with an input-level failure.

## Findings

1. **Counts and uniqueness.** The root recursion anchors the least remaining symbol, so every partition contributes exactly once. `uncovered & ~rejection(block)` correctly removes all negatives rejected by that finalized block, regardless of overlap. The polynomial coefficients count by blocks, so their sum, highest nonzero degree and that coefficient give C, k* and O respectively. Empty-alphabet and contradictory-label branches behave consistently with C028.
2. **Prefix completion.** Each suffix symbol is assigned to exactly one existing fixed block or left for a new block. The ordered subsets selected by `extend` are disjoint and uniquely determined by a completed partition, and the anchored `counts` call enumerates each leftover partition once. Nonempty prefix blocks remain nonempty. Thus each completion contributes once even when several blocks reject the same negative. `best-q` is the number of new blocks; the coefficient feasibility test selects exactly the optimal completions.
3. **Canonical order and witnesses.** Prefix extensions use legal labels 0 through q in ascending order; the first position admits only zero. Exact feasibility pruning discards only subtrees with no eligible completion. Lexicographic DFS therefore returns the first two compatible and, separately, optimal RGSs. The empty partition is separately handled after root feasibility has been established. Serialized witness factors and first rejecting-block indices come from the frozen C028 helpers and are replayed; the exact-count sanity checks handle single-witness cases.
4. **Budget and failure behavior.** Every non-None `max_candidates`, including zero, negative values, booleans and other invalid values, is delegated before normalization to the C028 reference, preserving its prefix budget semantics and exact error reasons. Unlimited runs validate and detect contradictions first, catch `MemoryError`, `KeyboardInterrupt`, and recursion exhaustion as INCOMPLETE with null mathematical fields, and return ERROR for detected reconstruction/replay failures. An external kill or failure before/at import can yield no result; incomplete results are not optima. The DP's resource behavior can differ from the iterative baseline and no speedup follows from correctness.
5. **Costs.** The stated exponential DP and per-prefix query bounds are conservative with polynomial coefficient, bit and arithmetic factors. For the zero-existing-block case, interpret the G-state bound with `q+1` rather than q (the boundary call exists even at q=0); this is an editorial asymptotic endpoint, not a correctness defect. Reference helper costs and witness materialization remain part of end-to-end work.

## Independent checks

Executed the frozen candidate against the existing independently implemented C028 set-insertion oracle and witness replay on **2,206** edge and exhaustive binary-labeling cases. Also compared **13** invalid/edge unlimited records and **104** budget calls with the frozen baseline, including invalid budgets. All comparisons passed. This finite corpus does not establish general correctness or performance.

Biggest overlooked issue: exact feasibility of a prefix must quantify over future additions to *existing* blocks as well as new blocks, and a replayable optimum is not enough to establish total counts or canonical witness order. The reviewed implementation addresses these separately.
