# An Algorithm for Partitioning Traces

@ Certified alphabet partitioning with the exhaustive teacher · V46

## Abstract

Given positive and negative traces, we find an event-alphabet partition with the largest number of blocks whose projected regular languages classify the sample conjunctively. The method retains the exhaustive fixed-partition teacher described in the supplied manuscript. A sufficient trie bound makes its completed decisions exact for the unrestricted-state objective. The outer SAT search converts completed rejections into witnessed constraints and returns either an attained structural bound or a checked unsatisfiability proof above the reported optimum. At 0.25 s per input, 1,247 of 2,261 synthetic cases completed and passed certificate checking. The other 1,014 were incomplete. In an uncapped diagnostic, local DFA table construction took 99.4% of solve time.

**Keywords:** trace projection, passive automata learning, alphabet partitioning, SAT, optimality certificates.

## 1. Problem Statement

Let Σ be the finite ordered alphabet of declared event IDs and D=(S⁺,S⁻) two finite sets of labeled traces over Σ. A partition P consists of disjoint nonempty blocks covering Σ, including any events absent from the traces. The projection π_B deletes events outside B and preserves the remaining order. The algorithm partitions the alphabet and thereby splits each trace into its block projections.

For each B∈P, let K_B be a regular language over B. Compatibility requires π_B(x)∈K_B for every x∈S⁺ and every B∈P. For every y∈S⁻ it requires π_B(y)∉K_B for at least one B∈P. We seek one compatible P of maximum size k=|P| and a checkable upper bound. Local state counts are unrestricted. Uniqueness of an optimum and physical identification are outside the objective.

**Lemma 1 (canonical projected languages).** Put H_B={π_B(x) : x∈S⁺}. A partition is compatible exactly when each negative y_i has a block B with π_B(y_i)∉H_B. *Proof.* Any factors accepting S⁺ contain H_B on each block. If π_B(y_i) belongs to every H_B, all such factors accept y_i. Conversely, choose K_B=H_B simultaneously. All positives pass and every negative fails on its witnessing block. Each finite H_B is regular, including the empty language. ∎

**Boundary cases.** A trace with both labels makes the two requirements contradictory. For Σ=∅ the empty conjunction accepts ε, so the empty partition is compatible exactly when S⁻=∅. On nonempty Σ with disjoint labels, π_Σ is the identity and Lemma 1 makes the one-block partition compatible. Duplicate labeled observations can be removed while retaining the first occurrence of each trace and the declared alphabet.

**Exact cached projections.** A prefix node denotes its parent's word followed by its last event. Interning the ordered pair (parent, event) identifies equal prefixes by induction on length. For B⊆C, applying π_B after π_C equals π_B directly. Replacing each parent by its projected parent, then keeping or erasing the last event, implements this identity by induction on prefix length. The witness indices and rejection marks are computed from those completed projections.

<!-- page -->

## 2. Correctness of the Exhaustive Teacher

The implementation retains the local-table and forest procedure of [1, Sections 5.1–5.3]. For a nonempty block B use a bound m(B) of one when H_B is empty, and otherwise the number of distinct prefixes of H_B, including ε, plus one. The complete prefix trie starts at ε. On a symbol it extends to a valid prefix or enters a rejecting sink with self-loops. Mark exactly the complete words of H_B as final. This DFA recognizes H_B. The empty language needs one rejecting state. By Lemma 1 a compatible partition therefore has simultaneous witnesses within the bounds. In the reverse direction any bounded DFA tuple is a tuple of regular languages. So sufficient trie bounds preserve the decision in both directions.

### 2.1 Exhaust the local behavior space

For h from 1 through m(B), enumerate every complete transition function on h named states and every set of final states, fixing the initial state to zero. Retain only DFAs accepting all projected positives. Record the Boolean row of negative rejections with one witnessing DFA per distinct row. The retained rows all satisfy the bound and the positives. Conversely, renaming any bounded DFA's states so its initial state is zero puts its behavior in the enumeration. Thus R_B is exactly the realizable behavior relation. Its column x_(B,i) is indexed by the original negative, even when projected words coincide.

### 2.2 Enforce every negative and solve the join

The table Q_i allows exactly the tuples with at least one rejection bit equal to one. The natural join of the R_B and Q_i is nonempty exactly when one witnessed row per block satisfies every Q_i. A match to a projected positive forces x_(B,i)=0 in R_B, so imposing and removing that constant at both occurrences preserves the join decision.

After substitution use the responsibility graph with one vertex per table and an edge for each remaining shared column. Select a spanning forest. A join solution fixes one assignment to the omitted edge bits. For each assignment, filter both incident tables for each fixed bit and remove the assigned columns. This preserves exactly the solutions consistent with the assignment. The remaining graph is the forest.

Root each component. A leaf row has an extension to its own subtree. In the upward pass a parent row survives if it has a matching surviving row at every child. By induction on subtree height, this is equivalent to extendibility over its subtree, since distinct child subtrees have no shared free columns and meet the parent only through their edge bits. A nonempty root table in every component therefore suffices. In the downward pass a child row without support from a surviving parent is removed. Starting from a chosen root row, every selected parent retains a supporting child row because the upward pass supplied one and that row still has this parent as support. Reconstructing recursively gives a compatible join row. If every assignment has an empty root table, the original join is empty. Hence the completed teacher accepts exactly the compatible partitions.

