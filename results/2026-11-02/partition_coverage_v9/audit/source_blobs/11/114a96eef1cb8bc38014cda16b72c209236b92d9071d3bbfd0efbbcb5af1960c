# C009 bounded scale correctness cells — v1

This protocol is preregistered after the accepted 129-case independent gate and accepted controls. It freezes four correctness-only inputs before any scale provider invocation. Each case is run once, sequentially, with `--seconds 27 --enumerate` and a 30-second hard capture cap. Do not rerun a timeout, incomplete result, mismatch, or provider error. Preserve its output and mark the cell censored/rejected as appropriate. No timing comparison, speed claim, or additional scale cell is authorized.

## Three partial-identification cells

For `m=10,12,14`, alphabet symbols are grouped into `r=m/2` fixed adjacent atoms `(a,b),(c,d),...`. The one positive word is the alphabet order with every symbol once. There is one negative per atom, obtained by swapping just that adjacent pair in the positive word. The trusted allowed component counts are:

* `m=10, r=5, K={2,4}`;
* `m=12, r=6, K={3,5}`;
* `m=14, r=7, K={2,4}`.

No hidden partition is planted. Proof of the exact compatible family: if the two letters in an atom were separated, swapping their adjacent order would be invisible in every block projection, so that negative would match the positive projection in every component and could not be rejected. Thus every compatible partition keeps each atom together. Conversely, any partition of the atoms is compatible: the block containing the swapped atom sees the reversed adjacent pair, absent from the sole positive projection. Therefore compatible symbol partitions are exactly coarsenings of the `r` atoms with `k∈K` blocks.

The independent scale oracle enumerates partitions of at most seven atoms by set insertion (Bell(7)=877), expands atoms to symbols, filters K, and computes the exact full set and pair counts. It does not invoke or copy the provider DP. For `r` atoms, total `Z=Σ_{k∈K} S(r,k)`. Within-atom coownership count is `Z`; across two atoms it is `Σ_{k∈K} S(r−1,k)`. Expected `(Z,cross-coown)` values are `(25,8)`, `(105,26)`, and `(413,96)` respectively. Cross-atom relation is ambiguous; within-atom relation is forced same.

## Separate long-word cell

Alphabet `{a,b,c,d}`, positive `a^2048 b^2048`, negative `b^2048 a^2048`, `K={2}`. The input has two words of length 4096. Splitting `a,b` leaves the negative's projection equal to the positive's in every block, so they must be together. The exact compatible partitions are `{ab,d}|{c}`, `{ab,c}|{d}`, and `{ab}|{cd}`: exactly three. Thus `a,b` are forced same and every other pair is ambiguous. The independent oracle enumerates all Bell(4)=15 symbol partitions directly and applies the projection test.

## Acceptance and censoring

For a complete output, independently compare exact full partition sets, per-k counts, all pair same/different counts and relations, and replay projection witnesses. For an incomplete result require `status=unknown`, `complete=false`, and no exact counts/ownership claims; classify it as censored, never as success or mismatch. A complete incorrect answer rejects that cell and is preserved. Candidate hashes remain solver `79255b0a306f8a30dffdd813c018bc4fd9368dad880c07489a86abd50968a5e7` and CLI `356ac0db3ca272403d95bc275e4babc48c5d7fc29caf00cb9685f8e49aed8507`.
