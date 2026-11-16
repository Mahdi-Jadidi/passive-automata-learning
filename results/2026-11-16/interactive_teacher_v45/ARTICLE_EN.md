# Interactive Alphabet Partition Optimization with an Unchanged Exact Teacher

## Generalized failure cuts, shared projections, and an empirical cost boundary

Technical research report | Implementation V45 | 16 November 2026

## Abstract

We implement an exact counterexample-guided optimizer for alphabet partitions from positive and negative global traces under conjunctive projected acceptance. The fixed-partition teacher follows the exhaustive local-table and forest-conditioning procedure of the supplied manuscript without replacing its internal algorithm. Finite trie-derived parameters make that teacher sufficient for unrestricted-state sample compatibility. The outer learner proposes a maximum-block partition under accumulated constraints. A failed teacher call is explained by a negative word and positive projection witnesses; maximal non-rejecting regions then yield a constraint eliminating an entire family of partitions while preserving every valid solution. Acceptance of a relaxation optimum establishes global optimality, certified by a structural bound or a checked refutation. Shared prefix representations reuse projection work outside the teacher. Tests validate the master, region cuts, certificate consumer and teacher against bounded independent oracles. Experiments expose a substantial boundary: exhaustive teacher construction dominates the runtime and the current Python prefix store is slower than a dictionary-cached scanner on the selected microbenchmarks. The implementation is exact under sufficient resources, but no general speedup, established scientific novelty or field validation is claimed.

## 1. Problem and authorization boundary

Input is a declared ordered alphabet Σ and D=(S+,S-). A partition P consists of disjoint nonempty blocks covering Σ. Each component over B reads the erasing projection π_B and global acceptance is conjunctive. We seek one sample-compatible partition maximizing |P|, with a checkable optimum certificate. Component state counts are unrestricted; learning the local DFAs is not the output objective. Unused declared symbols remain in the optimization. Conflicting labels are infeasible; the historical empty-alphabet convention is retained.

The user requested an interactive outer search while explicitly forbidding changes to the teacher algorithm in main.pdf [1] without further approval. That constraint is implemented literally. The new reference teacher enumerates named DFA representations, builds exact local relations, creates negative-obligation tables, substitutes positive-forced zeros, conditions non-tree edges and runs upward/downward semijoins on forests. No canonical-language shortcut, state symmetry reduction, partial table shortcut or replacement SAT teacher is activated. The supplied PDF is copied unchanged and hashed. Conformance is to its pseudocode, not to an unavailable original executable.

## 2. Calling the bounded teacher without restricting the problem

Let H_B=π_B(S+). A block can reject negative y_i exactly when π_B(y_i) is absent from H_B. Necessity follows because every admissible language contains H_B. Sufficiency follows by choosing the finite language H_B itself. Thus a partition is compatible iff each negative is separable on at least one block.

**Lemma 1 (sufficient caller parameter).** If H_B is empty, set m(B)=1. Otherwise set m(B) to the number of distinct prefixes in H_B, including epsilon, plus one. The unchanged teacher with these parameters decides unrestricted-state sample compatibility exactly.

**Proof.** A prefix trie with a rejecting sink is a complete DFA for H_B within this bound. If any unrestricted-state composition explains D, choosing these canonical finite languages preserves every negative's separating block and all positive projections. Conversely a bounded composition is an unrestricted one. This is a completeness-preserving parameter selection by the caller, not an assumed state ceiling on the real devices. It may be computationally very expensive and need not be a minimum state bound.

The reference implementation retains a DFA witness for every distinct local rejection row. Original local tables are cached by block, projected sample and bound; only complete constructions enter the cache. Every global solve receives fresh working relations. Semijoin deletions and conditioning from one query therefore cannot corrupt a later query.

## 3. Shared projection infrastructure

All input words are interned in an exact prefix DAG. A node is identified by the pair of its parent ID and final event, so dictionary hashing is checked by exact key equality. For a new symbol mask B, choose the cached superset C of minimum cardinality, breaking ties by numeric mask. Transform its terminal nodes iteratively, memoizing each encountered source node for that request. The identity π_B(π_C(w))=π_B(w) justifies reuse. Complete entries retain labelled projected tuples, first-positive witnesses and the negative rejection mask.

