# Correctness of the exact teacher-guided optimization

Let Σ be the finite, explicitly declared alphabet and D=(S⁺,S⁻) the sample of two finite sets of words over Σ. For B⊆Σ, π_B erases all symbols outside B. A partition P is compatible when there are regular languages K_B⊆B* such that all positives belong to ⋂_{B∈P} π_B⁻¹(K_B) and no negative belongs to that intersection. The objective is one compatible P with maximum |P| under unrestricted local state counts. A declared symbol remains in Σ even if it occurs in no sample word. The empty conjunction equals Σ*, so for Σ=∅ the empty partition is compatible exactly when S⁻=∅. A word with both labels makes every instance infeasible. Otherwise, if Σ is nonempty, the one-block partition is compatible by Lemma 1.

## Lemma 1. Projection criterion and the sufficient teacher bound

For B⊆Σ define H_B={π_B(x): x∈S⁺} and, for each negative y_i, let r_i(B) mean π_B(y_i)∉H_B. Then P is compatible if and only if

    ∀i ∃B∈P: r_i(B).                                             (1)

Indeed any factor accepting every positive must contain H_B, so it cannot reject a negative whose projection is in H_B. Conversely, choose K_B=H_B for every block. These finite languages are regular, contain the projected positives, and (1) makes every negative fail at least one factor. This also proves that disjoint labels imply compatibility of {Σ} for nonempty Σ. The canonical languages prove feasibility; the required output need not contain or learn their DFAs.

The unchanged V45 teacher enumerates bounded complete DFAs. If H_B is empty, one rejecting state realizes the empty language. Otherwise use the distinct prefixes including ε as states and add a sink. The initial state is ε. From prefix u on a, go to ua if it is a prefix and to the sink otherwise. The sink loops on all symbols, and exactly the prefixes in H_B are final. This complete DFA accepts exactly H_B. Hence m(B)=1 when H_B=∅ and m(B)=1+|Pref(H_B)| otherwise suffices. If an unrestricted solution exists, the canonical languages simultaneously satisfy all obligations within those bounds. In the reverse direction every bounded factor is regular. The bound is sufficient and can exceed the minimum.

## Lemma 2. Exactness of the completed fixed-partition teacher

For each B, the teacher enumerates every transition function and accepting-state set for every number of named states from 1 through m(B), using state 0 as initial. Every bounded complete DFA has such a representation after renaming. Keeping one representative per vector of negative rejection bits therefore preserves exactly the possible vectors. For each negative, the relation Q_i allows precisely assignments with at least one rejection bit equal to 1; a bit forced to zero by a positive projection match may be removed. Consequently the natural join of the local tables and Q_i relations is nonempty exactly when bounded local factors jointly satisfy the sample.

The teacher conditions every non-forest edge of the responsibility graph on both possible bit values. Every full assignment appears in exactly one such branch. In a branch the remaining graph is a forest, with one shared bit per edge. Bottom-up semijoins remove a parent row only when no child row agrees on their shared bit. Inductively, a surviving row has a consistent assignment throughout its descendant subtree. If every root retains a row, select one root row and then, independently in each child subtree, a supporting row; this reconstructs a global assignment. Conversely every global assignment survives all semijoins. The subsequent downward pass and reconstruction retain this property. Isolated vertices are included. Exhausting all branches therefore decides the join. An interrupted enumeration or join is incomplete, not a rejection.

## Lemma 3. Mandatory atoms and lifting

Rejection is upward monotone: if B⊆C and r_i(B), then r_i(C). Otherwise π_C(y_i)=π_C(x) for some positive x, and projecting that equality to B contradicts r_i(B).

Call symbol a mandatory for negative i when r_i(Σ∖{a}) is false. By monotonicity every B rejecting i must contain a. Thus all symbols mandatory for the same negative occur together in its rejecting block in every compatible partition. Take the transitive closure of these forced co-memberships and call its equivalence classes atoms. Every compatible partition is a union of atoms, and every partition of the atoms expands uniquely to a partition of Σ with the same number of blocks and the same projection behavior. This is an exact lifting statement: no claim is made that atoms are physical devices. An atom-count upper bound is therefore valid. Mandatory tests involving the empty subset use its actual projection, including ε; they are not inferred from symbol occurrence alone.

## Lemma 4. Soundness and progress of witnessed covers

