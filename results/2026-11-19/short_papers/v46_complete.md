# Certified Maximum Alphabet Partitioning with an Exhaustive Automata Teacher

@ V46 · Standalone research manuscript

## Abstract

We study the maximum number of blocks in an alphabet partition whose projected regular languages classify a finite sample of positive and negative traces conjunctively. We retain a fixed-partition teacher that enumerates bounded local automata and decides compatibility by a relational join. A sample-derived trie bound makes its completed decision exact for the unrestricted-state objective. An outer SAT relaxation selects a maximum-block proposal and learns a witnessed cut from each completed rejection. An accepted proposal is certified by direct feasibility checks and a structural upper bound or a checked refutation. At 0.25 s per input, 1,247 of 2,261 synthetic cases completed and passed checking. A separate uncapped case located 99.4% of solve time in local table construction.

**Keywords:** passive automata learning, alphabet partitioning, SAT, proof certificates.

## 1. Problem and Contribution

Let Σ be a declared ordered alphabet of event IDs and let D=(S⁺,S⁻) be finite sets of labeled words over Σ. The map π_B erases events outside B⊆Σ. An alphabet partition P is compatible if there exist regular languages K_B over its blocks such that every positive word passes every factor and each negative fails at least one. We seek one compatible P maximizing k=|P|, with a checkable upper bound. Declared events absent from the data remain in Σ. Contradictory labels are infeasible. On empty Σ the empty conjunction accepts ε, so the empty partition is compatible exactly when S⁻ is empty.

The practical question is whether the supplied local-table teacher [1] can be used unchanged while an exact outer solver avoids proposing every partition explicitly. We use maximum-count SAT proposals, necessary cuts derived from witnessed complete failures, and verifiable certificates. The cut transfers information from one examined partition to other partitions, including those unrelated by refinement. The objective concerns alphabet blocks under finite-sample compatibility. Identifying latent physical components or fitting a smallest local automaton is a separate problem.

**Lemma 1 (projection criterion).** Put H_B=π_B(S⁺). A partition is compatible exactly when every negative y_i has a block B with π_B(y_i)∉H_B. *Proof.* Every locally accepting factor must contain H_B. If all projected negatives for y_i lie in their H_B, every such factor accepts that trace. Conversely, take K_B=H_B simultaneously on every block. These finite regular languages accept the positives, and the stated condition rejects all negatives. ∎

<!-- page -->

## 2. Fixed-Partition Teacher

The teacher follows the exhaustive procedure in [1, Sections 5.1–5.3]. For each nonempty block B its caller sets m(B)=1 if H_B is empty. Otherwise m(B) is the number of distinct prefixes of H_B, including ε, plus one rejecting sink. A complete trie automaton starts at ε, advances to a longer prefix if it exists, and goes to the sink otherwise. Its final states are exactly the complete words of H_B. Therefore each H_B has a DFA within the bound. By Lemma 1 every unrestricted compatible partition has simultaneous witnesses within the bounds, and bounded witnesses are regular languages. The derived parameter therefore preserves the unrestricted decision.

### 2.1 Local and global relations

For each h from 1 through m(B), enumerate every transition function on h named states with initial state zero and every final set. Discard machines that reject some projected positive. The remaining machines produce one row of R_B, the relation of joint rejection behaviors on the ordered negative indices. Retain one witness per distinct row. Every bounded complete DFA can rename its initial state to zero, so this enumerates all realizable rows. Indices remain distinct when two projected words coincide.

For each negative y_i, Q_i permits all Boolean assignments in which at least one block rejects. A shared column x_(B,i) occurs in R_B and Q_i. Matching a projected positive forces that column to zero. The join after substituting those constants is nonempty exactly when the corresponding witnessed local rows jointly classify the sample.

### 2.2 Conditioning and forest reduction

The responsibility graph has one vertex for each table and one edge for each remaining shared column. Select a spanning forest. Each complete join row belongs to one Boolean assignment on the feedback edges. In a branch, condition both tables incident to each assigned column and remove the column. The remaining graph is a forest. In the upward semijoin pass, a parent row survives exactly when every child subtree contains an agreeing extension. This follows by induction on subtree height because distinct subtrees share no free column across their boundaries. A nonempty row set at every root therefore permits a joint solution. The downward pass eliminates child rows without support in a surviving parent. A supported child subtree can replace a parent's existing child extension because the connecting edge is its sole remaining shared column. Reconstruction then selects a root row and agreeing child rows. Exhausting all branches with no solution proves rejection.

