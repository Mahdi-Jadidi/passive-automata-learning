# C011 phase 1 — exact reductions for larger trace collections

Direct proofs; independent review pending. No runtime, novelty, measured speed
or completeness-of-literature claim. C010's no-K independent unrestricted
regular-factor model, exact complete-word labels and full output remain fixed.
Faster computation cannot remove its physical-identifiability obstruction.

## T1. Contextual two-letter anagram interval must-link

Suppose p=u s v is positive and n=u t v is negative, x≠y,
s,t∈{x,y}*, and #x(s)=#x(t), #y(s)=#y(t). Then x,y coown in every
sample-compatible partition. In consistent input s≠t automatically.

Proof. If owners differed, a block containing x but not y would project s,t
to the same unary x word. The y-owner similarly sees the same unary y word;
other blocks see epsilon. The identical contexts u,v also have identical
block projections. Thus every block sees the same local word for p and n.
Any independent product accepting p must accept n, contradiction. ∎

This catches aabb/bbaa, as well as adjacent swaps. It works with arbitrary
outside context containing x,y or other symbols; context must be identical
and outside a contiguous replacement interval. A sound verifier checks exact
prefix/suffix equality, middle alphabet containment, two exact counts and
opposite labels. A candidate hash alone is never proof.

An equivalent convenient verifier uses equal word lengths, strips their
maximal common prefix and a nonoverlapping common suffix, and checks that
the remaining entire intervals use only x,y and have equal counts. If some
valid interval exists, stripping more equal boundary letters preserves the
two-letter/count premises. No unequal-length replacement can have equal
counts over exactly the same two-letter alphabet.

### Rejected extension and explicit regular countermodel

p=acb, n=bca differ only at positions containing a/b, with equal a/b counts,
but the interval also contains c. The partition ac|b distinguishes them:
π_ac(p)=ac, π_ac(n)=ca. Choose local finite languages {ac} and {b}; the
product accepts p and rejects n with a,b separated. Therefore identifying
only letters at mismatching positions is UNSOUND. Preserving counts without
preserving the order relative to interior third letters is insufficient.

## T2. Indexed discovery can avoid irrelevant cross-label comparisons

Every T1 witness has equal full Parikh vectors (all per-letter counts).
Thus exact Parikh-vector bucketing excludes word pairs that cannot satisfy
T1. Comparing only opposite-label words within a bucket is complete for
this rule. Complexity is linear in total input length for count extraction
plus the cross-products inside buckets; worst-case all words share a vector,
so the quadratic positive-negative scan is not eliminated in general.

A stronger optional index: for a chosen pair x,y, enumerate each maximal
nonempty contiguous {x,y}-run in every word. Key it by exact outside prefix,
outside suffix, x,y and the two run counts. An opposite-label match with
unequal run strings is a T1 witness. To see coverage, extend any valid T1
interval to maximal pair-only runs. Identical outside context extends both
by identical pair-only prefix/suffix portions; equal counts and contexts
remain, giving the same key. This proves completeness for each enumerated
pair, not a cheap implementation for all pairs.

Naively doing this for all pairs can cost O(m² times total input length),
and copying long prefix/suffix strings for every run can use quadratic
space in word length. Shared offsets/tries or hashed lookup followed by
exact verification can reduce candidate-index overhead, but require their
own implementation accounting. A bounded subset of candidate pairs/runs
is safe if every inserted edge is verified: missed edges only weaken
contraction; they do not remove valid partitions from the exact fallback.
The graph must not be advertised as a complete must-link relation then.

## T3. Unary/binary distinguishing supports give exact block tests

Reuse the established C002 lemma: two words are equal iff all singleton
and two-letter projections agree (singletons handle unary boundaries).
Proof: unary counts agree; unequal words with equal counts have a first
different letter after their common prefix, say x versus y. Projecting onto
{x,y} retains that disagreement. Equal counts rule out a proper-prefix case.