Repeated masks do not rebuild projections. Common prefixes and cached supersets can share work across teacher calls, atom preprocessing and failure explanations. The teacher receives ordinary projected words and is unaware of this representation. New masks still require transformations and tuple materialization; shared structure does not guarantee lower elapsed time. Native tuple scanning may outperform Python graph traversal. The measurements below include that unfavorable result.

## 4. Learning from a completed negative answer

A teacher REJECT is followed by an external explanation. Find the first normalized negative y_i such that every current block has a positive projection match. The external criterion is checked against the completed teacher answer; a mismatch raises an error instead of silently substituting another teacher. Interrupted teacher calls return INCOMPLETE and produce no new cut.

For each rejected block, greedily add atoms while a positive match remains. The matching positive may change between additions. Let the resulting non-rejecting regions be U1,...,Us; keep unique masks in deterministic order and retain one original positive index witnessing equality for each region.

**Lemma 2 (generalized cut).** Every compatible partition satisfies: there exists a block B that is not contained in any Uj. The rejected partition violates this condition.

**Proof.** Rejection is monotone under extending a block: equality on a larger alphabet would imply equality after erasure to the smaller one. A compatible partition has a block rejecting y_i. It cannot be a subset of any Uj, each of which has a positive match. In the rejected partition, every original block is contained in the region grown from it, so none escapes all regions. The cut therefore removes the current candidate and potentially many others, while preserving every compatible partition. No arbitrary particular merge is forced.

The greedy growth yields an inclusion-maximal false region: an addition that already causes rejection cannot become allowable after further growth. Maximality strengthens a cut but is not needed by its certificate. The consumer only needs positive projection equality for each region. Covers can overlap, so this is more general than blocking one partition or only its refinements.

## 5. Exact master and operational algorithm

Pair variables express same-component equivalence on mandatory atoms. Triple clauses enforce transitivity; one least-index representative per class permits an exact counting recurrence. For anchor a, its class escapes U automatically when a is outside U; otherwise escape is the OR of same-class variables e_ab for b outside U. Conjoin escapes over U and disjoin over anchors to encode Lemma 2. All auxiliary gates use full equivalences and Boolean constants are distinguished from integer SAT literals.

**Algorithm 1. Unchanged-teacher interactive optimizer.**

1. Validate and normalize D, handling contradictions and the empty alphabet. Construct the shared projection store and the reference teacher. Submit the singleton partition; if accepted, return it with the symbol-count bound.

2. Derive mandatory atoms. If deleting a symbol prevents a negative from being separated, every block rejecting that negative must contain the symbol. Union all such mandatory equalities. If the atom partition differs from singletons, submit it to the teacher; acceptance attains the atom-count upper bound.

3. Explain rejection of the atom partition and add its generalized cut. Initialize the equivalence/count master; no complete minimal-witness family W_i is constructed and no V43 fallback is used.

4. Find a maximum-block model of the current relaxation, using threshold queries and a persistent native SAT session. Reuse valid upper bounds across rounds. The full-alphabet block supplies a feasible one-block lower bound for normalized disjoint labels.

5. Submit this maximizing candidate to the unchanged teacher. On REJECT, construct a new witnessed cover cut, append its clauses and return to step 4. On ACCEPT, retain the partition and certify its optimum. A resource interruption produces INCOMPLETE with null mathematical result fields.

**Theorem 1 (correctness and finite continuation).** Under exact computations, sound complete SAT and sufficient resources, Algorithm 1 returns a maximum compatible partition.

**Proof.** Mandatory equalities are necessary for every compatible partition. Every learned cut preserves every compatible partition by Lemma 2. Therefore the master remains a relaxation containing all true solutions. A maximum relaxation model of size k is an upper bound on all compatible partitions. If the teacher accepts it, that bound is attained. A rejected candidate is excluded by its new cut and cannot recur. There are finitely many atom partitions, and the teacher terminates with its sufficient finite parameters. Hence the loop terminates. This argument does not prove polynomial work or exclude a very large worst-case number of proposals. Acceptance of an arbitrary non-maximizing candidate would not establish optimality; the maximization-before-query step is essential.

