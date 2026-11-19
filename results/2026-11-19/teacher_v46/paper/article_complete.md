# Certified Maximum Alphabet Partitioning with an Exact Interactive Teacher

Research article · V46 evaluation of the frozen V45 procedure · 19 November 2026

## Abstract

Given positive and negative whole traces over a declared event alphabet, we seek one disjoint alphabet partition with the greatest number of blocks whose projected regular languages classify the sample conjunctively. We derive a sufficient positive-trie parameter for the supplied bounded-DFA teacher, preserving the unrestricted mathematical objective. An exact SAT master maximizes the block count subject to accumulated necessary constraints. After each completed rejection, projection witnesses justify a generalized cover cut that eliminates the failed partition while preserving all compatible partitions. The first accepted relaxation maximizer is globally optimal. The certificate combines direct sample feasibility with a structural bound or a checked refutation above the returned block count. The longer-budget audit verified 1,247 of 2,261 inputs and left 1,014 incomplete. V45 finished 6/10 fixed cases at 60 seconds, compared with 10/10 for V43. Finite tests concern sample compatibility and proof validity.

## 1. Introduction

Passive trace labels give global outcomes while leaving the local decomposition unspecified. Under the whole-trace AND model, each component reads only the events in its block. A positive trace must pass every component, whereas a negative trace must fail at least one. Many different partitions may explain a finite sample. We optimize the number of blocks because that is the stated objective, and return one maximizer with a checkable upper bound. Distinct maximizers can be incomparable under refinement. The objective therefore supplies no uniqueness or identification theorem.

The main contribution is an exact combination of an alphabet-partition relaxation, the supplied manuscript's fixed-partition teacher, witnessed negative feedback encoded as a general cut, and a separate proof consumer. The unrestricted projection criterion connects the decision interface to the target objective. The cut uses a failed negative and multiple witnessed regions without arbitrarily choosing a merge. V46 evaluates V45 with larger resource limits, extends its correctness review, and retains the benchmark and microbenchmark limitations. Implementation and experiment revisions are confined to the new evaluation artifacts.

## 2. Related work and position

Finite-sample DFA identification and decompositional learning provide important context. Heule and Verwer [HV10] encode exact identification of a smallest consistent DFA in SAT; their optimization concerns states of one automaton. Lauffer et al. [LYVSS22] learn conjunctions of DFAs from labeled examples and enumerate Pareto-optimal candidate decompositions, using bounded automata and a different optimization space. Here the unknowns are blocks of a disjoint partition of the declared alphabet, the objective is the number of blocks, and local state counts are unrestricted. The finite projected positive languages supply existence witnesses; the output need not identify component DFAs or the physical system that generated the observations.

Natural projections and language decomposition also appear in supervisory control. Komenda, Masopust, and van Schuppen [KMvS12] study conditional decomposability of a specified language with respect to given alphabets, including extension of a common alphabet. Their language-wide control setting and potentially shared alphabets differ from the present finite-sample compatibility question and disjoint partition objective. Henry et al. [HNMS26] refine potentially overlapping alphabet distributions while actively learning a synchronous system using queries and counterexamples. Those observations motivate a comparison, but their active-learning objective and model are not the present passive maximum-partition problem.

The proposed interaction has recognizable precedents in refinement and decomposition. CEGAR [CGJLV00] checks abstract models and refines them using spurious counterexamples; CEGIS [SL08] alternates candidate synthesis and validation using counterexample inputs. The present master similarly proposes a candidate and adds information after a completed failure, but its failure explanation is a witnessed cover of non-rejecting atom regions, not necessarily a counterexample trace supplied by an external oracle. Logic-based Benders decomposition [HO03] gives a particularly useful structural analogy: a master optimization problem is strengthened by logically justified constraints derived from a subproblem. The analogy does not claim that the general framework, SAT solving, or learning constraints from failures is new. The proof obligation specific to this construction is that every learned cover cut preserves *all* compatible partitions and excludes the failed candidate.

The supplied manuscript is the project source for the local-table teacher. Its bounded local-DFA relations and constraint propagation are used through the V45 reference implementation with a sample-derived sufficient trie bound. The tree reduction belongs to the established family of semijoin algorithms for acyclic database schemes [Yan81]. The derived bound bridges the teacher interface to unrestricted-state finite-sample feasibility. V43 and V44 are historical project baselines. V43 uses complete minimal rejecting-set extraction without calling the manuscript teacher, and V44 assesses and documents that approach. V45 keeps the reference teacher in the feasibility loop and derives generalized cuts externally after completed rejections without eager extraction of all minimal rejecting sets.

