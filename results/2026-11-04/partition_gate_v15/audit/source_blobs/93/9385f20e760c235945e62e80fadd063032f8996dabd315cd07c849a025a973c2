# C015 — prerequisite gate for certified partitioning

Direct proofs, independent review pending. No experiments, historical edits,
new agents or source implementation. A successful gate certifies a declared
finite-sample inference problem, not unconditional physical ownership.

## 1. Model and exact gate theorem

Σ is finite known nonempty, blocks are nonempty disjoint and cover Σ,
factors are independent arbitrary regular languages preserving local order.
P,N are finite exact labels on complete words. Optional explicit trusted
K⊆{1,...,m} constrains counts; default K={1,...,m}. There is no prime,
state-bound, shared-symbol or noise assumption. Let V(P,N,K) be the set of
distinct unordered ownership partitions admitting some such consistent model.
We count partitions, not DFA implementations; infinitely many factors may
realize one partition.

**T1 (necessary and sufficient certification).** With the actual model in
the declared class and its count in K, ownership is uniquely identifiable
from the supplied observations iff |V|=1. Only then should the gate release
a certified partition. If |V|≥2, two distinct feasible partitions and their
regular witness factors certify ambiguity. If |V|=0, exhaustive proof certifies
incompatibility with the declared assumptions, not a vacuous ownership result.

Proof. Singleton V means every possible true model has the same partition.
Two members give identical input in two worlds with different ownerships,
so no algorithm using this input alone can guarantee which world is actual.
Zero members means no model in the class explains all observations. ∎

A timeout is UNKNOWN/INCOMPLETE, not “insufficient information”: the unvisited
branches may contain zero, one or multiple answers. Two already verified
different witnesses can establish ambiguity without exhaustion; a single
found witness cannot establish uniqueness. The certainty of the goal decision
and the completeness of enumerating all answers are separate fields/concepts.

## 2. Exact admissibility and regular countermodels

For each nonempty block B define H(B)={π_Bp:p∈P}, and R(B) as indices of
negatives n whose π_Bn is absent from H(B). A partition Π is feasible iff
|Π|∈K and union_{B∈Π}R(B) covers every negative.

Proof. Every consistent factor contains H(B), so a negative whose images all
occur there cannot be rejected. Conversely the finite regular languages H(B)
accept all positives and reject all negatives if the masks cover them. ∎

Thus a witness partition can be checked independently against fixed labels
and K without accessing hidden devices. H(B) supplies its explicit possible
factor language. It is not a claim that the real factor is finite or exactly
H(B). Restrictions such as prime factors or a state cap need a different
admissibility test; they are not silently checked here.

## 3. Complete goal-directed search, stop after two

Fix symbol/atom order. Initially each singleton may be an atom, or contract
connected components of a sound must-link graph. An adjacent positive to
negative unequal-symbol swap forces its two letters to coown: separated
owners see identical projections and could not assign different labels.
Hence every feasible partition coarsens the atoms; contraction gives a
bijection between feasible atom partitions and original symbol partitions.
Missing edges do not establish separate owners.

DFS state is (rem,covered,j,prefix), with remaining atoms, previously rejected
negative indices, number of selected blocks, and the selected block list.
For rem≠∅ choose the least remaining atom s, and branch on each B⊆rem
containing s. Compute R(B) on its expanded symbol union when needed, recurse
on rem\B, covered OR R(B), j+1. At rem=∅ accept exactly if covered=ALL and
j∈K. Record the first valid partition and continue; stop when a second
distinct one is validated.

Safe count pruning: if rem has q>0 atoms, any completion has between j+1
and j+q blocks. If K has no member in this interval, discard the branch.
At rem=∅ apply the exact leaf test rather than that interval. Optional
remaining-mask pruning is sound: R(B)⊆R(rem) for any B⊆rem, because equality
on rem implies equality after further projection onto B. If
covered OR R(rem) !=ALL, no completion can reject the missing negative.
All masks are exact fixed-sample computations; an unevaluated mask is not zero.

**T2.** The DFS is sound, complete and duplicate-free up to its explicit
two-answer stop. Every partition has one unique block containing s; removing
it gives a unique child. Induction proves the statement. All pruning above
excludes mathematically impossible completions. Sound atom contraction loses
no feasible answer. At exhaustion zero answers proves incompatible and one
answer proves unique. At two validated answers T1 proves ambiguity without
needing any other branch. ∎

This goal search needs no all-count vector, Bell family listing, pair table
or full upfront 2^m block-mask array. It may compute masks lazily, cache them,
or recompute under a bounded cache; memory savings and runtime are separate.
Proving uniqueness or incompatibility can still require exponential search.
Do not claim the two-answer stop makes every input cheap. Deadline handling
must invalidate unsupported exact claims from unfinished proof work.

Suggested result semantics:

* CERTIFIED_UNIQUE: exactly one partition plus model witness and completed
  uniqueness proof (exhaustion or valid shortcut).
* CERTIFIED_AMBIGUOUS: two distinct checked partitions and regular witnesses;
  all-family enumeration may be incomplete but the ambiguity proof is complete.