Let D(n,p) contain all size-one/two sets U whose projections distinguish n,p.
Then for every block B,

    π_B(n)≠π_B(p) iff some U∈D(n,p) satisfies U⊆B.

Forward: apply the lemma within B. Reverse: equality on B would remain
equality after projecting to U. Pairs containing an already distinguishing
singleton are redundant and may be removed while retaining that singleton.

For each negative n the exact block-rejection function is therefore

    R_n(B) = AND_{p∈P} OR_{U∈D(n,p)} [U⊆B].

Empty AND is true (no positives); empty OR is false. This formula is valid
for arbitrary blocks, so it can supply exact lazy masks to C010's atom DP.
Its quantifiers matter: the SAME B must distinguish n from EVERY positive;
one cannot choose a different rejecting block for each positive when testing
an entire partition. Conversely projection equality with some positive
requires one fixed positive to match on all relevant unary/binary supports.

If D(n,p) consists solely of {x,y}, that pair must coown in any compatible
partition: otherwise no block contains a distinguishing support and n,p
match on every block. More generally several alternative pair supports
give a disjunction; forcing every pair as an edge would be unsound.

Precomputing exact unary counts and binary projection strings once per
word permits repeated support comparisons without scanning full words for
every block. However up to |N||P| families with O(m²) entries each can be
needed, with binary strings/projections also costly. This can lose badly
on large data even when it reduces DP block-query time. Compile lazily,
deduplicate identical support families and compare against direct cached
projections; no claimed dominance. This revisits C002 rather than inventing
its reconstruction lemma. The primary references are in SOURCES_v1.md.

## T4. Exact cache and witness reuse

For a fixed immutable sample, π_B(w) is a pure function of expanded block B
and exact word w. Sharing it across mask construction, direct feasibility
and witness construction preserves every value. Cache boundaries must use
canonical symbol/atom sets, not unstable object IDs. A cached projection
language is a set of exact strings, not unverified hash digests.

Different pair rows often refer to the same partition witness. Canonicalize
the unordered blocks, compute that witness once and reuse its immutable
contents internally. Default expanded JSON can still contain all required
rows and witness fields; deduplication must not silently change output.
Copying/serialization may dominate even when calculation is shared. Time
comparisons must include the same full output; compact mode needs a separate
contract and reconstructible expansion.

## T5. Symbolic and parameterized directions: limited recommendation

BDD/ZDD representations can compile Boolean block tests or feasible set
families, and exact-cover/ZDD work is directly relevant (SOURCES_v1.md).
But a graph-partition frontier algorithm does not directly solve arbitrary
trace compatibility: a frontier state must retain sufficient positive-match
or negative-coverage information. Dropping that information merges unequal
subproblems and loses exactness. No small frontier/treewidth bound follows
from large trace count or a missing must-link edge. Diagram variable order
and size can be decisive; worst-case exponential blowup remains possible.

Useful independent cost axes: total input characters and unique |P|/|N|;
alphabet size m versus contracted atoms r; reachable negative-coverage masks;
number of distinct projection/support signatures; and expanded output size.
A large |N| can increase DP coverage dimension even for modest r. Reducing
one axis does not bound the others. No parameterized runtime theorem or
NP-hardness claim for this exact problem is asserted from related literature.

## Bounded implementation recommendation

First retain the C010 exact fallback and default output; add exact count
signatures to avoid irrelevant pair scans, verify T1 intervals for selected
candidates, and share projection/witness results. All extracted edges must
carry replayable labels and interval evidence. Missing candidates are safe
because graph completeness is unnecessary for sound contraction. Every
shortcut must still check full atom-partition feasibility.

Only if measured block projection work dominates, consider T3 lazy support
compilation as a separately frozen candidate. Full support preprocessing or
a new decision-diagram engine is not recommended as the first bounded
implementation: memory/coding cost and possible negative performance need
separate evidence. Stop after the preregistered comparison, preserving slower
and censored cells. No runtime has been performed by this theory author.
