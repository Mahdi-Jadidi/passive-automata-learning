# Certified Maximum-Component Alphabet Partitioning from Global Traces

## Exact structural reductions, region-based witnesses, and proof-carrying optimization

Technical research manuscript | Implementation V43 | Assessment V44 | 16 November 2026

## Abstract

We consider a passive finite-sample problem: partition a declared alphabet into the greatest possible number of disjoint component alphabets such that independent regular factors accept every positive global trace and reject every negative global trace under conjunctive projected acceptance. Component state counts are unrestricted. We describe an exact optimizer that contracts logically mandatory symbol groups, solves a single-negative subproblem by a minimum-witness theorem, extracts minimal rejecting sets through monotone region elimination, and otherwise optimizes an equivalence-relation encoding. A feasible partition and a structural upper bound or a checked SAT refutation certify optimality. We give proofs of the reductions, extraction, encoding and overall algorithm, plus a restricted-family separation from a specified exhaustive baseline. Bounded audits include 2,261 optimum/certificate comparisons, 15,664 encoding checks and 120 comparable benchmark trials. The method has exponential worst-case costs and does not universally dominate dynamic programming. Existing operational logs were audited but lack the required whole-trace AND-acceptance semantics; no successful field validation is claimed. Scientific novelty and final software correctness remain subject to independent review.

## 1. Problem, scope, and contribution boundary

The aim is an exact optimization algorithm, not a heuristic partition proposal and not a learner of local DFAs. The input is a declared ordered alphabet Σ of opaque event identifiers and a finite sample D=(S+,S-). A word is an array of whole identifiers; epsilon is an empty array. Duplicate words within a label are normalized by first occurrence. Unknown identifiers, malformed records and duplicate alphabet identifiers are invalid input. Contradictory labels instead form a well-encoded infeasible sample. Declared identifiers absent from all traces remain in the problem.

A partition P={B1,...,Bk} consists of disjoint nonempty blocks covering Σ. For each B, let π_B erase events outside B and let K_B be a regular language over B. A word is globally accepted iff every π_B(w) belongs to its corresponding K_B. The objective is to maximize k=|P| over sample-compatible partitions. We return one optimum, not counts of compatible or optimal partitions, and not every tied optimum. No component-state bound, known component count, prefix labels, generative distribution or physical ownership information is assumed. An empty-alphabet extension follows the historical implementation convention: its sole empty partition accepts epsilon and is feasible iff S- is empty.

The main deliverable is a proof-carrying implementation of this contract. Its structural reductions are exact and its candidate order affects runtime only. The code imports a general SAT solver but no prior partition-solving backend. Claims of first discovery, universally fastest execution, or a polynomial algorithm for unrestricted inputs are expressly not made. The technical distinction is avoiding an explicit outer loop over complete partitions and avoiding enumeration of all satisfying partition models.

## 2. Projection characterization

For each nonempty B, choose the canonical finite language K_B=π_B(S+). Define reject(B)={i: π_B(y_i) is not in π_B(S+)}, where y_i enumerates normalized S-. We do not call this set R_B: that symbol denotes a local behavior relation in the supplied working manuscript [1]. Define W_i as the family of inclusion-minimal nonempty atom sets capable of rejecting y_i.

**Theorem 1 (exact finite-sample criterion).** P is compatible iff the union of reject(B), over B in P, contains every negative index.

**Proof.** Any admissible factor must contain each positive projection. Therefore, if that factor rejects a negative projection, the negative projection cannot equal any positive projection on its block. Conversely the finite languages π_B(S+) accept every positive projection and reject each negative having a covering block. A finite language is regular: a prefix trie with a rejecting sink realizes it. This proves necessity and sufficiency without learning or bounding that realization. The quantifier order is: for every negative, there exists one block that differs from every positive. The empty conjunction gives the stated empty-alphabet convention.

**Lemma 1 (monotonicity).** If B is contained in C, reject(B) is contained in reject(C).

**Proof.** Equality of two projections on C implies equality after erasing further to B. Thus a difference on B cannot disappear by passing to C. In particular, coarsening a compatible partition preserves compatibility. For nonempty Σ and disjoint labels, the one-block partition is feasible because projection onto Σ is the identity.

## 3. Mandatory atoms and exact closed cases

