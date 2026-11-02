# C010: no-K identifiability and exact computational reductions

Status: direct proofs ready for independent review; no experiments or novelty
claim. The target model is known finite nonempty disjoint Σ, independent
regular local acceptor languages, exact finite whole-word labels P,N, and
no supplied K, state bound or prime restriction. Ownership means an unordered
partition, not assignment to named physical devices. Physical conclusions
assume the true system belongs to this model class.

## T1. Eliminating K is possible; guaranteeing nontrivial ownership is not

For any partition Π define H(B)={π_Bp:p∈P}. It is feasible exactly when
every n∈N has some block B with π_Bn∉H(B). Necessity follows because every
consistent factor contains H(B); sufficiency follows by choosing the finite
regular factors H(B). These are possible models, not inferred true languages.

If P∩N=∅, the one-block factor F_Σ=P is always a regular witness. If labels
conflict there is no model (an input validator may reject them directly).
Thus a nonempty unrestricted partition version space always contains {Σ}.

Exact physical ownership is identifiable iff all consistent models induce
the same partition: two differing models give identical observed input and
defeat a guaranteed identifier; a singleton ownership image guarantees the
partition conditional on the model assumptions. Consequently, without K,
exact ownership is identifiable iff the **only** feasible partition is the
one-block partition. A nontrivial feasible partition and the one-block
witness already prove non-identifiability, regardless of computing resources.
This is not the assertion that every dataset is ambiguous: Σ=ab, P={ab},
N={ba} excludes the singleton split and uniquely forces one block.

Every pair is together in the one-block witness. Therefore a nonempty no-K
version space has no forced-different pairs. It can still have forced-same
pairs and ambiguous pairs, meaningful partial physical information.
An empty version space certifies no ownership relation vacuously. A cutoff
is unknown, not evidence of uniqueness or absence of a nontrivial model.

## T2. The obstruction is structural, not a DP limitation

Merging independent regular factors on B,C into the regular language
{u:π_Bu∈F_B and π_Cu∈F_C} preserves the complete global language. Thus
unrestricted physical count/ownership ambiguity can survive even complete
global membership. A nontrivial same-k example is per-letter even counts
on abcd, grouped ab|cd versus ac|bd. Both global languages are identical.
The paired parity factors are decomposable; do not call this a prime example.

Prior C008 PROOFS_v1.md T4 gives the stronger **finite-horizon** example:
F_xy=E_xy\{x^(2M)y^(2M)}, with E_xy requiring even counts of x,y. These
nonempty infinite regular factors are prime because their unary projections
are both even unary stars but their product contains the deleted word.
ab|cd and ac|bd agree on every word shorter than 4M, yet have different
ownership and known k=2. This construction can contain positive and negative
observations and applies without a state bound. It does not give equal
complete languages: a^(2M)b^(2M) distinguishes them.

References within the immutable project: C008
`../partition_identification_v8/theory/PROOFS_v1.md` T1–T4 and
`../partition_identification_v8/theory/ADDENDUM_PREFIX_CLOSED_v1.md` P1–P4.
The latter separately gives all-positive finite-horizon ambiguity with prime
prefix-closed LTS factors, not a mixed-label prefix-closed theorem. Neither
prime nor prefix closure is imposed in C010. Complete nonempty language
with a prime-factor restriction is a different identifiable variant discussed
separately in C008's OPTIONAL_COMPLETE_LANGUAGE_PROOF_v1.md; coarsening
need not preserve that restriction. Do not extend unrestricted impossibility
to that class by silently admitting decomposable merged factors.

## T3. Sound must-link atoms preserve all answers bijectively

An edge joins symbols proven to coown in every sample-consistent model.
For the adjacent-swap rule, n is obtained from a positive p by swapping
adjacent unequal letters x,y. If they had different owners, each block's
projection would be unchanged by that swap; accepting p would force accepting
n, contradiction. Therefore the edge xy is sound. The actual positive,
negative, position and swapped letters permit direct replay of its premise.

Let A₁,...,A_r be connected components of any such sound graph, including
isolated vertices. Transitivity makes every A_i a subset of one block in
every feasible partition. Hence every feasible partition is a coarsening
of these atoms.

Map a partition of atom indices to symbol blocks by replacing each index
set I with union_{i∈I}A_i. This is a bijection between **feasible ownership
partitions** on atom indices and all original feasible partitions, provided
feasibility of a quotient block is evaluated on its expanded symbol set.
Indeed each original block is uniquely a union of atoms; expansion and
contraction are inverse and preserve all projections and the block count.
This is not a bijection between all possible DFA implementations or language
choices. Counts here are numbers of unordered partitions only.

Pairs in the same atom are forced same whenever the version space is
nonempty. Relations of distinct-atom symbol pairs equal those of their atom
indices. Absence of an edge is not a proof of independence or separate owners.