### 2.3 Cost

For s=|B|, an uncached local table visits exactly ∑ from h=1 to m(B) of 2^h h^{sh} named automata. Explicit obligations can have 2^k−1 rows and f feedback bits can require up to 2^f branches. The caller caches exact projections and the teacher caches completed local tables. Neither cache removes first-time enumeration. The outer loop is finite but can also visit a Bell-scale number of proposals.

<!-- page -->

## 3. Exact Search and Optimality Certificates

Let r_i(B) denote the absence of π_B(y_i) from H_B. This predicate is upward monotone in B. A match on a larger alphabet projects to a match on every subset. Thus if Σ∖{a} fails to reject y_i, every block rejecting y_i contains a. All such mandatory symbols for the same negative must belong to the same block. Taking the transitive closure gives disjoint atoms that every compatible partition respects. Expansion from atom blocks preserves the number of blocks and the original projection semantics.

**A cut from a completed rejection.** Choose a negative y_i rejected by none of the current blocks. Enlarge each block to an atom region U that still fails to reject y_i, recording an original positive whose projection equals that of y_i. Greedy single-atom additions suffice for an inclusion-maximal region. Once an addition causes rejection, monotonicity makes that addition impossible after any further enlargement. Require the next partition to contain some block C with C ⊄ U for every recorded region U. The current partition violates the cut, as each of its blocks is covered. Any compatible partition has a block rejecting y_i, and that block cannot lie in any witnessed region by monotonicity. This proves validity for all compatible partitions.

**Boolean master.** One variable e_ab per unordered atom pair represents co-membership. The three transitivity implications per triple characterize equivalence relations with implicit symmetry and reflexivity. Atom a represents its class exactly when no earlier atom is equivalent to a. If r_j is the representative bit of atom j, the recurrence t(j,d) = t(j−1,d) ∨ (r_j ∧ t(j−1,d−1)) counts at least d class representatives. Its base is true for d=0 and false for d>0 at j=0. For anchor a, its class escapes region U if a lies outside U or some b outside U has e_ab=true. A conjunction over regions and a disjunction over anchors express the cut. All gate encodings enforce equivalence, so models decode to precisely the permitted partitions.

**Algorithm 1.** Handle contradictory labels and the empty alphabet directly. Check the singleton and contracted-atom partitions for immediate upper-bound attainment. Otherwise solve the master for a candidate of maximum block count. Ask the teacher, append a witnessed cut after a complete rejection, and repeat. On acceptance at k blocks, certify that the rebuilt master at threshold k+1 is unsatisfiable. On interruption, return INCOMPLETE without a claimed partition or optimum.

**Theorem 2.** With exact completed calls and sufficient resources, Algorithm 1 returns a global optimum on every compatible input. *Proof.* The master initially contains all compatible partitions and each cut retains them. Thus its current maximum is a valid upper bound. An accepted maximizing candidate attains it. A rejection removes at least the current candidate, and the one-block partition is compatible on nonempty Σ with disjoint labels. Finite strict shrinkage therefore guarantees termination. The inherited upper bound remains valid after every cut, and exact SAT threshold queries find the maximum of each relaxation. ∎

**Certificate replay.** The consumer checks the partition and every negative against the original words. It checks an attained symbol or atom bound, or validates each region witness and reconstructs the threshold CNF. A reverse unit propagation addition follows from the current formula because its negation propagates to conflict. Induction over additions and a final conflict prove unsatisfiability [3]. A better compatible partition would satisfy every checked cut and the threshold, so it is ruled out. The deterministic encoder and normalization remain part of the trusted code.

<!-- page -->

## 4. Experiments

We used the archived Windows x64 CPython 3.12.14 and Glucose3 environment. Fixed timing cases ran in sequential fresh processes. Solver time excludes startup and standalone certificate replay. The corpus is a correctness and completion audit. It covers 2,187 labelings of seven two-symbol words, four empty-alphabet boundaries, ten fixed synthetic cases, and 60 seeded cases. Completions were compared with exhaustive reference optima and checked certificates. Censored runs contribute no mathematical result.

