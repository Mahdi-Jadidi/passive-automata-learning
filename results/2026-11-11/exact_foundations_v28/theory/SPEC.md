# C028 frozen reference specification

Status: proposed specification for independent proof review; implementation and official provider experiments are gated on reviewer approval. Biggest overlooked point? The empty alphabet has one empty partition, whose empty conjunction accepts every word over it, namely epsilon.

## Scope and exact input

Only independent disjoint regular factors, finite alphabets, noiseless Boolean full-word membership labels, and conjunctive acceptance are modeled. P and N are observations; unobserved words are unconstrained. There is no externally supplied number of factors K, ownership, target machine, state bound, or physical-truth metadata. This does not cover arbitrary log semantics, prefix closure, noisy labels, bounded-state factors, or infinite input streams without a separate model.

The input is a JSON-like record with exactly the keys `Sigma`, `P`, `N`. `Sigma` is an array of pairwise distinct, nonempty string symbol IDs. Its array order is the canonical symbol order. Each of `P` and `N` is an array of words; each word is an array of IDs occurring in `Sigma`. An empty word is `[]`, not an empty string. IDs are atomic strings, never tokenized by character; multi-character IDs, Unicode, punctuation, and IDs containing each other are allowed. Equality means exact string equality, with no case folding or Unicode normalization. Duplicate words within P or within N are removed while preserving their first occurrence. Sigma duplicate IDs, unknown IDs, wrong types, missing/extra keys and empty-string IDs are INVALID_INPUT; no valid mathematical claim follows from them. Duplicate traces across labels constitute contradictory observations, not malformed input, and are INCOMPATIBLE. Empty Sigma, P, N and arbitrarily many unused Sigma symbols are allowed.

For empty Sigma there is exactly one partition, the empty partition. Its AND over zero factors is true. Since Sigma*={epsilon}, it fits iff N is empty, including when P is empty or contains epsilon. This convention is part of the model and is not inferred from data.

## Semantic model and objective

A partition consists of nonempty, disjoint blocks covering Sigma. The empty alphabet has the one empty partition above. For a block B and word w, projection `pi_B(w)` retains its letters belonging to B, in order. Regular block languages F_B induce acceptance iff every factor accepts its corresponding projection. A partition is compatible if some such factors accept P and reject N.

For each block B define `H_B = {pi_B(p): p in P}` and `reject(B) = {n in N : pi_B(n) not in H_B}`. The criterion is: each n in N must belong to reject(B) for at least one block B. Equivalently, one block must distinguish that negative from every positive, potentially a different block for each negative. A compatible partition has explicit finite regular factors H_B. For every negative retain one block B with n in reject(B) as its rejection witness; with no negatives this list is empty. For P empty H_B is empty; the finite-language factor is then a valid regular language. The zero-block product uses its separate convention.

"Best" means maximum number of blocks among compatible partitions. This is a data-based recommendation, not the original physical partition or a recovered K. A canonical restricted-growth string (RGS) labels blocks by first occurrence in Sigma order. Pick the lexicographically least compatible RGS among all maximizers; this is a reproducible choice, not a uniqueness assertion.

## Complete output contract

Only after a completed exhaustive search return:

- `status`: INCOMPATIBLE if compatible_count=0; UNIQUE_COMPATIBLE if compatible_count=1; AMBIGUOUS if compatible_count>=2. Counts are exact arbitrary-precision nonnegative integers. These statuses concern all compatible partitions, not physical truth or optimal ties.
- `compatible_count`, `optimal_count`; if no compatible partition, both are 0 and `max_blocks` and `recommendation` are null. Otherwise `max_blocks` is the exact maximum, `optimal_count` counts all optimum partitions, and `recommendation` is the lexicographically least optimal RGS and its blocks.
- Up to two distinct compatible partition witnesses, and up to two distinct optimal partition witnesses, each with per-block finite factor languages H_B and one rejecting block for each negative. The lists have size min(2, respective exact count); the optimal list includes the canonical recommendation. The two lists may overlap. A factor witness contains arrays of arrays of IDs, not a potentially ambiguous flattened string.
- `optimal_unique` is null if infeasible, otherwise whether optimal_count=1. It does not imply UNIQUE_COMPATIBLE. `physical_truth_identified` is not an output assertion: finite data alone does not establish the true generating partition.

Malformed input returns INVALID_INPUT, with all mathematical counts, recommendation, and uniqueness fields null. An interrupted run returns INCOMPLETE, with those same mathematical result fields null; no partial count, maximum, uniqueness or incompatibility is claimed. A completed contradiction check may return INCOMPATIBLE immediately, since it is a proof of zero feasible partitions. A malformed record cannot be treated as a contradiction. Validation must finish before a mathematical status is returned. Resource exhaustion or an external interruption never implies infeasibility. The solver promises mathematical termination given finite input and unbounded computation and storage; it does not promise completion by a deadline or under finite available resources.

## Reference algorithm, frozen structure

Input validation, normalization and contradiction checking precede the search. Generate every RGS of length |Sigma| once, in lexicographic order. Length zero generates exactly the empty RGS; otherwise s[0]=0 and for i>0, 0<=s[i]<=1+max(s[0..i-1]). Convert each RGS to its partition, directly evaluate all projections against all positive projections, and check every negative is rejected by at least one block. No forced atoms, DP, greedy decisions, pruning, hidden known K, or non-exhaustive sampling. Count every compatible RGS, maintain the maximum block count and exact number of maximizers, and keep at most two compatible and at most two current-best optimal witnesses. On a strictly better candidate reset optimal_count and the optimal witness list; on an equal candidate increment and retain it only if fewer than two are stored. Lexicographic enumeration makes the first optimum after the final best update the canonical recommendation. Save enough data to construct or replay all retained factor and rejection witnesses after enumeration, and verify witnesses before returning. If zero candidates fit, return INCOMPATIBLE.

This is a semantic reference method, not a claim of efficient runtime. Exact counts may exceed machine integer widths; use arbitrary precision. No proof of a general polynomial exact algorithm is claimed. When Sigma is nonempty, a consistent P,N always has a compatible oneblock partition, but that optimization is not needed by the exhaustive baseline.

## Gate

Independent reviewer must approve the proof obligations and algorithm, including empty-alphabet convention, before implementation. An independent auditor may prepare test fixtures and an oracle before that gate. No official provider runs until proofs are approved and implementation/source/test inputs are frozen. Historical files remain read-only; no public entrypoint changes. Record actual test results only after execution.
