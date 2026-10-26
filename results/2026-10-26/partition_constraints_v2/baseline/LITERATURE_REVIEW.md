# Literature review: passive discovery of disjoint alphabet components

**Research question.** Given a finite alphabet \(\Sigma\) and finite, noise-free positive and negative word samples \(S^+,S^-\), can we discover a partition \(\Pi=\{B_1,\ldots,B_k\}\) (initially \(k=2\)) before learning component DFAs, when each global word interleaves symbols from component languages? The intended semantics are

\[
L=\bigcap_{i=1}^{k}\pi_{B_i}^{-1}(L_i),
\]

where \(\pi_{B_i}\) erases symbols outside \(B_i\), the blocks are pairwise disjoint and cover \(\Sigma\), and each \(L_i\subseteq B_i^*\) is regular. The task is not to assign whole examples to components: every example is a global interleaving. It is also not active learning: there is no membership or equivalence oracle.

## Main finding

There is substantial neighboring work, but the formulations differ in ways that matter. The closest finite-sample result found is Henry et al. (2026), whose Proposition 5 gives an exact criterion for whether a **given** (possibly overlapping) alphabet distribution can explain finite labeled observations as a product observation. Their Section 6 characterizes failures using a negative word whose local projections are witnessed by positive observations. The paper explicitly says Section 4.1 does not prescribe how to find a distribution. Its full algorithm is active, uses a teacher and counterexamples, and treats distributions that may overlap. This is a close conceptual and mathematical antecedent to feasibility checking, not a passive disjoint-partition discovery algorithm.

The DFA-decomposition papers of Lauffer et al. (2022) and Meng et al. (2025) do use finite labeled examples, but each factor DFA is over the same full alphabet \(\Sigma\), and the target is an intersection of arbitrary component languages over \(\Sigma^*\). They do not impose the inverse-projection semantics or discover disjoint symbol supports. Cano Gómez (2010) studies passive inference of regular trace languages from positive and negative samples; the Springer abstract identifies an independence relation in the trace-language semantics, but does not establish whether that relation is supplied or inferred. The abstract does not claim discovery of an unknown disjoint alphabet partition, and the precise assumption must remain unverified until the chapter is read. Jones and Oates (2010) study recovery from interleavings of multiple task instances, a distinct source of interleaving, and focus on restricted workflow language classes.

Thus the narrow, defensible gap is: **passive inference of a disjoint alphabet partition jointly with regular component constraints from finite global positive/negative samples, under an explicit model-selection or identifiability criterion.** This review does not establish that no such work exists. The gap is narrower than “learning decompositions from examples,” which is already established, and narrower than “automated alphabet refinement,” which exists in active compositional learning.

## Selected primary sources and scope

### 1. Henry, Mousavi, Neele & Sammartino (2026), *A Detailed Account of Compositional Automata Learning through Alphabet Refinement*

