# An Algorithm for Partitioning Traces

@ Certified alphabet partitioning with a polynomial teacher · V47

## Abstract

We partition the event alphabet of a finite labeled trace sample to maximize the number of blocks whose projected regular languages jointly classify that sample. For a fixed partition, an exact polynomial test uses membership in the projected positive languages. We prove equivalence with the exhaustive local-automata teacher for the sufficient trie-bound calls made by the optimizer. The outer search uses witnessed constraints and a checked upper bound. Finding the maximum over an arbitrary declared alphabet remains NP-hard, even with one empty negative and positives of length two. All 2,261 corpus inputs completed at a 0.25 s per-case limit. In a matched ten-case comparison at 2 s, the projection version completed ten cases and the exhaustive version completed three.

**Keywords:** trace projection, exact search, alphabet partitioning, proof certificates, NP-completeness.

## 1. Problem Statement

The input is a finite ordered alphabet Σ of event IDs and a labeled sample D=(S⁺,S⁻) of words over Σ. An alphabet partition P has disjoint nonempty blocks covering Σ, including any declared events absent from the sample. A projection π_B deletes the events outside B and retains order. A trace is split into its projections onto the blocks of P.

Compatibility means that regular languages K_B over the respective blocks accept π_B(x) for each x∈S⁺ and every B∈P, and for each y∈S⁻ at least one block rejects π_B(y). We seek one compatible partition of maximum size k=|P| with a checkable upper bound. Local state counts are unrestricted. The objective gives no uniqueness or identification guarantee.

**Lemma 1 (canonical projected languages).** Define H_B={π_B(x) : x∈S⁺}. Then P is compatible exactly when for every negative y_i there exists a B with π_B(y_i)∉H_B. *Proof.* A local factor accepting the positives contains H_B, so membership in every H_B makes rejecting y_i impossible. Conversely choose K_B=H_B on every block. These finite regular languages accept the positives and reject each negative on its witnessing block. ∎

**Boundary cases.** A word with both labels cannot satisfy the conjunction conditions. When Σ=∅, the empty conjunction accepts ε, so the empty partition is compatible exactly when S⁻=∅. On nonempty Σ with disjoint labels, the identity projection on Σ shows that the one-block partition is compatible. Deduplicating labeled traces preserves these conditions and keeps the declared alphabet.

**Exact cached projections.** A prefix node represents its parent's word followed by its last event. Interning by the pair (parent, event) identifies equal prefixes by induction on length. If B⊆C, applying π_B after π_C gives π_B directly. Projecting the parent and then keeping or erasing the last event proves the cached transformation by induction. Witness indices and rejection marks follow from these projections.

The method uses Lemma 1 as the teacher and retains the SAT relaxation for selecting P. SAT-based DFA identification [4] and conjunctive DFA decomposition [5] seek automata in different spaces. The outer necessary cuts relate to logic-based Benders decomposition [2]. Their validity here comes from witnessed projection equalities.

<!-- page -->

## 2. Correctness of the Polynomial Teacher

### 2.1 Test a fixed partition

The teacher receives the projected word lists for a valid P. Each list of projected negatives is aligned to the same original indices. Repeated projections of different negative traces retain distinct indices.

```
U ← all negative indices
for each block B while U is nonempty:
    H ← set of projected positives on B
    U ← indices i in U with projected negative i in H
return ACCEPT if U is empty, otherwise REJECT
```

**Invariance.** Initially U contains every negative because the conjunction over no processed blocks is true. Suppose after j blocks U equals the indices whose projections belong to H_B on each of those blocks. At block j+1, constructing H_B inserts every projected positive, and filtering U intersects the previous set with the membership condition on this block. Therefore the invariant holds for j+1.

**Verdict.** An empty U means every negative has failed some processed factor. Future intersections cannot add indices. At exhaustion, a nonempty U contains exactly the negatives that pass every canonical projected positive language. Lemma 1 proves that the two returned verdicts are sound and complete. A resource interruption propagates without a verdict.

### 2.2 Recover the exhaustive teacher's decision

The exhaustive teacher [1] decides existence of bounded local DFAs. The optimizer's bound for a block is one for empty H_B, or the number of distinct prefixes of H_B including ε plus one. Build a complete DFA with those prefixes, start at ε, accept exactly words of H_B, and send any absent extension to a self-looping rejecting sink. For empty H_B use one rejecting state. Thus every canonical H_B fits the corresponding bound. If the projection teacher accepts, the tuple of canonical DFAs is a bounded witness. If the exhaustive teacher accepts, its bounded DFAs are regular factors, which imply acceptance by Lemma 1. Both implications apply to these optimizer calls.

