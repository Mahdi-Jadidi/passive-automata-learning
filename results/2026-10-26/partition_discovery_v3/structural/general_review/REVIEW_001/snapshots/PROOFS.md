# C003-B001: continuing graph-quotient search

Status: derivation and small captured smoke passed; independent audit pending.
Model: exactly two nonempty disjoint blocks, exact finite labels, unrestricted
regular factors. This is construction of a compatible partition, not recovery
of an unobserved planted factorization. No novelty/performance claim is made.

## Feasibility and graph quotient

For any partition, all positive projections must be locally accepted. Each
negative must therefore have a projection absent from the positive projections
on some side. This is sufficient too: take each local language to be exactly
its finite set of positive projections. These languages are regular.

The read-only prior witness_graph yields necessary must-link edges. A positive
and its negative adjacent swap cannot swap letters on different sides, since
both side projections would then remain equal. For insertion rescue xy+,
xay-, xaby+ (or xbay+), if a,b were on different sides, the side containing a
would see the negative's projection in the rescued positive, while the other
side would see it in xy. Both sides would accept that negative. Thus a,b must
share an owner. Taking graph connected components as indivisible atoms loses
no feasible partition. Component order starts with the one containing the
smallest alphabet symbol; fixing that component to zero removes side symmetry.
Requiring some component on side one ensures both blocks are nonempty.

## Sound learned cuts

Unequal words are distinguished by a singleton or two-letter projection:
singletons fix counts; unequal words with equal counts have a common prefix
followed by distinct first letters a,b, whose pair projection differs at that
position. Apply this to the words projected onto any proposed block. Thus
T_s(n,p), a disjunction of ownership conjunctions for distinguishing singleton/
pair subsets, is equivalent to inequality on side s. Map the symbols in each
subset to their component indices; duplicate indices collapse because graph
components have a common owner. Removing pairs containing an already differing
singleton is redundant. These operations preserve T_s equivalence.

For an incompatible complete candidate choose a negative n supported by positive
projections on both sides, and the lexicographically first matching positives
p0,p1. Add T_0(n,p0) OR T_1(n,p1). Both terms are false at that candidate.
Any feasible partition must reject n on one side s against EVERY positive, hence
also against p_s, and satisfies the cut. No feasible partition is removed.
The implementation verifies that each new cut actually excludes its source leaf.

## Continuing DFS invariant and completeness

The explicit stack stores pending prefixes of component assignments. Children
are pushed one then zero, yielding lexicographic zero-first DFS when popped.
Every prefix has a unique parent and is pushed at most once. A popped prefix
is checked against ALL currently accumulated cuts before either descending or
testing a complete leaf. Therefore cuts added after a prefix was pushed are
not bypassed. A false cut value means every term has a known opposite literal;
no completion can satisfy it. Unknown cut values never prune.

No prefix or candidate is revisited: there is no root restart and no recursion
depth dependence. A feasible leaf is recorded once. The stack remains in place
after each answer, so seeking the second answer resumes the same traversal.
No answer blocker is needed. Quotienting, pruning and traversal preserve all
feasible unvisited leaves; exhausting the stack therefore enumerates all F2
and certifies none if the list is empty. Restricting max_solutions stops after
that many answers, preserving them in exactly the fair reference's order.

The fair reference shares validation, quotient, direct projection test and DFS
implementation but uses learn=False: no cut construction or evaluation. This
isolates the incremental cut mechanism while keeping the task and ordering equal.
It is a fair comparator, NOT an independent correctness oracle. The auditor
must use separate or previously validated exact references for correctness.

## Results, stopping and boundaries

A first solution decides existence (decision_complete=true), but generally leaves
search_exhausted=false and uniqueness=unknown. Two distinct solutions certify
ambiguous. Unique is asserted only after actual stack exhaustion with one answer.
Exhaustion may also be known when an answer limit is reached with an empty stack.
No solution plus complete exhaustion is infeasible for general_regular_product.
On interruption, status=incomplete and all already completed witness records
remain. Existence is still decided if an answer was stored; ambiguity remains
proved if two were stored. An interrupted incomplete traversal never establishes
uniqueness or infeasibility. Immediate expired deadlines return no false decision.

Input validation is independent and accepts arbitrary alphabet size >=2, distinct
single-character symbols, duplicate/reordered words normalized to sorted sets,
and rejects contradictory labels or unknown letters. It does not call the old
validator capped at ten. Absent symbols remain atoms. Empty positive or negative
classes allow the expected vacuous feasibility cases. A one-component quotient
has no nonempty two-block model and exhausts without emitting a solution.

All search is iterative. This removes a Python recursion-limit artifact, but does
not remove exponential worst-case search: at most 2^(c-1)-1 full nonempty component
assignments exist. Cut creation can cost quadratic symbol-pair preprocessing per
new (negative,positive) pair; evaluating accumulated cuts can be expensive. A
sound cut does not guarantee a timing win, including in find-first tasks.

Provider timing includes validation/import of the read-only graph, graph work,
separation, cut creation and search. Phase timers measure completed phases;
interruption inside a phase can leave its partial time represented only in total
provider_seconds. End-to-end external timing remains the comparison authority.
Deadlines are checked at nodes, cut checks, sample loops and between outer pair
iterations. A long graph/helper operation, Python validation or final JSON work
is not preemptible internally; a hard external process deadline is still needed.

## Prior art boundary

The feasibility criterion and singleton/pair reconstruction are inherited
mathematical facts documented in C002 baseline/LITERATURE_REVIEW.md and
approaches/eager/SOURCES.md. C002/B PROOFS.md proves the two-match cut. This
iteration changes search control and its task limit; no new primary-source
search was performed in this implementation task and no novelty claim follows.
