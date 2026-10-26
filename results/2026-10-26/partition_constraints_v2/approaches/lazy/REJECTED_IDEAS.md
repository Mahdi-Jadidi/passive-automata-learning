# Rejected algebraic ideas

## B-TRAP-001: exchange of rejecting-side quantifiers

Scientific status: **refuted by an explicit counterexample**.
Lifecycle: **rejected by proof before implementation**.
Execution status: **not run; algebraic analysis only**.
Parent idea: B001 / C002 exact projection feasibility.
Motivation: a per-positive clause may look simpler than retaining one side that
distinguishes a negative from all positives. This simplification is unsound.

Correct requirement for each negative n:

    exists s in {0,1}, forall p in S+: pi_Bs(n) != pi_Bs(p).

Rejected replacement:

    forall p in S+, exists s in {0,1}: pi_Bs(n) != pi_Bs(p).

Counterexample: Sigma={a,b}, S+={a,b}, S-={epsilon}. The only unordered nonempty
two-block partition is {a}|{b}. Its projections are:

| word | onto {a} | onto {b} |
|---|---|---|
| epsilon (negative) | epsilon | epsilon |
| a (positive) | a | epsilon |
| b (positive) | epsilon | b |

The rejected condition holds: a differs from the negative on side {a}, and b
differs on side {b}. The correct condition fails: on side {a}, positive b has
the negative's epsilon projection; on side {b}, positive a has that projection.
Therefore neither side can reject epsilon while accepting all positives.
Equivalently, both local languages must contain epsilon, so their product accepts
the negative epsilon. The true F2 is empty, whereas the weakened condition would
accept the sole partition.

Decision: reject this quantifier exchange. It is not enabled in lazy or eager.
No faulty implementation, execution command, run log, or measured result exists
for this idea; none is claimed or reconstructed. This is a mathematical failure
of a proposed reformulation, distinct from a program error or an environmental
failure. The counterexample was supplied in the scoped review assignment and
checked algebraically here; it is not claimed as an independently discovered
experimental counterexample. No minimization run was performed.