The contribution claimed here is the objective-specific combination of the exact partition relaxation, unchanged teacher interface, witnessed failure generalization, and independently checkable upper-bound evidence, together with its proofs and measured behavior under stated limits. The construction is positioned relative to the cited work, not claimed as the first of its kind; establishing scientific priority would require a broader systematic search. Tests and proof checking do not imply formally verified software, recovery of physical devices, or a universal performance advantage.

## 3. Algorithm and implementation

The declared alphabet Σ is ordered, with opaque distinct nonempty string IDs. The wire fields are alphabet, positive, negative. Normalization validates word symbols, removes duplicates separately in first-occurrence order, and retains ε and all declared IDs. Certificate indices are positions after this deduplication. The result fields blocks and max_devices encode P and k=|P|. The word “component” refers to a mathematical factor on a block. All projections erase symbols without reordering, quotienting, or interpreting their names.

### Algorithm 1. Solve and certify

```
Normalize D and check the deadline.
If labels conflict or Σ is empty with a negative, emit direct infeasibility.
If Σ is empty, emit the empty partition with a symbol bound.
Build the projection store. Ask Algorithm 2 about singleton blocks.
If accepted, return singleton blocks with a symbol bound.
Compute mandatory atoms. If their partition differs, ask Algorithm 2.
If accepted, return the atom partition with an atom bound.
Use the completed rejection of the atom partition to learn its first cover.
Build the atom master with that cut. Set upper to the atom count.
Repeat:
    Find a maximum-count model at or below the inherited upper bound.
    Set upper to its decoded block count k and expand its blocks.
    Ask Algorithm 2 about this partition.
    If rejected, add Algorithm 3's cut and continue.
    If accepted, refute threshold k+1 in a fresh proof-enabled SAT solver.
    Check the assembled certificate and return the partition and proof.
On resource exhaustion, return INCOMPLETE with null result fields.
```

Singletons give the largest count possible over Σ. The mandatory contraction tests Σ with each individual symbol removed for each y_i, and takes the equivalence closure of forced co-memberships. If its partition agrees with the singleton proposal, the previous rejection is reused. The master starts from all atom partitions, constrained by the first cut. For fixed cuts, querying threshold t asks whether some partition has at least t classes. Try the inherited upper bound first, then binary search if it fails, keeping one feasible maximizing model. The lower endpoint is witnessed by the all-in-one partition on disjoint labels. Adding clauses preserves learned constraints and can only lower the upper endpoint. The final proof query uses the current clauses and the next threshold regardless of how the search reached k.

### Algorithm 2. Fixed-partition teacher and exact projection

```
For each block B of P:
    Retrieve exact labeled projections. Derive m(B) from positive prefixes.
    Enumerate every named complete DFA of size 1 through m(B).
    For DFAs accepting all positives, insert the rejection row in R_B
    with one DFA witness per distinct row. Publish a completed table.
Construct each Q_i as the relation of assignments rejecting y_i.
Substitute projection-forced zeros and build the responsibility graph.
Choose a spanning forest. For each assignment to the other edge bits:
    Filter and project fresh working tables using the assigned values.
    Discard the branch if a relation is empty.
    Apply upward semijoins. Discard a branch with an empty root.
    Apply downward semijoins and reconstruct compatible local rows.
    If reconstructed, return ACCEPT with witnesses.
Return REJECT after exhausting all branches.
```

The teacher names column x_(B,i) by both block and negative index, including when projected negatives coincide. A table entry holds the original rejection row for witness recovery. Cache keys include the block, both ordered projected samples and m(B). Cached local tables are complete and never conditioned in place. The wrapper checks every completed teacher answer against the direct projection predicate and stops on disagreement. This agreement check occurs after the call. The manuscript's Sections 5.1 through 5.3 define the implemented decision procedure. Full behavior queries in the manuscript and the partition optimizer in this article have different interfaces.

The external projection store hash-conses exact (parent, symbol) pairs. It first records terminals for the full alphabet. On a cache miss, it selects the smallest cached superset of the requested mask, breaking ties by numeric mask, and transforms its reachable prefix nodes iteratively from the root. The root denotes ε. Each other node is the word of its parent followed by its symbol, so two distinct interned nodes cannot represent the same word by induction on depth. If B⊆C, then π_B(π_C(w))=π_B(w). For an old node, append its symbol to the transformed parent exactly when it lies in B. This implements that identity by induction on depth. Terminal ranks preserve sample order. Materializing each distinct terminal once per entry and recording the first matching positive yields exact membership and witnesses. A mask entry becomes visible only after its projections, witness map and rejection mask are complete. Partly created nodes are valid prefix nodes but supply no completed entry. This cache avoids redoing a cached mask and can trade tuple scans for pointer walks, hashing and word reconstruction.

### Algorithm 3. Generalize a completed rejection

