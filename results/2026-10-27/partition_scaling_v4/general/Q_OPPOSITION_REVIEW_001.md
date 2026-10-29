# C004 Q-opposition certificate: independent proof review

**Review ID:** C004-G-QOP-001  
**Review type:** proof-only; no provider, test, or experiment run  
**Scientific status:** sound sufficient certificate under the stated finite-language semantics; not a complete solver  
**Scope:** master proposal C004-QOP001, reviewed while the stage-1 serial timing window is active. No source code was changed.

## Model and exact finite-sample feasibility condition

Assume known alphabet `Sigma`, known k nonempty disjoint blocks that partition
`Sigma`, complete positive and negative words, and exact labels. Each factor
has a finite local language of size at most q, with q>=1. The positive sample
is nonempty for the certificate below.

For a block B, define its observed positive projection set
`S_B = {pi_B(p): p in P}`. Any compatible local language must contain `S_B`,
so `|S_B| <= q` is necessary. Conversely, if every block has `|S_B|<=q` and
each negative n has some block B with `pi_B(n) not in S_B`, selecting each
local language to be exactly `S_B` accepts every positive and rejects every
negative. Thus these two conditions are necessary and sufficient for a fixed
partition. The second condition also supplies a checkable witness for every
negative.

This condition distinguishes factor languages from observed sets: an actual
compatible factor could contain extra unobserved words, but for finite-sample
existence it is sufficient to choose exactly the observed projections. For
each negative, rejection by any compatible factor implies its projection is
outside `S_B`, since that factor contains every observed positive projection.

## Pair q-opposition must-link-to-separation edges

For each unordered pair `{a,b}`, let `D_ab` be the set of distinct positive
projections onto `{a,b}`. If a and b lie in one block B, then every projection
onto `{a,b}` is obtained by projecting `pi_B(p)` again. This is a function
from `S_B`, so `|D_ab| <= |S_B| <= q`. Therefore

`|D_ab| > q  =>  a and b cannot belong to the same block`.

The implication holds for any positive sample, arbitrary repetitions, and any
k. Edges are sound cannot-links for the q-bounded model. At q=1 this reduces,
for nonempty positive samples, to the singleton opposition edge: a pair is
opposed exactly when its positive binary projection is not constant.

For a singleton set U={a}, the same implication has a different consequence:
if a has more than q distinct positive unary projections, no partition can
work, because a must belong to some block. This is a direct infeasibility
certificate and should be checked separately; it cannot be represented as a
pairwise cannot-link edge.

## Complete-k-partite uniqueness certificate

Let Gq contain exactly the pair edges with `|D_ab| > q`. Every compatible
partition is a proper coloring of Gq. If Gq is complete k-partite with k
nonempty parts, those parts form the unique unordered surjective k-coloring:
one representative from each part forces k distinct colors, and every other
vertex is adjacent to the representatives of all other parts, leaving only
its own part’s color. This gives one candidate partition for arbitrary known
k. Do not replace the graph-property check with connectedness for k>=3.

The candidate still needs the full fixed-partition feasibility check, because
pair projection counts do not establish `|S_B|<=q` for a larger block. Check
all positives to form each complete block projection set, verify its full
cardinality is at most q, and for every negative return an unseen full-block
projection. If the unique candidate fails either check, no other q-compatible
partition exists (all would have to be proper k-colorings of Gq), so it is
infeasible within this bounded model. If Gq lacks the complete-k-partite
certificate, the method must abstain or use a separate exact coloring/search
provider; it has not shown infeasibility or uniqueness.

## Why the full-block cardinality check is necessary

For q=2, take alphabet `{a,b,c}` and positives
`abc`, `bca`, `cab`, `acb`. The three core words `abc`, `bca`, `cab` are
different orderings of the same three-symbol word; the fourth is a different
ordering. Every binary pair sees at most two distinct projections:

| Pair | Distinct projections |
|---|---|
| `{a,b}` | `ab`, `ba` |
| `{a,c}` | `ac`, `ca` |
| `{b,c}` | `bc`, `cb` |

Thus G2 has no edges, yet the full projection set onto `{a,b,c}` has four
distinct words, which cannot fit in a local language of size two. In
particular, pairwise tests alone cannot validate an all-symbol block. The
direct full-block check catches this. This is a mathematical example, not an
executed experiment.

## Boundary cases and claims

- With a nonempty positive sample, each block has at least one observed
  projection, including when some projection is epsilon. The empty *word* and
  empty *positive sample* are different cases.
- With no positive samples, there is no reference projection set. Whether an
  empty local language is allowed is a separate semantics choice; this
  certificate makes no conclusion. Do not infer singleton-exactly-one target
  recovery from an empty positive sample.
- At q=1 and nonempty positives, `|D_ab|>1` is the singleton opposition
  condition. At q>1, pair edges are only necessary constraints; they are not
  the full feasibility test.
- A returned compatibility witness establishes existence. Unique recovery is
  only class-conditional on known k, finite local languages of size at most q,
  exact labels, and the graph certificate. No arbitrary-DFA or unknown-k
  identification claim follows.
- The certificate is sufficient and potentially sparse. Failure to find its
  graph shape must not be reported as infeasibility.

## Conclusion

C004-QOP001 is mathematically sound as a polynomial sufficient certificate
when the pair graph is exactly complete k-partite and the implementation also
checks full-block positive cardinalities and all negative witnesses. Its key
benefit is the q-aware threshold `>q`; its limitation is that pair counts do
not enforce full-block cardinality. No code or experiments were used to reach
this conclusion.
