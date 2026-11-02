# C009 — Exact cover, trusted count sets, and partial ownership

Status: direct proofs ready for independent review. No experiments, new
dependencies, novelty claim, or general speed claim. The algorithms below
are exponential in the worst case and identify physical ownership only
conditional on the declared model assumptions being true.

## 1. Model and target

Let Σ be a known finite nonempty alphabet of m symbols. A model consists of
an unordered partition Π into nonempty disjoint blocks and arbitrary regular
local languages F_B⊆B*. Its global language is

    L = {w∈Σ*: π_B(w)∈F_B for every B∈Π}.

Projection erases other symbols and preserves order. The input S=(P,N)
contains finitely many exactly labelled complete words. A trusted set
K⊆{1,...,m} specifies permitted component counts. With no count information,
K={1,...,m}. K may be noncontiguous. The true model is assumed to satisfy
these conditions, including |Π_true|∈K. There is no prime-factor, state-size,
nonempty-language, positive-only sampling, or additional coverage restriction.
Nonempty **blocks** must not be confused with nonempty **local languages**.

Ownership means the unordered partition, not names/IDs of physical devices.
Anonymous observations cannot resolve a permutation of those names.

Write V(S,K) for all such consistent models and A(S,K) for their distinct
partitions. Exact ownership means |A|=1. Partial ownership quantifies over
all Π∈A. If A is empty, the assumptions/data are inconsistent and no pair
relation or ownership is vacuously identified. Exact statements require
completed computation or a separate complete mathematical certificate.

## 2. Block rejection masks give exact feasibility

Index negatives by j=0,...,n−1, and let T be the set of all such indices.
For every nonempty block B⊆Σ define

    H(B) = {π_B(p):p∈P},
    R(B) = {j∈T: π_B(n_j)∉H(B)}.

Use sets or exact bit masks interchangeably; set union is bitwise OR.

**T1 (projection criterion).** Π∈A(S,K) if and only if |Π|∈K and

    union_{B∈Π} R(B) = T.

Proof. If a true factor accepts every positive, it must contain H(B).
If a negative has its projection in H(B) on every block, every factor
necessarily accepts it, contradicting its negative label. Thus every
negative must be rejected by at least one block mask. Conversely choose
F_B=H(B). Each H(B) is finite and regular, all positives are accepted, and
each negative is rejected by the mask condition. These explicit finite
factors are witnesses of possibility, not inferred real factor languages. ∎

There is no requirement that rejection masks be disjoint: a negative can
be rejected by several blocks. The **symbol blocks**, not negative masks,
form an exact cover. Requiring disjoint negative coverage would lose models.

For P=∅, every H(B)=∅ and every R(B)=T, so every partition meets the label
criterion; empty local languages explain all-negative data. For N=∅,
T=∅ and every partition is feasible as well. Extra assumptions such as
nonempty or prime factors need a different admissibility theorem; T1 alone
does not check them.

## 3. Canonical exact-cover recurrence

Fix an order of symbols. Let S⊆Σ be the not-yet-covered symbols and U⊆T
the negatives not yet rejected by previously selected blocks. Define
C_t(S,U) as the number of partitions of S into exactly t blocks whose
combined masks cover U. Counts refer to distinct unordered partitions,
not to factor-language choices, which may be infinitely many.

Base cases:

    C_0(∅,∅)=1;
    C_t(∅,U)=0 otherwise;
    C_t(S,U)=0 if t<0 or t>|S| or (S≠∅ and t=0).

For S≠∅, let s be its least symbol and define D(S)={B⊆S:s∈B}. Then

    C_t(S,U) = sum_{B∈D(S)} C_{t−1}(S\B, U\R(B)).        (1)

All masks R(B) are defined from the original fixed sample, not recomputed
from a selected subset of positives. The initial state is (Σ,T).

**T2 (soundness, completeness and uniqueness).** Recurrence (1) counts
each valid partition of its state exactly once.

