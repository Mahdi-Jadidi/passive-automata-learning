# C011 auditor static review: binary-anagram interval must-link rule

Status: **semantic soundness cleared for the exact-context rule; implementation completeness and collision handling remain gated on a frozen candidate source review.** This is an independent mathematical review of the proposed rule as communicated by the master, not a review of an implementation (none is present in C011 yet).

## Soundness lemma

Let a positive word and a negative word have the form

`p = u s v`, `n = u t v`,

where the outside strings `u` and `v` are exactly equal, both interval strings use only two distinct symbols `{x,y}`, and `s` and `t` have equal counts of `x` and equal counts of `y` (hence equal interval lengths). Consider any ownership partition that separates `x` and `y`. In the block owning `x`, projection erases every `y`; `s` and `t` both project to the same number of `x` symbols. The block owning `y` has the symmetric property. Every other block erases the entire interval. Since `u` and `v` are identical, the complete projection of `p` and `n` is equal on every block. Any componentwise model accepting `p` must therefore accept `n`, contradicting the labels. Every compatible partition must co-own `x,y`.

This proof uses exact complete-word labels, disjoint ownership, and exact equality of both outside contexts. It does not require a state bound or a prime-factor promise. It is a sound necessary must-link; it does not by itself prove that all semantic must-links will be found.

## Hash/index obligations

Fingerprints may select candidate keys only. Before adding an edge or emitting a certificate, the implementation must verify the exact prefix and suffix bytes, interval boundaries, that the interval contains no symbol outside `{x,y}`, the two exact symbol counts, and the positive/negative labels. If the implementation claims exhaustive interval extraction, it must retain every representative in a fingerprint collision class; keeping only the first representative can miss a valid context even when the final DP still happens to return the right partition family.

A constant-fingerprint audit control is preregistered. `hash_collision_keep_all_contexts` places two positive contexts in the same collision class; only the second exactly matches the negative's `d/d` context, so the extractor must retain it and provide a replayable `a,b` certificate. `hash_collision_exact_context_guard` has matching interval boundaries/counts but `c/c` and `d/d` outside contexts; it must not create an `a,b` certificate, and the direct oracle must retain a separating partition witness.

## Completeness and boundary cases

The description “RLE groups of consecutive transitions with the same unordered pair” needs a precise implementation definition. If it literally means equal edge labels at every transition, it may only see alternating runs and can miss other valid binary windows such as `aabb` versus `bbaa`. The frozen regressions include non-adjacent two-symbol anagrams, repeated-symbol intervals, exact shared-context intervals, and the unsafe `acb`/`bca` case. For `acb`/`bca`, each three-symbol whole window violates the binary-interval premise; direct RGS enumeration should show that no pair is forced same. No transition-pattern heuristic may create an edge when the exact two-symbol premise fails.

The interval extractor's *coverage* is distinct from solver correctness: an omitted sound edge is safe for correctness if the exact fallback remains exhaustive, but it invalidates a claim that the extractor finds every interval and may lose the intended speed benefit. The audit therefore checks exact family equality and separately checks promised certificate coverage.

## Large-family proof gate

For structured performance cells, the independent certificate checker will replay every positive/negative adjacent swap, verify that the union components are the advertised groups, directly verify that every negative is rejected by the advertised atom partition, and then use the already reviewed coarsening theorem. Thus expected families are all coarsenings of `r` groups and counts are `Bell(r)` / `S(r,k)`; it never enumerates `Bell(m)` for the full alphabet. The report must state `m` (symbols) and `r` (atoms) separately: m=64 contracts to r=8, and m=128 contracts to r=16. In particular, Bell(16)=10,480,142 is computed by the recurrence, not enumerated.

The graph-empty m=8 fallback control has no adjacent-swap edges and an infeasible singleton partition. Its full family and all pair witnesses use direct RGS enumeration over at most Bell(8)=4,140 symbol partitions.

## Decision

Soundness of the exact-context theorem is cleared. Final static clearance remains contingent on the exact proof/addendum text and candidate source/readiness hashes. The candidate must preserve every baseline count, pair relation, and witness by default; additive interval certificates are replayed independently. The hash-collision controls and all 138 full-set cases must pass before any candidate timing.

No provider, baseline timing, or memory run was performed in this review.