Suppose a completed teacher call rejects an atom partition P. By (1), there is a negative y_i for which every block B∈P is nonrejecting. For each B select a set U of atoms containing B that remains nonrejecting. Algorithm 3 finds such a region by greedy enlargement. A positive x justifies U when π_U(x)=π_U(y_i), where π_U denotes projection onto the union of the symbols in those atoms. Different regions may use different positives. Greedy maximality is unnecessary for validity. With disjoint labels, Σ rejects every negative, so these nonrejecting regions are proper subsets.

For the resulting family F impose the cut

    ∃C∈P′ ∀U∈F: C⊄U.                                           (2)

The rejected P violates (2), since each of its blocks is contained in its own region. Every compatible P′ satisfies it: some C rejects y_i, and C⊆U for a nonrejecting U would contradict monotonicity. The cut is valid for arbitrary partitions of the atoms, including partitions neither refining nor coarsening P. A certificate need only supply the negative and, for each region, an original positive whose projection equals the negative projection. The verifier can check these equalities directly; it need not trust the teacher or maximality.

## Lemma 5. Exactness of the Boolean encoding

For q atoms, introduce e_ab for each unordered pair, interpreted as same block. For each triple with pair variables a,b,c, impose ¬a∨¬b∨c, ¬a∨¬c∨b, and ¬b∨¬c∨a. Together with implicit reflexivity and symmetry they define precisely the equivalence relations and hence atom partitions. Let r_a be equivalent to the conjunction of ¬e_ba over b<a. Exactly the least-indexed atom of each class has r_a=true. For a conjunction of literals l_1 through l_d, constrain output v with (¬v∨l_j) for each j and (v∨¬l_1∨…∨¬l_d). For a disjunction use (v∨¬l_j) for each j and (¬v∨l_1∨…∨l_d). The binary clauses propagate each required implication and the long clause supplies the reverse implication. Constant gates and one-literal gates can be simplified. With C(j,0)=true and impossible counts false, the recurrence C(j,t)=C(j−1,t)∨(r_j∧C(j−1,t−1)) expresses that the first j atoms contain at least t representatives. To see this, either they already include t before j, or j is a representative and at least t−1 precede it. Induction on j proves the threshold interpretation.

For anchor a and region U, the class of a escapes U exactly when a∉U or some b∉U satisfies e_ab. Conjoining these escape expressions for all U and disjoining over anchors encodes (2). Full equivalence clauses for the gates give both directions: every partition satisfying the cut extends to a satisfying assignment, and every satisfying assignment decodes to a partition satisfying the cut. The master with any learned cuts is therefore a relaxation containing every compatible partition; its class threshold has its stated meaning.

## Theorem 1. Exact optimization and termination

At each round the master is solved exactly for its largest attainable number of classes, and a maximizing partition is sent to the teacher. If accepted, it is compatible by the teacher result and (1). Since all compatible partitions remain in the master, the master maximum is an upper bound on their block counts; the accepted maximizing candidate attains it and is globally optimal. Acceptance of an arbitrary nonmaximizing master candidate alone would not establish optimality.

If rejected, the new cut eliminates that particular candidate while retaining all compatible partitions. There are finitely many atom partitions, and each teacher and master computation is finite under exact solving and sufficient resources. Repeated rounds therefore terminate at an optimum. The number of partitions grows as a Bell number. Section 5 gives the additional cost of the local enumeration, explicit negative relations and feedback-edge conditioning.

## Theorem 2. Soundness of accepted certificates

The consumer validates that blocks are nonempty, disjoint and cover the declared Σ. It checks (1) directly on the original words. For a symbol-bound certificate, counting disjoint nonempty blocks immediately gives an upper bound of |Σ|. For an atom-bound certificate, recomputing Lemma 3 gives an upper bound of q. In either case feasibility and equality with the upper bound prove optimality. For a direct infeasibility certificate, a positive/negative collision is impossible to classify and an empty partition cannot reject any negative. For the general certificate, the consumer recomputes mandatory atoms, checks each region witness, reconstructs the pair, counting and cut clauses, and checks a DRUP refutation of threshold |P|+1. Each cut is valid for every compatible partition by Lemma 4, and any better one would therefore extend to an assignment satisfying that formula by Lemma 5. The refutation excludes such an assignment. The following RUP induction justifies the refutation test. An incomplete producer has no accepted optimum certificate.