Proof by induction on |S|. The base is the unique empty partition, valid
exactly when no uncovered negative remains and no block is requested.
For a nonempty S, every partition has exactly one block B containing its
least symbol. That B is in D(S). Removing it leaves a unique child partition
of S\B. The parent's mask union covers U exactly when the child's mask union
covers U\R(B). Conversely any such child plus B gives a valid parent.
Different branches have different least-symbol blocks and cannot duplicate
an unordered partition. Apply the induction hypothesis to the children. ∎

The vector of all C_t can be memoized at each (S,U). Every recursive call
strictly reduces |S|, so the state graph is acyclic and finite. A crude
state bound is 2^m·2^n·(m+1) scalar count entries; this is not a practical
memory promise. Block subset enumeration is exponential, and obtaining
masks also costs projection work on the words. There is no polynomial-time
or general preprocessing/speed advantage claim.

**T3 (arbitrary trusted K).** The exact admissible partition count is

    Z = sum_{t∈K} C_t(Σ,T).                              (2)

Distinct t give disjoint families, so the sum is exact. Noncontiguous sets
must be used literally; replacing K by [min K,max K] changes the model.
If K excludes every feasible count, Z=0 means model/data inconsistency,
not “the nearest feasible count is the truth.” Mathematically K=∅ also
gives Z=0; a CLI may instead classify an empty or malformed K as invalid
input according to its declared validation contract. Invalid input and
an exhausted valid model search are separate execution outcomes.

## 4. Exact pair counts within the same recurrence

For each unordered pair i≠j define Q^{ij}_t(S,U) as the number of the
C_t(S,U) partitions in which i,j are together; set Q=0 if either symbol
is outside S. The empty-state values are all zero. For S≠∅ use

 Q^{ij}_t(S,U) = sum_{B∈D(S)} [
       1_{i,j∈B} C_{t−1}(S\B,U\R(B))
     + 1_{i,j∈S\B} Q^{ij}_{t−1}(S\B,U\R(B)) ].         (3)

The first term represents a pair whose unique block has already been
chosen. The second carries an unresolved pair into the child. A pair
split between B and the remainder contributes zero. In particular, child
coownership counts must not be applied to a pair whose symbol has already
been removed. The base state may have C=1 but has no coowned pair.

**T4 (pair aggregation).** Equation (3) counts coownership exactly once
per partition, without counting it at every recursion depth.

Proof. Use the same unique branch decomposition as T2. In each branch
there are three exclusive cases: both symbols in B (every child completion
coowns them), both in the remainder (precisely the child's counted
completions coown them), or split (no completion coowns them). For both-in-B,
later states do not contain the symbols, so there is no repeated addition.
Induction on |S| and summation over disjoint branches proves the formula. ∎

Aggregate over the exact allowed count set:

    q_ij = sum_{t∈K} Q^{ij}_t(Σ,T),
    d_ij = Z − q_ij.

These are exact nonnegative integer counts of same-block and different-block
partitions, respectively. They are not counts of DFAs or probabilities about
the real system. The fraction q_ij/Z is only a fraction of partitions under
this combinatorial enumeration; no uniform physical prior is assumed.

## 5. Partial ownership, witnesses and physical interpretation

**T5.** Provided Z>0 and the counts are exact:

* forced_same iff q_ij=Z (equivalently d_ij=0);
* forced_different iff q_ij=0 (equivalently d_ij=Z);
* ambiguous iff 0<q_ij<Z.

Proof. The counts partition all admissible ownership answers by the
pair relation. A universal relation is exactly the absence of a witness
for its opposite; ambiguity is exactly nonempty families on both sides. ∎

If the actual model belongs to V(S,K), every forced relation is true of
it. Ambiguous means the available assumptions and observations permit
both ownership relations; it does not mean the actual system changes
ownership or has a random pair relation. A unique complete partition is
obtained exactly when Z=1. Consistent pairwise universal relations can
also reveal only part of the physical ownership even when Z>1.