The interface here is fixed-partition compatibility for an unrestricted-state sample. Computing the earlier teacher's entire relation of realizable bounded behaviors, supporting prescribed partial assignments, or honoring independent tighter state limits is outside this equivalence. The optimizer only consumes a completed verdict. It also compares that verdict with the union of cached block rejection masks before learning a cut.

### 2.3 Cost of the decision

For k blocks, p positives, r negatives and L symbol occurrences in the input, materialized images have at most k(p+r) rows. Their total symbol length is L because the blocks partition Σ. Building the sets and testing membership costs O(k(p+r)+L) under ordinary hash-table costs on interned event IDs. Even under worst-case hash collisions at most p stored tuples are probed per set operation, which gives a polynomial worst-case comparison bound in the explicit input length. The decision uses O(p+r) additional references and indices. Constructing the images by direct projection is polynomial. The shared outer cache can grow with the number of distinct queried masks.

<!-- page -->

## 3. Reduction to a SAT Relaxation

Order the atoms by their first event in Σ. When an atom set occurs as the argument of a projection or rejection predicate, expand it to the union of its events. Write r_i(B) for π_B(y_i)∉H_B.

### Step 1. Contract mandatory events

**Lemma 2.** Rejection is upward monotone. If B⊆C and r_i(B) holds, then r_i(C) holds. *Proof.* If π_C(y_i)=π_C(x) for a positive x, projecting again onto B gives π_B(y_i)=π_B(x), a contradiction. ∎

For negative y_i form M_i={a∈Σ : r_i(Σ∖{a}) is false}. A block rejecting y_i must contain each a∈M_i. Otherwise it lies inside Σ∖{a}, contradicting Lemma 2. Hence all symbols in M_i share a block of every compatible partition. Join the symbols within each M_i and take the transitive closure. The resulting equivalence classes are the atoms. Every compatible partition contracts uniquely to atom blocks and expands back without changing its count or any projected word. Thus q atoms give an upper bound of q blocks. A compatible singleton partition attains |Σ| and a compatible atom partition attains q.

### Step 2. Turn a completed rejection into a necessary cut

By Lemma 1, a rejected partition has an index i for which every block B fails r_i. For each such B, start from its atom mask and add an atom only if the larger region U still fails r_i. Keep a positive x_U with π_U(y_i)=π_U(x_U). An addition skipped because it would reject cannot become legal later by Lemma 2. Therefore one scan yields an inclusion-maximal false region per block. A positive match alone suffices for validity.

**Lemma 3.** Require some block C of the next partition to satisfy C⊄U for every recorded U. The rejected partition fails this requirement because each of its blocks has its own containing region. In any compatible partition, some C rejects y_i. If it were contained in a recorded U, Lemma 2 would force that U to reject y_i despite its witness. Therefore the cut preserves every compatible partition and excludes the rejected one. ∎

### Step 3. Encode exactly the partitions, counts and cuts

Use e_ab for each unordered atom pair. Set the diagonal implicitly to true and interpret e_ba=e_ab. For a<b<c, with pair bits x=e_ab, y=e_ac, z=e_bc, impose (¬x∨¬y∨z), (¬x∨¬z∨y) and (¬y∨¬z∨x). These are exactly the three transitivity implications for distinct atoms. Cases with repeated atoms follow from reflexivity and symmetry. Every model therefore yields equivalence classes, and every partition gives one such pair assignment.

Let z_j be true exactly when no earlier atom is equivalent to j. This selects the least index of each class once. Define T(j,d) as “at least d representatives among the first j atoms.” Set T(j,0)=true and T(0,d)=false for d>0. For d>0 use T(j,d)=T(j−1,d)∨(z_j∧T(j−1,d−1)). Induction on j proves it by splitting on whether the first j−1 already suffice. Thus T(q,d) is the exact block-count test.

For anchor a, the class of a escapes U if a lies outside U or some b outside U has e_ab=true. Conjoin these tests over U and disjoin over a. This implements Lemma 3 because each class has an anchor. Each AND output v over inputs l_j uses (¬v∨l_j) for each j and the clause (v∨¬l_1∨…∨¬l_d). The OR clauses are the dual. Hence each gate is equivalent to its function. A partition satisfying the cuts extends to a model by evaluation, and every model decodes to a partition satisfying all cuts.

