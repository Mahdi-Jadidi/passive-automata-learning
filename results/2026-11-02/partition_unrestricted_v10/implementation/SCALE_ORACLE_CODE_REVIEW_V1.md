# Static code review: C010 scale oracle v2

Reviewed only `audit/scale_oracle_v2.py`, read-only. No script was executed and
no audit file was edited. Reviewed source SHA-256:
`ad597963724cad18a1ab682d0001897133519abc9c6844c74d8731fc2f7e3de3`.

## Findings

**No blocker found for the four frozen scale cells.** The v1 list/set defect is
fixed in the fallback comparison: both families are normalized to tuples
before set comparison. `rgs` emits list rows, and all later pair indices refer
to positions in the sorted alphabet, matching the RGS coordinate order.

The two quotient cells enumerate partitions of 7 or 8 atom indices once,
expand them to symbol blocks, and check every lifted partition. Their edge
component checks and atom-feasibility checks establish that these are the full
families. The two fallback cells enumerate all symbol partitions (m=10 and
m=4), compare those exact families against the declared semantic-atom
coarsenings using tuple-normalized RGS rows, and then check spectrum and pair
counts. The expected pair formulas match the Bell contraction counts:
877/203, 4140/877, 52/15, and 5/2, respectively. No list/dict/index mismatch
was found in those paths.

One scope caveat: the relation expression labels a pair `forced_same` when no
different witness exists, and otherwise labels it `ambiguous`; it does not
produce `forced_different` if no same witness exists. That is sound for these
four consistent unrestricted samples because the one-block partition always
provides a same witness. Do not reuse this oracle helper for empty version
spaces or a restricted-K problem without making the relation classification
three-way.

The 64-symbol cell checks a deliberately structured input: eight disjoint
8-symbol paths whose 56 edges are witnessed swaps. It validates this quotient
oracle construction, not arbitrary 64-symbol coverage or performance.

**Static decision: cleared for the four specified cells, with the scope caveat
above.** This is source reasoning only; it does not certify runtime execution,
provider agreement, or the independent gate as a whole.
