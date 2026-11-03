# C011 I003 — multiple binary rearrangements and trace normal forms

Scientific status: direct proofs ready for independent review.
Implemented=false; measured=false; no code, experiments or current candidate
changes. This is future research and does not delay the frozen candidate gate.

## 1. Concrete limit of the single-interval index I001

Let p=abcab be positive and n=bacba be negative. Their unary counts agree
(a:2,b:2,c:1). Binary projections are

    pair    p       n
    ab      abab    baba
    ac      aca     aca
    bc      bcb     bcb.

Thus a,b are forced to coown. Proof without invoking reconstruction: if
they were separate, every block is a subset of either {a,c}, {b,c}, or a
singleton (no block may contain both a,b); projection equality on ac and
bc and their subsets makes p,n identical on every block. A positive and
negative could not then be distinguished. Contradiction.

The data are consistent: local finite factors {abab} on ab and {c} on c
accept p and reject n. This is not a vacuous conclusion from empty models.

No one contiguous binary-anagram interval has identical outside contexts:
the first differing position is 0 and the last is 4, so any replacement
interval covering all differences must be the whole five-letter word,
which contains three letters. The I001 exact-context single-window index
therefore cannot match these two words, although both of their ab windows
are independently rearranged. It must not be described as complete for all
semantic must-links. Its prior completeness theorem concerned only the
single-interval witness rule, so that theorem is not refuted.

An implementation retaining the exact uncontracted fallback remains correct
if this edge is missed. Missing graph edges are not proofs of independence.

## 2. A stronger exact pair normal form

Fix x<y. Decompose any word uniquely as

    s₀ z₁ s₁ z₂ ... z_h s_h,

where each z_i is a single letter outside {x,y}, in its original order,
and each s_i∈{x,y}* (possibly empty). Define C_xy(w) by replacing each
s_i with x^(#x(s_i)) y^(#y(s_i)), leaving all z_i in place.
In practice one need only transform maximal pair-only intervals containing
both letters: unary/empty segments already equal their own normal forms.

**I003-T1.** C_xy(p)=C_xy(n) iff p and n can be transformed into one
another using only adjacent commutations xy↔yx, in any number of segments.

Proof. One such commutation preserves the outside-letter sequence and
counts within each gap, so preserves C_xy. Conversely within each gap,
adjacent swaps bubble all x's before all y's, reaching the canonical sorted
segment while never crossing an outside letter. Both words reach the same
canonical word when their normal forms coincide; reversing one path gives
a commutation path between them. ∎

**I003-T2.** If an opposite-label p,n have equal C_xy forms, then x,y
coown in every compatible model.

Proof. If their owners were separate, each allowed adjacent commutation
would leave every block projection unchanged. By T1 a sequence of those
commutations relates p,n, so all block projections are equal, contradicting
their labels. ∎

For the concrete example C_ab(abcab)=abcab and C_ab(bacba)=abcab; the
stronger rule finds the forced pair beyond I001. It still does not claim
completeness for every semantic must-link in arbitrary labelled samples.

## 3. Relation to the primary trace-projection lemma

Let the only independent ordered letter pairs be (x,y) and (y,x); every
other pair, including diagonals, is dependent. Equality in that trace
monoid is exactly the commutation equivalence of T1. The projection lemma
characterizes it by equality on all dependent-pair projections. Thus this
is equivalently equality of all unary counts and all binary projections
except possibly {x,y}. Unequal opposite-label words then have precisely
the sole binary distinguishing support {x,y} after redundant supports are
removed. This matches the general support argument already in C002 and
C011 T3, rather than a new trace-theory theorem.

Primary source: Köcher, Kuske and Prianychnykova, *The inclusion structure
of partially lossy queue monoids and their trace submonoids*, RAIRO52(2018),
55–86, Section6, Proposition6.1, DOI10.1051/ita/2018003,
https://www.numdam.org/item/10.1051/ita/2018003.pdf .
The limited source review is recorded in SOURCES_v1.md. T1/T2 above also
give direct proofs, so no transfer of unrelated queue-model assumptions is
needed.

## 4. Future candidate discovery, not a proven fast implementation

For each observed pair x,y, transform **all** of that pair's maximal
segments, not just one. A possible index key is pair, length and a rolling
fingerprint of C_xy(w). Compute a candidate canonical fingerprint as the
full word fingerprint plus replacement deltas for its disjoint pair windows,
with position-weighting and exact counts. Match opposite labels by key,
then compare their complete canonical streams exactly before unioning x,y.
The streamed verifier emits sorted letters within each segment and original
outside letters, so need not materialize a separate full canonical string.

Hash equality is only a lookup filter. Each fingerprint bucket must retain
representatives of distinct **exact canonical forms**; keeping only its first
word can hide a valid match after a collision. Exact verification prevents
unsound edges, and exact-form representative separation is needed for the
claimed discovery completeness. In a consistent labelled sample an opposite
label cannot be the identical word.

RLE transition grouping enumerates windows for all observed pairs with total
window characters at most twice word length (RLE_INTERVAL_INDEX_PROOF_v1.md).
For a fixed pair these windows are disjoint, allowing delta contributions
to be summed. That combinatorial fact does not yet prove a linear complete
implementation: repeated-symbol fingerprint sums, modular powers, per-pair
key storage, exact canonical-stream comparisons, collisions and shared-context
verification all need explicit cost accounting. A word can participate in
many pair comparisons even if window enumeration is linear.

No repeat-symbol hash formula, collision policy, runtime bound or speedup
has been implemented/benchmarked here. No pure digest replaces exact checks.
Any future implementation must preserve default output, receive a new frozen
source version and independent gate, and keep the exact fallback.

## 5. Preserved failed hypotheses and bounded decision

* “I001 finds every forced pair”: rejected by abcab/bacba above.
* “Sorting only one selected pair window is complete for global xy
  commutations”: rejected by the two separated ab windows in that example.
* “Equal total x/y counts suffice”: rejected by acb/bca and compatible ac|b;
  outside-letter barriers and per-gap counts matter.
* “Equal canonical fingerprints suffice”: rejected as a correctness rule;
  digest collisions need exact streamed comparison and separate exact groups.
* “Linear total window length proves linear whole indexing”: unsupported;
  verification, arithmetic, key/collision and output costs remain.

Decision: retain the stronger normal-form rule as a sound THEORY-ONLY future
candidate. The current candidate, its protocol and its gate are unchanged.