<!-- page -->

## 4. Algorithm, Exactness and Verification

**Algorithm 1.** Maximize the number of compatible blocks.

```
Validate and normalize D. Resolve label conflicts or an empty alphabet.
Test singleton blocks with the teacher. If compatible, certify |Σ|.
Construct mandatory atoms. If their partition is compatible, certify q.
Learn the first cut from the rejected atom partition.
repeat:
    Maximize T(q,d) under the current cuts by SAT threshold queries.
    Decode a maximizing partition P and ask the teacher.
    If it rejects, learn a witnessed cover cut and repeat.
    If it accepts, let k = |P| and obtain a refutation at threshold k+1.
    Return P and the checked certificate.
On resource exhaustion, return INCOMPLETE with no optimum claim.
```

The atom test reuses the singleton verdict when the partitions coincide.

**Step 4. Maximize the current relaxation.** The bounds start at an attained lower endpoint 1 and upper endpoint q, or an upper endpoint certified in a previous round. The one-block partition is compatible on disjoint labels over nonempty Σ, so every learned cut preserves it. New cuts only shrink the relaxation. If a query for T(q,d) is satisfiable, a decoded model attains some m≥d and supplies the updated lower endpoint and candidate. If it is unsatisfiable, no relaxation partition has count ≥d, so d−1 is a valid upper endpoint. The algorithm tests the inherited upper endpoint and otherwise bisects the remaining interval. Each interior query strictly reduces the interval and preserves both bounds, so at convergence the retained candidate attains the exact relaxation maximum.

**Theorem 1 (soundness, optimality and termination).** On a valid input with sufficient resources for exact calls, Algorithm 1 returns a certified infeasibility result or one optimal compatible partition. *Proof.* The boundary cases are justified in Section 1. For the general case, by Step 1 every feasible partition is represented and by Lemma 3 each learned cut retains it. The current relaxation maximum is therefore an upper bound on every compatible objective. A completed teacher acceptance of a maximizing candidate attains that bound. After each completed rejection, the failed proposal is removed permanently and at least one compatible partition remains. The domain of atom partitions is finite. The exact teacher operations and threshold searches terminate on each call, so the algorithm eventually accepts. A resource interruption supplies neither a rejecting verdict nor any cut derived from an unfinished teacher check. ∎

**Step 5. Replay the certificate.** For infeasibility, check the label conflict or empty-alphabet condition in Section 1. For optimality, check that the blocks are nonempty, disjoint and cover Σ, then check Lemma 1 directly. Check the attained bound for a structural certificate. Otherwise recompute the atoms, check each equality π_U(y_i)=π_U(x_U), and regenerate the CNF at k+1. By Lemma 3, these matches suffice for cut validity. Every better compatible partition would satisfy the reconstructed formula.

**Step 6. Check the refutation.** Unit propagation under the negation of each added clause must yield conflict. Propagations are logical implications, so by induction all retained additions follow from the initial CNF even if deletions are ignored. A final conflict without assumptions proves unsatisfiability [3]. With Step 5 this proves optimality. The checker trusts the shared normalization, contraction and encoder.

For existence, discard tautologies and eliminate each variable by retaining pivot-free clauses and adding the non-tautological resolvents of opposite-sign pivot clauses. A remaining assignment extends unless it violates a retained clause or forces both pivot values, violating a resolvent. Unsatisfiability therefore yields the empty clause. Negating a resolvent forces both pivot signs, which verifies the addition.

<!-- page -->

## 5. Experiments

The matched comparisons retained the outer SAT policy, cuts and certificate consumer. We used Windows x64, CPython 3.12.14 and Glucose3. Timed matched runs were sequential in fresh processes with identical worker and checker budgets. Solver time excludes startup and standalone verification. Completed results were compared against reference objectives and checked certificates.

| Evaluation | Observed result |
|---|---|
| Corpus, 0.25 s per input | 2,259 checked optima and two checked infeasibility results. All 2,261 completed. |
| Ten fixed cases, 2 s per solver and checker | Projection 10/10 completed and exhaustive 3/10. Projection solve times were 0.195–45.262 ms. |
| Ordinary interactive fixture, two matched repetitions | Median solve time 4.137 s exhaustive and 7.528 ms projection. All four results certified. |
| 158 previously audited inputs | 121 checked optima and 37 checked infeasibility results, all agreeing with the independent reference. |
| 103 graph-derived inputs | All matched brute-force minimum covers through the reduction in Section 6 and passed certificate replay. |