### 2.3 Enumeration cost

For s=|B|, a fresh local table enumerates 2^h h^{sh} automata at each h. An explicit Q_i can contain 2^k−1 rows, and f omitted bits yield up to 2^f forest branches. Caching completed tables avoids repeated builds for the same key. The fresh-table cost remains.

<!-- page -->

{{OUTER}}

<!-- page -->

## 5. Experiments

The corpus replay and fresh-process benchmarks used Windows x64, CPython 3.12.14 and Glucose3. Solver time excludes process startup and standalone replay of the certificate. Each completed result was compared with the frozen reference and passed the consumer. The corpus has 2,187 labelings of seven short two-symbol words, four empty-alphabet boundaries, ten fixed cases and 60 seeded cases. Incomplete runs carry no mathematical result.

| Evaluation | Observed result |
|---|---|
| Corpus, 0.25 s per input | 1,245 checked optima and two checked infeasibility results. All 1,014 incomplete runs stopped in the teacher phase. |
| Ten fixed cases, 60 s per solver and checker | With the exhaustive teacher, 6/10 completed. The V43 exact baseline completed 10/10. |
| Three bounded diagnostic fixtures | All accepted by the consumer. The fixture paths used one cut, two cuts and an attained atom bound. |
| oneblock_8, 300 s escalation | Incomplete during a fresh local table, after 4,401,840 representations in the active call. |
| overlap_8, a separate uncapped run | Six blocks, four cuts and an accepted 44-line DRUP certificate. |

**Observed bottleneck.** The uncapped overlap_8 run took 59.156 s. Local tables took 58.809 s and enumerated 4,219,768 named automata across five calls. An uncached two-symbol table at bound four visited 1,054,474 representations. This run used external instrumentation and is a diagnostic separate from the fixed timed trial.

**Projection cache.** All outputs and witness digests agreed with a cached direct scanner in four paired workload settings. The prefix store was slower in each. Thus the evidence supports exactness of the shared projections without an observed speed advantage in those tests.

**Verification beyond the timed suites.** A follow-up replay verified all 2,330 completed historical result records against their references. These records include repeated inputs. The audit checked that 2,249 incomplete records had no mathematical result. On 158 new end-to-end runs, every complete result agreed with exhaustive partition enumeration and passed certificate replay. Independent master tests checked 62,013 partition assignments, 1,255 thresholds and 36 refutations.

<!-- page -->

## 6. Discussion and Conclusion

The proof separates fixed-partition acceptance from optimization. The teacher decides whether the proposed partition can classify the sample. A negative witness explains a completed failure. The exact outer search uses that witness to exclude a family of partitions while preserving every compatible partition. The certificate consumer checks the attained objective from the original data and the refutation. This arrangement lets the optimizer retain the original teacher while using an independently checkable optimality argument.

With q atoms, the number of master candidates is at most the q-th Bell number, plus at most two initial structural tests. SAT and certificate construction add costs beyond that count. The measured failures show that one fresh teacher table can dominate an entire run. The 60 s comparison favors V43 on completion count. The reported experiments use synthetic cases. There are zero valid field trials under whole-trace AND labels. The checks establish sample compatibility and optimality on the completed cases.

### Related work

Exact DFA identification by SAT typically optimizes one automaton's state count [4]. Conjunctive DFA decomposition uses labeled examples with a different hypothesis space [5]. Here the unknown is a disjoint partition of the declared event alphabet. The relaxation and necessary constraints fit the general logic-based Benders framework [2]. The specific construction is the projection-witnessed false-region cut and its use in a threshold refutation, composed with the supplied teacher's exact decision.

### Reproducibility

The tagged archive contains the supplied manuscript, source, frozen reference corpus, raw experiments, certificate records and environment. @link(V46 artifact archive|https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/v46/CHECKPOINT_2026-11-19.md)

## References

[1] *Passive Compositional Automata Learning*. Supplied manuscript, Sections 5.1–5.3. @link(Archived manuscript|https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/v46/results/2026-11-16/interactive_teacher_v45/sources/main.pdf)

[2] J. N. Hooker and G. Ottosson. Logic-based Benders decomposition. *Mathematical Programming* 96, 33–60, 2003. @link(DOI|https://doi.org/10.1007/s10107-003-0375-9)

[3] SAT Competition 2013. *Certified UNSAT*. DRUP specification. @link(Specification|https://satisfiability.org/competition/2013/certunsat.shtml)

[4] M. J. H. Heule and S. Verwer. Exact DFA identification using SAT solvers. *ICGI*, 66–79, 2010. @link(DOI|https://doi.org/10.1007/978-3-642-15488-1_7)

[5] N. Lauffer, B. Yalcinkaya, M. Vazquez-Chanlatte, A. Shah, and S. A. Seshia. Learning deterministic finite automata decompositions from examples and demonstrations. 2022. @link(arXiv:2205.13013|https://arxiv.org/abs/2205.13013)
