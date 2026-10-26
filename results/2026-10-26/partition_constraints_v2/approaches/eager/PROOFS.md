# A exact eager ownership constraints

Status: formal derivation and candidate implementation; independent audit is
separate. No novelty or performance claim is made. Model: the fixed C002
noise-free, disjoint two-block product model with unrestricted regular factors.

## 1. Previously established feasibility criterion

For a candidate partition Pi={B0,B1}, define P_B={pi_B(p):p in S+}.
Then Pi is feasible iff every n in S- has a block B with pi_B(n) not in P_B.
Necessity follows because all positive projections must be accepted. For
sufficiency, choose each local factor to be exactly P_B, a finite regular
language. This is the disjoint-block specialization of the product-observation
criterion in Henry et al., arXiv:2504.16624v3, Section 4.1 Proposition 5 and
Section 6.1 Corollary 12; it is not a new identification theorem.

## 2. Distinguishing subsets of size at most two

Lemma: two words over a finite alphabet are equal iff all their singleton and
two-letter projections agree. Unary alphabets are handled by the singleton.
For larger alphabets, singleton projections give identical letter counts.
If unequal words have a longest common prefix w, equal counts exclude either
word being a proper prefix of the other. Write the remaining first letters a
and b, with a != b. Their {a,b}-projections disagree immediately after the
projection of w, contradicting equality of every two-letter projection.
The binary-projection statement is established, for example, as Lemma 3.11 in
Baumann et al., STACS 2022, page 7:10. The argument here states explicitly the
singleton/unary boundary needed by our code; no new reconstruction result is
claimed.

Define D(n,p) to contain all singleton and pair subsets U with
pi_U(n) != pi_U(p), excluding pairs containing an already distinguishing
singleton. For every block B,

    pi_B(n) != pi_B(p) iff some U in D(n,p) is contained in B.

Proof: containment of a distinguishing U prevents equality after projecting
again from B to U. Conversely, apply the lemma to the two B-projected words.
If a differing singleton was removed only as part of a redundant pair, that
singleton itself remains and is contained in B. Thus the redundancy removal
does not change this existential condition. The empty block case is false
on both sides and is excluded from ownership models anyway.

## 3. Exact ownership formula

Let x_a in {0,1} be the block owning symbol a. For s in {0,1}, put

    T_s(n,p) = OR_{U in D(n,p)} AND_{a in U} (x_a=s).

By Section 2, T_s(n,p) holds iff the side-s projection of n differs from that
of p. Consequently the constraint for one negative is

    C_n = (AND_{p in S+} T_0(n,p)) OR (AND_{p in S+} T_1(n,p)).

The full formula is AND_{n in S-} C_n. It says that each negative has ONE
side on which its projection differs from EVERY positive projection. This is
exactly the feasibility criterion in Section 1. The side may vary between
negative examples, but must not vary independently between positive examples
for the same negative. Eager preprocessing materializes this formula.

All observed swap/rescue graph equalities are additionally conjoined. Their
soundness is proved in the frozen baseline theory note, so this conjunction
removes no feasible model. Fixing the smallest symbol to side zero removes
only the symmetry between the two unordered blocks. Requiring a side-one
symbol enforces the second nonempty block. Therefore complete satisfying
ownership assignments correspond one-to-one with F2(S), with no auxiliary
witness-variable duplicates.

## 4. Search, records and interruption

The engine traverses lexicographic 0/1 extensions in fixed symbol order.
Literal evaluation is exact when assigned and unknown otherwise. AND is false
only after a false child; OR is false only when all children are false. An
induction over the immutable expression tree shows a partial false value has
no satisfying completion. Thus pruning only false constraints loses no model.
Every unpruned complete nonempty assignment is evaluated exactly and emitted
once. A separate direct projection check constructs and checks its witnesses.

An expired cooperative deadline raises SearchInterrupted. Eager catches that
exception and returns only records already constructed, with complete=false,
status=incomplete, exact count null and a found count that is only a lower
bound. No uniqueness or infeasibility inference is made from that partial set.
Deadline checks occur between preprocessing word pairs and search nodes and
constraints. A single helper call is not preempted inside Python; the external
auditor process timeout supplies the hard per-input limit.

## 5. Boundary cases and claim limits

- Empty S+ gives empty inner conjunctions, so every C_n is true. Empty local
  languages explain every negative; all bipartitions are feasible.
- Empty S- gives an empty overall conjunction, also allowing all bipartitions.
- Duplicate words are normalized by baseline validation; contradictory labels
  and out-of-alphabet letters are rejected before enumeration.
- Symbols absent from all examples remain ownership variables, rather than
  being silently removed or assigned invented semantic roles.
- No known-target model is assumed merely because F2(S) is nonempty. A unique
  finite feasible partition identifies a declared target only if that target
  exists in this model and its true factor count is two.
- The explicit feasible set can have 2^(m-1)-1 members. Output itself is then
  exponential; reducing leaf search does not prove total-time improvement.
- This work neither identifies true local languages nor establishes a state
  bound, general passive recovery, or runtime improvement over the baseline.

## 6. Implementation correspondence

engine_candidate.py implements Section 4. common_helpers_candidate.py computes
the minimal D families and the direct projection witness records.
eager_solver.py constructs C_n exactly as Section 3, uses the common engine
and retains incomplete-result semantics. driver_candidate.py keeps the frozen
baseline as the default method; it never promotes eager automatically.

The default baseline adapter calls the immutable v1 implementation unchanged.
Its cooperative deadline is checked before and after that call, not within it;
the runner must enforce the hard process deadline equally for every method.

## Recorded initial verification

Attempt A001_initial_candidate_smoke is stored under attempts with its exact
command, full source snapshots, stdout, stderr and exit status. It checked the
four baseline examples, 100 seeded ternary samples, all 169 word pairs over
{a,b,c} through length two against all eight blocks, one-class samples, a
shared-rejecting-side regression, engine truth-value cases and an already
expired deadline. All checks passed. This is an initial source-level smoke
check; broad independent correctness and performance evidence belongs to the
auditor and is not inferred from this run.
