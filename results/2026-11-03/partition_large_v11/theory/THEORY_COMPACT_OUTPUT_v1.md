# C011 future note — lossless compact ownership certificates

Status: proposed mathematical representation, not implemented, activated or
benchmarked. No source, protocol or timing changes to the current candidate.
No runtime or speed result is claimed. The current default expanded contract
remains authoritative. This closes the bounded theory scope for this round.

## 1. Why expanded witnesses can dominate

Let m be the symbol count. There are m(m−1)/2 unordered symbol pairs. A full
partition witness contains each of the m symbols exactly once, irrespective
of its block count. Each pair row may contain one or two such witnesses.
Thus repeated witness-symbol occurrences alone are O(m³) in expanded output.
This is not merely a loose upper bound: in the all-coarsenings family with
m singleton atoms and m≥2, every pair has the one-block same witness and
the singleton-partition different witness. There are exactly

    2m * binomial(m,2) = m²(m−1)

witness-symbol occurrences, hence Θ(m³). Even repeated copies of only the
same witness would suffice for a cubic lower bound. This counts symbol
occurrences, not serialized bytes: symbol identifier lengths, punctuation,
encoding and integer digits contribute separately.

Sharing Python objects internally avoids some construction/allocation but
ordinary expanded JSON serializes their contents at every occurrence. It
does not automatically remove that output-size lower bound.

## 2. Exact witness registry: preserve an existing output verbatim in information

Canonicalize each distinct unordered partition (sorted symbols within each
block, blocks sorted by a fixed total order). Store its exact partition value
once in an immutable registry under an unambiguous ID; replace every witness
occurrence with that ID. Preserve null witness markers explicitly. If exact
list ordering of the original output is contractual, either retain its stored
ordered value as the registry entry or retain a permutation descriptor at
each reference; canonicalization alone must not silently change ordered JSON.

**C1.** This encoding is lossless: recursively replace every reference by a
copy of its registry entry, applying any stored ordering descriptor. Every
original field, null and witness list is recovered. Proof is immediate by
induction on the JSON tree: primitive/nonreference nodes are unchanged, and
each reference is replaced by exactly the subtree it replaced. ∎

Identifiers must refer to exact entries, not unchecked hashes. A digest can
index entries, but equality must be checked and collisions separately stored.
Expansion must reject missing IDs, malformed partitions and invalid reference
types, not substitute a guessed witness. A partition-only registry does not
by itself encode projection records; those must be preserved separately or
reconstructed from an explicitly bound immutable sample and verified procedure.

With d distinct witnesses, their symbol payload is O(dm), plus O(m²)
references. This may be much smaller but does not guarantee d is small:
an arbitrary exact output can contain many distinct witnesses. Expansion
still has the full original output cost.

## 3. Atom-pair representation for generic exact DP results

Let A₁,...,A_r be sound must-link atoms covering all symbols, and assume a
nonempty fully characterized compatible partition family F of size Z.
Every member of F coarsens the atoms. Let atom(i) denote the atom of symbol i.

**C2.** For any distinct symbols i,j:

* If atom(i)=atom(j), their coownership count is Z and difference count zero.
* Otherwise their coownership indicator in every Π∈F depends only on the
  unordered atom pair {atom(i),atom(j)}. Thus every original symbol pair
  crossing that same atom pair has identical exact counts and relation.

Proof. No feasible partition splits an atom. Its quotient partition puts
two atoms together or apart as whole sets. The indicator for any two chosen
representatives from those atoms is therefore identical in every Π.
Summing over F proves equal counts. ∎

Consequently a compact logical certificate can contain: the symbol-to-atom
map, Z and other global exact fields, one same/different count record per
unordered atom pair, a shared witness registry, and one global same-atom
witness. Original pair rows can be generated in canonical symbol order.
If an atom-pair witness puts its atoms together/apart, it witnesses that
relation for every crossing symbol pair; the same full partition can be
referenced for all those rows. This holds in the generic fallback DP too,
not only in a closed-form family. Sound contraction, not graph completeness,
is the premise.

Two notions of losslessness must be distinguished. C1 can reproduce the
exact chosen witnesses of an existing result. C2 preserves all exact counts,
relations and valid witness information but may choose one common witness
instead of different valid witnesses previously chosen for individual pairs.
If literal equality of previously chosen JSON witnesses is required, retain
per-symbol-pair witness-ID overrides (and ordering metadata) as needed.
The count/atom table alone cannot encode arbitrary earlier witness choices.
A future compact API must explicitly define deterministic expansion or this
override policy; it must not promise identical bytes without it.

If r=1, there are no distinct-atom records. All actual symbol pairs, if any,
have count Z and a same witness; no different witness exists. If m=1, no
symbol-pair row exists. If the version space is empty, do not instantiate
universal pair rules vacuously: preserve model-inconsistent status and absence
of pair claims. An incomplete result likewise cannot be promoted to a compact
exact certificate merely because its unfinished tables are small.

## 4. Closed-form all-coarsenings certificate

If the atom partition itself passes the direct projection criterion, the
feasible family is all atom coarsenings. Its entire pair-count rule is

    same atom:       q=Z=Bell(r), d=0;
    different atoms: q=Bell(r−1), d=Bell(r)−Bell(r−1), for r≥2.

Per-k totals are S(r,k); distinct-atom per-k same counts are S(r−1,k).
The registry needs only the one-block same witness and the feasible atom
partition as a different witness (the two coincide at r=1, where no distinct
atom pair exists). The atom map and these two rules can expand all m(m−1)/2
rows without storing an atom-pair table. It still needs the exact fixed-input
projection evidence and sound must-link certificates proving the premises.
It is not evidence that the finest atoms are physical truth: their coarsenings
are alternative compatible ownerships.

## 5. Counts, immutability and honest cost accounting

Big-integer magnitude is distinct from witness duplication. Bell(r) grows
with r, so its decimal representation has a growing digit count. A simple
upper bound Bell(r)≤r^r gives O(r log r) bits for a count; for r≥2, pairing
the first floor(r/2) symbols independently with distinct partners already
gives at least floor(r/2)! partitions, yielding Ω(r log r) bits asymptotically.
Thus total-count bit length is Θ(r log r). Exact decimal rendering cannot
be treated as constant-size. Repeated integers can also use typed references,
or a closed-form rule with an exact integer arithmetic specification; do not
round counts into floating point. Storing the entire per-k spectrum costs
additional digits even if pair-witness repetitions are removed.

Registry entries and the bound input should be immutable. Returned mutable
aliases allow one caller mutation to corrupt many expanded witnesses. A
decoder can return independent copies, immutable views, or a clearly declared
read-only result. The certificate must bind its format/version and exact
sample identity so references are not accidentally reused across datasets.

A future performance study must compare expanded-output methods on the same
expanded contract, and report compact-mode size/time separately. Smaller output
is a useful separate product mode, not evidence of a faster identical-output
solver. Compression does not remove the exponential fallback worst case or
physical non-identifiability. Beyond128 symbols this is a concrete path to
lower output/storage cost for structured atom families, not a demonstrated
capacity or speed guarantee for this round.

## Preserved rejected claims

1. Internal object interning automatically compresses JSON: false.
2. Atom-pair counts retain arbitrary original witness choices byte-for-byte:
   false without witness overrides/order information; C1 handles exact recovery.
3. Sound atoms require a complete must-link graph: false; soundness suffices.
4. Small symbolic rules imply constant-size exact counts: false; digit costs grow.
5. A compact incomplete table certifies uniqueness: false.
6. Compact versus expanded time is an identical-output speed comparison: false.

No experiments, source changes or benchmark claims accompany this note.