| Evaluation | Outcome |
|---|---|
| Corpus, 0.25 s per input | 1,245 optima, 2 infeasible, 1,014 incomplete. All 1,247 completions passed. |
| Fixed cases, 60 s per input | Interactive teacher 6/10 completed. Exact V43 baseline 10/10. |
| Three bounded diagnostic fixtures | All accepted by the consumer. The runs used one cut, two cuts, and an attained atom bound, respectively. |
| Selected escalation, 300 s | oneblock_8 remained incomplete inside a local table. |
| Uncapped overlap_8 diagnostic | Six blocks, four cuts, and an accepted 44-line DRUP certificate. |

**Bottleneck.** In the uncapped overlap_8 diagnostic, the solver completed in 59.156 s. Local table construction took 58.809 s and enumerated 4,219,768 named representations across five teacher calls. Each uncached two-symbol table at bound four visited 1,054,474 representations. The same case had been censored in the separate 60 s trial. This diagnosis concerns the measured run. The 300 s escalation of oneblock_8 visited 4,401,840 representations in an unfinished table whose total enumeration space is about 10^83.

**Projection cache.** Across four paired workload settings, projected traces, witness indices and rejection digests matched the cached direct scanner. The prefix representation was slower in all four settings. Its medians ranged from 190 to 726 ms, against 130 to 295 ms for the scanner, including digest work.

**Outer verification.** A subsequent audit replayed 2,330 completed result records from overlapping historical suites and checked the null mathematical fields of 2,249 incomplete records. In 158 new end-to-end runs, every result matched an independently enumerated optimum or infeasibility outcome and passed the consumer. Tests of the master alone checked 62,013 partition assignments, 1,255 thresholds and 36 refutations on 36 synthetic instances.

<!-- page -->

## 5. Discussion and Conclusion

The extension is a certified, exact outer optimizer around a specified teacher. It avoids eager extraction of every minimal rejecting set. This gives the teacher a clear decision role and keeps the upper-bound proof independent of its exhaustive DFA tables. A completed rejection yields a cut with projection witnesses, and a small consumer checks the meaning of the reported optimum from the original traces.

The experiments show that preserving the teacher has a computational cost. Relaxation search can reduce the number of candidates presented to the teacher, yet an individual local table can exhaust the budget. The measured interactive solver finished fewer fixed cases than V43. The results support exactness on completed inputs and characterize the resource bottleneck on the measured workloads. All evaluated cases are synthetic, and there are zero valid field trials with whole-trace AND labels.

### Related work

SAT-based DFA identification typically optimizes a state count for specified observations [4]. Conjunctive DFA decomposition also uses labeled examples, but optimizes automata in a different hypothesis space [5]. Here the variables describe disjoint alphabet blocks and the objective is a maximum block count with unrestricted local states. The master-and-failure-cut arrangement is related to logic-based Benders decomposition [2]. The task-specific contribution is the witnessed false-region cut and its use in a checkable threshold refutation, together with the interface proof for the fixed teacher.

### Reproducibility

The V46 tag publishes the supplied manuscript, source, frozen reference corpus, raw timing records, certificate logs, review scripts and machine configuration. The uncapped diagnostic and independent master audit are stored separately from the timed suites. @link(V46 artifact archive|https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/v46/CHECKPOINT_2026-11-19.md)

## References

[1] *Passive Compositional Automata Learning*. Supplied manuscript, §5.1–5.3. @link(Archived manuscript|https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/v46/results/2026-11-16/interactive_teacher_v45/sources/main.pdf)

[2] J. N. Hooker and G. Ottosson. Logic-based Benders decomposition. *Mathematical Programming* 96, 33–60, 2003. @link(DOI|https://doi.org/10.1007/s10107-003-0375-9)

[3] SAT Competition 2013. *Certified UNSAT*. DRUP specification. @link(Specification|https://satisfiability.org/competition/2013/certunsat.shtml)

[4] M. J. H. Heule and S. Verwer. Exact DFA identification using SAT solvers. *ICGI*, 66–79, 2010. @link(DOI|https://doi.org/10.1007/978-3-642-15488-1_7)

[5] N. Lauffer, B. Yalcinkaya, M. Vazquez-Chanlatte, A. Shah, and S. A. Seshia. Learning deterministic finite automata decompositions from examples and demonstrations. 2022. @link(arXiv:2205.13013|https://arxiv.org/abs/2205.13013)