Witness requirements:

* For any reported possible relation, supply a partition with |Π|∈K and
  finite regular factors H(B) whose projections validate every label.
* For an ambiguous pair, supply two such models, one same and one different.
  A single witness of one relation is insufficient.
* For a forced relation, one model establishes nonemptiness, but universal
  force also requires the completed exact count or a complete proof that
  the opposite constrained family is empty. One agreeing model alone
  proves only possibility.

**T6 (witness extraction).** Any positive count in (1) or (3) permits
construction of a corresponding partition by recursively choosing a
positive-contribution branch until the valid base case.

Proof. The recurrence is a finite sum of nonnegative integers. A positive
total has a positive summand, and every child decreases |S|. T2/T4 show
that the recovered blocks form a partition satisfying the requested
coverage/count/relation conditions. Associate H(B) to every recovered
block to obtain the explicit regular model from T1. ∎

Equivalent pair-specific procedure: repeat the exact DP with one pair
constraint. For “same,” forbid selecting a block containing exactly one
of the two symbols while both remain. For “different,” forbid selecting
a block containing both. Continue normally after the relation has been
resolved. These restrictions exactly select the two respective subfamilies;
they can count or merely find witnesses. In the first procedure one must
also disallow separation at the first block removing either symbol, not
just search for some later block containing both.

Counts of zero require completed exploration of every relevant canonical
branch (or sound pruning covering them). A timeout cannot turn a missing
witness into a forced relation. Under this cycle's contract, interrupted
outputs are unknown/incomplete and carry no exact total or universal
ownership claims. Previously validated witnesses may be retained explicitly
as possibilities. Two validated opposite witnesses are mathematically an
existential ambiguity proof even without exhaustion, but they do not make
unfinished global counts exact or override the declared incomplete status.

Sound pruning examples are t>|S| and insufficient possible remaining mask
union to cover U. Any additional pruning must have its own proof. Current
sample-finest blocks, heuristic correlations, guessed k, and an interrupted
search are not sound automatic pruning premises.

## 6. Broader coverage than a particular witness graph

**T7 (empty old graph yet exact identification).** Let Σ=abcdef and

    P={ε,aabb,ccdd,eeff},    N={bbaa,ddcc,ffee}.

If a,b belonged to different blocks, aabb and bbaa would have identical
projections on every block: aa on a's block, bb on b's, and ε elsewhere.
The positive would force acceptance of the negative. Thus a,b coown in
every feasible partition. The identical argument forces c,d and e,f.
The partition Π*={ab,cd,ef} itself is feasible: each negative's reversed
doubled projection is absent from the positive projection set of its pair
block. Every coarsening is feasible, because coarsening cannot destroy
the existence of a regular witness (merge the corresponding factor products).
Conversely every feasible partition must be a coarsening by the three
forced pair arguments. Therefore its exact counts by k are

    C_1=1, C_2=3, C_3=1, and C_4=C_5=C_6=0.

The old adjacent-swap graph has no edge: swapping the only unequal adjacent
boundary in aabb produces abab, not bbaa, and likewise for the other two
positives; ε has no boundary. Insertion-rescue rules requiring a positive
base one letter shorter than a negative and a positive rescue one longer
cannot fire: all nonempty observed words have length four, with ε the only
other positive. Thus that particular graph has r=6 singleton components.
No claim is made that every possible semantic must-link extractor is empty:
the direct doubled-pair argument above supplies semantic must-links.

With trusted K={3}, Z=1 despite r=6≠k. The exact-cover method therefore
certifies cases beyond the old graph's r=k shortcut. With trusted interval
K={3,4,5,6}, equivalently a trusted lower bound k≥3, Z is still 1 and the
unique physical ownership has three blocks. This uses the lower bound;
it does not infer true k unconditionally from the sample. Noncontiguous
K={3,5} also gives Z=1, while K={1,3} gives Z=2, not the five answers of
its interval hull. K={4,6} gives Z=0, not a four- or six-block answer. ∎