For negative y_i, a symbol a is mandatory for its rejecting block if removing a from Σ prevents rejection of y_i. All mandatory symbols for the same negative must share a block in any compatible P. Take the transitive closure of these equalities and call the resulting groups atoms; let q be their count. Atoms are proven preprocessing units, not recovered physical devices.

**Theorem 2 (safe contraction).** Contracting mandatory groups gives a bijection between compatible original partitions and compatible partitions of atoms, preserving the number of blocks.

**Proof.** If a rejecting block omitted a mandatory symbol, it would be contained in Σ without that symbol. Lemma 1 would contradict its rejection. Every compatible P must therefore respect all derived equalities and their transitive closure. Expansion of a partition of atoms recovers a unique original partition, and contraction is its inverse. Rejection is always computed on the expanded original identifiers, so compatibility is preserved.

If the singleton partition is compatible, k=|Σ| is immediately optimal. If the atom partition is compatible, k=q is immediately optimal. Both are attained upper bounds rather than guesses. Their certificates are reconstructed from the original sample by the consumer.

**Theorem 3 (one negative).** With exactly one negative and q mandatory atoms, let d be the minimum size of a nonempty rejecting atom set. Then the optimum is q-d+1.

**Proof.** Every compatible P has a rejecting block containing at least d atoms. Its other blocks together use at most q-d atoms, hence at most q-d blocks. Conversely a minimum rejecting set as one block, with each remaining atom as a singleton block, is compatible by Theorem 1 and has q-d+1 blocks. Enumerating subsets in increasing cardinality can stop at the first rejecting set; it need not enumerate all minimal witnesses or construct a SAT instance. The consumer verifies the partition and independently rules out smaller rejecting sets.

## 4. Complete extraction through unexplored regions

For fixed i, define monotone f_i(A) on nonempty atom subsets: the expanded set A rejects y_i. The extractor maintains known minimal witnesses and a frontier of maximal unexplored regions. A region U represents its nonempty subsets. Initially U is the set of all atoms. Empty regions are discarded.

If f_i(U) is false, all subsets of U are false. If U contains a known witness T, replace U by the regions U without a, for each a in T. Otherwise f_i(U) is tested; when true, successively remove an atom whenever the resulting nonempty set still rejects. Emit the resulting T and split U in the same way. Retain only maximal frontier regions and never process an identical region twice. One per-solve cache maps original symbol subsets to rejection bitmasks for all negatives, sharing projection work across obligations and preprocessing stages.

**Lemma 2 (minimization).** The deletion step produces an inclusion-minimal nonempty rejecting set.

**Proof.** It preserves rejection and nonemptiness. When removing a failed, the tested larger set without a was false. Every subsequently smaller set without a is false by monotonicity. Thus no retained atom can be removed at termination. Any proper rejecting subset would permit removing at least one retained atom, a contradiction.

**Theorem 4 (extraction completeness).** On successful exhaustion, the extractor returns exactly W_i and terminates under sufficient resources.

**Proof.** Maintain the invariant that every undiscovered minimal witness is contained in a pending region, or in descendants already generated from a processed region. A false region contains no witness. An undiscovered minimum cannot contain a distinct known minimum T, so it omits some a in T and is covered by U without a. Removing a frontier region dominated by a larger region preserves that coverage. A processed identical region already delegated its potential witnesses to its descendants, so processing it again is unnecessary. Lemma 2 proves soundness of every emitted set; the invariant proves completeness when the frontier is empty. There are only finitely many atom masks and children strictly shrink, establishing termination. This argument does not imply output-polynomial enumeration.

## 5. Equivalence constraints and direct optimization

For unordered atom pairs introduce e_ab meaning that they belong to the same block. Three implications for each triple enforce transitivity; symmetry is implicit and reflexivity is constant. Each nonempty witness T has a fully equivalent conjunction gate saying that all its members share the block of its first member. Each negative obligation Q_i requires at least one witness gate from W_i. A singleton witness gate is true. Representative r_j is true exactly when no earlier atom shares j's block. A fully equivalent sequential counting network expresses thresholds on the sum of representatives.

**Theorem 5 (representation and objective).** Models of these constraints correspond to compatible atom partitions, and the representative sum equals their number of blocks.

