# C011 implementation handoff

Read the contract and inspected C010 v2 statically. No candidate code has been
written or executed, and no timing was collected. C010 remains unchanged.

The clearest first experiment is exact swap-hash lookup: generate every
adjacent unequal swap of each positive, then exact-lookup the resulting word
in a set of negatives. This replaces the `P×N` full-word scan while preserving
the existing edge predicate; the audit should compare complete edge sets
against the frozen slow reference. A second low-risk candidate is memoized
exact word/block projections shared across precheck, lazy masks and witnesses.

Two-letter anagram-interval must-links may prove useful for graph-empty
doubled-pair samples. The proposed condition and the required three-symbol
near-miss guard are documented in
[STATIC_HOTSPOT_REVIEW_V1.md](STATIC_HOTSPOT_REVIEW_V1.md); theory approval and
auditor counterexample search should precede implementation.

Suggested measurement keeps the complete default output identical, records
whole fresh-process time and output bytes, and separates sample volume, word
length, alphabet/atom size, negative coverage and output size. Collect lookup,
projection/cache, mask, DP and unique-witness counters; measure memory
separately or mark it unmeasured. Three repetitions and the contract's per-run
and total-suite caps apply. Do not interpret a compact-output timing as a
same-output speedup.

## Decision requested from master

Route the exact swap-index proposal and the anagram-interval statement through
theory/audit review, then provide the frozen method contract and selected
first candidate. This worker will not start implementation or execution until
that review/freeze is available.
