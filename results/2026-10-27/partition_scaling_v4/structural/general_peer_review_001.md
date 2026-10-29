# C004 structural peer review of general v3 — read only

Review ID: C004-A-PEER-001. Date: 2026-10-27. Scientific status: static reasoning accepted for the stated valid-input semantics; execution status: no experiment or provider execution performed by this review. Independent runtime audit remains required. No source was edited.

Files read and frozen identities:

- general/known_k_v3.py — SHA256 `1519189883c8dcfa9dcfa8e309f8e2c942b46a53d1988720baae58c4ab817ed9`
- general/contextual_swap_proof.md — SHA256 `bf855121565d9eac6de1643193025500fb33641eb2cfa7c8c09146ab8bc5cdb1`

## Correctness findings

No blocking mathematical or valid-input partition-enumeration defect found in this static review.

The adjacent-swap rule is sound for any number of disjoint factors and arbitrary local languages: different-block symbols produce identical block projections before and after the swap. The insertion-rescue rule is also sound: if the two displayed symbols were separated, every negative block projection is supplied by one of the base/rescue positives. The same reasoning holds for bounded local-language classes because the positives must still be accepted. Context words can be arbitrarily long and nonempty; neither lemma depends on observing epsilon as a whole trace.

Connected components of these sound must-link edges can be contracted without losing any compatible partition. Every feasible block is a union of components. The implementation visits starting symbols in sorted alphabet order, so components are listed by increasing smallest symbol. Restricted-growth assignments beginning at color zero therefore give one canonical unordered partition of the atoms, and consequently of the original alphabet. Side choices 0..min(used,k-1), pruning used+remaining<k, and final used==k enforce exactly k nonempty blocks without duplicate color permutations. No conclusion from ordinary connectedness to unique k-coloring is used.

The direct leaf checker constructs each local language as exactly its set of positive projections. This accepts all positives, and a negative is excluded iff at least one block projection is outside that block's language. The reported block_index/projection and all_unseen_block_indices form direct rejection witnesses. For unrestricted regular languages, choosing these finite languages is sufficient whenever any regular factor product fits: every such product must contain the observed positive projections, so a negative whose projections all occur cannot be rejected by any alternative larger local languages. This is partition feasibility, not identification of the planted factor languages.

Cap pruning is sound. If two positive projections onto a partial block differ, extension cannot merge them, because erasing newly added symbols would recover the original distinct projections. Thus cardinality exceeding q cannot be repaired. Complete leaves satisfy at most q distinct positive projections per block. The code's comment that extension can only add projection words should be read as cardinality monotonicity; literal inclusion of string sets is not needed and generally does not hold when their alphabet grows. The accompanying proof gives the correct erasing argument.

Empty-positive semantics are consistent with the declared at-most-q finite-language class: all local languages may be empty, making all negatives rejected. This includes q=1 but differs from exactly-one singleton languages. The proof explicitly distinguishes the classes. The structural singleton provider's unresolved empty-positive case must not be treated as disagreement with this at-most-q result. With no negatives either, the empty product language still fits the empty labeled sample for every candidate partition.

Hash collisions do not cause unsound must-links. The adjacent-swap modular update only selects negative candidates; exact equality with the constructed swapped string guards every added swap edge. The deletion index also only selects candidates. A rescued positive is checked by exact prefix/suffix equality around the deleted symbol before the insertion-rescue implication is added. Collisions can increase work, but neither hashing path adds an edge based on hash equality alone. Duplicate deletion positions may create duplicate candidates/work; edges are deduplicated by unordered symbol pair.

Full exhaustion is correctly distinguished from a first answer: hitting max_solutions checks whether stack is empty; otherwise uniqueness remains unknown unless at least two solutions demonstrate ambiguity. A timeout preserves found solutions but does not mark search_exhausted. If fewer contracted atoms than k remain, impossibility follows because splitting a forced component is unsound. A fully rejected search correctly reports infeasible within the declared class.

## Material limitations / nonblocking hardening notes

1. Negative insertion-rescue preprocessing remains quadratic in individual negative length in the worst case: every position builds `word[:i]+word[i+1:]`, incurring O(L) copying/hashing for O(L) positions, even when no base positive matches. Total baseline is O(sum_negative L²); a hash-filtered negative deletion lookup could reduce ordinary work but is not implemented here. Exact verification of many colliding or repeated candidates can add further work. This should be reported in scaling results, especially at length 4096/16384.
2. Input validation performs whole-word set construction and sorting/deduplication before the first deadline check. Those operations and exact string slices/equalities are not interruptible internally. Negative by-position candidate grouping also lacks a per-candidate deadline check. External hard capture timeout is necessary; cooperative deadline is not a strict wall-clock bound over all preprocessing.
3. Unlike the structural v1 provider, this version does not type/finite-validate deadline. NaN disables the ordinary comparison and incompatible types can raise TypeError. This is an API hardening gap for malformed optional arguments, not a counterexample to valid-input partition correctness. It should be documented or handled in a future preserved version if the root contract requires consistent malformed-argument behavior.
4. Exhaustive search is exponential in the number of unconstrained atoms; the proof gives completeness, not a general polynomial bound. Cap checks rescan positive words at internal nodes. Hash preprocessing, contraction, cap pruning, leaf projection, materialized output, and serialization should remain separately accounted for. This review does not establish performance.
5. The API explicitly permits k>=2 only. That is consistent with the current requested k=2,3,4,6,8 grid, but the arbitrary-regular unknown-k one-factor obstruction remains a separate theoretical observation and is not evaluated through this provider.

## Existing Persian structural candidate report

`results/2026-10-27/partition_scaling_v4/structural/REPORT_S001_STAGE1_FA.md`

Absolute path: `C:/Users/Mahdi/Documents/ChatGPT/passive automata learning/results/2026-10-27/partition_scaling_v4/structural/REPORT_S001_STAGE1_FA.md`.

It reports Stage1 proof/smoke readiness only, explicitly leaving independent audit and official timing pending. Stage2 files v2/v3 and their prepared proof remain unexecuted as of this review.
