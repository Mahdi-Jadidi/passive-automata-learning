# Exactness and preservation of the manuscript teacher

## Contract and scope

Input is the declared alphabet Sigma and D=(S_plus,S_minus). Output is one compatible partition maximizing its block count and an optimum certificate. There is no state restriction on the mathematical problem. Contradictory labels are infeasible. The empty alphabet follows the historical empty-conjunction convention. Teacher implementation follows Sections 5.1–5.3 of the supplied main.pdf; Section 5.5 inspires the outer candidate/test/learn loop, but its bounded local-behavior problem is not silently identified with alphabet optimization.

### Lemma 1: sufficient finite parameter, without a new hypothesis restriction

For a nonempty block B, let H_B=pi_B(S_plus). If H_B is empty, a one-state rejecting DFA realizes it. Otherwise a trie containing every distinct prefix of H_B, including epsilon, plus a rejecting sink is a complete DFA accepting exactly H_B. Set m(B) to this number. For every candidate compatible with unrestricted regular factors, each negative has a block whose projection is absent from H_B: every admissible local language must contain H_B. Conversely the finite H_B realize every such separation simultaneously and fit m(B). Hence calling the unchanged finite-bound teacher with these derived parameters decides unrestricted sample compatibility exactly. These parameters can be very large computationally; the lemma proves sufficiency, not efficiency or minimality of m(B).

### Lemma 2: projection sharing

The root node denotes epsilon and intern(parent,symbol) denotes appending symbol to the parent's word. Dictionary keys are exact pairs, not unverified fingerprints. Induction on node depth proves uniqueness and correctness of represented words. For B contained in cached C, projection of pi_C(w) onto B equals pi_B(w). The iterative transformation either skips the final symbol or appends it to the transformed parent. Induction proves all terminal IDs and materialized tuples correct. Completed entries cache all labelled images and first-positive witnesses. A partial computation is never published as a complete entry. Sharing changes representation and work only, not teacher input semantics.

### Lemma 3: safe atoms

Write reject_i(B) for pi_B(y_i) absent from H_B. If B is contained in C and reject_i(B), equality of projections on C would imply equality on B, so reject_i(C). If Sigma without a cannot reject i, any rejecting block must contain a. All such symbols for one i must share its rejecting block. Transitive closure is therefore respected by every feasible partition. Contraction and expansion preserve compatible partitions and their block counts.

### Lemma 4: generalized rejection cut

If the unchanged teacher rejects P, Lemma 1 gives some i for which each B in P has a positive projection match. For each B, greedily enlarge its atom set while preserving that match, possibly changing which positive supplies it. The resulting U contains B and is false for reject_i. A failed addition cannot become successful later: rejection is monotone. Thus a single ascending scan yields an inclusion-maximal false region; maximality is not needed for soundness.

Learn C_U(P') := there exists B' in P' such that for every U in the returned cover, B' is not contained in U. The current P violates C_U because each of its blocks is contained in its own returned region. Any compatible P' has a block rejecting i. This block cannot be contained in any false U by monotonicity. Consequently C_U preserves EVERY feasible partition, not only refinements or coarsenings of the current candidate. The producer cannot replace this disjunction of possible repairs with an arbitrary forced merge.

### Lemma 5: Boolean master

The three pair clauses per triple make the symmetric same-block relation transitive. Its equivalence classes are exactly the atom partitions. A class has exactly one least-index representative. Fully equivalent AND/OR gates and the recurrence C(j,t)=C(j-1,t) OR (r_j AND C(j-1,t-1)) count classes exactly, with true/false constants distinguished from integer literal IDs.

For anchor a and false region U containing a, OR of e_ab over b outside U expresses that a's class escapes U. If a is outside U, escape is already true. AND these escape conditions over all U, then OR over anchors. This is precisely the cut in Lemma 4. Gate equivalences preserve feasibility and class count; they are not heuristic penalties.

### Theorem 1: first accepted relaxation optimum is globally optimal

At all times every feasible original partition satisfies the master: Lemma 3 preserves it and Lemma 4 preserves it after every cut. The master is a relaxation, not a presumed exact precomputed witness encoding. The inner threshold search finds its maximum class count k using a sound complete SAT procedure. The one-block partition is a feasible lower bound after disjoint-label validation. Upper bounds inherited from prior rounds remain valid because adding cuts cannot increase a maximum. If the teacher accepts the maximizing candidate, it is feasible and attains an upper bound on every feasible original partition. It is therefore globally optimal. Positive teacher feedback for a non-maximizing candidate would NOT suffice; the code optimizes the relaxation first.

### Theorem 2: finite exact continuation

Every rejected candidate violates its newly added cut and can never return, whereas no feasible partition is removed. There are finitely many atom partitions. Every local table construction and forest-conditioning solve is finite under the derived finite bounds. Thus with sufficient resources and correct exact computations the procedure terminates with an optimum. This proof does not exclude Bell-number-scale behavior or guarantee practical runtime. The implementation has no outer enumeration loop, but a worst-case sequence can still be very large. A deadline abort produces INCOMPLETE with no blocks, objective or certificate, never a rejection or a learned cut from an unfinished check.

### Theorem 3: proof-carrying optimum

The consumer directly checks covering/disjoint nonempty blocks and negative rejection against original words. For every cut region it checks the supplied original positive and negative projections are equal. This suffices to prove the region false; neither maximality nor trusting MainTeacher is necessary. It reconstructs atoms and deterministic pair/count/cut CNF, then checks a DRUP refutation of threshold k+1. Since every true solution satisfies each cut, refuting the relaxation above k proves no better solution exists. Each RUP addition follows from the current clauses by unit propagation with its negation; induction and the final conflict prove unsatisfiability. Deletions may be ignored safely; duplicate literals are normalized and tautologies are redundant. Empty proofs require a base unit-propagation conflict.

## Trust and authorization boundaries

The consumer does not import MainTeacher, ProjectionStore or a native solver. The normalization, atom and master encoder specifications remain shared trusted code. This is not formal software verification or independent scientific peer review. The referenced teacher is a new implementation of the supplied pseudocode, not a pre-existing executable that can be asserted byte-identical to an unavailable source implementation. The supplied PDF itself is copied and hashed unchanged.

No symmetry breaking, early stop on a dominating row, bounded-state SAT replacement, canonical-language shortcut or substitute teacher is used in production. Such changes require user approval. The projection-criterion check AFTER a completed teacher call is an assertion and external explanation mechanism, not an acceptance bypass.