```
Pick the first y_i for which every proposed block is nonrejecting.
For each proposed block B:
    Set U to the atom set of B.
    Scan atoms in declared order and add an atom if U remains nonrejecting.
    Retain a matching original positive for the final U.
Deduplicate and sort the witnessed regions by mask.
Require some future block to escape every retained region.
```

If adding an atom causes rejection, any later superset containing that addition still rejects by monotonicity. Hence one scan yields an inclusion-maximal false region for each initial block. This rule may find different maximal regions from different starting blocks or scan orders. Maximality generalizes the prohibition but is unnecessary for certificate soundness. The certificate records the negative index, atom-space region masks, and normalized positive indices witnessing equality of original-word projections.

### Algorithm 4. Check a result

```
Normalize the input and validate the certificate and partition schemas.
For direct infeasibility, check a labeling contradiction or empty-alphabet case.
For optimality, check the declared cover and all negative separations directly.
For a symbol bound, compare k with |Σ|. For an atom bound, recompute atoms.
Otherwise, recompute atoms, validate every region witness and rebuild the CNF.
Apply RUP checks to the refutation of the threshold k+1 formula.
Accept only if the required checks complete and succeed.
```

### 3.5. An interactive example

Let Σ=(a,b,c), S⁺={cba}, and S⁻={abc,bac}. Every singleton projection agrees with the positive for both negatives. No two symbols are forced together. All two-symbol projections separate abc, while bac can be separated on {a,c} or {b,c}. For abc and the singleton partition, ascending atom growth leaves precisely the three singleton regions. Each is witnessed by cba. The cut requires a block of size at least two. Taking {a,c} and {b} gives a compatible partition of size two. Threshold three in the one-cut master is unsatisfiable. The fixture exercises this reasoning with an actual teacher call and a proof checked on the original sample.

The first rejection on the fixed overlap_8 case illustrates generalization beyond excluding a single partition. Its positive traces are ε and the ordered concatenation of all events. The negative consisting of s0 has the false regions {s0} and Σ∖{s0}, witnessed by the full positive and ε, respectively. A block escapes both regions exactly when it contains s0 and at least one other event. The cut excludes every partition leaving s0 alone, while allowing any choice of a companion that satisfies the remaining constraints.

## 4. Correctness and optimality

Let Σ be the finite, explicitly declared alphabet and D=(S⁺,S⁻) the sample of two finite sets of words over Σ. For B⊆Σ, π_B erases all symbols outside B. A partition P is compatible when there are regular languages K_B⊆B* such that all positives belong to ⋂_{B∈P} π_B⁻¹(K_B) and no negative belongs to that intersection. The objective is one compatible P with maximum |P| under unrestricted local state counts. A declared symbol remains in Σ even if it occurs in no sample word. The empty conjunction equals Σ*, so for Σ=∅ the empty partition is compatible exactly when S⁻=∅. A word with both labels makes every instance infeasible. Otherwise, if Σ is nonempty, the one-block partition is compatible by Lemma 1.

### Lemma 1. Projection criterion and the sufficient teacher bound

For B⊆Σ define H_B={π_B(x): x∈S⁺} and, for each negative y_i, let r_i(B) mean π_B(y_i)∉H_B. Then P is compatible if and only if

    ∀i ∃B∈P: r_i(B).                                             (1)

Indeed any factor accepting every positive must contain H_B, so it cannot reject a negative whose projection is in H_B. Conversely, choose K_B=H_B for every block. These finite languages are regular, contain the projected positives, and (1) makes every negative fail at least one factor. This also proves that disjoint labels imply compatibility of {Σ} for nonempty Σ. The canonical languages prove feasibility; the required output need not contain or learn their DFAs.

The unchanged V45 teacher enumerates bounded complete DFAs. If H_B is empty, one rejecting state realizes the empty language. Otherwise use the distinct prefixes including ε as states and add a sink. The initial state is ε. From prefix u on a, go to ua if it is a prefix and to the sink otherwise. The sink loops on all symbols, and exactly the prefixes in H_B are final. This complete DFA accepts exactly H_B. Hence m(B)=1 when H_B=∅ and m(B)=1+|Pref(H_B)| otherwise suffices. If an unrestricted solution exists, the canonical languages simultaneously satisfy all obligations within those bounds. In the reverse direction every bounded factor is regular. The bound is sufficient and can exceed the minimum.

### Lemma 2. Exactness of the completed fixed-partition teacher

For each B, the teacher enumerates every transition function and accepting-state set for every number of named states from 1 through m(B), using state 0 as initial. Every bounded complete DFA has such a representation after renaming. Keeping one representative per vector of negative rejection bits therefore preserves exactly the possible vectors. For each negative, the relation Q_i allows precisely assignments with at least one rejection bit equal to 1; a bit forced to zero by a positive projection match may be removed. Consequently the natural join of the local tables and Q_i relations is nonempty exactly when bounded local factors jointly satisfy the sample.

