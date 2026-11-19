# C024-A proof and implementation obligations v1

Status: mathematical review; no executions or performance evidence. This is reintegration of C006 T1–T4/T7/T9, not a new theorem. Alphabet A is finite and nonempty; blocks are nonempty, disjoint, cover A, and are unordered. P,N are finite complete-word samples over A. Factors are arbitrary regular languages without state/cardinality bounds. Contradictory labels are excluded from the following propositions (the current API reports them incompatible after full validation).

## Exact criterion and coarsening
For nonempty S⊆A write p_S for erasing symbols outside S and P_S={p_S:p∈P}. Define R(S)={n∈N:n_S∉P_S}. A partition π is feasible iff union_{B∈π}R(B)=N. Necessity: every factor accepts every positively forced projection; a rejected negative needs one block whose projection differs from ALL positive projections. Sufficiency: choose each factor language P_B, which is finite and regular. The existential block can depend on n; its positive comparison is universal.

If S⊆C, R(S)⊆R(C): equality n_C=p_C would imply n_S=p_S. Thus any coarsening of a feasible partition is feasible. Any partition with at least two blocks coarsens to a bipartition, and a bipartition is itself nontrivial. Therefore a nontrivial feasible partition exists iff a feasible bipartition exists. The oneblock partition {A} is feasible because P∩N=∅. These claims classify compatible architectures, not hidden physical truth or a unique factor language.

## Sound atom quotient and canonical coverage
An adjacent distinct-symbol swap between a labelled positive and negative forces both symbols into one block: separate owners give identical projections on every block. Transitive connected components are therefore contained in every feasible block. Let these sound forced atoms be Q0,...,Q(r−1). Feasible partitions of A correspond exactly to feasible partitions of these atoms (expand unions); an atom proof is required to exclude partitions splitting atoms. Incompleteness of the graph does not invalidate this quotient.

Represent a split by a mask M containing atom 0, M≠F=2^r−1; its other side is F xor M. Every atom bipartition has exactly one such representation: precisely one side contains atom 0. Consequently all odd M with 1≤M<F cover exactly 2^(r−1)−1 splits, without duplicates. Both sides are nonempty. For r=1 the family is empty.

## Contract and stop1
Scope of the proposed substitution: only no-K fallback after validated shortcuts and failure of the atom partition. Keep the validated oneblock witness available. If any canonical split passes exact coverage, return ambiguous with that split and oneblock: these are two distinct feasible partitions. One split is sufficient; searching for two splits is unnecessary. If all splits fail, coarsening and quotient completeness exclude every nontrivial feasible partition, so only oneblock remains and certified_unique is justified. The fallback cannot return incompatible on valid disjoint labels without K.

Do not infer uniqueness from a prefix, zero discovered solutions, cache contents, a node counter, or a search_exhausted flag alone. Exhaustion means every canonical surviving split was actually rejected, with sound atom proof excluding the others. Compact status metadata is not an independently replayable exhaustion certificate; C006 T9 explains the potentially exponential collision cover.

## Edges and resource exits
Empty P: every nonempty-block partition is feasible, including when N contains epsilon. Empty N: every partition is feasible vacuously. For r>1 these give ambiguity; for r=1 uniqueness. Epsilon, duplicates, declared unobserved symbols and Unicode do not change the proof; exact projection and validated alphabet semantics must remain intact. m=1 admits only one partition. Invalid structure/symbols/known_k must preserve validation behavior; late invalid records cannot be bypassed by an early witness. A supplied known_k stays on its existing path: bipartition reduction does not classify fixed-K uniqueness.

A halt, deadline, recursion or memory failure before a certified return is unresolved. If final emission polls and times out after mathematical evidence was gathered, unresolved remains sound. No return should claim completed exhaustive search after interruption. Poll enumeration, projection, witness construction and output; a hard timeout remains an external resource control.

## Source-review obligations
candidate_a_v1/gate_v1.py was absent at this review snapshot; no code approval is claimed. Verify: insertion only at stated fallback; immutable canonical atom ordering; exact complementary masks; first atom fixed; full proper-mask coverage; witness uses the full sample and all negatives; oneblock helper retained; stop1 produces two distinct replayable witnesses; exhausted-only unique; known-K routes unchanged; cache/metrics describe actual work; timeout handling covers the new loop. Independently compare small complete families and replay certificates. Manager owns final actual-source review.