**Proof.** An equivalence relation defines one partition and vice versa. A block rejects y_i iff it contains a minimal nonempty rejecting subset: descend finitely inside any rejecting block for necessity and use Lemma 1 for sufficiency. Therefore Q_i is precisely the required negative condition. Each equivalence class has exactly one earliest atom, so it contributes exactly one true representative. Auxiliary gates implement their stated functions by equivalences, not by unproved one-way approximations. The encoding preserves both feasibility and the maximum-block objective.

Let d_i be the minimum cardinality of a witness in W_i. Every solution has k at most q-d_i+1; taking the smallest such bound gives U. The optimizer starts with a feasible one-block lower bound and searches thresholds between it and U. It reuses a single CDCL instance and its learned clauses, with threshold assumptions, updating the incumbent from each SAT model and the upper bound after each UNSAT result. There is no model-blocking enumeration. Once the bounds meet, it either returns an attained structural bound or generates a fresh, assumption-free refutation of the threshold k+1 formula.

**Theorem 6 (overall exactness).** Assuming exact finite computations and a sound complete SAT procedure, the algorithm terminates with a maximum compatible partition, or a correct infeasibility result, given sufficient resources.

**Proof.** Validation and direct infeasibility cases are exact. Theorems 1-3 justify every shortcut and contraction. Theorem 4 constructs complete constraints; Theorem 5 preserves their feasible partitions and objective. SAT thresholds are monotone, and each update preserves a feasible lower bound and a valid upper bound, strictly narrowing their gap. The final incumbent attains the common bound. All constructions, frontier traversals and the threshold interval are finite. A caught resource interruption instead returns INCOMPLETE with null mathematical claims.

**Algorithm 1. Certified maximum-component partition (operational specification).** Input: D and ordered Σ. Output: one optimum and certificate, or an explicit non-optimum status.

1. Normalize and validate whole event identifiers and labels. Handle contradictory labels and the empty alphabet directly. Initialize the shared rejection-mask cache. If the singleton partition covers all negative obligations, return it with the symbol-count bound.

2. For each negative and symbol a, query rejection on Σ without a. Union the mandatory equalities and expand their transitive groups into atoms. If the atom partition covers all obligations, return it with the atom-count bound.

3. If exactly one negative remains, query nonempty atom subsets in increasing cardinality until a rejecting subset T is found. Return T as one block and the remaining atoms separately, with its minimum-cardinality certificate.

4. Otherwise extract each W_i by the region procedure of Section 4. Build the equivalence, witness, representative and counting constraints once. Set L=1 with the one-block incumbent; set U to the minimum witness-size upper bound.

5. While L is smaller than U, set t=floor((L+U+1)/2). Query the incremental SAT instance under the assumption that at least t representatives are true. If SAT, decode and retain its partition and set L to its actual number of blocks. If UNSAT, set U=t-1. Interrupted queries do not update either mathematical bound.

6. Once L=U, attach an independently reconstructible attained upper bound when available; otherwise generate a fresh threshold L+1 CNF without assumptions and its DRUP refutation. In this general path, check feasibility and replay a DRUP proof when present, then return OPTIMAL. Shortcut returns in steps 1-3 construct their certificates directly and bypass this internal check. The separate consumer verifies all certificate types. A resource interruption returns INCOMPLETE, never a claimed optimum without the required certificate.

For example, on Σ={a,b,c}, S+={ab} and S-={ba}, singletons cannot reject ba. Both a and b are mandatory for its rejecting block, while c is free. Contraction immediately returns P={{a,b},{c}}, and q=2 certifies optimality without constructing a witness family or SAT formula. This example illustrates a structural shortcut; it is not an empirical benchmark.

## 6. Optimality certificates and software trust

A consumer first checks nonempty disjoint blocks covering Σ and replays original projections. An attained symbol or atom bound is verified directly. A single-negative bound requires independently checking the absence of a smaller rejecting atom set. An edge-size bound requires reconstructing the exact witness families. Otherwise the consumer reconstructs the deterministic threshold k+1 CNF and checks a DRUP refutation. A producer-supplied CNF or solver UNSAT flag is not trusted.

