# Static implementation review: QOP001 prepared provider

**Review ID:** C004-G-QOP-IMPL-001  
**Review type:** read-only source/proof alignment review; no provider/test/experiment run  
**Status:** no blocking mismatch found by static inspection; prepared source remains unexecuted and unaudited  

## Reviewed identities

| File | SHA-256 |
|---|---|
| `structural/bounded_certificate_v1.py` | `0a8e542d3d44650f454e779137a5c9ac1057cd863bc162c94b45519f253636d5` |
| `structural/PROOFS_QOP001_PREPARED.md` | `b299cf86d4bf5e4a7f6378630b96d76a5aa5938472525bd51ef27c2fdea919c6` |

## Proof-to-code correspondence

- The pair value dictionaries retain distinct binary positive projections,
  adding one edge only when the count becomes `q+1`. Each edge stores the
  q+1 positive indices and projections that witness it. This implements the
  strict threshold and is separate from singleton threshold-one opposition.
- Unary projections are checked by symbol. Since each unary projection is a
  repetition of that symbol, distinct unary values are exactly distinct
  positive counts; `q+1` counts correctly prove infeasibility for every owner
  of that symbol.
- `certificate_partition` receives only the q-opposition graph and known k.
  Complete-k-partite uniqueness is sound for this necessary coloring
  relaxation. The inherited connected-bipartite shortcut is limited to k=2
  and is sound as a unique proper 2-coloring certificate. It is not used as a
  k>=3 connectedness claim.
- After one graph-forced candidate is obtained, the code builds every full
  block’s distinct positive projection set and rejects it at q+1; it then
  checks each negative for a block whose projection is absent from that set.
  These checks are essential and correctly remain after pair coloring.
- The no-positive branch returns unresolved coverage status. It does not
  confuse the empty word with an empty sample or claim singleton recovery.
  At-most-q semantics explicitly permit empty factor languages; the provider
  still chooses to abstain for no positives.
- The generic singleton implementation is imported for validation,
  projections, pair bucket extraction, certificate construction, and deadline
  checking. Static inspection found no call to its singleton `solve`, no
  equal-count prerequisite, and no threshold-one edge rule.

## Limitations and verification boundary

The provider is certificate-only: failure to find the graph certificate
returns `insufficient_coverage`, which is not infeasibility. `max_solutions`
is validated but cannot enumerate alternative partitions; uniqueness is
claimed only after the graph certifies the only proper surjective k-coloring
and the full bounded-language checks pass. The q+1 cap limits retained values
per pair, but stored strings still consume length-proportional memory, as the
prepared proof notes. Runtime behavior, hash/source integration, correctness
against an independent full-set oracle, and captured evidence remain pending;
this review supplies none of those.

## Conclusion

No proof-to-code mismatch was found in the prepared implementation. In
particular, the crucial full-block cap and negative rejection checks are
present and are not replaced by pair-level evidence. This is only a static
review during the timing window; no run was performed.