[arXiv:2504.16624v3 (full text)](https://arxiv.org/html/2504.16624v3), revised 1 Apr 2026.

**Full text read:** Sections 1–6, with special attention to §4.1, Proposition 5 and §6.1–6.3. The paper’s formal alphabet object is a *distribution* \(\Omega=\{\Sigma_1,\ldots,\Sigma_n\}\) whose sets cover the global alphabet and may overlap; this is not necessarily a partition (§4.1, Definition “Distribution”). A product language is the parallel composition of local languages, equivalently membership is the conjunction of membership of each projected word (Lemma 4, §4.1).

**Closest result:** Proposition 5 (§4.1) says a finite observation function is a product observation over a fixed distribution iff, for every observed word, its global label equals the conjunction of the labels induced on its local projections. Corollary 12 (§6.1) restates this as emptiness of the counterexample set. A counterexample is a negative global observation plus, for every block, a positive observation agreeing on that block’s projection (Definition in §6.1). This directly supplies a finite-sample *consistency test for fixed supports*, including the fact that a negative example can only be explained if at least one local projection is forced negative.

**Critical limitation / attribution boundary:** The authors explicitly state that §4.1 “does not prescribe how to find such a distribution” (discussion immediately before Proposition 5). The full method starts with singleton alphabets and iteratively refines/merges them when global counterexamples arrive (§6–7); it learns a synchronizing transition system with an active teacher, membership queries, and equivalence queries (§3, §5, Theorem 18). It permits overlapping component alphabets. It does not solve the stated passive problem of selecting a disjoint partition from a fixed finite sample and then identifying regular component DFAs. Nevertheless, Proposition 5 and its projection-witness characterization are direct prior art for the finite-sample feasibility part; any novelty claim must acknowledge them and specify what is added (disjointness, fixed-k partition search, passive objective/identifiability, and regular-language component constraints).

### 2. Lauffer, Yalcinkaya, Vazquez-Chanlatte, Shah & Seshia (2022), *Learning Deterministic Finite Automata Decompositions from Examples and Demonstrations*

[arXiv:2205.13013v1 (full text)](https://arxiv.org/html/2205.13013), May 2022; also [author-hosted PDF](https://repositum.tuwien.at/bitstream/20.500.12708/81368/1/Lauffer-2022-Learning%20Deterministic%20Finite%20Automata%20Decompositions%20from%20E...-vor.pdf).

**Full text read:** §§I–III and visible problem formulation/encoding. Their DFA-DIP takes labeled examples \((S^+,S^-)\) and a given integer \(n\), and finds \(n\) DFAs whose language intersection is consistent with those examples (§II). They use SAT encodings and search Pareto-optimal state/edge allocations; the paper also illustrates recovering subtasks from unlabeled demonstrations through a separate pipeline.

**Fit to question:** This is the central passive-learning precedent and must be cited. But §II defines all factors as DFAs over one fixed \(\Sigma\); a word is accepted iff all component DFAs accept that same word. No local projection/erasure is present, and the alphabet supports are not learned. The component languages may therefore depend on every symbol, unlike the requested disjoint-block semantics. Their finite consistency objective alone does not identify the generating target uniquely.

### 3. Meng, An, Li, Turrini, Xu, Zhan & Zhang (2025), *Efficient Decomposition Identification of Deterministic Finite Automata from Examples*

[arXiv:2509.24347v2 (full text)](https://arxiv.org/html/2509.24347), revised 12 Oct 2025; [author-hosted PDF](https://lcs.ios.ac.cn/~znj/papers/SETTA2025-Efficient_DFA_DIP.pdf).

**Full text read:** §§1–5 and formal definitions. Definition 3 and the DFA-DIP formalization (§3) again define each factor as a DFA over the same full \(\Sigma\), with conjunction/intersection semantics; input is finite positive and negative examples and a specified number of factors for the traditional Pareto-optimal variant. The paper’s new states-optimal variant compares decompositions with potentially different factor counts, using total states and an entropy tie-breaker. Its contribution replaces redundant APTA-derived encodings with a 3-valued DFA representation to improve SAT efficiency.

**Fit to question:** Recent and important follow-up for passive DFA decomposition. It improves the search for same-alphabet conjunctions, not the discovery of projection supports. The benchmark varies alphabet size but does not make the per-factor alphabets unknown. It is useful algorithmically, yet does not close the partition gap.

### 4. Cano Gómez (2010), *Inferring Regular Trace Languages from Positive and Negative Samples*

[Springer chapter / abstract and bibliographic record](https://link.springer.com/chapter/10.1007/978-3-642-15488-1_3), LNCS 6339, pp. 11–23, DOI [10.1007/978-3-642-15488-1_3](https://doi.org/10.1007/978-3-642-15488-1_3).

**Access level:** Springer abstract and chapter metadata only; full chapter text was not available in the sources opened for this review. The abstract says the method learns regular trace languages from positive and negative samples, models partial commutation using an independence relation, uses asynchronous cellular Moore machines and an RPNI-like merge procedure, and proves convergence.

**Fit to question:** Directly relevant to passive learning under interleaving/commutation, but the exact status of the independence relation (given input versus inferred structure) is **unverified** from the abstract and metadata reviewed here. It does not claim to infer an unknown disjoint alphabet partition. Before building on theorem-level details, inspect the full chapter and verify how the independence relation is treated and what convergence assumptions apply.

### 5. Jones & Oates (2010), *Learning Deterministic Finite Automata from Interleaved Strings*

[Springer chapter / abstract and bibliographic record](https://link.springer.com/chapter/10.1007/978-3-642-15488-1_8), LNCS 6339, pp. 80–93, DOI [10.1007/978-3-642-15488-1_8](https://doi.org/10.1007/978-3-642-15488-1_8).

**Access level:** Springer abstract and chapter metadata only. The abstract frames interleaving as concurrent processing of multiple task instances, abstracts workflow recovery as grammar induction, gives negative results motivating restricted language classes, and states that a DFA for “terminated languages” can be recovered in the limit from interleaved strings.

**Fit to question:** Similar surface wording (“interleaved strings”) but materially different model: interleaved executions of multiple instances of a workflow, not one word generated by shuffling events from disjoint component alphabets. The stated guarantee is limit recovery for a restricted class, not fixed finite-sample support partition identification. Do not conflate it with the target problem.

### 6. Mukund (2002), *From Global Specifications to Distributed Implementations*

[Springer chapter, DOI 10.1007/978-1-4757-6656-1_2](https://link.springer.com/chapter/10.1007/978-1-4757-6656-1_2); also [author’s institutional page](https://cmi.ac.in/~madhavan/papers/synthesis-icatpn01.php). Henry et al. cite this exact work as [Muk02] and attribute their Lemma 4’s product-language characterization to its Lemma 5.2. Springer lists pages 19–35; the author page lists 19–34.

**Access level:** Springer and author bibliographic records/abstract; the cited Lemma 5.2 was checked through Henry et al., but the original chapter was not separately read. The chapter’s abstract formulates synthesis from a global transition system given a distribution into local components, considering loosely cooperating and synchronously communicating systems. This is system realizability/decomposition, not passive grammatical inference from finite labeled samples. Consult for formal semantic foundations, not as evidence that the partition-learning problem is solved.

### 7. Heule & Verwer (2010), *Exact DFA Identification Using SAT Solvers*

[Springer chapter / metadata](https://link.springer.com/chapter/10.1007/978-3-642-15488-1_7), LNCS 6339, pp. 66–79, DOI [10.1007/978-3-642-15488-1_7](https://doi.org/10.1007/978-3-642-15488-1_7).

**Access level:** Springer bibliographic page and cited use in Lauffer et al.; not independently read in full. This is a monolithic SAT-based DFA identification antecedent that Lauffer extends to conjunctions. Relevant as a likely primitive for a joint encoding, but it has no alphabet partition semantics itself.

### 8. Jecker, Mazzocchi & Wolf (2026), *Decomposing permutation automata*

[Journal of Computer and System Sciences, DOI 10.1016/j.jcss.2025.103721](https://doi.org/10.1016/j.jcss.2025.103721).

**Access level:** Publisher abstract/highlights only. The paper studies decomposing a given DFA language into intersections of smaller DFA languages and complexity for permutation DFAs, explicitly distinguishing this from cascade-product decomposition. This is a useful “known automaton” contrast: given-model decomposition is not the same input problem as inferring both an automaton family and alphabet supports from labeled examples. The article is new (2026 issue), so verify the full text if the project broadens toward complexity boundaries.

## Comparison against target assumptions

| Work | Input / learning mode | Factor alphabets | Semantics | What it establishes | Difference from target |
|---|---|---|---|---|---|
| Henry et al. 2026 | Adaptive membership/equivalence queries, active | Unknown *distribution*, potentially overlapping | Parallel LTS composition; projected local observations | For a fixed distribution, exact finite-observation product consistency (Prop. 5); active alphabet refinement and termination | Active teacher; generalized overlaps/synchronization; does not provide passive disjoint partition search |
| Lauffer et al. 2022 | Fixed finite labeled samples; passive | Same known global \(\Sigma\) for every DFA | Intersection of DFAs evaluated on the whole word | SAT-based Pareto search for consistent DFA decompositions | No erasure projections/support partition |
| Meng et al. 2025 | Fixed finite labeled samples; passive | Same known global \(\Sigma\) for every DFA | Intersection on whole word | More efficient encodings; Pareto and states-optimal variants | No unknown disjoint supports/projection semantics |
| Cano Gómez 2010 | Positive/negative samples; passive (per title/abstract) | Trace alphabet; an independence relation is mentioned, but whether it is supplied or inferred is unverified | Trace-closed regular languages | RPNI-like convergent inference under trace assumptions | Abstract does not claim discovery of a disjoint support partition; exact relation assumptions require full-text verification |
| Jones & Oates 2010 | Interleaved workflow traces; limit inference | Workflow language structure | Multiple concurrent instances / interleaving | Negative results and learnability for terminated languages | Different interleaving mechanism and restricted class |
| Jecker et al. 2026 | Given DFA (decomposition decision) | Factors not framed as disjoint local supports | Intersection of smaller DFAs | Complexity of decomposing known permutation DFAs | Input is an already known automaton, not a labeled sample |

## What finite labeled data can and cannot identify

For a **fixed** candidate partition, finite sample consistency has a simple exact criterion: no negative global word may have all of its block projections among the projections of positive words. This is the disjoint-block specialization of Henry et al.’s product-observation criterion. The condition is necessary, and it is sufficient without a state bound: choose each local language to be exactly the finite set of positive projected words. Each resulting local language is finite and therefore regular. Thus regularity alone adds no restriction to finite-sample consistency in this unbounded setting. A component state bound changes the problem because the finite projected sample may require more states than allowed. Neither unbounded consistency nor bounded-state feasibility guarantees a unique partition or recovery of the generating supports/languages from finite samples.

In particular, any proposal should distinguish at least three claims: (1) **sample consistency**: one partition and component automata fit the finite labels; (2) **selection**: a preferred solution is chosen among many consistent partitions/models (for example, minimum total states, minimum description length, or Pareto frontier); and (3) **recovery/identifiability**: under an explicit sampling or characteristic-set assumption, the selected supports/languages equal the generating ones. A finite sample generally admits many extensions; uniqueness needs substantive assumptions. A “given partition cost” analysis addresses none of (2) or (3).

## Narrow research opportunity and required caveats

A viable next contribution could formulate **fixed-\(k\) passive disjoint-support DFA decomposition identification**: choose \(k=2\) (then generalize), require blocks to be nonempty/disjoint/cover \(\Sigma\), and either (a) decide finite sample consistency, for which unbounded regular components admit the simple exact criterion above, or (b) impose component state bounds and jointly identify bounded DFAs over each \(B_i\). A substantive partition-learning contribution needs an explicit selection or identifiability objective, because many partitions can satisfy the finite labels. Compare (a) unconstrained intersection learning from Lauffer/Meng, (b) candidate partition enumeration plus component DFA learning, and (c) a joint SAT/SMT encoding. The evaluation should report partition ambiguity, not only whether a consistent model exists.

The proposal document in the project’s prior-work context is explicitly a proposal. Literature found here supports treating Henry’s finite projection criterion as prior art and same-alphabet DFA-DIP as adjacent art; it does **not** validate a claim that a graph-based heuristic, a particular objective, or recovery guarantee is already established. Before asserting novelty, search should continue in terminology for distributed-alphabet inference, passive trace-language learning with unknown independence, and Boolean matrix/factorization formulations, and full texts should be checked for Cano and Jones.

## Recommended reading order

1. Henry et al. 2026, §4.1 Proposition 5 and §6.1–6.3: understand the exact finite-observation projection-feasibility antecedent and its limits.
2. Lauffer et al. 2022, §II–III; then Meng et al. 2025, §3–4: understand same-alphabet passive DFA decomposition and existing SAT objectives.
3. Cano Gómez 2010: determine from the full chapter whether the independence relation is fixed input or an inferred object; full chapter is needed before theorem-level use.
4. Jones & Oates 2010: establish why instance interleaving is different from alphabet projection/shuffle semantics.
5. Mukund 2002 and Jecker et al. 2026 if the semantic or known-automaton complexity background becomes central.

## Explicit unresolved questions

- Is there earlier work specifically on **inferring an unknown independence relation or disjoint distributed alphabet from finite positive and negative words**, rather than learning a trace language for a supplied relation?
- With a fixed partition and no state bound, finite regular-component consistency reduces to the projection obstruction described above. How does adding component state bounds change feasibility and complexity as \(|\Sigma|\), \(k\), and the bounds vary?
- What objective makes a partition meaningful when many are consistent: minimum sum/product of states, MDL, component nontriviality, or a Pareto set? How should trivial components that accept all local words be handled?
- Which assumptions permit support recovery: characteristic samples, bounded component DFA sizes plus exhaustive coverage, random sampling with a specified distribution, or an explicit identifiability condition?
- Does a partition define the true component split uniquely, or only a coarsest/fine-grained quotient under redundant factors and symbols that are observationally unconstrained?
- Can stronger component alphabet semantics actually be tested from finite data, or does the target reduce to same-alphabet DFA-DIP for some classes of samples/languages?

## Source verification note

Full HTML texts were read for Henry et al. (2026), Lauffer et al. (2022), and Meng et al. (2025). Cano Gómez and Jones–Oates were checked from Springer publisher abstracts/metadata; their full chapters were not read. In particular, no claim is made here about whether Cano Gómez assumes a supplied independence relation. Mukund was checked against Springer and the author’s institutional record, plus Henry et al.’s citation and reproduced theorem; its full chapter was not independently read. Heule–Verwer was checked from Springer’s primary chapter page/abstract. The 2026 JCSS decomposition paper was checked from the publisher abstract/highlights only. Claims above are scoped accordingly.