The teacher conditions every non-forest edge of the responsibility graph on both possible bit values. Every full assignment appears in exactly one such branch. In a branch the remaining graph is a forest, with one shared bit per edge. Bottom-up semijoins remove a parent row only when no child row agrees on their shared bit. Inductively, a surviving row has a consistent assignment throughout its descendant subtree. If every root retains a row, select one root row and then, independently in each child subtree, a supporting row; this reconstructs a global assignment. Conversely every global assignment survives all semijoins. The subsequent downward pass and reconstruction retain this property. Isolated vertices are included. Exhausting all branches therefore decides the join. An interrupted enumeration or join is incomplete, not a rejection.

### Lemma 3. Mandatory atoms and lifting

Rejection is upward monotone: if B⊆C and r_i(B), then r_i(C). Otherwise π_C(y_i)=π_C(x) for some positive x, and projecting that equality to B contradicts r_i(B).

Call symbol a mandatory for negative i when r_i(Σ∖{a}) is false. By monotonicity every B rejecting i must contain a. Thus all symbols mandatory for the same negative occur together in its rejecting block in every compatible partition. Take the transitive closure of these forced co-memberships and call its equivalence classes atoms. Every compatible partition is a union of atoms, and every partition of the atoms expands uniquely to a partition of Σ with the same number of blocks and the same projection behavior. This is an exact lifting statement: no claim is made that atoms are physical devices. An atom-count upper bound is therefore valid. Mandatory tests involving the empty subset use its actual projection, including ε; they are not inferred from symbol occurrence alone.

### Lemma 4. Soundness and progress of witnessed covers

Suppose a completed teacher call rejects an atom partition P. By (1), there is a negative y_i for which every block B∈P is nonrejecting. For each B select a set U of atoms containing B that remains nonrejecting. Algorithm 3 finds such a region by greedy enlargement. A positive x justifies U when π_U(x)=π_U(y_i), where π_U denotes projection onto the union of the symbols in those atoms. Different regions may use different positives. Greedy maximality is unnecessary for validity. With disjoint labels, Σ rejects every negative, so these nonrejecting regions are proper subsets.

For the resulting family F impose the cut

    ∃C∈P′ ∀U∈F: C⊄U.                                           (2)

The rejected P violates (2), since each of its blocks is contained in its own region. Every compatible P′ satisfies it: some C rejects y_i, and C⊆U for a nonrejecting U would contradict monotonicity. The cut is valid for arbitrary partitions of the atoms, including partitions neither refining nor coarsening P. A certificate need only supply the negative and, for each region, an original positive whose projection equals the negative projection. The verifier can check these equalities directly; it need not trust the teacher or maximality.

### Lemma 5. Exactness of the Boolean encoding

For q atoms, introduce e_ab for each unordered pair, interpreted as same block. For each triple with pair variables a,b,c, impose ¬a∨¬b∨c, ¬a∨¬c∨b, and ¬b∨¬c∨a. Together with implicit reflexivity and symmetry they define precisely the equivalence relations and hence atom partitions. Let r_a be equivalent to the conjunction of ¬e_ba over b<a. Exactly the least-indexed atom of each class has r_a=true. For a conjunction of literals l_1 through l_d, constrain output v with (¬v∨l_j) for each j and (v∨¬l_1∨…∨¬l_d). For a disjunction use (v∨¬l_j) for each j and (¬v∨l_1∨…∨l_d). The binary clauses propagate each required implication and the long clause supplies the reverse implication. Constant gates and one-literal gates can be simplified. With C(j,0)=true and impossible counts false, the recurrence C(j,t)=C(j−1,t)∨(r_j∧C(j−1,t−1)) expresses that the first j atoms contain at least t representatives. To see this, either they already include t before j, or j is a representative and at least t−1 precede it. Induction on j proves the threshold interpretation.

For anchor a and region U, the class of a escapes U exactly when a∉U or some b∉U satisfies e_ab. Conjoining these escape expressions for all U and disjoining over anchors encodes (2). Full equivalence clauses for the gates give both directions: every partition satisfying the cut extends to a satisfying assignment, and every satisfying assignment decodes to a partition satisfying the cut. The master with any learned cuts is therefore a relaxation containing every compatible partition; its class threshold has its stated meaning.

### Theorem 1. Exact optimization and termination

At each round the master is solved exactly for its largest attainable number of classes, and a maximizing partition is sent to the teacher. If accepted, it is compatible by the teacher result and (1). Since all compatible partitions remain in the master, the master maximum is an upper bound on their block counts; the accepted maximizing candidate attains it and is globally optimal. Acceptance of an arbitrary nonmaximizing master candidate alone would not establish optimality.