For every added clause C, reverse unit propagation checks that the current formula together with the negation of C reaches conflict. Hence the current formula entails C. Induction over accepted additions preserves the set of satisfying assignments, and a final propagation conflict proves that the original threshold is unsatisfiable. Deletion records can be ignored safely because retaining additional already-entailed clauses does not weaken this implication. An empty proof is valid only if the original threshold is already unit-inconsistent. Indexed checking stores literal occurrences once and uses fresh per-check assignments; it processes clauses affected by newly false literals rather than rescanning every clause per unit.

The implementation's trusted base includes normalization, direct projection equality, mandatory-group construction, complete witness extraction, CNF reconstruction and proof checking. Producer and current consumer share the deterministic encoder. Cross-checking against an older exhaustive encoder and a scanning checker reduces the risk of shared mistakes, but does not constitute independent peer review or machine-checked verification of the software. Native SAT is used through pinned local PySAT 1.9.dev22 and Glucose3. Proof logging and assumptions are supported by the documented API [5]. Python deadlines are cooperative; native calls are interruptible; hard termination may yield no response.

## 7. Complexity and a precise superiority theorem

With q atoms, equivalence encoding uses O(q squared) pair variables and O(q cubed) transitivity clauses, plus witness incidence and an O(q squared) counting network. Witness families, frontier states, SAT search, proof size and cache memory can still be exponential. The cache evaluates a symbol mask at most once per solve; this is not a bound on the number of distinct masks. Region management may increase membership queries on some inputs while avoiding many frontier candidates. State-count restrictions from the supplied manuscript are not imported.

**Theorem 7 (restricted-family separation).** Fix Σ_m={a,b,u1,...,u_(m-2)}, S+={ab}, S-={ba}, with m at least two. V43 constructs an optimum of m-1 blocks using polynomial work in the explicit input size. The specified exhaustive optimum baseline, after failing its singleton test, visits Bell(m) partitions.

**Proof.** Removing a makes both projections b; removing b makes both a. Thus a and b are mandatory in the same block. Removing any u_j leaves ab distinct from ba and creates no further obligation. The atom partition {a,b}, {u1}, ... is compatible, attaining the q=m-1 upper bound. There are O(m) rejection-mask queries, each using polynomial projection and mask operations, and polynomial-size stored data. No witness extraction or SAT call is needed. The fixed exhaustive baseline's singleton shortcut fails, and its defined traversal visits all Bell(m) partitions before claiming a maximum. This proves a separation against that baseline on this family; it says nothing about every possible competing algorithm, which could implement the same reduction.

The mathematical contribution claimed here is this problem-specific chain of exact reductions, certificates and scoped bounds. A globally fastest algorithm is not established. Experiments cannot prove that no better algorithm can be found, and correctness proofs do not establish first-in-literature novelty.

## 8. Validation and comparative experiment

The frozen V43 audit compared optimum values and verified certificates on 2,261 instances: all 2,187 distinct ternary labelings of seven words of length at most two over two symbols, four empty-alphabet cases, ten fixed synthetic cases and 60 seeded three-to-five-symbol cases. Every extracted witness family also matched the old exhaustive subset extractor. Separate checks covered all 167 antichains of nonempty subsets on four atoms, 4,000 indexed-versus-scanning propagation comparisons, 14 boundary cases, three mutations and two zero-limit cases. Three new DRUP traces were replayed by the frozen V42 encoder/checker in separate processes.

The V44 assessment additionally tested every pair assignment and threshold for 100 seeded three- or four-symbol samples: 15,664 checks agreed with direct projected compatibility. A further replay records every individual assignment, threshold and observed/expected Boolean result. Theorem 7 was exercised at m=2,3,4,8,16,32,64,128,256. All nine outputs were optimal with accepted atom-bound certificates. These structured inputs are generated tests, not field observations. None of these finite audits proves the absence of every software defect.

For performance, four methods solved the same one-optimum-plus-checked-proof task on ten fixed synthetic inputs, with three fresh child processes per method/case, cyclic order and a 60-second outer limit. All 120 trials completed OPTIMAL and their per-case objective values agreed. Enumeration and DP baselines include the exact singleton shortcut; neither counts all compatible partitions. They use the new final certificate pipeline, while their search procedures differ. Timed totals include solving, necessary construction, proof production, self-checking where implemented, and external consumer verification; imports and serialization are excluded and startup wall time is recorded separately.