**Decision replay.** Across all 2,187 disjoint labelings of the seven words of length at most two on two symbols, both partitions agreed with direct pairwise projection tests. These 4,374 comparisons exercise the teacher independently of the search. An injected interruption returned no verdict. Direct trace replay checked the six master maxima and the six learned cuts observed on the 158 audited inputs.

**Bottleneck after the change.** On overlap_8, a 45.262 ms solve spent 0.152 ms inside the projection decision and 0.429 ms in the teacher-call path including projection retrieval. At 2 s, clique instances on 10, 12 and 16 vertices ended incomplete during the internal certificate check. The 20-vertex instance ended incomplete in master search. Each has optimum two by Section 6. These measured workloads support the reduction in teacher cost while showing that the remaining costs can matter. Every incomplete run abstains.

**Reproducibility and scope.** The tests use synthetic traces. There are zero valid field trials with whole-trace AND labels. The archive includes the exact input lists, run limits, traces, code and certificate replay. @link(V47 artifact archive|https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/799d1aa3154044534321d5f3855dd512c7238e63/CHECKPOINT_V47.md)

<!-- page -->

## 6. Complexity of the Outer Problem

**Theorem 2.** Deciding whether a compatible partition has at least K blocks is NP-complete, even for S⁻={ε} and positive words of length two.

*Proof.* A partition is a polynomial-size witness. Its block count and sample compatibility can be checked in polynomial time using Section 2. For hardness, reduce Vertex Cover [6]. Start from a simple graph G=(V,E) with at least one edge and a bound 1≤t≤|V|. The omitted trivial boundary cases are decidable directly. Declare Σ=V and choose an order. For each edge {u,v} put the word uv in S⁺, ordered by Σ. Put only ε in S⁻. This construction is polynomial and the labels are disjoint.

For a block B, π_B(ε)=ε. The projection of an edge word equals ε exactly when B contains neither endpoint. Hence B rejects ε exactly when it meets every edge. By Lemma 1 the partition is compatible if and only if one of its blocks is a vertex cover. Write τ for the minimum cover size and n=|V|. Any such block uses at least τ vertices, leaving at most n−τ singleton positions and therefore at most n−τ+1 blocks in total. A minimum cover as one block and all other vertices as singletons attains that count. Thus a cover of size at most t exists if and only if a compatible partition has at least K=n−t+1 blocks. ∎

A worst-case polynomial bound for arbitrary Σ on exact optimization would imply P=NP. For fixed |Σ|, the number of possible atom partitions, covers and distinct CNF instances is bounded independently of trace length. The exact master and proof steps then have costs bounded in terms of |Σ|, and the polynomial projection and witness work gives polynomial total time in the sample encoding. This statement allows the constant to depend on |Σ|.

## 7. Conclusion

The projection teacher removes the DFA enumeration cost for the stated decision and preserves the certified optimization contract. The graph reduction identifies a separate complexity barrier for finding a maximum partition, consistent with the measured cost of search and proof replay on the stated stress cases.

## References

[1] *Passive Compositional Automata Learning*. Supplied manuscript, Sections 5.1–5.3. @link(Archived manuscript|https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/v46/results/2026-11-16/interactive_teacher_v45/sources/main.pdf)

[2] J. N. Hooker and G. Ottosson. Logic-based Benders decomposition. *Mathematical Programming* 96, 33–60, 2003. @link(DOI|https://doi.org/10.1007/s10107-003-0375-9)

[3] SAT Competition 2013. *Certified UNSAT*. DRUP specification. @link(Specification|https://satisfiability.org/competition/2013/certunsat.shtml)

[4] M. J. H. Heule and S. Verwer. Exact DFA identification using SAT solvers. *ICGI*, 66–79, 2010. @link(DOI|https://doi.org/10.1007/978-3-642-15488-1_7)

[5] N. Lauffer, B. Yalcinkaya, M. Vazquez-Chanlatte, A. Shah, and S. A. Seshia. Learning deterministic finite automata decompositions from examples and demonstrations. 2022. @link(arXiv:2205.13013|https://arxiv.org/abs/2205.13013)

[6] R. M. Karp. Reducibility among combinatorial problems. *Complexity of Computer Computations*, 85–103, 1972. @link(DOI|https://doi.org/10.1007/978-1-4684-2001-2_9)