The example remains valid with unrestricted infinite regular factors as
possible truths: (aabb)*, (ccdd)*, (eeff)* fit all labels on Π*. Their
merges fit the same sample (and preserve the complete global language).
There is no finite-language restriction on the real generator.

On the same example with default K={1,...,6}, Z=5: every within-pair
relation is forced_same, whereas every pair from distinct Π* blocks is
ambiguous (one same-block coarsening and Π* itself already show both).
For any such cross pair q=2 and d=3: it is together in the one-block
partition and in the unique two-block partition merging its two atoms.
Within-pair q=5 and d=0. For K={2}, Z=3 and each cross-pair q=1,d=2.
These explicit counts check the meaning of partial ownership without
assuming a unique answer.

## 7. Boundaries and independent assumption counterexamples

**B1: default K cannot force different.** For consistent exact labels,
the one-block factor F_Σ=P is a regular witness. More generally, if any
partition is feasible and 1∈K, its one-block merge is feasible as well.
Thus Z>0 and 1∈K implies q_ij≥1 for every pair; no pair is forced_different.
With default K, exact physical ownership can only be uniquely one-block.
This does not prevent forced_same partial structure such as T7.

**B2: no-label / positive-only count checks.** If P=∅ or N=∅, every
partition is feasible under this model. With allowed counts K,

    Z=sum_{k∈K} S(m,k),    q_ij=sum_{k∈K} S(m−1,k),

where S is the Stirling number of the second kind and the second formula
contracts the fixed pair to one atom. In particular default K yields
Bell(m) partitions and Bell(m−1) same-pair partitions. These are enumeration
checks, not a probability model. On m=1 there are no symbol pairs.

**B3: false K invalidates physical guarantees.** Let the full global language
on abcd require even counts of each letter. It can be implemented with
true ownership ab|cd and decomposable parity factors. A trusted but false
K={4} selects the unique singleton partition, even if complete language is
known, while actual k=2. This is not an algorithmic error: the true model
was excluded. Observations alone cannot validate arbitrary K.

**B4: false graph edges are not coverage evidence.** On positive-only
P={ε} over abcd, true ownership may be ac|bd with universal factors and
known k=2. Fabricated edges ab and cd give exactly two components but the
wrong ownership. Merely cooccurring in a log or appearing in a candidate
cluster is not a sound must-link proof. T8 of C008 requires verified edges;
an empty old graph is likewise not proof of absence of semantic links.

**B5: malformed/model-empty/interrupted are distinct.** An out-of-range K,
non-integer constraint, or symbol outside Σ can be rejected as invalid
input. For valid K, T7 with K={4,6} is a genuine empty model version space.
An interrupted search with no answer found proves neither one. Conflicting
labels P∩N≠∅ also have no consistent model mathematically (a positive
projection prevents rejecting that same word on every block), although a
CLI can reject the input earlier. Neither case creates vacuous forced pairs.

**B6: no unstated prime/state restriction.** The finite factors H(B) prove
existence in this cycle's unrestricted regular class. A prime-factor or
state-bound version space may exclude them and requires a separate exact
existence test. Finding one arbitrary regular witness does not certify
membership in such a stronger class. The conditional result cannot be
promoted to named-device ownership without identity metadata either.

## 8. Delivery limits

This document supplies exact recurrences, completeness and canonical-count
proofs, witness requirements, and counterexamples; no implementation has
been executed by theory. Independent all-partition enumeration must check
the implemented complete answer sets and pair counts. Implementation
performance, interruption behavior, provenance and accepted test results
remain separate evidence. Rejected ideas are preserved in
REJECTED_IDEAS_v1.md; claim statuses and hashes are in the companion ledger
and readiness file. No claim of unconditional recovery of true k or true
ownership is made.