| Case | Enumeration (s) | DP (s) | V42 (s) | V43 (s) |
|---|---:|---:|---:|---:|
| empty_all_8 | 0.000217 | 0.000206 | 0.000215 | 0.000287 |
| all_compatible_10 | 0.000249 | 0.000224 | 0.000211 | 0.000166 |
| oneblock_8 | 0.436126 | 0.005585 | 0.000814 | 0.001593 |
| ties_8 | 0.140743 | 0.003585 | 0.043689 | 0.000506 |
| reverse_9 | 0.703059 | 0.010121 | 0.070405 | 0.000558 |
| reverse_10 | 4.602137 | 0.015891 | 0.088171 | 0.000898 |
| overlap_8 | 0.319586 | 0.043492 | 0.311766 | 0.064956 |
| repeated_projections_9 | 0.000389 | 0.000314 | 0.000375 | 0.000646 |
| long_words_4 | 0.001857 | 0.002564 | 0.002432 | 0.001640 |
| many_words_3 | 0.008749 | 0.004944 | 0.006253 | 0.004260 |

Table 1. Median end-to-end pipeline and consumer-verification time in seconds, three repetitions. V43 had smaller medians than V42 and DP in seven cases each, and than enumeration in eight. On reverse_10 it was about 98 times faster than V42 and 17.7 times faster than the DP baseline. DP remained faster on overlap_8; V42 was faster on oneblock_8. Submillisecond differences are particularly sensitive to scheduling noise. The Windows median process peak working set for V43 ranged from approximately 22.16 to 22.64 MiB and includes Python and native imports; this does not establish algorithm-only memory superiority. No universal speed or memory ranking follows from ten synthetic cases and three repetitions.

## 9. Real-data readiness and field-test boundary

The repository contains a real BlueGene/L log sample and simulator-derived traces previously studied under selected last-event output semantics. The BGL sample has 2,000 rows, 120 event types, 1,857 non-alert and 143 alert messages. Its source identifies labels as per-message alerts [6]; it does not establish whole-trace conjunctive acceptance. No event type in the inspected sample had both alert and non-alert labels. Treating those records as isolated one-event words would therefore risk a trivial type-label problem rather than test recovery of component structure.

We executed a provenance/schema readiness audit and recorded the raw CSV digest and label counts, but did not manufacture an AND-acceptance data set or apply the selected-output theorem to a different model. The number of valid AND-model field experiments is zero. Field validation requires independently supplied whole-trace acceptance labels, declared event identifiers, episode/reset provenance, and a documented sampling protocol. The project owner explicitly confirmed that suitable field data are currently unavailable and requested that this limitation be recorded. Consequently the experimental evidence in this article is limited to synthetic, exhaustive small-instance and structured-family tests; operational AND-model performance remains unvalidated. A lack of field data is an open validation requirement, not a successful field result or a counterexample to the optimizer.

## 10. Related work and novelty audit

The supplied working manuscript [1] studies bounded local DFA behavior tables, coordination of global negative responsibilities and exact fixed-partition reasoning; its unknown-partition procedure still enumerates partitions. Our task retains unrestricted local state counts and only optimizes the alphabet partition. Thus the bounded-capacity behavioral dependencies are not transferred as additional constraints. Exact DFA identification by SAT is established work [2], but optimizes state structure for given labeled strings rather than our alphabet partition. Conjunction-based decomposition learning also has prior SAT formulations [3]; their existence means that conjunctive negative responsibilities and use of SAT are not standalone novelty claims.

Minimal true sets and monotone dualization are longstanding subjects [4]. Our region implementation must not be presented as the discovery of monotone enumeration, nor does it inherit the complexity of a different dualization algorithm automatically. Active compositional alphabet refinement [7] concerns a different query-enabled setting and possibly overlapping component alphabets. These comparisons identify relevant overlap and differences, not an exhaustive novelty certification. The defensible current contribution is the exact objective-specific construction, explicit certificates, implementation and reproducible scoped evaluation. A submission-level novelty claim needs an independent expert literature review.

## 11. Reproducibility, acceptance status, and conclusion

Code remains in results/2026-11-16/exact_optimizer_v43. The solver, encoder and checker are frozen by digests, and raw oracle comparisons, proof cross-checks, phase timings, extraction diagnostics and all benchmark outputs remain in the repository. The read-only summary script validates source integrity, trial identities, proof acceptance and the common optimum before recomputing medians. This V44 assessment adds structural-family evidence, bounded encoding checks, real-data readiness and a claim-status ledger. The generated article source and PDF builder are retained with a hash manifest.