## T4. A compatible atom partition gives a complete closed-form family

Test the atom partition itself by the exact projection criterion. If it is
feasible, every coarsening is feasible: merge its regular witness factors,
preserving the global language. Conversely T3 excludes any partition that
splits an atom. Therefore all answers are **exactly all coarsenings**.

The count at k is S(r,k), total Z=Bell(r). Here S is the Stirling number of
the second kind, with S(0,0)=1, S(r,0)=0 for r>0 and
S(r,k)=S(r−1,k−1)+k S(r−1,k). Bell(r)=sum_k S(r,k).

For two symbols in the same atom, coownership count is Z. For symbols in
distinct atoms, coownership partitions correspond bijectively to partitions
of r−1 objects by identifying those two atoms; hence q=Bell(r−1), or
q_k=S(r−1,k) at each k. Difference counts are Z−q. These are combinatorial
fractions, not physical probabilities. For r≥2, both same and different
witnesses exist: the one-block partition and the atom partition respectively.
For r=1 there is no distinct-atom pair; there is only one answer and all
symbol pairs coown. Do not invent a Bell(−1) or a distinct-atom relation.

The atom partition with factors H(A_i) is a direct regular witness. Its
coarsenings can be witnessed by merged factors, or directly by H(B) on each
expanded block using the feasibility theorem. Pair witnesses therefore need
no exhaustive listing of Bell(r) partitions. A caller requesting that whole
list still incurs its unavoidable output cost and must receive incomplete
if listing stops. A finest sample partition is not necessarily nature's
ownership: for r≥2 the shortcut itself exhibits several possible truths.

Stirling/Bell scalar counts can be computed in O(r²) arithmetic operations,
with big-integer cost additional. Graph extraction, word projections,
compatibility checking and witness output are separate costs; pair output
alone can have Θ(m²) entries. This is not an end-to-end polynomial guarantee
for all inputs or a measured speedup claim.

## T5. If shortcut fails: exact atom DP with lazy masks

For any nonempty atom-index block B, define R(B) as the negative indices
whose projection on the expanded symbol union is absent from all positive
projections on that union. Compute it only when requested, memoizing its
exact result. Laziness changes when a value is computed, not its definition;
it cannot discard a block merely because its mask has not been computed.

Use state C(rem,covered,left), with rem a set of atom indices. The empty
state is 1 exactly when left=0 and covered=ALL, otherwise 0. Impossible
left<0, left>|rem|, or nonempty rem with left=0 return zero. For nonempty
rem choose its least index s and use

    C(rem,covered,left)
      = sum_{B⊆rem,s∈B} C(rem\B,covered OR R(B),left−1).

Every partition has exactly one block containing s; deleting that block
leaves a unique child. Induction proves soundness, completeness and no
duplicate count, and T3 transports the result to the original alphabet.
Sum roots for all k=1,...,r; larger counts are impossible by sound contraction,
not by external K. Coownership vectors use the same proved C009 recurrence:
both atom indices inside B add child total, both in remainder add child
coownership, split adds zero. Same-atom pairs use total directly.

For B⊆S, R(B)⊆R(S): equality of some positive and negative projection on
S implies equality after further projection onto B. Taking the contrapositive
proves the inclusion. Therefore if rem≠∅ and

    covered OR R(rem) != ALL,

the state has zero completions: every future block is a subset of rem,
and cannot reject an uncovered negative outside R(rem). This is a sound
prune, not a sufficient feasibility test. The empty-state base remains
unchanged. Lazy evaluation of R(rem) for this bound is exact, but its cost
must be counted; no mask may be guessed from a graph's absent edges.

Witnesses follow positive-contribution branches; pair ambiguity needs both
same and different feasible models. Universal claims need exact completed
counts or a complete separate proof; timeout must not return exact counts
or forced relations based on unexplored states. Worst case r=m, masks up
to 2^m−1 and DP remain exponential. No automatic reduction is guaranteed
when the graph has no edges or the family is not a full coarsening family.

## T6. Spectrum and cost interpretation

Unrestricted feasible counts form 1,...,kmax when the version space is
nonempty: start at a maximum-block witness and merge down to every smaller
count. Thus kmax is a sample upper bound on actual k conditional on this
model, never a data-derived lower bound above one or automatic recovery of
the real declared count. The no-K API can legitimately report this spectrum
and partial ownership while rejecting a promise of guaranteed nontrivial
physical identification.

C009 already used memoized count/pair DP **without materializing all Bell
partitions by default**; complete listing was optional. Its unconditional
preprocessing computed every one of 2^m−1 nonempty symbol-block masks. The
proposed improvements are sound contraction, a verified full-family shortcut,
lazy masks and the remaining-coverage prune, not the invention of counting
without enumeration. Their actual resource benefit is a separate empirical
question. This proof author ran no experiments and changed no historical code.