## 6. Certificates and software interfaces

The existing input keys alphabet, positive and negative and output keys status, blocks, max_devices and certificate are retained. The public functions remain solve_optimal and solve_profiled in the new version directory. General certificates have type teacher_cut_drup and contain the normalized negative index, false-region masks and original positive witness indices for every cut, followed by a DRUP trace refuting k+1 blocks. Structural shortcuts use symbol_bound or atom_bound. Detailed profiles expose teacher calls/time, partial enumeration progress, cuts, SAT queries, projection counters and the interruption phase.

**Theorem 2 (certificate sufficiency).** A feasible k-block output, verified false-region witnesses, and a checked refutation of the reconstructed relaxation at k+1 certify global optimality.

**Proof.** Direct original-word projection checks prove feasibility and each false region. Lemma 2 shows all true solutions satisfy the reconstructed cuts. A DRUP refutation proves that this relaxation has no partition above k, so neither does the original problem. The consumer checks each clause addition by reverse unit propagation and final conflict. Retaining deleted entailed clauses is sound; duplicate literals are normalized and tautologies are redundant.

The consumer imports neither MainTeacher, ProjectionStore nor a SAT solver. It reconstructs constraints from original data and witnesses rather than trusting producer-supplied CNF. Normalization, mandatory grouping and the deterministic master encoder remain a shared trusted base. Finite tests and AI-assisted reviews do not constitute formal software verification or independent scientific peer review. The source-level duplicate-literal checker concern raised in review was corrected without changing the teacher; the original review is preserved.

<!-- EVALUATION -->

## 8. Interpretation, limits and next authorized step

The new outer method implements informative rejection: one failed partition yields a necessary constraint on many partitions. It obtains an optimum certificate without eagerly extracting all W_i. The production examples demonstrate this mechanism, including multiple successive negative answers. That is a functional result, not evidence that the whole system is currently faster.

The unchanged teacher enumerates sum over q=1..m(B) of q^(|B|q)*2^q named DFA representations. In the ordinary interaction example, the final call enumerated more than one million representations even though the outer search needed only one cut. Three of ten benchmark cases completed in V45 within each one-second budget; V43 completed all ten. The teacher cost dominates the proposed sharing and cut mechanisms on these tests. A more suitable teacher implementation could matter more than further tuning the outer search, but it has not been substituted without permission.

A separately documented, NOT APPLIED follow-up observes that for this sufficient-bound, positive-OR feasibility interface, the canonical rejection row dominates every other local row and is itself realizable. It could support a restricted fast adapter. This would not preserve the manuscript's arbitrary partial-assignment and behavior-query interfaces, so it must not be advertised as a general replacement of main.pdf. Any implementation of that adapter requires explicit user approval; the exhaustive reference remains unchanged.

No first-in-literature novelty or universal performance superiority is claimed for SAT, projection sharing or candidate/test/refine loops. The present contribution is a specified exact outer construction, proof-carrying failure generalization, faithful reference integration and reproducible evidence including negative results. The project owner confirmed that suitable whole-trace AND-model field data are currently unavailable. Valid field trials remain zero. Synthetic test agreement does not identify physical device boundaries or labels of unobserved words.

## References

[1] Passive Compositional Automata Learning from Global Logs. User-supplied working manuscript, main.pdf, 11 pages. Sections 5.1-5.3 specify the exact bounded fixed-partition teacher; Section 5.5 describes a local candidate/cover-test/clause loop. Copied unchanged to sources/main.pdf; digest recorded in manifest.json. This manuscript is not treated as peer-reviewed evidence.

[2] Project V43 implementation and V44 assessment, 16 November 2026. Frozen local comparison artifacts in results/2026-11-16/exact_optimizer_v43 and final_assessment_v44. New V45 raw experiments, tests and AI-assisted reviews are retained separately; no historical evidence was rewritten.