If rejected, the new cut eliminates that particular candidate while retaining all compatible partitions. There are finitely many atom partitions, and each teacher and master computation is finite under exact solving and sufficient resources. Repeated rounds therefore terminate at an optimum. The number of partitions grows as a Bell number. Section 5 gives the additional cost of the local enumeration, explicit negative relations and feedback-edge conditioning.

### Theorem 2. Soundness of accepted certificates

The consumer validates that blocks are nonempty, disjoint and cover the declared Σ. It checks (1) directly on the original words. For a symbol-bound certificate, counting disjoint nonempty blocks immediately gives an upper bound of |Σ|. For an atom-bound certificate, recomputing Lemma 3 gives an upper bound of q. In either case feasibility and equality with the upper bound prove optimality. For a direct infeasibility certificate, a positive/negative collision is impossible to classify and an empty partition cannot reject any negative. For the general certificate, the consumer recomputes mandatory atoms, checks each region witness, reconstructs the pair, counting and cut clauses, and checks a DRUP refutation of threshold |P|+1. Each cut is valid for every compatible partition by Lemma 4, and any better one would therefore extend to an assignment satisfying that formula by Lemma 5. The refutation excludes such an assignment. The following RUP induction justifies the refutation test. An incomplete producer has no accepted optimum certificate.

### Search invariants and consumer details

The bound inherited at each new round is the previous relaxation maximum. Every assignment in the new formula was feasible in the old formula on its old variables, so the maximum cannot increase. In the binary search, the retained candidate proves the lower endpoint achievable. A SAT answer may increase that endpoint to the full count of its decoded model, and an unsatisfiable threshold reduces the upper endpoint to t−1. The one-block witness satisfies every cut because it is compatible. At convergence the retained model is a maximum, including when the search never increases the lower endpoint above one.

For the downward semijoin, a child row surviving its upward subtree reduction can be extended outside its subtree exactly when a surviving parent row agrees. The parent row already has a full extension by induction from a surviving root. Its child-subtree choice can be replaced by the candidate child row's extension since the edge bit is the only shared column across that cut. This proves downward reduction preserves exactly the extendable rows. Taking one supporting row per child is consequently consistent. Conditioning erases only columns fixed on both incident relations, which retains all compatibility constraints.

For DRUP [SAT13], negate all literals of each proposed addition. Unit propagation preserves implications of the current formula and the negated addition. If it derives a contradiction, the current formula entails that addition. By induction, all retained additions follow from the rebuilt threshold formula. Ignoring deletions retains entailed clauses, allowing at least as much propagation. Removing repeated literals preserves clause semantics and detects unit clauses reliably. A tautological addition is always entailed and can be discarded. A final conflict with no assumptions proves unsatisfiability of the base formula. Even an empty proof log must establish that conflict. No SAT search run by the producer serves as an axiom of the consumer.

## 5. Complexity and resource behavior

Write n=|Σ|, q for the number of atoms, N=|S⁻|, and L for the total symbol occurrences after normalization. Let s=|B|. For one uncached block the number of enumerated named DFA representations on a completed call is exactly A(s,m)=∑_{h=1}^{m} 2^h h^{sh}. Positives can short-circuit simulation. With word-length sum L_B and W_B projected words, simulation and candidate construction take O(A(s,m)(1+L_B+W_B+s m)) elementary operations. Building the prefix set by tuple slicing costs O(∑_{w∈π_B(S⁺)} (|w|+1)²) when the sum is taken over the input projection list with repeats. The local table has at most min(2^N,A(s,m)) rows. A witness needs O(sm+m) entries plus its rejection vector. The bound m is at most L_B+2 when there are positives, and is one otherwise. The resulting enumeration can be very large even for tiny alphabets with long words.

For a candidate with k blocks, let T_v be the size and d_v the schema width of working relation v before conditioning. A negative relation explicitly generates 2^{d_v} assignments and retains 2^{d_v}−1. With f feedback edges, there are at most 2^f branches. One branch filters rows in O(∑_v(1+T_v)(1+d_v)+f), apart from hashing and graph bookkeeping, and uses at most twice the sum of T_u T_v across forest edges in pairwise support comparisons. Column lookup, traversal and reconstruction add polynomial work in the graph and table sizes. Only one branch's reduced tables need to be retained at a time. Completed local caches can persist across calls.

