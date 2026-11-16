# Exact optimization for D=(S⁺,S⁻): V43

Shared names are defined in `docs/ALGORITHM_NOTATION.md`. P is the alphabet
partition, B a component alphabet, K_B its language and k=|P| the objective.
There is no state bound and no DFA inference step. Code rejection bitmasks are
not the manuscript's behavioral relation R_B. W_i is the family of minimal
nonempty atom sets able to reject y_i. This is a further exact constraint
optimizer, not a claim of a new complexity class or scientific novelty.

## Basis and mandatory atoms

Choose K_B=π_B(S⁺). A partition is compatible iff each y_i has some block with
π_B(y_i) outside K_B. Necessity holds since any positive-consistent factor
contains K_B; sufficiency is witnessed by these finite regular languages.
If B is enlarged, its rejection ability cannot decrease: equality on a larger
projection implies equality after projection to the smaller alphabet.

If removing symbol a from Σ makes it impossible to reject y_i, every block
rejecting y_i must contain a. Thus all such mandatory symbols for the same
y_i share a block in every compatible partition. Transitive closure gives
mandatory atoms. Contracting them is bijective on feasible partitions and
preserves their number of blocks. A compatible atom partition attains the
upper bound q and can be returned without mining or SAT solving. Compatible
singletons similarly attain |Σ|. Contradictory labels and the empty alphabet
are checked separately, after complete schema/ID validation.

## Complete region-based extraction of W_i

For fixed i define monotone f_i(A): the union of atoms A rejects y_i. We seek
its minimal NONEMPTY true sets. A region U represents all nonempty subsets
of U; initially the region is all atoms.

* If f_i(U) is false, every subset of U is false and the entire region is removed.
* If U contains a known minimal witness T, every as-yet-unknown minimal witness
  in U omits at least one member of T. Replacing U by the regions U\{a}, a∈T,
  therefore covers every possible new witness.
* Otherwise, if f_i(U) is true, successively remove an atom whenever rejection
  remains true and the set remains nonempty. A previously failed removal
  cannot become feasible after subsequent removals by monotonicity, so the
  result T is inclusion-minimal. Emit it and perform the same region split.

Removing a queued region contained in another queued region preserves coverage.
Identical processed regions need not be processed again: their surviving
subsets were already covered by their descendants, subject to the same invariant.
Thus the pending antichain always covers every undiscovered minimal witness.
Every processed region is an atom subset and descendants strictly shrink, so
the process is finite. When no regions remain, W_i is exact. No feasible
partition or minimum witness is discarded due to a score or a probabilistic
criterion. The same symbol-subset rejection is evaluated once per solve and
cached for ALL y_i obligations. Retaining a mask from one obligation never
assigns independent local negative labels or changes the AND acceptance model.

## Representation and optimum

For a SINGLE negative y_1, let d be the minimum cardinality of an atom subset
rejecting y_1. Every compatible partition contains a rejecting block of at
least d atoms, and therefore has k≤q-d+1. A minimum such subset as one block,
with every other atom in its own block, attains equality. Thus cardinality-ordered
subset search can stop at the first rejecting subset and certify the optimum;
there is no need to construct all W_1 or call SAT. The consumer independently
tests smaller sizes, along with the compatible witness. This is an exact
subproblem theorem, not a guessed candidate or an approximate answer.

For every negative, a nonempty block rejects it iff it contains a member of W_i.
The forward direction follows by finite minimal-subset descent; the reverse by
monotonicity. Pair variables e_ab and all three triangle implications encode
an equivalence relation on the atoms. Full-equivalence gates require all atoms
of each witness T to share a block. Each Q_i is a disjunction of those witness
gates. This encodes exactly all compatible P, without enumerating complete P.

Representative r_j is true iff no earlier atom shares j's block; sum r_j is
exactly |P|. A full-equivalence counting network supports threshold assumptions.
For d_i=min{|T|:T∈W_i}, any solution has a block containing d_i atoms, hence
k≤q-d_i+1. Taking the minimum across i gives a sound upper bound U. The full
alphabet gives a feasible one-block lower bound for every noncontradictory
nonempty instance. Binary threshold search maintains a feasible incumbent
lower bound and an infeasibility-derived upper bound, and terminates at the
optimum. One CDCL instance preserves learned clauses across threshold calls;
returned partitions are decoded and checked against the original D. No models
are blocked to enumerate solutions. Arbitrary optimal ties are allowed.

## Certificates and trust

The lower-bound witness P is replayed from raw projections. Symbol, atom or
edge-size upper bounds certify optimality when attained. Otherwise a FRESH
assumption-free proof-enabled solver refutes the fixed threshold k+1 formula.
Self-check reuses the already built immutable formula. A separate consumer
checker rebuilds the formula and W_i from the independently supplied original D.
This reconstruction is necessary verification work, not hidden solver work.
It shares the deterministic encoding source with the producer; independently
implemented encoding and human/agent proof review are still pending.

DRUP checking never trusts SAT/UNSAT status. For each added C it checks that
unit propagation on F and the negation of every literal in C reaches conflict.
Thus F entails C. By induction all accepted additions preserve unsatisfiability
equivalence, and final conflict proves the input threshold unsatisfiable.
Deletion lines are safely ignored because retaining extra already-entailed
clauses cannot invalidate the implication. The indexed checker stores literal
occurrences once. Each check starts fresh assignments/counts and processes only
clauses affected by newly false literals, with initial unit clauses seeded.
Satisfied clauses remain satisfied along a propagation run; normalized clause
counts and all initial/derived units therefore produce the same conflict
criterion as the earlier scanning checker. Empty proofs are valid only when
the rebuilt threshold is already unit-inconsistent.

## Complexity and acceptance status

Minimal witnesses, regions, rejection cache and the CNF can all grow
exponentially. Region management is not claimed output-polynomial or universally
better than cardinality-ordered subset search. Membership calls may INCREASE
on some instances while region visits fall. The new upper bound and reuse do
not establish a general polynomial exact algorithm or a universally fastest
algorithm. Resource interruption returns INCOMPLETE with null result claims.
Deadline checks are cooperative in Python and interruptible in native SAT;
hard process termination need not produce a response.

The proof above is the author's mathematical reasoning. Software validation,
source integrity and independent formal/peer review are different obligations.
Executed audits support only the documented inputs and proof mutations.
