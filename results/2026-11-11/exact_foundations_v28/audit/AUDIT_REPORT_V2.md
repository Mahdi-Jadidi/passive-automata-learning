# C028 independent audit report v2

## Result

**PASS for the frozen finite reference implementation on the amended contract.** An independently written set-insertion oracle matched every tested compatible count, optimal count, all-compatible status, maximum block count, optimal uniqueness result, and canonical least optimal RGS. Every returned compatible and optimal witness was independently replayed, including its blocks, tuple projections, finite factors, first-occurrence factor serialization, and first rejecting block for every normalized negative.

The source hash remained `5f60b27447b37ec07f1fd6bce75be6199b898573d4b32e90413e900e3a615a94`, matching the implementation freeze. Amendment 2 was independently approved before this rerun; its SHA-256 is `4c4f81154c3d861859a4f95ec88fcaf7bfc2c5a19f1725615c00d4cb641750c4`. The approval clarifies that `negative_rejected_by` indexes the first-occurrence-deduplicated negative list and names the first rejecting block in canonical block order. The final result and review hashes are recorded in `INDEPENDENT_AUDIT_RESULTS_V2.json` and `AUDIT_MANIFEST_V2.json`.

## Coverage

- 2,187 exhaustive three-way labelings of all seven words over `{a,b}` of length at most two.
- 60 deterministic seeded records, ten per alphabet size 3–8.
- 19 edge records for empty alphabet and epsilon, empty positive/negative sets, unused IDs, contradictions, quantifier order, non-chain maxima, C026 counterexamples, duplicate words, opaque/multicharacter/Unicode/punctuation IDs, raw-concatenation collision, a 10,000-symbol trace, and a sparse 8-ID alphabet. The empty-ID case returned `INVALID_INPUT`.
- 11 malformed schema records returned `INVALID_INPUT` with mathematical fields null.
- Three finite samples from withheld DFA systems with mixed factor counts and state counts. Only labels were supplied to the solver; the target partitions were checked for fit but were not expected as recommendations.
- Metamorphic checks for injective symbol renaming, positive/negative input order, duplicate normalization, and sample extension. In the extension fixture the maximum remained two while the canonical RGS changed from `[0,0,1]` to `[0,1,0]`.
- A 1,200-ID, one-candidate-budget case returned `INCOMPLETE` with all mathematical fields null. Static inspection confirmed the frozen RGS generator is iterative.
- Incomplete and exact-budget controls covered both the null-output contract and completion at Bell(3)=5 candidates.

All successful comparisons had zero mismatches and zero witness replay failures. These finite checks corroborate the reviewed proof; general correctness and finite-input mathematical termination come from the proof, not the test count. The solver does not promise completion under a practical deadline or finite resources.

## Clarification history

The pre-Amendment-2 audit artifacts are retained. The initial attempt failed in the auditor's checker because it compared a rejection-index list with the raw duplicate-bearing negative list. First-occurrence deduplication was in the original specification, but the serialized witness index domain was not. Amendment 2 and its independent prospective approval settled that representation. The same frozen implementation and same fixture sets were then rerun; the final run uses explicitly normalized order and verifies each index and serialized factor list. See `audit_stderr_v1.txt`, `audit_stderr_v2.txt`, and the pre-clarification result in `INDEPENDENT_AUDIT_RESULTS_V1.json` for the earlier history; `audit_stdout_v4.txt` and `audit_stderr_v4.txt` capture the final full run.

No implementation source changed. The finalized successful command, raw captures, environment and all input/source hashes are listed in `AUDIT_MANIFEST_V2.json`.

## Interpretation

The optimum is a maximum compatible partition of the finite sample under the stated model. It is not a physical ownership certificate. Even complete behavior can admit distinct ownership partitions when factors are decomposable; optimal-tie uniqueness and uniqueness among all compatible partitions remain separate.

Biggest thing overlooked? Treating the data-based optimum—or a unique optimum—as proof of the original physical partition. The contract and output correctly avoid that claim.