The master starts with q(q−1)/2 pair variables, 3 binom(q,3) transitivity clauses, and O(q²) additional representative and counting variables and literal occurrences. For a cut with u regions, let W=∑_{U}(1+|U|(q−|U|)). The anchor/escape construction uses O(W+q+qu) literal occurrences and O(q u+q) auxiliary variables. The current loops can take O(q²u) mask tests to construct a cut, even when many gates simplify. The number of SAT calls per round is O(1+log q). Worst-case solving time is exponential in the CNF variables by exhaustive Boolean search, and the deployed backend has no practical polynomial-time guarantee. The number of distinct rejected proposals is at most the qth Bell number, and the greedy step tests at most kq enlargements per rejected proposal. A cache miss examines the existing mask keys and visits the selected source's reachable prefixes once, plus materialization and index construction. Across all masks the cache can still be exponential in n. Counts treating tuples, hashing, and integer masks as elementary operations describe the encoding and enumeration scales. Python tuple length, hashing and multiword integers contribute separately to actual runtime.

The checker scans original words for feasibility, atoms and cut witnesses. Its simple repeated-scan RUP routine makes at most V+1 passes over the current clauses per addition or final conflict, where V is the number of encoded variables. Its worst-case time in a fixed formula and proof is O((p+1)(V+1)F), with p proof lines and F an upper bound on current literal and clause occurrences, plus clause parsing and normalization costs. The current normalization uses membership scans of clauses to discard tautologies. The proof size itself is not generally polynomially bounded. Timeouts are cooperative, with an interrupt timer around native SAT. Windows peak working set is a process-level measure including runtime and native imports.

## 6. Experimental methods and results

Trials were sequential. V43 and V45 ran in separate fresh Windows x64 CPython 3.12.14 processes for each timed trial. The pinned Glucose3 backend was supplied by python-sat 1.9.dev22. Both solver calls had 60-second cooperative limits, with independent 60-second consumer limits. First trials were run for all ten fixed V33 cases per solver. Initial completions received two further trials with alternating method order. Censored first trials were not duplicated. Solve times below exclude startup and standalone consumer time and include any in-solver proof self-check. Each group shows completed/attempted; a median is shown only with repeated completions. The corpus correctness/resource audit used one V45 process at 0.25 seconds per input and a 2-second consumer limit. This is not a representative workload timing comparison.

**Corpus.** Of 2,261 inputs, 1,245 were optimal, 2 infeasible and 1,014 incomplete. All 1,247 completed outputs matched the frozen exhaustive reference and passed the V45 checker. The corpus contains 2,187 labelings of seven small two-symbol words, four empty-alphabet boundaries, ten fixed cases, and 60 seeded small cases. The historical 0.03-second audit yielded 1,052 checked completions and 1,209 incomplete results. Its concurrent workload makes it unsuitable as a controlled timing baseline.

**Fixed cases.** First trials finished for V43 on 10/10 and V45 on 6/10 cases. All completed results passed their own consumers and matched the frozen optimum. The historical clean one-second values were 10/10 and 3/10, respectively. The case labels describe synthetic workloads and carry no population-level performance claim.

| Fixed case | Optimum | V43 finished / trials | V43 median (s) | V45 finished / trials | V45 median (s) |
|---|---|---|---|---|---|
| empty_all_8 | 8 | 3/3 | 0.00043 | 3/3 | 0.00205 |
| all_compatible_10 | 10 | 3/3 | 0.00056 | 3/3 | 0.00200 |
| oneblock_8 | 1 | 3/3 | 0.00252 | 0/1 | — |
| ties_8 | 7 | 3/3 | 0.00163 | 3/3 | 16.44911 |
| reverse_9 | 8 | 3/3 | 0.00122 | 3/3 | 13.03583 |
| reverse_10 | 9 | 3/3 | 0.00181 | 3/3 | 26.67107 |
| overlap_8 | 6 | 3/3 | 0.11028 | 0/1 | — |
| repeated_projections_9 | 9 | 3/3 | 0.00069 | 3/3 | 0.05435 |
| long_words_4 | 4 | 3/3 | 0.00343 | 0/1 | — |
| many_words_3 | 1 | 3/3 | 0.01230 | 0/1 | — |

**Fixtures.** All three outputs passed the checker and a direct partition-enumeration oracle. Every recorded cut was replayed from the input against its preceding rejected proposal. The two-cut input was selected using the solver model order and is a diagnostic.

| Fixture | k | Cuts | Proof lines | Solve (s) |
|---|---|---|---|---|
| ordinary | 2 | 1 | 0 | 14.591 |
| two_cut | 3 | 2 | 0 | 31.843 |
| ab_ba | 1 | 0 | 0 | 14.063 |

**Censoring.** The first censored V45 case in fixed order was preselected by rule for one 300-second solve escalation. Other 60-second censored cases were retained without extra runs. Named-DFA progress below counts the final teacher call only. The bound is the last reported local-table bound. A dash indicates that the recorded telemetry does not identify the active block size.