* INCOMPATIBLE: zero after complete search/proof.
* UNKNOWN: computational budget/interrupt stopped required proof; any single
  saved candidate is explicitly provisional, not a released certified partition.
* INVALID_INPUT: malformed labels/constraints according to a fixed validator.

The implementation may choose other names but must preserve these meanings.

## 4. Exact shortcut families, count-truncated at two

### Unary all-partitions test

Let C_a={|p|_a:p∈P}. The condition
for every n∈N, some a satisfies |n|_a∉C_a
is equivalent to feasible singletons. Unary factor witnesses {a^c:c∈C_a}
prove sufficiency; forced positive projections prove necessity. Every
coarsening is then feasible, so all partitions fit. With K, the gate can
evaluate min(2,Σ_{k∈K}S(m,k)) instead of exact large Bell counts. Nonnegative
Stirling recurrence admits saturation at2 at every step without changing
the capped result. If the capped count is2, construct two allowed partitions;
if1, construct the unique allowed partition. If0, K was empty/out of range
or invalid under its input contract. Default no-K with m≥2 is immediately
ambiguous, m=1 uniquely one-block.

### Feasible sound-atom partition

If the atom partition itself fits, every coarsening fits by regular product
merging, and no feasible partition can split an atom. Therefore the family
is exactly all atom coarsenings. For r atoms the same capped decision uses
Σ_{k∈K}S(r,k); k>r contributes0. Construct actual expanded witness partitions,
not merely the number2. If this test fails, fall back to the complete DFS;
failure is not proof of ambiguity or impossibility.

For optional known K=r, only the atom partition can fit; its feasibility
test yields unique or incompatible without search. A successful shortcut
does not establish physical truth without the T1 class/count assumptions.

## 5. Coverage beyond a specific graph certificate

Take Σ=abcd, P={ε,aabb,ccdd}, N={bbaa,ddcc}, K={2}. If a,b were separate,
aabb/bbaa would project identically on every block. Thus a,b coown; c,d
likewise. The partition ab|cd itself fits. Every feasible partition is its
coarsening, and the only two-block one is ab|cd: unique under trusted K2.

The adjacent-swap graph is empty: swapping aabb's unequal middle boundary
gives abab, not bbaa; ccdd behaves similarly; no other opposite-label pair
is an adjacent swap. Thus the basic graph sufficient certificate fails,
yet exact goal search certifies uniqueness. The proposed fallback covers
all mathematically feasible samples in the declared class if it exhausts,
not only those with a chosen witness-coverage condition. Without K this
example has two answers ab|cd and abcd and is ambiguous.

Known K alone is not sufficient either. Full per-letter even-count language
on abcd has both realizations ab|cd and ac|bd with local parity factors.
Their complete behavior agrees, with true K2 in each case. For a finite
example P={ε,aa,bb,cc,dd}, N={a,b,c,d}, the unary shortcut admits every
partition: all seven K2 answers survive.

## 6. Positive-only, invalid and physical scope

If N=∅, every partition is feasible in this class, including when P=∅.
For fixed known k, the number is S(m,k), uniquely1 only at k=1 or k=m;
intermediate 1<k<m is ambiguous. General K is handled literally, including
noncontiguous sets. If P=∅ but N nonempty, empty factor languages witness
all partitions too; a hidden nonempty/prefix-closed-factor restriction cannot
be inferred from generator conventions and silently applied.

Conflicting labels are mathematically incompatible; a validator may instead
classify them as invalid before inference, as long as that contract is explicit.
Malformed K, foreign symbols and invalid word types are input errors, not
completed zero-answer scientific proofs. Timeout proves neither invalidity
nor insufficient observational information.

With default no-K, F_Σ=P is always a one-block regular witness for consistent
labels. Any nontrivial feasible partition proves ambiguity against it. Only
one-block ownership can be uniquely certified in the unrestricted no-K class.
This is not “every sample is ambiguous”: Σ=ab, P={ab}, N={ba} uniquely forces
one block. Optional K can make nontrivial ownership identifiable on some
data, but cannot be invented from the maximum feasible count.

The finite input cannot itself establish that real hardware obeys the assumed
independence/disjoint/noise-free semantics or that externally supplied K is
true. For example the same even-count complete language can be generated
with true ab|cd, while falsely supplied K={4} makes singleton ownership
uniquely admissible. The computation is correct for that false restricted
class, but its physical interpretation is wrong because truth was excluded.
Anonymous event labels also cannot identify named physical device IDs.

## 7. Preserved rejected hypotheses and boundaries

Rejected: one feasible answer proves uniqueness; two answers require all-count
enumeration; missing graph edges imply independence; graph failure implies
no certifiable sample; known count always suffices; timeout is insufficient
information; exact finite-data gate verifies the hardware assumptions; and
positive-only logs implicitly contain negative labels.

All examples are direct mathematical constructions, not claimed executed
worlds. Correctness claims here await independent source/gate verification;
no runtime, speedup or universal low-cost guarantee is asserted.