The API returns OPTIMAL with blocks, maximum device count and a checkable certificate; INFEASIBLE with a direct certificate; or INVALID_INPUT/INCOMPLETE without mathematical result fields. Unknown resource outcomes are not infeasibility. The dependency is a local platform-specific PySAT installation; checker, parser and deterministic encoding are part of the trusted software base. Two additional Terra agents performed AI-assisted proof and evidence reviews; their reports and the resulting reporting clarifications are retained. These are not independent scientific peer reviews. Complete formal verification, independent peer review, broad field validation and universal superiority are not achieved by this artifact. It should be treated as a reproducible research implementation and article, not as a final peer-reviewed or globally optimal software system.

The algorithm demonstrates that unrestricted-state alphabet partition optimization need not be implemented as an outer Bell-number loop: exact contraction, single-obligation analysis, monotone region elimination and direct equivalence optimization avoid substantial redundant work on structured instances. It remains exact without heuristic answers, while openly retaining exponential worst-case costs and unresolved scientific validation requirements.

## Appendix A. Explicit Boolean construction

For each ordered triple a<b<c, the clauses are (not e_ab or not e_ac or e_bc), (not e_ab or not e_bc or e_ac), and (not e_ac or not e_bc or e_ab). These exclude exactly the nontransitive pair assignments. A conjunction gate g for literals l1,...,ls is implemented by all clauses (not g or lj), and one clause (g or not l1 or ... or not ls). An OR gate uses the dual clauses (g or not lj), and (not g or l1 or ... or ls). A one-input gate aliases its input, and empty conjunction is the fixed true literal.

For witness T with least atom a, its gate is the conjunction of e_ab for all other b in T. For each negative, add one clause containing all its witness gates. Representative r_j is the conjunction of not e_aj over earlier a; the first representative is true. Define C(0,0)=true and C(0,t)=false for t>0. At step j, C(j,0)=true and C(j,t) is equivalent to the OR of C(j-1,t) and the conjunction of r_j with C(j-1,t-1). Induction on j proves that C(j,t) means at least t of the first j representatives are true. The threshold t formula adds the single unit clause C(q,t); t>q adds an empty clause. This recurrence fixes the auxiliary semantics used in Theorem 5, rather than relying on a cardinality library's unspecified encoding.

## References

[1] Passive Compositional Automata Learning from Global Logs. User-supplied working manuscript, 11 pages, main.pdf, examined 16 November 2026. Incomplete abstract, complexity and evaluation sections; not treated as peer-reviewed evidence.

[2] M. J. H. Heule and S. Verwer. Exact DFA Identification Using SAT Solvers. ICGI 2010, LNAI 6339, pp. 66-79. Author copy: https://www.cs.cmu.edu/~mheule/publications/DFA_ICGI.pdf

[3] N. Lauffer, B. Yalcinkaya, M. Vazquez-Chanlatte, A. Shah and S. A. Seshia. Learning Deterministic Finite Automata Decompositions from Examples and Demonstrations. FMCAD 2022; preprint arXiv:2205.13013. https://arxiv.org/abs/2205.13013

[4] M. L. Fredman and L. Khachiyan. On the Complexity of Dualization of Monotone Disjunctive Normal Forms. Journal of Algorithms 21(3), 618-628, 1996. DOI:10.1006/jagm.1996.0062. https://doi.org/10.1006/jagm.1996.0062

[5] PySAT documentation. SAT solvers' API and DRUP proof logging. Consulted 16 November 2026. https://pysathq.github.io/docs/html/api/solvers.html

[6] Loghub project. BGL data description and per-message label semantics. https://github.com/logpai/loghub/blob/master/BGL/README.md . The locally pinned CSV has SHA-256 3fe74103c0b02a28514534e2a47257a3f770135ca61afd425bbd3b9d6a31fe26.

[7] L. Henry, T. Neele, M. R. Mousavi and M. Sammartino. A Detailed Account of Compositional Automata Learning through Alphabet Refinement. arXiv:2504.16624v3, revised April 2026. https://arxiv.org/abs/2504.16624v3