| Case | Limit (s) | Outcome | Bound | Symbols | Named DFAs in final call |
|---|---|---|---|---|---|
| oneblock_8 | 60 | INCOMPLETE | 10 | 8 | 349,336 |
| overlap_8 | 60 | INCOMPLETE | 4 | 2 | 824,132 |
| long_words_4 | 60 | INCOMPLETE | 52 | 1 | 236,108 |
| many_words_3 | 60 | INCOMPLETE | 8 | 1 | 248,314 |
| oneblock_8 | 300 | INCOMPLETE | 10 | 8 | 4,401,840 |

Complete local enumeration scales were oneblock_8 ≈ 10^83.0, overlap_8 ≈ 10^6.0, long_words_4 ≈ 10^104.9, many_words_3 ≈ 10^9.6 named representations. These sizes describe the enumeration space. The progress counts are affected by short-circuiting on positive traces, so they do not directly predict finish time.

V43 median worker startup was 1.286 s and median standalone checking time was 0.00158 s on completed trials. Process peak working sets ranged from 27.1 to 27.8 MiB. The raw records retain per-trial counters and evidence for censored runs.

V45 median worker startup was 1.441 s and median standalone checking time was 0.00879 s on completed trials. Process peak working sets ranged from 27.3 to 28.1 MiB. The raw records retain per-trial counters and evidence for censored runs.

**Projection microbenchmark.** Both methods used identical mask lists and the historical seeded corpus and checker. Each row is a median of three paired repetitions. All projection, witness and rejection digests matched. Times include build, query and digest work. The historical V45 prefix store lost all four comparisons.

| Alphabet size | Requests | Scanner (ms) | Prefix store (ms) |
|---|---|---|---|
| 4 | distinct | 130.249 | 287.374 |
| 4 | repeated | 294.679 | 556.568 |
| 8 | distinct | 285.090 | 726.276 |
| 8 | repeated | 162.442 | 190.154 |

**Independent execution checks.** The four frozen V45 kernel scripts passed again, including the 30 raw Cartesian-join comparisons and 5,000-symbol projection case. The new review passed 27 independent small partition-oracle cases with opaque IDs, a deterministically interrupted teacher build, and 20 certificate replays and mutations. The interruption produced no completed local table, candidate verdict or cut. In the first opaque-ID attempt, one case exceeded the 2-second solver cap. It completed at the revised 60-second review cap. The initial resource outcome is preserved. The first review driver also invoked the verifier on the incomplete envelope. Its schema rejection carried no feasibility meaning. The replay submits completed mathematical results only.

The fixtures’ zero-line proof logs are valid when the reconstructed base formula at threshold k+1 already yields a unit-propagation conflict. The mutation campaign also used a nonempty, 14-line solver proof.

## 7. Limitations and trust boundary

The exhaustive named-state enumeration can dominate even the first singleton query. The projected finite-language witness proves that the teacher bound is sufficient, independently of how many states a real source might have. The experiments exercise finite synthetic and diagnostic inputs and report zero valid whole-trace AND field trials. Historical BGL and selected-output observations use different label semantics. These results support no statistical generalization or physical recovery guarantee. Solver rankings are workload-specific. In the historical four-method comparison, dynamic programming led on overlap_8 and V42 led on oneblock_8. The projection measurements concern the specified workloads and cached scanner.

The proof checker does not import the teacher, DAG projection store or native SAT solver. It shares normalization, atom construction and deterministic master encoding with the producer. Those components and the RUP interpreter are trusted for the correspondence from original data to clauses and from proof to conflict. The assessments, including Terra contributions, were AI-assisted. No formal verification or external peer review is claimed. Source-level conformance refers to the supplied manuscript algorithm and its reference implementation. There was no supplied original executable to compare with V45. Deadline granularity depends on cooperative polling and native interrupt handling. A deadline can also expire after a completed teacher call during explanation or proof. Only an already completed rejection can justify its recorded cut, and no mathematical result or certificate is returned on interruption.

## 8. Conclusion

The teacher-guided procedure offers an exact way to return one maximum compatible alphabet partition with a checked upper bound under sufficient resources. It connects bounded local-DFA tables to unrestricted sample feasibility and derives globally valid cut constraints from completed failed proposals. The 60-second budget increased fixed-case V45 completions from 3/10 to 6/10. The remaining censored cases and projection timings delimit the practical results.

## References

[CGJLV00] Edmund M. Clarke, Orna Grumberg, Somesh Jha, Yuan Lu, and Helmut Veith. “Counterexample-Guided Abstraction Refinement.” *Computer Aided Verification* (CAV 2000), LNCS 1855, 154–169. Springer, 2000. https://doi.org/10.1007/10722167_15

[HNMS26] Leo Henry, Thomas Neele, Mohammad Reza Mousavi, and Matteo Sammartino. “A Detailed Account of Compositional Automata Learning through Alphabet Refinement.” arXiv:2504.16624, version 3, 2026. https://arxiv.org/abs/2504.16624v3

