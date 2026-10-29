# Read-only review of the q=2 certificate and constructive coverage family

**Review ID:** C004-G-QCAP-FAMILY-001  
**Type:** independent proof review; no provider/test/experiment run  
**Conclusion:** the q-opposition inference and the prepared k-partite q=2 construction are sound under their stated conditions. The construction is sufficient, not a claim about arbitrary passive coverage.

## Reviewed proof/source identity

- `structural/PROOFS_QOP001_PREPARED.md` — SHA-256
  `b299cf86d4bf5e4a7f6378630b96d76a5aa5938472525bd51ef27c2fdea919c6`.
- `structural/bounded_certificate_v1.py` — SHA-256
  `0a8e542d3d44650f454e779137a5c9ac1057cd863bc162c94b45519f253636d5`.

This is static analysis only. It does not provide independent execution or
audit acceptance for the prepared provider.

## q-opposition inference

Fix a q-bounded product partition. For a block B, each pair projection
`pi_{a,b}(p)` is the image of the full local projection `pi_B(p)` under the
eraser map from B to `{a,b}`. An image cannot have more distinct values than
its domain. Since every observed full local projection must be in a local
language of cardinality at most q, a pair with more than q distinct positive
binary projections cannot be contained in a single block. Thus the >q edges
are necessary cannot-links.

Every feasible partition is consequently a proper surjective k-coloring of
the q-opposition graph. If the graph is complete k-partite with k nonempty
parts, the unordered coloring is unique by the representative-per-part
argument. All feasible partitions must equal that candidate. A direct check
that each complete block has at most q distinct positive projections and that
each negative has an unseen full-block projection is still essential. If
either check fails, the unique graph coloring is the only possible candidate,
so infeasibility within the bounded model follows. If the graph does not have
the unique-coloring certificate, failure of this method means unresolved
coverage, not infeasibility.

For singleton U={a}, >q distinct unary projections are different: a must be
assigned somewhere, so the condition refutes all partitions directly. The
prepared implementation checks this separately via distinct occurrence
counts. For nonempty positive samples, q=1 pair edges coincide with
singleton opposition; the empty-positive case is separately returned as
unresolved coverage, so it is not conflated with an observed epsilon local
word.

## Three-core-plus-fourth q=2 construction

Let there be k>=2 blocks of equal size s, and list the distinct symbols of
each block in a fixed internal order. For block i let `u_i` be that list
repeated twice, so every `u_i` has length 2s. Form positives:

1. `u_1 u_2 ... u_k`;
2. `u_k ... u_2 u_1`;
3. the round-robin interleaving of the k equal-length `u_i` streams, preserving
   order within each stream;
4. `(u_1 a_1)(u_2 a_2)...(u_k a_k)`, where `a_i` is the first symbol of block i.

For any two distinct symbols in one block, positives 1–3 project to the same
binary word: each component’s internal order is preserved and other blocks
erase away. Positive 4 contributes the projection of `u_i a_i`, so at most
two different local pair words occur. On the complete block, the observed
local words are exactly `{u_i, u_i a_i}`; the fourth positive makes the
second word genuinely distinct.

For a cross-block pair a,b, the first two positives project to `aabb` and
`bbaa` (each appears twice in its block word). In the round-robin trace, a and
b each occur at two positions in their respective equal-length streams. If
the first occurrence position of a precedes that of b within a block word,
the projected order is `abab`; if b’s position comes first, it is `baba`.
The two letters’ occurrence positions repeat in the same cycle, so these
alternating orders differ from both concatenation orders. Consequently the
binary pair has at least three distinct positive projections and becomes a
q-opposition edge for q=2. The graph is exactly complete k-partite: no
within-block pair is an edge, and every cross-block pair is.

The graph fixes the planted partition. The full local sets `{u_i,u_i a_i}`
have size two, so all positives fit. Adding epsilon as a negative is valid:
each `u_i` is nonempty, hence every factor’s observed projection set excludes
epsilon, giving an unseen projection (indeed in every block). This can make
the sample demonstrate negative-witness output too.

Equal block sizes are needed for the round-robin streams to have matching
length and for the fourth word construction to have the stated uniform local
sets. Repeated symbols in each `u_i` (two copies per symbol) are needed for
the `aabb` / `bbaa` / alternating pair patterns. Without these conditions,
the proof as written does not establish the complete q-opposition graph.

## Smallest prepared instance checked algebraically

For `ab|cd`, take `u_1=abab`, `u_2=cdcd`. Positives 1–4 are
`ababcdcd`, `cdcdabab`, `acbdacbd`, `ababacdcdc`. Local word sets are
`{abab,ababa}` and `{cdcd,cdcdc}`. For the cross pair `{a,c}`, the four
positive projections are `aacc`, `ccaa`, `acac`, and `aaaccc`, so the q=2
edge is present; by symmetry every cross pair has >2 values. Pair `{a,b}`
has only `abab` and `ababa`; `{c,d}` has only `cdcd` and `cdcdc`. Thus the
graph is K2,2, the full q=2 checks pass, and epsilon is a sound negative.
This instance was checked by hand only and is not execution evidence.

## Conclusion and boundary

The inference is sound because pair projections are functions of a larger
block projection; the q-cap applies to each local language, not merely to
pair data. The complete-k-partite graph is a sufficient unique-candidate
certificate only. Direct full-block cardinality and negative checks cannot
be omitted. The constructive family proves that q=2 instances can have a
complete k-partite opposition graph even when each block has two local words;
it says nothing about the frequency of such coverage in arbitrary samples.
