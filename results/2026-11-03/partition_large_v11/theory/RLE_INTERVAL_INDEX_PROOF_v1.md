# C011 bounded refinement: maximal binary intervals from RLE transitions

Direct proof, independent review pending; no runtime or provider edits.
This refines T2 of PROOFS_AND_RECOMMENDATION_v1.md, replacing the naive
all-alphabet-pairs discovery proposal. All earlier artifacts remain intact.

## 1. Linear interval enumeration

Run-length encode a word as (c₀,length₀),...,(c_{t−1},length_{t−1}), with
adjacent c's unequal. Record character start/end positions for each run.
For each transition i=0,...,t−2 let e_i be the unordered pair {c_i,c_{i+1}}.
Group consecutive transitions with equal e_i. A group of transitions i..j
defines the character interval spanning whole runs i..j+1, with alphabet e_i.

**R1.** These windows are exactly all maximal contiguous two-symbol intervals
that contain both symbols. No alphabet-pair enumeration is required.

Proof. All runs in a group alternate within its fixed pair x,y. If the
previous run were also x or y, its transition with the first window run
would have pair {x,y} (adjacent run labels differ), extending the group,
contradiction. The following boundary is symmetric. Thus the window is
maximal. Conversely a maximal pair-only interval containing both letters
must start/end at full run boundaries: trimming inside a boundary run
could be extended. Its interior transition pairs all equal its two-symbol
alphabet and its boundary transitions cannot, so it is exactly one group. ∎

For t≤1 there are no such windows. This loses no nontrivial two-letter
anagram witness: unequal equal-count middle words must contain both letters.

**R2.** There are at most t−1 windows and each run belongs to at most two.
If g is the number of groups, total run-window memberships are (t−1)+g
≤2(t−1). Total character length over windows is at most 2|w|.

Proof. Each run is incident to at most two transitions; the groups of those
transitions are the only groups whose windows contain it. A group with h
transitions has h+1 runs; sum h=t−1. Character lengths are counted at most
twice because every character lies in exactly one run. ∎

Therefore RLE, grouped-transition enumeration, exact per-window counts and
rolling fingerprint preprocessing can be organized in O(|w|) basic character
work per word, excluding dictionary big-integer/key overhead and exact-context
comparisons. Counts may also use alternating run totals. This is a bound on
candidate generation, not a bound on the full solver or hash-collision work.

## 2. Exact keys and contextual completeness

For window [l,h) on pair x<y form

    (|w|, l, h, x, y, count_x(window), count_y(window),
     fingerprint(w[:l]), fingerprint(w[h:])).

Fingerprints must be deterministic within the indexed run and identical
strings must get identical fingerprints. Collisions are permitted only as
extra candidates. Positions and counts are exact integers.

**R3.** Every contextual binary-anagram positive/negative pair from T1 has
matching maximal-window keys.

Proof. Write p=u s v, n=u t v, with s,t over the same two symbols and equal
per-letter counts. They have equal length; unequal opposite-label words
require both symbols. Extend both middle intervals left through the maximal
pair-only suffix of u and right through the maximal pair-only prefix of v.
The extensions are identical on the two words. Thus the resulting windows
have identical character boundaries, alphabet, counts and outside context,
and are maximal. R1 enumerates them, and equal outside strings produce
equal fingerprint components. ∎

This includes every exact adjacent swap and aabb/bbaa, with arbitrary shared
context. Completeness concerns these witness rules, not all semantic must-links.

## 3. Collision-safe representative storage

Inside each coarse fingerprint bucket, maintain one positive representative
for every **distinct exact outside context**. With common |w|,l,h, pair and
counts already in the key, compare representative[:l] and representative[h:]
exactly when deciding whether contexts coincide. Different-context collisions
must retain separate representatives. Store references/offsets rather than
unconditionally copying long contexts; slice allocation/comparison cost must
still be accounted for in the actual implementation.

For every negative window, scan all relevant exact-context representatives
in its coarse bucket until an exact match is found. Recheck actual positive/
negative labels, the stored intervals/pair, exact outside equality and exact
window counts/alphabet before inserting the edge. Emit a replayable witness
identifying the words, [l,h), pair and counts. Opposite labels in consistent
input ensure the two complete words are unequal; an explicit unequal-middle
check is harmless and makes the certificate premise transparent.

**R4.** One positive per exact context suffices to find an edge for every
negative window having a matching positive context/count/pair.

Proof. All positive representatives within one exact context and fixed key
have identical outside strings and the required pair counts. Thus any one
of them and the negative meet T1's premises. It cannot equal that negative
on the complete word because the label sets are disjoint. R3 ensures every
T1 positive/negative witness lands in such a group. Exact verification makes
every emitted edge sound, including when many unrelated contexts collide. ∎

Pseudocode (character positions, canonical unordered pairs):

```text
positive_index = {}
for p in positives:
    for interval in grouped_RLE_transition_windows(p):
        key = exact_fields_and_outside_fingerprints(p, interval)
        if no representative in positive_index[key] has same exact outside:
            retain reference(p, interval)
for n in negatives:
    for interval in grouped_RLE_transition_windows(n):
        key = exact_fields_and_outside_fingerprints(n, interval)
        for representative in positive_index.get(key, []):
            if verify_exact_T1_premises(representative, n, interval):
                union(pair); retain replayable certificate; break
```

Once a pair is already connected, additional certificates may be omitted if
only a sound graph is required; then do not promise a list of every witness.
Graph completeness is not needed for correctness of the exact fallback.
No candidate index may interpret a missing edge as independent ownership.

## 4. Counterexample attempts and cost limits

* **First representative per fingerprint bucket only:** rejected. Force a
  fingerprint collision for different exact contexts. If the retained
  positive has the wrong outside context, verification fails and the correct
  discarded positive is never tried. This loses extractor completeness even
  though it does not create an unsound edge. Exact-context representatives
  repair it. No actual hash-collision experiment was run.
* **Group transitions merely sharing a symbol:** rejected. For word abc,
  pairs ab and bc share b but their joint interval has three symbols. Groups
  must have identical unordered pairs, not intersecting pairs.
* **Scan only mismatching-position symbols:** rejected by acb/bca with the
  consistent independent countermodel ac|b, factors {ac},{b}; the unchanged
  interior c must be included in interval verification.
* **Assume linear total runtime:** rejected. Context comparisons may traverse
  long shared strings or hash-collision buckets, and emitted expanded witness
  text/output can dominate. Even without adversarial collisions, repeated
  exact comparison of long common contexts can cost substantially more than
  RLE enumeration. No guaranteed linear indexing-plus-verification theorem
  or general speedup follows from R2.

## 5. Shared witness computation, unchanged output

Memoizing exact projection records by canonical unordered partition and
immutable fixed sample preserves every record. Same/different pair rows may
internally reference a shared immutable witness partition without omitting
rows or fields from default expanded JSON. If output consumers can mutate
objects, avoid exposing shared mutable state or define copy semantics.
The time to serialize repeated data remains part of same-output comparison.

Recommendation: implement RLE interval enumeration plus collision-safe exact
verification and shared immutable projection/witness computation first;
retain the existing exact atom DP. Acceptance and resource benefit require
the independent frozen gate and preregistered comparison, not this proof.
