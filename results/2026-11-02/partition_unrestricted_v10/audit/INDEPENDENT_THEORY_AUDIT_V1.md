# Independent mathematical audit — C010 v1

## Scope and frozen inputs

This is an auditor's source-level review of the claims in `theory/PROOFS_v1.md` under `coordination/CONTRACT.md`. It does not run or modify the provider. The exact unrestricted sample oracle is separately checked in `oracle_validation_v1.json`.

| Artifact | SHA-256 |
|---|---|
| C010 contract | `4e4b5f1c29d604774b4e19ac62b75554221dd821ab1c2b435029c3c48df884fe` |
| Proofs v1 | `5e4e450209de4a53b879bad7d7c24cce69521e13410618c352bedd6ee688d606` |
| Provider v1 | `e2d3e0df3e59acb7b359b4be7a41243d99e7c71f4743a2bb76192cbbebdded1c` |
| Independent corpus manifest | `82fbc29c1b960cd4b7ca3b177bba586cfdfb8b7cedad55fbade06334d3e13e4c` |
| Independent oracle | `f14d31d8c1dc2b69e742478b80407bf6ba1efc51e70a10ceb395b6f221206cb9` |

## Proof review

**T1 (no-K identifiability): accepted.** For a partition block `B`, every factor fitting positives must accept every positive projection `π_B(P)`. Conversely choose the finite language `H(B)=π_B(P)`; it is regular. A complete word is rejected globally exactly when at least one block projection is outside its `H(B)`. Thus the criterion is necessary and sufficient. Under consistent labels, the one-block factor `P` is a finite regular witness. This proves a same-block witness for every symbol pair and rules out `forced_different`; only a singleton version space can guarantee ownership, and that singleton must be the one-block partition.

**T2 (coarsening ambiguity): accepted under the stated unrestricted class.** For factors on disjoint symbol sets, the merged factor language `F={u : π_B(u)∈F_B and π_C(u)∈F_C}` is regular and exactly preserves the global language after replacing `B,C` by `B∪C`. The report correctly does not carry this closure claim over to prime-factor or other restricted classes. The finite-horizon claims are attributed to the earlier C008 proof, rather than asserted as newly proved here.

**T3 (adjacent-swap atoms): accepted.** If positive `p` and negative `n` differ only by swapping unequal adjacent `x,y`, then under separate owners both local projections are unchanged, so accepting `p` entails accepting `n`. This contradiction proves coownership. Connected components therefore form sound must-link atoms. Expanding or contracting blocks is a bijection and leaves the block feasibility predicate invariant. An absent graph edge carries no separation meaning.

**T4 (all coarsenings): accepted mathematically; provider-v1 implementation is blocked.** If the atom partition is feasible, merging factors preserves feasibility; T3 excludes every partition that splits an atom. Hence the family is exactly all partitions of `r` atoms. Its exact-k spectrum is `S(r,k)`, total is `Bell(r)`, and coownership of two distinct atoms is `Bell(r−1)` (or `S(r−1,k)` at fixed k). The corresponding all-in-one and singleton-atom witnesses are valid. However, provider v1 uses `Bell(k)` in place of `S(r,k)` in its shortcut spectrum; see `PROVIDER_V1_STATIC_FINDINGS.json`. This concrete disagreement blocks v1 acceptance even though the theorem is sound.

**T5 (fallback DP and prune): accepted as written.** Anchoring each recursive block at the least remaining atom gives every set partition a unique first block and child, so the recurrence neither omits nor duplicates a partition. The mask `R(B)` is exact by T1. If `B⊆S`, projection equality on `S` implies projection equality on `B`; contraposition gives `R(B)⊆R(S)`. Thus no future subdivision of `rem` can reject an uncovered negative outside `R(rem)`, making the stated remaining-coverage prune sound. Full listing must be distinguished from count-only mode and remain incomplete on interruption.

**T6 (feasible k interval): accepted.** Starting with any feasible `k_max` partition, successive block merges preserve feasibility and realize every smaller positive block count. Therefore a complete nonempty unrestricted spectrum has no gaps. The distinction between exact spectrum-derived maximum and a reported atom-count upper bound is necessary.

## Candidate-specific cautions

1. V1 is not executable-gate accepted: its Stirling/Bell shortcut spectrum is wrong. The exact smallest clear mathematical counterexample has two singleton atoms and no labels: total `2`, expected spectrum `{1:1,2:1}`, but `Bell(k)` yields `{1:1,2:2}`.
2. Static peer review also notes that v1's swap extraction and union-find preprocessing occur before its `try`/first deadline poll. An already-expired deadline is eventually reported as unknown after preprocessing, but cancellation during this phase may escape instead of returning the structured incomplete result. Interruption/deadline controls are therefore still required on the corrected candidate.
3. `k_max_upper_bound=r` is not generally the exact feasible maximum on the DP branch. Derive exact kmax from the largest positive entry of a complete correct spectrum; preserve the field name/meaning as an upper bound.
4. Provider-internal time fields omit some returned witness work. Use captured wall time only for an explicitly approved runtime comparison; this round authorizes correctness checks and reported search counters, not a performance benchmark.

## Decision

The mathematical reductions T1–T6 are sound within the frozen assumptions, with the implementation qualification above. The independent RGS oracle is accepted. Provider v1 remains rejected for the shortcut count-spectrum defect, and no provider code was executed in this audit. The sole provider-launch attempt, which failed while snapshotting an invalid source path before starting a child, is retained at `attempts/20261102T185902.503032Z_db01f59272`. Continue only after a new provider version and readiness hashes are frozen; preserve v1 unchanged.