[HO03] John N. Hooker and Gudmundur Ottosson. “Logic-based Benders decomposition.” *Mathematical Programming* 96, 33–60, 2003. https://doi.org/10.1007/s10107-003-0375-9

[HV10] Marijn J. H. Heule and Sicco Verwer. “Exact DFA Identification Using SAT Solvers.” *Grammatical Inference: Theoretical Results and Applications* (ICGI 2010), LNCS 6339, 66–79. Springer, 2010. https://doi.org/10.1007/978-3-642-15488-1_7

[KMvS12] Jan Komenda, Tomáš Masopust, and Jan H. van Schuppen. “On Conditional Decomposability.” arXiv:1201.1733, 2012. https://arxiv.org/abs/1201.1733

[LYVSS22] Niklas Lauffer, Beyazit Yalcinkaya, Marcell Vazquez-Chanlatte, Ameesh Shah, and Sanjit A. Seshia. “Learning Deterministic Finite Automata Decompositions from Examples and Demonstrations.” arXiv:2205.13013, 2022. https://arxiv.org/abs/2205.13013

[SL08] Armando Solar-Lezama. *Program Synthesis by Sketching*. PhD thesis, University of California, Berkeley, 2008. Technical report UCB/EECS-2008-176. https://www2.eecs.berkeley.edu/Pubs/TechRpts/2008/EECS-2008-176.html

[SAT13] SAT Competition 2013. “Certified UNSAT,” DRUP format and reference checker specification. https://satisfiability.org/competition/2013/certunsat.shtml

[Yan81] Mihalis Yannakakis. “Algorithms for Acyclic Database Schemes.” Proceedings of the Seventh International Conference on Very Large Data Bases, 82–94, 1981. https://www.vldb.org/dblp/db/conf/vldb/Yannakakis81.html

The supplied manuscript is retained locally as `results/2026-11-16/interactive_teacher_v45/sources/main.pdf`; its bibliographic authorship and publication status are not inferred. Primary sources accessed 19 November 2026. This targeted search is not a systematic priority review.

## Appendix A. Reproduction

Use Windows x64 CPython 3.12 with the committed PySAT wheel contents and run each solver version in its own process. From the repository root, run the new harness with the following commands, choosing a new output directory each time. The retained environment records file digests, commit, CPU, interpreter, native binary versions or hashes, and each frozen-manifest check. The raw JSONL gives the input, worker and consumer limits, profiles, proofs, verdicts and measured durations.

```
python -B results/2026-11-19/teacher_v46/run.py all --out new-results
python -B results/2026-11-19/teacher_v46/summarize.py new-results
python -B results/2026-11-19/teacher_v46/audit/review.py new-review.json
```

The release directory contains the full raw evidence, review scripts and generated tables. V43 exports finer phase timings. V45 exports total duration, teacher-call duration including image retrieval on the completed path, per-call trace and the current or final teacher-call counters. The timings and counters have these scopes, so last-call enumeration is not cumulative. Separate process timing captures standalone verification and worker startup. The builder uses ReportLab with the installed Windows Times New Roman, Consolas and Segoe UI Symbol fonts. The rendered page images and layout checks apply to the archived PDF. The teacher source and supplied manuscript are identified by the verified V45 manifest.

## Final section. Proposals for future teacher strengthening

Future teacher changes require explicit approval. First, try canonical state numbering or accessible-state enumeration. Removing representations equivalent under state renaming preserves all behavior rows when each original DFA still has a representative of no greater size. Unreachable states can be removed without affecting behavior and the bound is an upper bound. Reconstruct a named DFA witness for each row and compare full tables on bounded cases, including partial assignments and behavioral queries. Measure the cost of canonicalization alongside enumeration savings.

Second, encode the bounded DFA and acceptance constraints in SAT, with transition-function, designated initial state, final-state and path variables. A decision solver for prescribed rejection bits can preserve bounded existential responses if the encoding is proved equivalent and checked witnesses are decoded. Full table and behavior-query interfaces additionally require complete projected enumeration or exact support queries over the same relation. A single satisfiable model does not establish table completeness. A third approach is to index semijoin support by shared bits, preserving conditioned rows and witness recovery at the same interface. Each proposal needs its own equivalence and performance study against the frozen reference.

For the restricted unrestricted-state feasibility call only, the canonical H_B produces a maximal local rejection row that dominates the other rows. For positive-OR obligations Q_i and no externally fixed bits, putting these rows together decides compatibility by the projection criterion. A direct feasibility adapter could exploit this property. It would change the evaluated teacher and would not answer general partial assignments, arbitrary bounded calls or all realizable behavior queries. No proposal in this section was implemented.
