# 04 — Information-Efficient Partition Query Selection

**Research module:** 04 / adaptive query policy  
**Reference repository:** `Mahdi-Jadidi/passive-automata-learning`  
**Pinned commit:** `7c90eb59561bd25ec4fdca5ac08b0e5d60d17fd`  
**Target directory:** `implementation/partition_feedback_final/`  
**Status:** proposed research design, mathematical guarantees under stated hypotheses, and implementation specification; not a deployed solver or a measured end-to-end improvement.

## Executive recommendation

Implement **Certificate-Directed Adaptive Query Selection (CDAQ)**: a small, budgeted pool of complete partition proposals, ranked by the value of the *proof work* that each conclusive outcome would remove. Maintain a protected exact-search anchor, a verified incumbent, and a certificate ledger independent of the scoring model. Use:

1. a guaranteed conditional NO elimination score based on refinement and, optionally, known same-negative zero-region closure;
2. a guaranteed conditional ACCEPT score based on the incumbent cutoff;
3. an optional, explicitly heuristic expected additional feedback score and cost model;
4. a limited exploration budget and a compulsory exact-search fallback.

The policy is not a new oracle, a new DFA learner, or a replacement for the exact search. It changes which complete partition is submitted next. In particular, a diagnostic can be coarser than the current minimum-cost frontier because a NO there may remove many cheaper alternatives. An ACCEPT at that diagnostic is not an optimality certificate unless the lower-cost region is already proved closed.

**Main research contributions proposed here:** (i) an outcome-conditional certificate-progress functional with a conservative robust score that requires no prior over future tables; (ii) a sparse frontier implementation of that functional; (iii) a guarded scheduling theorem separating optional diagnostics from compulsory progress; (iv) a conditional contraction bound on query complexity and a model-specific diagnostic localization example. The previous reports already suggested expected elimination, weighted diagnostic queries, zero-region closure, and witness-based optimization. Those ideas are foundations, not claimed as new discoveries. The contribution is their precise operationalization and the additional guarantees below. Novelty relative to all published literature remains to be established.

**Primary engineering conclusion:** at 100,000 symbols the current representation and teacher-output costs can dominate before query ranking is reached. Query selection cannot cure those bottlenecks by itself. Preserve the external interface; optimize the selector's data structures and use only compression explicitly supported by the external response format.

---

## 1. Problem and external contract

### 1.1 Mathematical model

Let \(\Sigma\) be a finite nonempty declared alphabet, \(n=|\Sigma|\). The sample \(D=(X,Y)\) consists of original indexed positive and negative ordered words, \(X=(x_j)_{j=1}^p\), \(Y=(y_i)_{i=1}^q\), over \(\Sigma\). Duplicate IDs may share a word but must not be conflated in transmitted or certified feedback. Erasing projection \(\pi_B\) preserves order and multiplicity. Unused declared symbols remain part of every submitted complete partition.

Let \(\mathcal P\) be the admissible family (all set partitions by default). Write \(R\preceq Q\) when each block of \(R\) is contained in one block of \(Q\) (R is finer). Define
\[
c(P)=n-|P|,\qquad
s_i(B)=\mathbf1[\forall j:\pi_B(y_i)\ne\pi_B(x_j)].
\]
Under the unrestricted model, compatibility is
\[
f(P)=1 \Longleftrightarrow \forall i\ \exists B\in P:\ s_i(B)=1.
\]
We minimize \(c(P)\) subject to \(P\in\mathcal P\) and \(f(P)=1\). The paper's Lemma 1 proves this criterion: finite languages of positive projections suffice, with complete DFAs. Proposition 1 proves that structural failure propagates to refinements. The paper's Theorem 1 establishes NP-completeness of the unrestricted decision problem, already for length-two traces. Thus a universal polynomial exact optimizer is not implied by an efficient selector.

If labels conflict, identical positive and negative words prove infeasibility. For unrestricted nonempty \(\Sigma\), all partitions are feasible if either trace class is empty. If the sample is disjoint and the one-block partition is admissible, that partition is feasible. A restricted admissible family can still be infeasible. For an empty alphabet (outside the paper's assumption), explicitly reject input or document the unique empty partition as feasible iff there are no negatives; do not let an empty block stand in for a nonempty component.

For the unrestricted all-partitions problem, absent symbols can be made singleton without weakening separation. A sound contraction of mandatory same-block classes supplies a quotient root: all feasible partitions coarsen it. Root cost must be measured against the **original** alphabet. For restricted families or finite state bounds, prove any unused-symbol reduction separately or disable it.

### 1.2 What the main paper actually promises

Source: supplied *Passive Compositional Automata Learning from Global Logs*, pp. 3–4, 7–9, 12–17, 23–24; in particular Fig. 2, §5.1, Eq. (23), §5.2 and Appendix B.

| External event | Paper's semantics | Safe selector action |
|---|---|---|
| Projection failure | Returns partition, ordered negative indices, one failing original negative and a positive witness on each block, plus \(R_B^\infty\) per block. May pass these by reference. | Record structural NO, validate witnesses, extract every certified zero/free column; refinement closure is safe. |
| Unrestricted success | Returns partition and complete local DFAs witnessing sample consistency. | Verify response/partition and witness artifact, update incumbent; do not require tables. |
| Bounded success | Returns local DFA witnesses under fixed bounds; the bounded solver also constructs a joint rejection assignment internally. | Verify sample and bounds when available. Do not assume extra internal data are exposed. |
| Completed bounded failure | Exact FAIL for this sample, partition and capacity configuration. Richer explanation interface remains open (§5.1). | Record exact-partition NO only, unless separately verified structural evidence exists. |
| Timeout, cancellation, truncation, malformed response | Operational extension, not a mathematical NO defined in the paper. | Keep unresolved; count attempted work, retry/defer or obtain a permitted independent proof. |

The unrestricted local table \(R_B^\infty\) is the set of bit vectors with
\[
\pi_B(y_i)\in\pi_B(X)\Rightarrow r_i=0,\quad
\pi_B(y_i)=\pi_B(y_j)\Rightarrow r_i=r_j.
\]
The paper explicitly permits a compact representation: fixed-zero columns and groups of identical projections; free groups choose independent bits. Thus a column fixed to zero in a **complete unrestricted table** is equivalent to a positive projection match. One feasible row with a zero is not evidence of fixedness. A non-fixed column proves that a rejecting local DFA exists in the unrestricted setting; the simultaneous all-free-one row exists. A returned fixed-zero column need not carry a positive ID except for the named failure witnesses; recover a matching ID from the raw words if necessary for the independent verifier, or retain a trusted complete-table assertion with provenance. Do not manufacture witness IDs. Non-fixed equal columns in a complete unrestricted table imply equal negative projections; fixed-zero columns need not be equal projections. Use named same-pair unary/binary equality stitching only when its premises are established.

The paper's bounded base relation \(R_B\subseteq R_B^\infty\) consists of jointly realizable rows from a single positive-consistent DFA of at most \(m(B)\) states. Fixed zeros can arise because of capacity, not because of equal projections. Reduced/conditioned relations are additionally specific to a partition or branch. Neither may be treated as an unrestricted zero region. A complete bounded NO does **not** exclude refinements or coarsenings. Paper Example 5: positives \(\{\epsilon,aa,bb,aabb\}\), negatives \(\{a,b,ab\}\), two states per block; singleton blocks work but one merged block does not. Paper Example 11 gives different feasibility among partitions of the same cost. A bounded solver may reject even the coarsest partition. Do not initialize a bounded incumbent from disjoint words alone.

**Deployment decision:** this report's main policy assumes no state bounds, as specified in the assignment. The adapter must explicitly declare regime, sample digest, admissible family and response semantics. If capacity is unknown, use the safe bounded/generic mode (exact NO only, verified ACCEPT cutoff, structural deductions from raw equalities still valid), disable unbounded-only positive inference and quotient shortcuts not independently justified, and report the discrepancy. No proposed change to the external evaluation or learning system is required.

### 1.3 The information paradox: passive traces, not active labels

For fixed raw D, unrestricted compatibility and \(R_B^\infty\) are deterministic functions of D. In an information-theoretic sense, \(H(f,R^\infty\mid D)=0\) under any distribution on D. Returned witnesses or choice of failing negative can vary operationally, but do not add unknown ground-truth labels. Our queries are requests to a computational service over known data, not membership/equivalence queries to the target system. Active-learning concepts are useful **analogies for budgeted evidence acquisition**, not evidence that we learn new traces.

Distinguish:
- **Full raw reasoning:** can solve the unrestricted problem with zero compatibility calls, though optimization and verification may be exponentially expensive. If the external workflow requires the returned machines, submit the proved optimal partition once as a handoff.
- **Budgeted raw reasoning:** local proof production is limited and external evaluations may be cheaper or provide convenient complete evidence.
- **External-confirmation mode:** only an externally confirmed success counts as the deployable incumbent. Raw feasibility proofs are mathematically valid, can guide ranking and may support a separately reported mathematical optimum, but an accepted partition/DFAs are required for the final operational result. Keep the two incumbent statuses explicit. A mathematical cutoff may use raw proofs only if the search contract permits that; otherwise protect its best candidate for confirmation.

Experiments must charge local preprocessing, independent verification, wire transfer and final handoff, not artificially suppress raw data to claim a universal reduction in queries. No positive black-box query lower bound exists for unrestricted optimization with unlimited local computation and no mandatory handoff.

---

## 2. Audit of supplied research and implementation

### 2.1 Previous reports (read in full)

[R2] *Independent algorithmic analysis: partition selection from traces*: zero regions indexed by original negative; deletion-witness hitting-set lower bound; joint block-cover DP; canonical parent branching; cross-table closure; suggested expected weighted elimination plus incumbent value. Its maximal-region enumeration and exact hitting-set/DP can be exponential. The report's all-zero inference must use unrestricted base tables, not bounded or truncated tables. The stated refinement count is mathematical coverage, not paid work saved.

[R3] *Choosing an optimal alphabet partition from trace evidence*: exact unary/binary discrepancy atoms (also main paper Lemma 2), minimum component-rank characterization, stronger named-equality stitching and clique test in the single-positive/single-negative case, explicit bounded-corpus implication reference procedure, and outcome-conditional avoided-work forecasts. Its example with diagnostics uses 11, 6, 4 calls under intentionally restricted raw information; it is not general speedup evidence. Complete atom families give exact necessity; partial atom lists certify found separating alternatives but cannot be mistaken for complete necessity. Both reports explicitly recognize zero semantic information gain with exhaustive raw reasoning.

**Extension beyond R2/R3:** replace verbal scoring advice by an outcome-indexed function over a common residual search measure; prove outcome-conditional lower bounds, conditional worst-case contraction, and scheduling/overhead guarantees; define efficient feature generation, incremental cache semantics, calibration and fair fallback. Retain all prior evidence rules instead of re-deriving a separate optimizer. Note that same-negative regions from different queries can jointly exclude partitions outside the union of the individual refinement cones. Cross-negative unions of regions are not a proof.

### 2.2 Pinned repository and newer supplied packages

The pinned directory was accessed through GitHub. Inspected `search.py`, `model.py`, `staged.py`, `compact.py` and `RESEARCH_STATUS.md` at the specified ref; compared the local archive's core implementation and read `hybrid.py`, the scale report and measurement summaries. Core `search.py` is the same length/structure in the pinned and scale versions; the scale archive extends `model.py` and `staged.py` with sparse reverse-pair mandatory contractions. Do not silently treat those snapshots as identical. The pinned repository was read, not modified.

Key functions:
- `model.ProjectionOracle.row` caches per-block positive matches `zeros=[[i,j],...]` and free groups `free=[[i,...],...]`. `__call__(partition,purpose)` returns **tables on both ACCEPT and NO**, a first failing index, block masks and verdict. The local protocol is stronger than the paper on success and on positive IDs for all fixed zeros.
- `search.check_reply` (pinned lines 275–294) expects a full table for every block and derives coverage from free groups even on ACCEPT. It requires an integer positive ID for every zero and assumes unrestricted table semantics. `compact.py` provides optional witness-ID normalization, not an external capacity adapter. A production interface must not require this emulator's richer contract.
- `Evidence.zero/ingest/regions/accepted` (lines 25–87) stores maximal zero regions and minimal separating sets, keyed by negative. `regions` makes a witnessed failure cover; `choose_region` maximizes the number of immediate merges hidden by that cover. This score is an existing branching heuristic, not predicted evaluation value.
- `diagnostic` (lines 222–274) looks at same-positive groups of covered atoms, greedily packs disjoint pair merges in two orders, tries up to three negatives, and ranks using estimated unknown immediate children divided by number of groups. It excludes already queried/inferred candidates, needs gain >=2, and is disabled by default (`diagnostic_limit=0`).
- `repair` (lines 183–220) tries known separating blocks or small witness transversals, with bounded local combination trials. The general search tries the repair once as an incumbent proposal; it is heuristic and does not supply a lower bound.
- `select` (lines 296–477) traverses cost layers, skips proven incompatibilities, uses certified bounds and a path-preserving crossing-merge rule. `following` deduplicates the next layer. It may run up to two diagnostics per processed node under the global diagnostic budget. It initializes a mathematically feasible top incumbent in the unrestricted disjoint-sample regime and may infer ACCEPT. Current timeout handling raises `DeadlineExpired` and can discard the accumulated transcript/incumbent; production should retain restartable state. `query_limit` must count all submitted attempts, including timeouts, not just unique completed replies.
- `staged.solve` and `hybrid.py` perform singleton/pair/two-pair/triple analysis, optional exact witness rank, and then general search. The newer archive checks a mandatory-root partition early via `ProjectionOracle` on an eligible default route. Its local shortcut is disabled for custom teacher and explicit query-limit configurations. In the new design do not accidentally bypass external query accounting or required confirmation.
- `verify.py` independently replays raw evidence and coverage certificates; preserve its independence from the selector and the score. Do not infer external bounded feasibility from this verifier's unrestricted projection test.

### 2.3 Mathematical and computational limitations

1. The diagnostic's score treats an immediate-child estimate and number of packed groups as a proxy for saved queries; neither is a reliable estimate of certification cost. A NO at a high-cost candidate is useful only if it closes still-relevant lower-cost work. An ACCEPT can change the entire residual frontier. Non-failing negative columns and reusable cross-query closure are not explicitly valued.
2. A scan of `combinations(partition,2)` is already ~5 billion pairs at 100,000 blocks, before containment tests. `list.remove`, nested region scans and full mask operations add overhead. A score must not generate the full layer or all pair merges.
3. Current Python integer bit masks use storage proportional to highest set bit, not to cardinality. On a 100,000-symbol singleton partition, storing one Python integer per symbol consumes approximately \(\sum_{i=1}^n i/8 \approx625\) MB of bit payload even before object overhead (CPython 30-bit digits stored in 4 bytes: about 667 MB for one such collection). Multiple copies and complement regions rapidly exhaust memory. `staged` builds dense singleton mask roots and contractions. Repeated `image` calls scan traces for each block, and full per-block per-negative output has potential \(\Theta(kq)\) entries. Big-integer operations are not unit cost.
4. Strict cost layers are excellent for certification but can be a poor query order. When the lower bound is loose, a coarse diagnostic or a quick incumbent can be valuable. A successful diagnostic alone is not sufficient to close earlier layers.
5. A coarse projection NO excludes refinements, not all descendants in a merge-up tree. Branch omission must retain coverage of every compatible extension; unrestricted canonical order and witness-directed branching cannot be combined without a fresh proof.
6. A budgeted candidate proposal is not a completeness mechanism. Capped pools, approximate features, heuristic hit probabilities, and sampling error must never cause irreversible search deletion.

### 2.4 Supplied benchmark evidence (historical, not new CDAQ measurements)

Both independent benchmark ZIP archives were extracted into the same working directory. The scale ZIP was extracted separately. The combined `ALL_MEASUREMENTS.csv` has 41 run records (including repeated cases under different resource budgets); 19 OPTIMAL, 14 INCOMPLETE, 8 MEMORY_LIMIT. Only 17 runs recorded VERIFIED; two OPTIMAL runs had INCOMPLETE verifier results. Reference/planted files are evaluation-only and must never enter policy input. No planted labels were used to score candidate partitions in this research.

| Historical case | Observed solver result | Implication |
|---|---|---|
| 1,000 symbols, 10,000 distinct traces, sparse reversal fixture | New scale archive: one mandatory-root query; OPTIMAL 14 blocks, cost 986; 0.109 s producer and 0.319 s verifier in default run. Earlier trial INCOMPLETE at 30 s, mostly pair scan. | Strong raw evidence may make ranking unnecessary; charge raw analysis and verification. |
| `medium_reverse_pairs` (1,000 symbols, 2,000 traces) | OPTIMAL 1.874 s; VERIFIED 0.984 s (5 s group). | Teacher time can dominate even with few proposals. |
| `large_reverse_dense` (10,000 symbols, 20,000 traces) | OPTIMAL 0.612 s, verifier INCOMPLETE 6.658 s (5 s group); 30 s group still verifier INCOMPLETE. | Solver success is not verified certification; replay scalability matters. |
| `large_reverse_pairs` (10,000 symbols, 20,000 traces) | INCOMPLETE at both 5 and 30 s, principally oracle partition stage. | Fewer calls do not eliminate a single expensive call. |
| `medium_choice`, `medium_long` (1,000 symbols, 2,000 traces) | INCOMPLETE at 5 s, mostly pair/triple scan. | Budget raw proposal generation. |
| `huge_reverse_unused`, `huge_long_active` (100,000 symbols, 20,000 traces) | MEMORY_LIMIT at 1,536 MiB in both 5 and 30 s groups. | Representation change is prerequisite. |
| `huge_reverse_unused` at 3,072 MiB | INCOMPLETE ~10.145 s; RSS ~2,304 MiB, oracle partition dominates. | Merely raising memory is not enough. |
| `huge_sparse_small` (100,000 declared, 2 active, 20 traces) | MEMORY_LIMIT at 1,536 MiB, INCOMPLETE at 3,072 MiB. | Never allocate one full-width mask per unused symbol. |

Scale timings are historical single runs, not controlled speedups or measurements of this policy. The pinned `RESEARCH_STATUS.md` also reports HDFS-1024 and holdout cost 2, eight-vertex path cost 4, and the old stress failure. The new scale report documents 2,529 exhaustive sample checks and verified certificates. These establish a baseline, not the performance of CDAQ. No end-to-end external run was available for this assignment.

---

## 3. Information state and exact proof responsibilities

At decision time \(t\), define the observable state
\[
I_t=(D,\mathcal P,\mathsf{mode},E_t,F_t,H_t,U_t,L_t,A_t,M_t,\mathsf{budget}_t).
\]
- \(E_t\): independently checkable evidence ledger: same-negative zero regions \(Z_i\), separating sets \(O_i\), named raw equality and discrepancy witnesses, mandatory contractions, exact NOs, accepted artifact IDs, and bound certificates. Retain original IDs, even if raw calculations share duplicate words.
- \(F_t\): exact engine's residual tasks/coverage records; a task can represent a node, a branch, a cost layer, or an unexpanded generator cursor. It has an admissible minimum completion cost and stable identity.
- \(H_t\): query attempts, responses and completeness status, latency, wire sizes, local computation and evidence provenance. Record timeouts.
- \(U_t=c(P_t^*)\): best verified incumbent, \(+\infty\) if none. Track external and mathematical incumbents separately if required.
- \(L_t\): certified lower bound on optimum (including all active tasks and incumbent as appropriate), not a prediction.
- \(A_t\): anchor, the exact engine's next required operation; may be local generation, proof, or a complete partition.
- \(M_t\): scoring state (feature summaries, outcome/cost model, sampled workload, random seed, revision).
- budgets: CPU steps/time, bytes, attempts, mandatory anchor cadence.

Let \(C_t\) denote the *conceptual* set of admissible complete partitions not yet certified infeasible, whose cost is strictly below \(U_t\), and still covered by the exact search. If \(U_t=\infty\), all unresolved candidates are relevant. This is a set used in definitions, not a materialized Bell-size collection. With a verified incumbent and proof that \(C_t=\varnothing\), the optimum is certified. Without an incumbent, exhausted admissible space proves infeasibility. A nonempty unresolved frontier after a timeout is not such a proof.

Do not equate three separate objects:
1. potential solution partitions in \(C_t\);
2. hypothesis models about unknown outcomes (version space over partially computed facts, not partitions themselves);
3. scheduled search tasks that might yield many candidates.

A dead current node can still have compatible coarsenings. Closing its candidate status does not necessarily close its task. A task closes only when its whole represented region is certified non-improving/infeasible or a proved replacement set covers its feasible completions.

### Common measure

For a bounded working sample \(S_t\subseteq C_t\) choose fixed nonnegative weights \(w_t(R)\) before scoring any query, and define
\[
\mu_t(A)=\sum_{R\in S_t\cap A}w_t(R),\quad W_t=\mu_t(C_t).
\]
Use a common sample and weights for all candidates in a round. Unit weights measure sampled candidate count. For avoided-call utility, use weights estimating probability of actually being externally evaluated by the anchor policy times one call (or times predicted evaluation seconds for runtime objective). Normalize when comparing scores across rounds. This estimate is not a certified number of saved calls. Lower-bound strata receive more weight only as a ranking choice, e.g. \(w=\widehat{\text{reach}}/(1+c-L_t)\). If no model, default unit weights within a fixed cost-stratified sample.

A frontier task may represent a large family. Do not credit its full weight for rejecting one representative. To claim a whole-task elimination, require a certificate applying to all its completions (e.g. lower bound cutoff or family containment). Use sampled representative candidates otherwise; track task metrics separately. Overlapping branch representations must not be summed as distinct partitions without deduplication or a documented multiplicity convention.

---

## 4. Proven outcome-conditional progress

### 4.1 Structural zero-region theorem (established)

For unrestricted structural evidence define
\[
\mathsf{Dead}(E)=\{R:\exists i\ \forall B\in R\ \exists Z\in Z_i,\ B\subseteq Z\}.
\]
If \(B\subseteq Z\) and a positive matches \(y_i\) on \(Z\), it also matches on \(B\). Thus every block of \(R\) fails to reject the same \(y_i\), proving incompatibility, with or without bounds. Distinct blocks may use different positives; distinct negatives may not be mixed. The complement of a certified zero region is a necessary hitting obligation for any separating block for that negative. The same-negative closure combines old and new regions and may be strictly larger than a union of individual NO cones. Only evidence modules, not scores, assert these facts.

### 4.2 The certificate-progress score (new operational formulation)

For a complete candidate \(Q\in\mathcal P\), define sets of relevant candidates removable by a specific outcome:

\[
A_t(Q)=\{R\in C_t:c(R)\ge c(Q)\},\quad
N_t(Q)=\{R\in C_t:R\preceq Q\}.
\]
In the first set, a verified ACCEPT can make \(U'=\min(U_t,c(Q))\). If \(c(Q)\ge U_t\), the set is empty. In the second set, a structural NO removes all refinements. Both definitions apply regardless of whether Q belongs to the sample.

**Theorem 1 (conditional progress floor).** If Q returns a complete structural NO, the residual candidate mass decreases by at least \(\mu_t(N_t(Q))\). If Q returns verified ACCEPT, the residual mass decreases by at least \(\mu_t(A_t(Q))\). Consequently for a conclusive unrestricted response, a certified outcome-independent lower bound on *sampled residual mass removed* is
\[
g_t(Q)=\min\{\mu_t(A_t(Q)),\mu_t(N_t(Q))\}.
\]

**Proof.** For NO use projection composition and the named failing negative on every block of Q. A refinement inherits one matching positive per block, hence is impossible. For ACCEPT Q is a feasible upper bound, so no R of cost at least c(Q) can strictly improve it. Both sets are intersected with the pre-query relevant sample and fixed weights. The actual applicable outcome removes its respective set; the minimum is valid before knowing which outcome occurs. No probabilities or future-table prediction are needed. ∎

This is a conditional guarantee on a fixed sample, not a lower bound on unseen candidate count, saved calls, or branch closure. At cost zero, an ACCEPT removes all residual candidates; the NO cone may contain only Q. At very high cost the reverse asymmetry occurs. A diagnostic at or above the incumbent can still produce useful NO evidence, but its ACCEPT cutoff credit is zero. If the response may time out, worst-case unconditional progress is zero. In bounded mode replace \(N_t(Q)\) with \(\{Q\}\cap C_t\) for generic NO, unless projection failure is independently certified for the particular response. A complete ACCEPT cutoff remains valid.

**Theorem 2 (history-amplified conditional NO floor).** Let \(J_t(Q)\) be a certified superset of the possible failing negatives if Q returns a structural NO. Initialize \(J_t(Q)=\{1,\ldots,q\}\). A negative can be omitted only if a certified separating subset lies in a block of Q (or an independent proof excludes it as a structural failure). For each \(i\in J_t(Q)\), hypothetically add all blocks of Q to \(Z_i\), leaving the other evidence unchanged. Let
\[
N_{t,i}(Q)=C_t\cap \mathsf{Dead}(E_t+\{(i,B):B\in Q\}).
\]
Then conditional on a structural NO, the mass removed is at least
\[
b_N(Q)=\min_{i\in J_t(Q)}\mu_t(N_{t,i}(Q))\ \ge\ \mu_t(N_t(Q)).
\]
If a particular failing negative is already proved, the minimum can use just that negative. If no possible failing negative remains, structural NO is impossible under the model; do not take a minimum over an empty set.

**Proof.** The response identifies some \(i^*\in J_t(Q)\) and certifies matches on all Q blocks for that negative. The actual ledger is at least as strong as the hypothetical ledger for \(i^*\); monotonicity of the same-negative closure proves the first inequality. Each refinement of Q belongs to every hypothetical exclusion set, proving the second. ∎

No speculative zero is inserted in \(E_t\). The update is a read-only simulation. Other columns may add extra actual value; ignoring them yields a lower bound. If evaluating all possible negatives is too expensive, use the refinement-only floor or calculate a lower bound over a **superset** of outcomes: take the minimum of evaluated branches and a generic refinement floor for all omitted branches. Taking a minimum only over likely negatives is not robust.

A useful refinement of this theorem is **conditional proof-work overlap**. For R not already dead, let \(D_i(R)\) be its blocks not covered by existing \(Z_i\). The simulated failing-i update excludes R exactly when
\[
\forall B\in D_i(R): B\text{ is contained in some block of }Q .
\]
This follows by separating old coverage from new containment. It requires no new raw projections and admits sparse implementation (§8). It extends a pure cone score to cross-table evidence at incremental cost.

### 4.3 Conditional query-complexity result

**Theorem 3 (balanced certified progress, conditional).** Suppose a finite explicitly defined candidate universe \(C\) with fixed unit weights is available conceptually, and the certificate engine removes candidates monotonically. Suppose at every nonterminal state there exists an admissible query with certified outcome-conditional elimination of at least \(\gamma|C_t|\) for *every* possible complete outcome, for a constant \(0<\gamma<1\), and the algorithm always selects such a query. If evaluations always finish and the engine recognizes all certified removals, then after at most
\[
\left\lfloor \frac{\ln |C_0|}{-\ln(1-\gamma)}\right\rfloor+1
\]
queries the residual candidate universe is empty (possibly earlier by optimality/infeasibility). For \(\gamma=1\) one conclusive query suffices. With positive arbitrary weights, replace the numerator by \(\ln(W_0/w_{\min})\) where \(w_{\min}>0\) is the minimum fixed candidate weight.

**Proof.** \(W_{t+1}\le(1-\gamma)W_t\), so induction gives \(W_t\le(1-\gamma)^t W_0\). Once this is less than one (or \(w_{\min}\)), no candidate can remain. ∎

The assumptions are strong. We have no universal balanced-query theorem for partition compatibility; the sampled score does not prove a global split. The theorem also counts queries only, not local proof search. If timeouts are bounded by a known number of retries per conclusive query, multiply accordingly; otherwise no finite attempt guarantee follows.

A weak unconditional conclusive-call bound for an exact finite search with no repeated conclusive queries is \(|\mathcal P|\le \operatorname{Bell}(n)\). If structural-only valid local analysis completes the problem, fewer or zero calls may be needed. A policy may need no queries at all on a root certified by raw evidence; with a mandatory external final witness, one final confirmation is necessary by protocol, not by an information lower bound.

**Abstract worst-case warning.** On the partition lattice, all partitions of a fixed cost k form an antichain. For a verdict-only monotone oracle consider a family accepting every partition of cost >k and rejecting all cost <k, with arbitrary ACCEPT/NO at cost k. Such monotone Boolean functions are valid on the lattice as order-theoretic objects. To distinguish the all-NO cost-k layer from a variant with one ACCEPT, an adversary can force testing all members of that layer if no other evidence exists. This is a lower bound for abstract monotone membership access only; it is not a claim that every such function is realizable by a corpus with full rejection tables, nor a lower bound on the actual raw-input problem. It refutes the inference “monotonicity alone implies logarithmic search.”

### 4.4 A structured diagnostic example with a real logarithmic bound

In a deliberately restricted evidence model, suppose it is known that a single positive-negative pair has exactly one discrepancy atom, an unknown two-symbol set \(\{a,b\}\), and no unary atoms. Then a complete query consisting of a test block T and singleton leftovers returns ACCEPT iff both endpoints lie in T (for |T|<2 the partition is the singleton and NO). Such a promise is realizable by a word and a single adjacent swap. Under this promise, one can locate the pair without testing all \(\binom n2\) pairs:

1. Split current possible endpoint set S into balanced halves A,B. Query the complete partition with A as a block. If ACCEPT, recurse in A. Otherwise query B. If ACCEPT, recurse in B. If both NO, the endpoints lie on opposite sides.
2. Once opposite sides are known, binary-search the endpoint in A using test block \(A'\cup B\), where \(A'\) is half of remaining A. ACCEPT means the A endpoint is inside A'; NO means it is outside. Then binary-search B similarly with the identified A endpoint included.
3. Submit the resulting pair block with singleton leftovers if its ACCEPT has not already been externally observed. The promise or an explicit singleton NO proves cost zero impossible.

At most \(2\lceil\log_2 n\rceil+1\) location and final pair calls suffice: if t same-half levels precede the split, at most 2t+2 tests are paid, then at most \(2(\lceil\log_2 n\rceil-t-1)\) endpoint tests; base case two symbols needs at most one final confirmation. An optional explicit singleton query adds one. This is a conditional example, not a default heuristic to infer a unique hidden pair. In raw-data unrestricted mode, the atom may be computed directly more cheaply; the point is the shape of informative **complete partition** queries and not a claim about hidden ground truth. With multiple atoms or negatives, both-NO need not imply exactly one endpoint per half.

---

## 5. Alternative policies, expected value and robust choice

### 5.1 Decision-tree interpretation

A version space \(\mathcal H_t\) can be defined over possible assignments of not-yet-computed projection facts, consistent with the partial evidence. A predictive distribution is a computational approximation, not uncertainty about the literal input D. For a query Q and discrete outcome O with possible full response patterns, the exact ideal Bayesian policy minimizes expected remaining query cost via
\[
V(I)=\min_Q\big\{\mathbb E[\kappa(Q,O)]+\mathbb E[V(I\oplus O)]\big\}
\]
with V=0 at a certified terminal state, assuming well-defined prior, transitions and eventual termination; add local-analysis actions if comparing proof production with external calls. A minimax variant replaces the second expectation with the worst allowed response, with explicit retry limits. Computing V requires knowing or modeling responses and future search states; it is generally intractable. This is a conceptual target, not an implemented recursion.

For finite equally weighted hypotheses and deterministic outcome classes of sizes \(h_o\), expected version-space elimination is \(h-\sum_o h_o^2/h\). Entropy gain is \(H(O)\) for deterministic O, or \(I(H;O)=H(O)-H(O\mid H)\) for stochastic feedback. Under an explicit posterior, use probabilities of classes, not candidate partition counts. A binary ACCEPT probability near 1/2 maximizes binary entropy, but might leave all cheaper candidates unresolved. Conversely a predictable NO can produce a large compact certificate. Full table entropy could be dominated by irrelevant columns or witness-ID choices. Treat ACCEPT/NO/timeout entropy as a baseline only; do not confuse it with information about the optimal partition. A useful target-specific entropy would concern possible optimum cost and certified decision classes, not all local tables.

### 5.2 Outcome-specific utility without double counting

For each Q, compute \(a=\mu_t(A_t(Q))/W_t\), \(b=\mu_t(N_t(Q))/W_t\) (or \(b_N/W_t\)). If \(W_t=0\) because the sample is empty, scores become unavailable and the anchor runs. The exact search, not this condition, decides termination.

For a complete response o, let \(K_t(Q,o)\subseteq C_t\) be the candidates provably removed by the ledger update, including incumbent cutoffs. Let \(a_t(o)=\mu_t(K_t(Q,o))/W_t\). For a timeout/incomplete response define \(K=\varnothing\) by default. Define an additional optimization utility
\[
d_A(Q)=\begin{cases}
1 & U_t=\infty,\\
\max(0,U_t-c(Q))/\max(1,U_t-L_t)& U_t<\infty,\ U_t>L_t,\\
0 & \text{otherwise}.
\end{cases}
\]
This is dimensionless incumbent-gap progress, not an extra number of candidates eliminated. If \(c(Q)<L_t\) despite the bound and Q is reported ACCEPT, quarantine inconsistent evidence/response rather than accepting an impossible score. If \(L_t=U_t\), no further search query is needed except required external confirmation.

Let \(\widehat p_C\) be the probability of conclusive completion and \(\widehat p_A\) the conditional ACCEPT probability. With possible failure indices i, let \(\widehat p_i\) be the conditional distribution over i given structural NO. In the recommended default, use only guaranteed conditional eliminations (possibly history-amplified), not guesses of unreturned table cells:
\[
\widehat e=\widehat p_C\left[\widehat p_A a+(1-\widehat p_A)
     \sum_i\widehat p_i\,\mu_t(N_{t,i}(Q))/W_t\right].
\]
For a generic NO regime replace the conditional NO term by its exact-partition credit or a separately modeled structural-failure probability. Missing tail mass uses the generic refinement floor in unrestricted mode, not zero-region simulation of unselected negatives. An optional upper forecast can sample hypothetical extra zero columns or bound improvements; explicitly report it as heuristic, clipped to [0,1], count the union of removals once, and never write guessed table cells into evidence.

With no reliable prior, use an ambiguity interval \(\widehat p_A\in[\ell,h]\) and completion interval \([c_\ell,c_h]\). Given normalized conditional utilities \(v_A=a+\lambda d_A\), \(v_N=b_N/W_t\),
\[
v_{\rm robust}=c_\ell\min\{\ell v_A+(1-\ell)v_N,\ h v_A+(1-h)v_N\}.
\]
This follows because the objective is affine in p and nonnegative; minima occur at interval endpoints. For \([0,1]\) and conditional completion, it reduces to \(\min(v_A,v_N)\). For unconditional unknown completion, \(c_\ell=0\) makes it zero. Use a timeout fallback instead of pretending otherwise. These are robust scores over an explicitly specified ambiguity set, not statistical confidence bounds without calibration.

Recommended hybrid ranking:
\[
\text{score}(Q)=
\frac{(1-\eta)\,v_{\rm robust}+\eta\,(\widehat e+
                 \lambda\widehat p_C\widehat p_A d_A)}
     {\max(\epsilon,\widehat\kappa(Q))}.
\]
Here \(\lambda,\eta\ge0,\eta\le1\) tune optimization vs exploration; \(\widehat\kappa=1\) for pure query count, or estimated end-to-end evaluation time (include serialization/response parse) for time-sensitive scheduling. Ranking overhead is budgeted separately. Default prototype uses \(\lambda=0.15,\eta=0.25\) after calibration, \(\eta=0\) when unavailable, and completion-conditional robust scores for ordering when timeout probabilities are completely unknown. These numerical defaults are proposed engineering choices, not proven optimal. A stricter certificate-first alternative ranks lexicographically by (robust mass, expected mass, gap progress, negative cost, stable ID). Include Pareto dominance on these dimensions as an optional **ranking** filter, not a prune of the search space.

### 5.3 Baselines and when they are appropriate

| Policy | Score / selection | Limitation |
|---|---|---|
| Random | seeded uniform over the same pool | Useful control; not uniform over the full lattice unless sampled correctly. |
| Cost-ordered / best-first | cheapest unresolved exact candidate, ties stable | Predictable certificate order; can miss coarse diagnostic gains. |
| Greedy witness/repair | predicted negative coverage per added merge | Good incumbent finder; partial witness hits not feasibility. |
| Current implementation | `choose_region`, `repair`, optional `diagnostic` gain / packed groups | Immediate-child proxy, default diagnostics off; expensive pair enumeration. |
| Expected elimination | \(\widehat e/\widehat\kappa\) | Sensitive to outcome and reach model calibration. |
| Worst-case elimination | \(\min(a,b_N/W_t)/\widehat\kappa\) | Conservative; zero for some useful high-cost probes, zero unconditional under arbitrary timeouts. |
| Entropy | binary verdict entropy or explicit hypothesis information gain | Can optimize irrelevant uncertainty. |
| Expected improvement | \(\widehat p_C\widehat p_A d_A/\widehat\kappa\) | Can find ACCEPT early without certifying optimum. |
| CDAQ | guarded robust+expected certificate mass plus bounded incumbent bonus | Depends on frontier sample quality; guarantees correctness through exact engine, not universal speedup. |

### 5.4 Why generic active-learning approximation guarantees do not transfer

Generalized binary search [4] proves logarithmic queries under specific query/hypothesis geometry, not for arbitrary restricted partitions. Bayesian experimental design [5] optimizes expected information or decision utility under an explicit model. Interactive submodular set cover [6], adaptive submodularity [7], and cost-sensitive equivalence-class determination [8] provide greedy guarantees under formal objective/distribution conditions. Those conditions must be proved for the certificate-progress objective before importing any competitive factor.

Counterexample to diminishing returns for our closure utility (new application of earlier cross-table example). Let positives be \(a,b,c,d\) as four single-letter words and negative \(\epsilon\). Target residual sample contains just \(ab|cd\); all proper subsets are dead for the negative, but ledger initially knows only singleton deadness. Query \(Q_1=ab|c|d\) and \(Q_2=a|b|cd\). Each structural NO alone leaves target unresolved by containment. After Q1, Q2 removes it. The marginal coverage of Q2 increases from zero to one as evidence grows. Even deterministic set coverage with this closure is not generally submodular; under a degenerate realization, adaptive diminishing returns also fails for this ledger-based target. This does not disprove all possible submodular surrogate objectives. A fixed union of independent direct refinement cones is a submodular coverage function, but misses cross-history synergy and ACCEPT-dependent cutoff. Greedy maximum coverage could be justified only for that restricted nonadaptive, fixed-outcome surrogate, not for general CDAQ.

---

## 6. Outcome estimation and incremental learning (heuristic only)

Use only public observable features:
- candidate cost, block count and size distribution, nontrivial support, distance in merges from anchor and incumbent;
- known separating-negative coverage; number of negatives with all blocks currently certified dead; number of uncovered necessary witness families and lower-bound slack;
- overlap with previous queried blocks; marginal sample refinement/closure score; projected cost strata eliminated by ACCEPT;
- raw length/count/order summaries, sparse mismatch witnesses, occurrence supports computed under a fixed local budget;
- actual completed outcome history, wall time, response bytes, timeout rate for comparable candidate shapes.

Do not use planted partition, reference cost, hidden solver caches, actual future table, or internal automata states. Reuse observable returned blocks/evidence only. If an external protocol provides a base-table reference, its observed cache/reuse effect may be measured, not assumed.

Cold start: robust score, unit weights, anchor and a few structurally diverse probes. After enough completed attempts, use a simple regularized model (or bins by cost slack and known witness coverage), e.g. beta-smoothed acceptance \((a+1)/(a+n+2)\) within a bin, using completed NO count n and ACCEPT count a. A separate completion model uses every attempt; timeouts are censored evaluations and not negative labels. Keep case-level validation splits. Failure-negative estimates may use observed distribution of named failures and unresolved witness loads; restrict to logically possible indices, include an OTHER mass for unmodeled negatives. A named failure can be chosen adversarially among several valid failures; default to robust or use broad intervals rather than relying on historical first-index selection.

Prefer a light feature model to training a complex neural predictor. Log feature and probability snapshots before the response, calculate Brier score and log loss on later completed outcomes, and evaluate calibration and prediction drift by instance family and size. Use Beta intervals as model-based credible intervals only under the corresponding exchangeability assumptions; adaptively selected observations are not iid by default. If calibration worsens or no independent calibration data are available, set \(\eta=0\) and/or revert to anchor. For query time, use observed binned median or conservative upper quantile, treating timeouts as right-censored rather than fast NOs. For count minimization set \(\widehat\kappa=1\); only latency tie-break if desired.

Do not fit a model by peeking at held-out benchmark reference partitions. Offline labels for calibration may be generated by querying candidates with the same external response protocol, charged as training expense. Separate training traces/seeds from test traces/seeds.

---

## 7. Candidate construction and safe adaptive scheduling

### 7.1 Bounded candidate pool

Do not enumerate Bell(n), all pairs, or all minimal separators for a score. Let M be a maximum number of proposals (start 16, scale to 32 only when cheap). Generate in deterministic bounded fashion:

- **Anchor:** next complete candidate from the exact engine. Always preserve a reference, even if score computation is interrupted.
- **Frontier alternatives:** up to a fixed number of cheapest pending candidates or generator outputs, sampled by lower-bound/cost stratum; do not exhaust a layer just to score.
- **Incumbent-oriented:** witness-based repair of the anchor or a proved lower-bound solution from another module, fill leftovers with singleton or mandatory atoms. Include low-cost improvements of the incumbent only when admissible and not already proven impossible.
- **Diagnostic packing:** take a bounded set of sampled promising blocks from cheap witnesses and live candidates. Greedily pack disjoint block unions (quotient atoms as units), with different stable orders or target negatives. Fill all remaining symbols by unchanged root atoms/singletons. Avoid unbounded pair scans: sample partners from sparse witness indexes; reject overlaps by hashed ID/member sets or DSU.
- **Cross-frontier probes:** union several nontrivial blocks from sampled candidates when disjoint, or join their equivalence relations under a merge-cost cap. These queries contain candidate refinements by construction; this can produce useful NO coverage.
- **Targeted subset/cut probes:** when the evidence suggests one localized obligation, try a few complete two-block or one-block-plus-rest candidates as in §4.4. Large blocks may be expensive; include only under a wire/runtime budget.

A diagnostic can deliberately have cost above the incumbent if predicted NO certificate value is substantial, but ACCEPT then yields no improvement. Default restrict diagnostics to cost at most U (when finite), unless a separate `allow_above_incumbent_probe` budget explicitly buys feedback. A known structural NO can still be queried for extra non-failing columns if there is a justified acquisition goal; default skip it because its guaranteed new certificate value is often zero. A known mathematical ACCEPT can be queried for required external confirmation. Deduplicate complete partitions by stable canonical IDs and structural equality; a hash collision is not a proof of equality. Never submit a partial partition.

All proposed Q must respect \(\mathcal P\), mandatory contractions, declared alphabet and mode. Exact-engine intermediate nodes need not themselves be eligible external queries in a restricted family. Keep the generator cursor when a pool cap is reached. Removing a proposal from a temporary pool is not removing it from the exact search.

### 7.2 Protected-anchor scheduler

At each round, exact engine supplies an anchor task A (possibly a local operation) and a snapshot. If A is resolved by evidence, advance without a query. Otherwise allow at most B optional diagnostic/incumbent probes while this anchor is pending (prototype B=2). On each complete response update evidence, invalidate relevant score caches, recompute bounds and revalidate A. If A is discharged by a valid certificate, count it as resolved and obtain another anchor. Otherwise, after B optional probes or the scoring budget, execute A; it cannot be deferred forever by a higher-scoring candidate. If A's external attempt is incomplete, keep A unresolved in a retry queue and continue fair scheduling of other tasks. Retry according to a documented policy (e.g. exponential timeout budget with a maximum global deadline), not an implicit NO. If no remaining evaluable tasks or resources, return INCOMPLETE with the best verified incumbent, lower bound, unresolved tasks and attempt history.

This is a modular schedule, not an instruction to discard a dead node in the existing merge-up tree. The anchor includes whatever continuation-generation record that engine needs. In particular, an optional NO at Q cannot by itself mark all coarsenings of Q closed.

**Theorem 4 (safety, optimality and completeness under fair exact scheduling).** Assume:
1. exact engine's initial tasks cover every admissible feasible partition, and task expansion preserves that coverage;
2. only independently verified incompatibility, admissible-bound cutoffs with verified incumbents, or path-preserving branch proofs remove tasks/candidates;
3. the engine has a finite exhaustive progress schedule (or other proved finite termination measure); each compulsory anchor eventually completes or is resolved by valid evidence;
4. optional probes per unresolved anchor are bounded, and each selection computation terminates.

Then changing the score, proposal distribution, probabilities, or ranking weights cannot invalidate a certified result. With unlimited resources and eventual conclusive evaluations (or a valid local proof fallback), the guarded schedule terminates with an optimal incumbent or a valid infeasibility certificate.

**Proof.** Initially every potential feasible improving partition is covered. Verified ACCEPT may lower U and discard only non-improving completions. Verified NO/structural deductions remove only impossible candidates; branch replacement preserves every feasible target covered by the old task. Hence the coverage invariant holds after each update, independently of the score. When all residual tasks are proved closed, no feasible partition has cost smaller than U; if no incumbent exists, there is no feasible partition in the covered family. For termination, each anchor can be preceded by at most B optional probes and finite scoring work; assumptions 3–4 give finite completion of the underlying progress schedule. Revalidation may close anchors earlier, never re-open a proved impossible region under fixed D/mode. Persistent incompleteness violates assumption 3 and yields INCOMPLETE, not a theorem of success. ∎

If r anchors are resolved or executed, there are at most Br optional submissions plus one final handoff and explicitly counted retries; the number of anchors is the realized schedule count, not a bound relative to the original implementation's run. No constant-factor performance claim follows, since the underlying frontier can change. Maintain a global optional-attempt budget too. In unrestricted finite exact search, a direct projection proof can replace a perpetually timing-out compatibility call if allowed, but cannot fabricate external DFA artifacts.

---

## 8. Scalability and data structures

### 8.1 Representations

For large n use stable dense integer symbol IDs plus an original-label dictionary; store raw words as flat `uint32` symbols and `uint64` offsets, preserving trace IDs and repeats. Maintain quotient DSU with `uint32` parent/size and stable canonical component IDs. On disk serialize the original full partition; inside the selector represent a partition as immutable nontrivial merge blocks relative to the shared root, plus implicit untouched root atoms. For large/coarse candidates store a dense label vector or sorted member arrays, not one arbitrary-width integer per singleton. Never omit unused symbols from a transmitted complete proposal; materialize them exactly once at the boundary.

Use sorted small arrays for sparse blocks, complement representation for deletion witnesses of small size, and optionally compressed bitmaps for genuinely dense sets. Canonical equality and hashing must compare semantic block membership, not DSU path-compression state. Keep stable original IDs for certificate replay. A compact complement such as \(\Sigma\setminus\{a\}\) should store `{a}` plus polarity, not a full mask for every witness. If a new representation cannot be replayed by existing `verify.py`, supply a translation for small legacy cases and a new independently implemented verifier for large cases; do not claim legacy verifier scalability.

Evidence store:
- maximal zero regions per original negative, minimal separating subsets, deduplicated shared block definitions with reference IDs;
- inverted index of witness support/region membership, per-block cached verified coverage and proof IDs;
- store identical raw word computations once with a mapping to every original ID;
- score cache keyed by sample digest, regime, candidate identity, evidence revision, incumbent, sample revision and model revision;
- separate persistent exact frontier cursor/task store and append-only response/certificate log.

Region subsumption may be skipped if expensive: retain extra sound facts, or bound the scoring view without deleting proof records required for verification. Evict score features and optional caches, never silently erase certified coverage needed for completeness. Disk-backed proof storage is acceptable. Compress repeated table structure by shared references only where the actual external interface supports it. The paper allows by-reference compact descriptions; it does not promise a sublinear response protocol.

### 8.2 Efficient scores on a bounded sample

Let K=|S|, M=number of proposals, r=number of simulated failure indices per proposal, h=maximum total number of active nonsingleton blocks/atoms per sampled partition above common root, k_0=number of root atoms. Let \(\ell_R\) be the number of blocks of R in its explicit representation and \(d_R\) the total members of its changed root blocks. For any Q:
- ACCEPT score: sort sample by cost and precompute suffix weighted sums, \(O(K\log K)\) setup, \(O(\log K)\) per Q (or precomputed histogram lookup).
- Refinement score: dense fallback label map Q on root atoms, test that all atoms of each R block share one Q label. Untouched root atoms in R are already contained by any valid Q, so only changed blocks require scans. With sparse overrides and shared root, cost \(O(d_Q+\sum_{R\in S} d_R)\) expected hash operations per proposal, or \(O(k_0+\sum_R d_R)\) with dense labels. For arbitrary nonshared representations use \(O(k_0K)\) per proposal. Construct a bitset of sample hits; weighted sum uses the set bits or a scan.
- History-amplified NO score: maintain for a bounded set of indices i a cached set \(D_i(R)\) of R blocks not already covered. Compute the bitset \(N_{t,i}\) by checking Q containment only for missing blocks. Untouched root atoms always fit some Q block; hence they need not be individually rechecked in this hypothetical update. If R already dead, it should not be sampled. Cache uses verified existing region facts; incomplete cache entries use a conservative missing-block overapproximation, never an optimistic underapproximation. Simulate only a small r (e.g. 4) and use cone floor for all omitted outcomes. If all possible failing indices were not exhausted, the robust minimum cannot exceed the fallback floor unless a separate proof bounds omitted scenarios.
- Expected bonus: weighted average of these conditional scores; no extra table generation required. Optional heuristic table forecasts use only sampled negatives/blocks and are never a proof.

**Lemma (sparse containment).** If Q and R coarsen the same mandatory root, every unchanged root atom in R is contained in Q automatically. Therefore \(R\preceq Q\) iff every explicitly merged block of R has all its root atoms assigned to one Q block. Proof: those two types exhaust R's blocks. The same argument applies to the missing-block test in Theorem 2. Thus for near-root partitions, a score need not scan all n labels or every block.

Full dense worst-case round work is \(O(MKk_0(1+r)+K\log K)\), excluding evidence cache initialization and proposal generation. Sparse expected work is \(O(M(d_Q^{\max}+(1+r)\sum_R d_R + K(1+r))+K\log K)\) with precomputed missing-block summaries, bounded hash maps, and O(1) root-label lookup. The cost of constructing/updating the summaries must be charged: in the absence of indexes, checking a block against a negative's zero-region list is proportional to the list size times containment cost; do not hide this under O(1). When caches miss heavily, skip history amplification and score with cones. A practical implementation should avoid Python object per sample per symbol.

Working memory for bounded sparse proposals and samples is \(O(\sum_Q d_Q+(1+r)\sum_R d_R+K r+M K/w+n)\) words for small membership sets, hit bitsets and shared root (w machine word width); dense partition vectors add \(O((M+K)n)\) if all materialized, avoid by streaming one at a time. Evidence/proof storage and exact frontier are additional and can be exponential. For example with M=16, K=128, n=100,000, a naive dense comparison would involve 204.8 million atom visits for just one cone round. With typical d_R=20, it needs roughly 40,960 changed-atom visits plus Q setup. This is a workload illustration, not a benchmark; coarse Q or huge changed supports destroy that advantage. Dense `uint32` label vectors cost 0.4 MB each; root DSU arrays around 0.8 MB for parent and size, versus hundreds of MB for full-width singleton masks.

### 8.3 Sampling and uncertainty

Preferred first implementation: fixed-size reservoir over an existing bounded frontier cursor, plus explicit cheapest layer samples and incumbent-near samples. Record selection distribution. A uniform sample of currently materialized tasks is not uniform over all partitions or over future paid evaluations. Scores estimate only the declared sampling measure. For disjoint strata with known masses use stratified weights. When sampling with replacement from a declared target distribution independently of candidate generation, the mean of a fixed [0,1] coverage indicator is unbiased; Hoeffding plus union bound gives for M fixed proposals
\[
\Pr(\max_Q|\widehat a(Q)-a(Q)|>\varepsilon)
  \le 2M e^{-2K\varepsilon^2}.
\]
For the two outcomes separately union-bound 2M tests; for r scenarios use M(1+r) tests. If the same sample is used to generate and select adaptive proposals, this fixed-class bound need not hold; split a proposal-generation sample from an independent scoring/validation sample, or treat uncertainty empirically. No such interval is a correctness certificate. Importance weights require bounded weights or a different concentration analysis.

Do not count all partitions by Bell numbers for ranking. As a small-scale analytic diagnostic, cost-stratified refinement counts can be computed from
\[
F_Q(z)=\prod_{B\in Q}\sum_{j=1}^{|B|}
           \left\{\begin{matrix}|B|\\j\end{matrix}\right\} z^{|B|-j}.
\]
Coefficient of \(z^k\) counts refinements of merge cost k; multiply independent choices on Q's blocks. If only a small cost range matters, truncate each polynomial and convolution. On a mandatory quotient use atom counts for *additional* cost and offset root cost. This formula does not subtract prior exclusions or account for restricted admissibility; use it only as an upper/shape feature or for exact small-case checks under its assumptions. Huge block sizes and large k still make the count expensive. Never enumerate all refinements to compute a score.

### 8.4 Wall-time and wire budget

The paper's unrestricted tables can have \(2^f\) explicit rows; never expand them when compact fixed-zero/free-group data is supplied. Even the compact format can require \(\Theta(kq)\) negative entries, potentially one billion for 100,000 blocks and 10,000 negatives (4 GB at one 32-bit integer per entry, before metadata). If the external service emits that much data, the selector cannot unilaterally redesign it. Stream or reference existing returned data where available; otherwise report the wire bottleneck and use query candidates with acceptable estimated footprint. A complete partition submission itself generally costs at least O(n) labels unless protocol supports a shared-base representation. Query selection must be cheaper than the work it saves.

Use a hard per-round token/operation cap and monotonic deadline. Prototype: M=16, K=128, r=4, B=2; cap ranking at min(50 ms, 10% of median recent conclusive evaluation time), and at 2e5 membership operations; these are starting parameters, not scale guarantees. Cold start uses a 5 ms budget and anchor fallback. Time check at bounded intervals inside loops; interrupt safely, keep anchor. A global ranking budget (e.g. 10% of overall time limit) prevents score overhead from consuming the run. Candidate generation, score cache updates and sample refresh all debit the same policy budget. Never call the external system to obtain a scoring feature without counting it as an actual query.

Operationally, if estimated ranking+optional query cost exceeds predicted anchor work saved, choose anchor. For pure query count experiments fix \(\widehat\kappa=1\) and still report time; for runtime objective predict total seconds and require a positive estimated net benefit. Scoring cap guarantees bounded **local ranking overhead**, not an end-to-end runtime bound. Exact generation, evidence extraction, oracle and verification may all remain expensive.

---

## 9. Implementation-ready interfaces and algorithm

### 9.1 Typed Python interfaces

Add a selector-side `query_policy.py` (proposed file, not yet implemented). Use immutable snapshots and explicit ownership. Types below are Python-like pseudocode; actual transport is supplied by the external integration, not this module.

```python
from dataclasses import dataclass
from typing import Literal, Protocol, Sequence

@dataclass(frozen=True)
class Candidate:
    key: str                    # stable canonical identity, collision checked
    partition: "PartitionRef"   # complete semantically; lazy materialization
    cost: int                   # original |Sigma|-|P|
    purpose: Literal["anchor", "frontier", "repair", "diagnostic", "handoff"]
    parent_task: str | None

@dataclass(frozen=True)
class Response:
    attempt_id: str
    candidate_key: str
    sample_digest: str
    regime: Literal["unrestricted", "bounded", "unknown"]
    status: Literal["ACCEPT", "NO_STRUCTURAL", "NO_BOUNDED",
                    "NO_GENERIC", "INCOMPLETE", "INVALID"]
    complete: bool
    negative_ids: tuple[str, ...] | None
    failed_negative: str | None
    failure_witnesses: "WitnessRef | None"
    base_tables: "TableRef | None"
    artifact: "ExternalSolutionRef | None"
    elapsed_s: float
    bytes_in: int
    bytes_out: int
    reason: str | None

@dataclass(frozen=True)
class QueryValue:
    accept_mass: float
    no_cone_mass: float
    no_robust_mass: float
    expected_mass: float | None
    incumbent_gain: float
    completion_estimate: float | None
    robust_score: float
    expected_cost: float
    final_score: float
    sample_revision: int
    evidence_revision: int
    assumptions: tuple[str, ...]

class ExternalAdapter(Protocol):
    def evaluate(self, complete_partition, attempt_id, deadline) -> Response: ...

class QueryPolicy:
    def build_query_candidates(self, search_frontier, evidence) -> Sequence[Candidate]: ...
    def estimate_query_value(self, partition, state) -> QueryValue: ...
    def estimate_query_cost(self, partition) -> float: ...
    def select_next_partition(self, state) -> Candidate | None: ...
    def update_query_policy(self, response: Response) -> None: ...
    def report_query_efficiency(self, history) -> dict: ...
```

`None` from select means execute local anchor, terminal state, or budget fallback as indicated by an explicit state/action enum; it must not mean certified exhaustion by itself. Production can expose a `Selection(action=QUERY|EXECUTE_ANCHOR|STOP_CERTIFIED|STOP_INCOMPLETE, candidate=...)` wrapper. `update_query_policy` updates predictor/cache only from validated events; the evidence engine owns authoritative ledger changes. The scoring module must not have APIs for proof deletion, incumbent mutation, or search cutoff. Use injected read-only `FrontierView`, `EvidenceView`, `Budget`, `Clock`, and `Random(seed)`. Do not pass `ProjectionOracle` objects, planted references or internal state into the policy.

Adapter normalization:
- Match attempt, sample digest, mode, full partition and original negative ordering to the submitted request. If the actual wire protocol lacks these fields, attach them in caller-side request bookkeeping, never invent remote claims.
- For structural NO require valid failing index and per-block witnesses or equivalent certified complete unrestricted table proof. Validate original trace IDs and recompute named projection equalities independently. Parse fixed-zero/free-group tables without row expansion; validate group/column coverage, disjointness, completeness and semantics; recover optional positive IDs using a bounded raw lookup with explicit pending verification. Grouping equality may be checked by raw projections as needed. Any raw verification failure quarantines the response. If only some trusted facts can be verified independently, the response remains incomplete for verdict purposes; default do not ingest partial tables into the proof ledger. A separately verified raw fact may be inserted as raw evidence, not as an inferred NO.
- ACCEPT can have no tables. Verify returned partition and artifact/capacity configuration; evaluate local DFAs against raw traces where artifact allows independent verification. If no artifact is exposed, record what is externally attested and separate trusted oracle certification from independent raw replay. Unrestricted raw feasibility can be independently checked even without DFA internals, but does not fabricate an external artifact.
- Completed bounded FAIL can lack tables. Treat exact partition as NO only. If the response does not provide a replayable bounded certificate, independent verification requires trusting the declared exact evaluator or an independent verifier; flag that limitation. Never treat a timeout as exact failure.
- For local emulator benchmarks implement a wrapper around `ProjectionOracle` that emits paper-shaped NO, strips tables on ACCEPT, and preserves only allowed public fields. Compare richer local protocol separately; not a production interface assumption. All candidate selection sees the normalized response only.

### 9.2 Main scheduling pseudocode

```text
CDAQ_SOLVE(D, admissible, regime, budgets, seed):
    validate D, IDs, alphabet, regime
    E, root, bound_proofs = RAW_ANALYSIS(D, bounded_preprocess_budget)
    exact = EXACT_ENGINE(root, admissible, E, mode=regime)
    incumbent = verified_raw_incumbent_if_permitted(D, E, admissible)
    H = persistent_history(); policy = QueryPolicy(seed)
    A = None; optional_used = 0

    while budgets.allow_progress():
        exact.apply_verified_updates(E, incumbent)
        if exact.certifies_optimality_or_infeasibility(incumbent):
            if external_artifact_required and feasible and not confirmed(incumbent):
                response = submit_complete(incumbent.partition, purpose="handoff")
                count_every_attempt(H, response)
                validate_and_commit(response, E, exact, incumbent)
                if not confirmed(incumbent): return INCOMPLETE_WITH_STATE()
            return verified_result_and_coverage_certificate()

        if A is None or exact.proves_task_resolved(A):
            A = exact.next_fair_anchor()  # includes local generation/proof tasks
            optional_used = 0
        if A is None: return INCOMPLETE_WITH_STATE()  # no proof of exhaustion
        if A.kind == LOCAL:
            exact.execute_local_anchor(A, E, budgets)
            A = None only if completed or safely replaced
            continue

        chosen = A.complete_candidate
        if optional_used < B and budgets.policy_available():
            snapshot = immutable_view(exact, E, incumbent, H)
            pool = build_query_candidates(snapshot.frontier, snapshot.evidence)
            pool = deduplicate_and_validate(pool + [chosen])
            sample = bounded_live_sample(snapshot, seed)
            best = score_with_deadline(pool, sample, snapshot)
            if best is eligible optional and beats_anchor_gate(best, chosen):
                chosen = best; optional_used += 1
        # fall back to A on any score error, exhausted budget or empty sample

        recheck revision, admissibility and complete partition
        if chosen is already conclusively answered:
            use cached validated evidence, no paid query
            if chosen is A:
                exact.complete_anchor_and_preserve_continuations(A, E); A = None
            else: exact.advance_if_resolved(A)
            continue
        if chosen is inferable and external confirmation not required:
            exact.commit_independent_proof(chosen)
            if chosen is A:
                exact.complete_anchor_and_preserve_continuations(A, E); A = None
            else: exact.advance_if_resolved(A)
            continue

        materialize complete original-alphabet partition
        response = submit_complete(chosen, new_attempt_id, evaluation_deadline)
        count_every_attempt(H, response)  # before processing; include failures
        event = validate_response_and_prepare_proofs(response, D, chosen)
        if event is INCOMPLETE or INVALID:
            exact.defer_unresolved_attempt(chosen, A, retry_policy)
            policy.update_query_policy(event)
            if chosen is A: move A to fair retry queue; A = None
            continue

        E.commit_verified(event)          # atomic, append-only provenance
        incumbent.update_if_verified(event)
        exact.apply_verified_updates(E, incumbent)
        policy.update_query_policy(event)  # no pruning permission
        if chosen is A:
            exact.complete_anchor_and_preserve_continuations(A, E)
            A = None
        elif exact.proves_task_resolved(A):
            A = None
        # otherwise rescore with new ledger and same protected anchor

    return INCOMPLETE(best_verified_incumbent, lower_bound, unresolved_tasks, H)
```

A previous attempt that is only incomplete does not enter the conclusive cache. For a retry, the ledger snapshot and current incumbent may make that partition irrelevant; skip only by a sound current cutoff, not by failed attempt. A diagnostic's validated result may pre-answer a future anchor. Store both its response and exact task-continuation requirements. The outer exact engine determines whether an anchored NO needs children.

### 9.3 Scoring and cache pseudocode

```text
ESTIMATE_QUERY_VALUE(Q, state):
    check state revisions; Q must be admissible and complete
    if no sample mass: return unavailable
    a = suffix_mass(cost(Q)) / W
    labels = sparse_root_label_map(Q)
    cone_bits = bitset(K)
    for R in sample (budgeted):
        if all changed_blocks_of(R) are contained in Q:
            cone_bits.set(R.index)
    b = weighted_mass(cone_bits) / W
    if cone scan not complete: untested hits count as zero (lower bound)

    if regime != unrestricted:
        b = sampled_identity_mass(Q) / W  # generic NO
    no_floor = b; no_expected = b
    if regime == unrestricted and time remains:
        J = proven_possible_failure_superset(Q)
        computed = {}
        for i in bounded_priority_sample(J):
            hits = cone_bits.copy()
            for R in sample not yet in hits:
                if missing_blocks(i,R) all fit in Q:
                    hits.set(R.index)
            computed[i] = weighted_mass(hits)/W
        if J exhaustive and nonempty: no_floor = min(computed.values())
        else: no_floor = min([b] + list(computed.values()))
        no_expected = failure_weighted_average(computed, OTHER=b)
    a_gain = incumbent_gap_progress(cost(Q))
    robust = interval_min(a + lambda*a_gain, no_floor)
    expected = predicted_completion * (
        predicted_accept*(a+lambda*a_gain)
        + (1-predicted_accept)*no_expected)
    score = blend(robust, expected, eta) / estimated_cost(Q)
    return QueryValue(..., revision, declared_assumptions)

UPDATE_QUERY_POLICY(validated_event):
    log pre-query features, response type, latency and bytes
    update completion model using all attempts
    if conclusive: update outcome model; record realized sample progress
    bump evidence/incumbent revision only on verified engine event
    invalidate affected cost suffixes, sample membership and cached closure
    maintain bounded score cache and rolling overhead budget
```

**Explicit default gate.** When the anchor has a score, accept an optional proposal only if its score is strictly greater than `1.1 * anchor_score` and its predicted completion-conditional progress is positive. If no reliable score is available, run the anchor. When reach weights are in units of expected paid calls, use a stricter alternative: require predicted avoided calls greater than one optional call plus a configurable safety margin; for a time objective require predicted avoided seconds greater than evaluation plus selection seconds. This latter threshold is a heuristic and must be evaluated separately from the normalized ranking score. Require remaining optional-attempt, wire and ranking budgets in all cases. A cached or already inferable candidate is handled locally; never let it monopolize optional selection.

For interrupted conditional simulations, include only definitely established sample hits and mark `computed[i]` as a lower bound; if missing-block coverage is not fully verified, treat uncertain blocks as missing. In generic NO mode, do not accidentally retain the cone bitset as certified NO coverage. If scores from different rounds have different sample weights, never compare them without recomputation.

### 9.4 Integration with the other modules

| Module / owner | Contract to CDAQ |
|---|---|
| Raw trace analysis / exact witnesses | Supplies mandatory atom root, named equalities, separating subsets, discrepancy families with completeness flags, cheap feature index, and certified infeasibility/feasibility when available. CDAQ never treats partial atoms as necessary complete alternatives. |
| Evidence/feedback and inference | Validates responses, same-negative region closure, named equality stitching, optional exact proof compression, proof provenance and monotone revision IDs. Returns read-only coverage queries and missing-block summaries. |
| Exact search and lower bounds | Owns all frontier coverage, admissible bounds, safe branch rules, strict incumbent cutoffs, certificate completeness, and fair anchors. Can supply high-priority witness-based candidates but cannot discard tasks on policy scores. |
| Query policy (this report) | Ranks bounded complete candidate pool; manages optional attempt cadence, budget, forecasts and metrics. Does not decide feasibility or build DFAs. |
| External black box | Unmodified complete-partition evaluation. Adapter consumes only public response contract. |
| Independent verifier / benchmark harness | Replays proof from raw IDs, verifies coverage and final candidate or external artifact; keeps planted/reference data outside selector process; reports certified outcomes separately from solver claims. |

Concrete insertion points in pinned `search.py`: factor nested `use_query` into a transport/event boundary and replace diagnostic call sites and one-shot repair scheduling with guarded CDAQ selection. Keep `Evidence` mathematical inference and existing branch-record generation in the engine. Extract local ranking features from `choose_region`/`supports` without recomputing every pair. `select` currently uses layer lists; add a generator/cursor or heap of exact tasks and maintain coverage proof semantics. For a minimal patch, do not reorder actual expansion: keep current layer order as anchor and allow CDAQ only optional proposals. Once verified, add safe within-layer reordering. `staged.py` must funnel mandatory-root, diagnostic, incumbent and final-confirmation submissions through the same attempt tracker (including newer scale package path). `compact.py` witness normalization is useful for legacy responses, but must not synthesize a full unrestricted table for ACCEPT or bounded FAIL. Keep legacy result and certificate formats readable; use an additive versioned transcript for policy metrics.

---

## 10. Counterexamples and failure tests

| Tempting rule | Counterexample / consequence |
|---|---|
| Prune coarsenings after NO | Positives ab, cd; negative epsilon; `ab|cd` NO, `abcd` ACCEPT. |
| Zero in one feasible row is fixed zero | Paper Example 10 has rows (0,0,0), (0,1,1) on a block. The last two are free, not fixed zero. |
| Combine zero evidence for different negatives | Positive epsilon, negatives a,b; `a|b` works despite each block being dead for some negative. |
| Union zero regions for same negative without same-pair proof | Positive ab, negative ba; a and b dead separately but ab separates. |
| Infer ACCEPT coarsening under unchanged finite state bounds | Paper Example 5 above. |
| Assume a bounded NO propagates to refinements | The merged block of Example 5 is bounded NO while singleton refinement works. |
| Treat bounded fixed zero as raw equality | Positive aa, negative epsilon with one-state unary bound: all positive-consistent DFAs accept epsilon even though the projections differ. |
| Discard zero-immediate-gain merges | Positives ab, cd, ef; negative epsilon: every first pair merge rejects zero negatives, but a three-symbol transversal gives optimal cost 2. |
| Greedily favor huge Bell refinement cone | A coarse NO may refine only candidates already closed by prior evidence; conditional marginal score then zero. High cone counts are not actual work savings. |
| Greedily favor ACCEPT probability only | A top partition is guaranteed feasible in unrestricted disjoint sample, but often gives no improvement over the initial mathematical upper bound; it need not certify any cheaper partition. |
| Greedily favor entropy only | A balanced verdict probe over irrelevant high-cost candidates can have high entropy and zero strict-improvement impact. A predictable NO can discharge the entire remaining low-cost sample. |
| Add gains from overlapping regions | One R covered by two negatives or by two simulated facts counts once. Use bitset union, not sums. |
| Restrict min to likely failing negatives | An unmodeled negative can be returned and only supply the direct cone. This invalidates a purported worst-case score. |
| Mark timeout NO or cache as complete | True optimum may be the timed-out candidate; no certificate permits closing it. |
| Treat all sample mass eliminated as global optimality | A bounded sample can miss the only improving partition; only exact engine coverage proves termination. |
| Infer all group constraints from singleton matches | Repeated occurrences and ordered traces matter: aba versus aab agree in counts, disagree in binary order. |
| Trust heuristic estimates as lower bounds | A partial atom list can omit a valid separating alternative; witness score cannot close a branch. |
| Assume a block's rejection table is globally feasible | Bounded tables are local and may lack a joint covering row (paper Example 15); never predict or impose internal responsibility choices. |

### Worked progress example (small, hand-checkable)

Let positives be the four singleton words a,b,c,d and negative epsilon. Start a restricted proof ledger with only singleton zero regions; assume an exact engine has a conceptual relevant sample of cost-one candidates plus `ab|cd`. All six cost-one pair partitions and the two-pair candidate have unit weights (W=7). An incumbent of cost 3 is mathematically available from the top partition; root singleton already certified impossible. Query `ab|cd` is cost 2: conditional ACCEPT cutoff covers one sample candidate; conditional structural NO direct cone covers `ab|c|d`, `a|b|cd`, `ab|cd` (three). Guaranteed conditional mass is min(1,3)=1. Query `abc|d` instead: ACCEPT cutoff one; NO cone covers the three pairs inside abc, but not `ab|cd`, giving three sample candidates. Both tie in robust score; expected score and cost may break tie. After `ab|c|d` has already been queried NO, the sample removes it; querying `a|b|cd` NO now additionally closes `ab|cd` through mixed historical coverage, not just its direct cone. Recompute marginal scores; don't count either already excluded candidate again. In this literal corpus, a full raw analyzer can prove the optimum directly; this example isolates the ledger-based acquisition behavior and is not evidence of practical savings.

---

## 11. Reproducible experimental and validation plan

### 11.1 Three experimental regimes

**A. Policy-only comparison.** Use exactly the same frozen raw evidence budget, candidate generation pool, exact frontier, admissible family, branch rules, verifier, response protocol and query/time cap. Only selection scores/cadence differ. Use paper-shaped `ProjectionOracle` wrapper for unrestricted simulated evaluation; no ACCEPT tables. Compare random, cost-ordered, witness-greedy, existing diagnostic heuristic on the same candidate pool (adapt its score rather than its generation), max expected, max robust, entropy, incumbent improvement and CDAQ. To isolate policy scoring, use the same protected-anchor cadence and optional budget across these variants; also report pure cost-order with zero probes. Log full proposal pool and chosen action per round. Use paired seeds.

**B. Native end-to-end baseline.** Compare actual pinned/default staged solver, scale-improved staged solver, default diagnostics disabled and diagnostics enabled (e.g. 2 and 8), and CDAQ integrated engine. Native variants may differ in candidate generation, response richness or proof rules; label these confounds and do not attribute all differences to query ordering. Report zero-query raw-only solver and one mandatory handoff mode. Keep all external evaluation counts, including mandatory-root probes and final artifact requests.

**C. External validation.** Run the real evaluator unchanged with documented capacity regime, response schema and independent artifact checks. No emulator cache/statistics or planted files accessible to policy. Evaluate with real latency/response sizes and separately a deterministic latency-injected local adapter to isolate overhead. If a bounded protocol is available, report it as a separate experiment; compare only like-for-like capacities and disable unrestricted positive rules. No such real-evaluator run has been performed for this report.

### 11.2 Datasets, isolation and run setup

- Exhaustive small alphabets (n<=7 or an explicit feasible limit), generate all partitions by restricted growth strings and compute compatibility independently by literal erasure of words. Include conflicting labels, empty traces, repeated symbols, unused symbols, shuffled declaration/IDs, duplicate words, multi-negative overlap, order-only differences and both state-bound counterexamples (bounded tests need an independent small exact bounded verifier).
- Use the two combined planted archives: all `input.json` files only for selector, covering reverse, singleton, count, choice, long, mixed, extra imbalanced and interleaved families; repeated budgets are separate historical records. Use `spec.json`, `reference.json`, planted certificates and reference checkers **only in the isolated evaluation process after the solver emits results**. Do not load their metadata into feature engineering or seed the candidate pool with generating partitions. Alternate optimal partitions are allowed; compare optimum objective and independent consistency, not exact equality to planted blocks.
- Use supplied HDFS-1024/holdout, path graph and 1,000-symbol stress inputs. Include hard cases with few useful mandatory contractions. Generate additional raw-only corpus fixtures at n=10,000 and 100,000, with 10,000 and 20,000 total traces, varying active symbols and word lengths. Specify total symbol occurrences as well as n and trace count.
- Use at least 10 paired seeds for randomized policies on nontrivial cases, deterministic stable tie order as a reproducible variant. Hold out entire families/seeds for estimator testing; do not train on the test benchmark references. Fix Python version, OS, CPU, memory cap, hash seed, generator commit, input digests, and budget (5/30 s; larger budget only as separate group). Charge verification separately and end-to-end. Run with process isolation and resource limits. Keep original historical result files unchanged.
- Use same external response regime in each controlled comparison. Inject adversarial but valid failing-index choices (first, random, index with minimum predicted coverage), witness-ID choices and table order; reorder column transmission only if IDs and semantic completeness are preserved. Simulate timeouts separately with seeded random and cost-dependent censoring. Never call an intentionally false table a valid NO. For missing or inconsistent evidence, test adapter rejection and replay recovery. Test failure of optional diagnostics under high-latency and low-latency regimes.

### 11.3 Metrics

Record per attempt, including timeout and malformed response:
`run_id, sample_digest, policy, seed, attempt_id, anchor_id, purpose, partition_key, cost, block_count, regime, incumbent_before, LB_before, score_components, model_version, sample_revision, selection_ms, generation_ms, eval_ms, parse_ms, verification_ms, status, complete, response_bytes, verified_evidence_ids, incumbent_after, LB_after, unresolved_sample_before, certified_sample_removed, exact_frontier_closed_count, retry_count`.

Report:
1. calls/time to first **external ACCEPT** (initial inferred feasible top incumbent does not count), first mathematical feasible proof (separate), first accepted partition of true optimum cost (retrospective, using independent reference only in evaluator), and certified optimum (coverage proof verified).
2. attempted, conclusive, diagnostic, regular, incumbent, retry and handoff counts. Number of distinct queried partitions is a separate metric.
3. newly eliminated candidates per response: exact distinct count on small fully enumerated instances; on large instances report exact explicit frontier closures, sampled weighted closure, and certificate-rule counts separately. Do not treat refinement-cone count or waived merge edges as distinct paid evaluations saved.
4. incumbent cost trajectory and gap U-L; final lower/upper bound on incomplete runs, plus source of both.
5. preprocessing, candidate generation, policy ranking, evaluator, parsing/ingestion, independent verification, total wall time and peak RSS, response sizes and proof bytes. Query-policy overhead as fraction of total, plus time of scoring per proposal.
6. verified optimality rate at fixed budgets, timeout/memory-limit rates, certified infeasibility rate and unsound-proof count (must be zero). Do not report solver OPTIMAL without independent verification as certified.
7. calibration (Brier/log loss, empirical acceptance/completion frequencies), robustness to adversarial choice of valid failing negative, missed/duplicated query accounting and scoring budget compliance.
8. actual saved queries vs paired cost-order baseline under same semantics, with median and interquartile range, paired bootstrap confidence intervals by instance (not treating repeated attempts as independent), and survival/censoring plots for time to verified certification. Include failures; don't average only completed runs.

Acceptance criteria for integration: no incorrect certificate; every small exhaustive optimum matches reference; no regression on fairness or incomplete handling; all explicit budgets honored; only then assess whether median and tail query counts/time improve. A query-count reduction with worse end-to-end time is not automatically successful; report both objectives and Pareto tradeoff.

### 11.4 Tests and reproducibility commands

Historical packages already contain `scale_regression.py`, `audit.py`, `verify.py`, `benchmark_planted.py`, `root_replay_regression.py`, measurement CSV/JSON, and per-case inputs/results. Preserve archives. From the extracted scale directory, historical replay commands:

```sh
python -B scale_regression.py
python -B staged.py evidence/synthetic_10000_traces_1000_symbols.json --transcript > fresh.json
python -B verify.py evidence/synthetic_10000_traces_1000_symbols.json fresh.json
```

For a new implementation, add tests and a runner (proposed names, **not currently present**):

```sh
python -m pytest -q tests/test_query_policy.py tests/test_query_adapter.py
python -m pytest -q tests/test_query_policy_exhaustive.py
python benchmark_query_policy.py --input-dir <inputs-only> --policies random,cost,greedy,current,expected,robust,entropy,ei,cdaq --seconds 30 --seeds 0:10 --protocol paper-unrestricted --out fresh_query_runs.jsonl
python verify_query_runs.py --runs fresh_query_runs.jsonl --references <isolated-reference-dir>
```

Unit tests:
- canonical complete partitions and unused-symbol restoration; root-relative cost identity;
- every structural NO floor and history-amplified floor subset of actual newly proved dead candidates; verify both outcomes on exhaustive small corpus; include already excluded sample members and duplicate weights;
- sparse refinement/missing-block test equals dense reference; mixed historical negative-specific coverage; no erroneous cross-negative unions;
- robust interval endpoints equal brute-force minimum; omitted failure scenarios use fallback; cost suffix sums include correct strict-improvement threshold; zero weights/empty sample handled;
- timeout/retry keeps cheaper candidate unresolved; external ACCEPT with no table accepted by adapter; bounded NO no propagation; malformed negative ordering and witness IDs quarantined; hash collision test;
- score interruption, empty/oversized pool and persistent optional preference cannot starve anchor; score randomization leaves certificate valid; no stale cached score used for pruning;
- verify all certs under legacy and new proof formats, corrupt each proof field and reject; independent verifier never imports ranking code;
- synthetic large sparse roots, complements, 100k unused symbols, large coarse blocks and large response stream; assert operation/memory budgets, not runtime universality.

**Finite check actually performed for this report.** A separate Python restricted-growth-style partition enumerator generated 15 partitions of four symbols. With seed 401, 250 random two-positive/two-negative corpora (word lengths 0–4, repeated letters allowed), two randomly selected historical queries per corpus (ingest only NO tables), and all 15 proposed partitions, the conditional floor inclusion assertions were checked. For every structural NO and every actual failing negative, the refinement set was contained in the history-amplified exclusion set, which was contained in the actual all-column closure. For ACCEPT the relevant cost-cutoff set was used. 3,900 conditional checks completed without assertion failure (some NO queries have multiple failing negatives). This validates finite instances of the set logic, not performance, the full scheduler, or external protocol behavior. The script outline in Appendix A makes the check reproducible. No CDAQ policy-vs-baseline runtime or call-count experiment was executed; historical measurements above are not new results.

### 11.5 Ablations and evaluation hypotheses

Ablate one factor at a time: cone only vs same-negative amplified floor; unit weights vs reach/cost weights; robust only vs calibrated expected; gap bonus off/on; optional cadence B=0,1,2,4; score overhead cap; sparse representation vs dense legacy on manageable cases; known-no table probe disabled/enabled; model-free vs learned cost. Use equal preprocessing and evidence rules. Hypotheses to test, not claimed outcomes:
- CDAQ reduces calls until certification mainly when cheaper unresolved candidate regions overlap coarse NO cones or mixed-history coverage.
- Strong raw mandatory contractions make all policies nearly equivalent; policy overhead should approach zero through anchor fallback.
- Runtime ranking helps when external evaluations are expensive and variable; a pure query-count score can select an expensive coarse query.
- Adversarial failing-negative selection damages expected extra-feedback estimates more than cone-based robust floors.
- Sparse representations reduce policy overhead for near-root candidates but cannot eliminate wire blowup or worst-case combinatorial search.

---

## 12. Remaining limitations and research questions

1. **Global balance:** characterize trace-derived partition lattices or quotient frontiers admitting a constant-factor split in the certificate-progress sense. Without this, no logarithmic general query guarantee.
2. **Proof-task mass:** build compact, provably disjoint frontier-region representations with exact cost-stratified mass, without exponential model counting. This would turn sampled guarantees into global guarantees on structured instances.
3. **Optimality-oriented version space:** define efficient model classes over incomplete discrepancy atoms and determine whether decision-target equivalence class identification or adaptive submodular surrogates can approximate optimal certification cost.
4. **Joint feedback forecasting:** estimate non-failing columns and new bound certificates from observable evidence without nearly duplicating full projection analysis. If predicting a table costs as much as deriving it, derive the proof directly and avoid the call where allowed.
5. **Raw vs external acquisition:** implement a unified scheduler for local witness scans and external complete queries, using measured marginal proof production per cost. This is distinct from redesigning the black box.
6. **Finite capacities:** structural NO remains robust, but generic bounded failure has much weaker cross-partition implications. Rich bounded failure semantics are explicitly open in the paper. Do not introduce unproven rules.
7. **Timeouts and artifacts:** persistent nonanswers prevent unconditional certification when external acceptance is required. Verify how real responses expose local DFAs, table completeness and IDs; adapter contract must be confirmed before deployment.
8. **100k scaling:** sparse selector and proof representation are necessary but not sufficient. Teacher and verifier may remain dominant, output may be intrinsically large, exact search exponential. Benchmark success cannot be assumed from a 1,000-symbol reverse fixture.
9. **Novelty and validation:** proofs in this report establish conditional safety/progress under explicit assumptions; no universal greedy approximation ratio, no polynomial exact search, no measured reduction in actual external evaluations, and no claim that the proposal is globally novel in all literature.

### Recommended integration sequence

1. Freeze and test the external response adapter, conclusive vs incomplete semantics, and separate mathematical/external incumbents.
2. Add persistent query/attempt accounting and fair protected anchor with optional budget B=0; ensure existing certificates still replay.
3. Implement sparse complete partition references and budgeted cone/cost-cutoff scoring; enable B=1 or 2 with robust default, run exhaustive tests.
4. Add same-negative missing-block simulation and cache revisioning. Use fallback for omitted failure scenarios. Validate exact sample progress and proof provenance.
5. Add expected-value and cost estimators, calibrated on training only, after robust baseline is measured.
6. Run controlled policy comparisons and end-to-end benchmarks, including 100k/10k+ cases, recording verified success and resource limits. Only enable a default policy after evidence supports it.

**Final recommendation:** select the next complete partition by predicted *marginal certified progress per paid evaluation*, using the minimum of ACCEPT-cutoff and structural-NO floors as the probability-free core. Exploit history for stronger conditional NO estimates, not guessed proof facts. Keep an exact, fair anchor and a separate independent certificate system. This is a safer and more scalable research direction than either pure cost-layer querying or maximizing estimated refinement count.

---

## Appendix A — Reproducible small conditional-floor check

The following standalone Python code reproduces the finite check described in §11.4. It intentionally uses a simple literal erasure evaluator and small explicit sets; it is not the scalable selector. It checks the candidate-set inclusion theorem, not calibrated scores.

```python
from random import Random

def parts(s):
    if not s:
        yield ()
        return
    a, *rest = s
    for p in parts(rest):
        yield ((a,),) + p
        for j in range(len(p)):
            yield (tuple(sorted((a,) + p[j])),) + p[:j] + p[j+1:]

def ref(P, Q):
    return all(any(b <= u for u in Q) for b in P)

def proj(w, B):
    return tuple(a for a in w if a in B)

def tables(xs, ys, Q):
    return [{i for i,y in enumerate(ys)
             if any(proj(x,B) == proj(y,B) for x in xs)} for B in Q]

def excluded(P, Z):
    return any(all(any(B <= U for U in zi) for B in P) for zi in Z)

rng = Random(401)
ps = [tuple(map(frozenset,p)) for p in parts(list(range(4)))]
assert len(ps) == 15
checks = 0
for _ in range(250):
    xs = [tuple(rng.randrange(4) for _ in range(rng.randrange(5)))
          for _ in range(2)]
    ys = [tuple(rng.randrange(4) for _ in range(rng.randrange(5)))
          for _ in range(2)]
    Z = [[] for _ in ys]
    for Q in rng.sample(ps, 2):
        ts = tables(xs,ys,Q)
        if set.intersection(*ts):
            for B,zeros in zip(Q,ts):
                for i in zeros: Z[i].append(B)
    live = [P for P in ps if not excluded(P,Z)]
    for Q in ps:
        ts = tables(xs,ys,Q)
        fail = set.intersection(*ts)
        A = {j for j,P in enumerate(live) if len(P) <= len(Q)}
        N = {j for j,P in enumerate(live) if ref(P,Q)}
        if fail:
            ZZ = [zi.copy() for zi in Z]
            for B,zeros in zip(Q,ts):
                for i in zeros: ZZ[i].append(B)
            actual = {j for j,P in enumerate(live) if excluded(P,ZZ)}
            for i in fail:
                hypothetical = [zi.copy() for zi in Z]
                hypothetical[i] += list(Q)
                G = {j for j,P in enumerate(live)
                     if excluded(P,hypothetical)}
                assert N <= G <= actual
                assert min(len(A),len(N)) <= len(actual)
                checks += 1
        else:
            assert min(len(A),len(N)) <= len(A)
            checks += 1
print(checks)
```

The last ACCEPT inequality is algebraic, not an independent proof of compatibility; stronger regression should verify that every cost-cutoff candidate indeed cannot improve a newly accepted Q, and test objective coverage and scheduler against a separate exhaustive optimizer.

## Appendix B — References and provenance

[R1] Supplied main manuscript, *Passive Compositional Automata Learning from Global Logs*, 31 pp. Lemma 1, Lemma 2, Theorem 1, Proposition 1–3, §5.1–5.5, Appendix B. File `main (1)(3).pdf`. Source of exact interface and model, not a published benchmark claim.

[R2] Supplied `independent_partition_selection_report(3).md`, *Independent algorithmic analysis: partition selection from traces* (288 lines). Zero-region closure, deletion hitting witnesses, branch/cutoff separation, diagnostic scoring proposal.

[R3] Supplied `Alphabet partition research report(3).md`, *Choosing an optimal alphabet partition from trace evidence* (301 lines). Discrepancy atoms, witness rank, named-equality stitching, diagnostic comparisons, exactness caveats.

[R4] Pinned implementation: https://github.com/Mahdi-Jadidi/passive-automata-learning/tree/7c90eb59561bd25ec4fdca5ac08b0e5d60d17fd/implementation/partition_feedback_final  
Relevant files: [search.py](https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/7c90eb59561bd25ec4fdca5ac08b0e5d60d17fd/implementation/partition_feedback_final/search.py), [model.py](https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/7c90eb59561bd25ec4fdca5ac08b0e5d60d17fd/implementation/partition_feedback_final/model.py), [staged.py](https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/7c90eb59561bd25ec4fdca5ac08b0e5d60d17fd/implementation/partition_feedback_final/staged.py), [compact.py](https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/7c90eb59561bd25ec4fdca5ac08b0e5d60d17fd/implementation/partition_feedback_final/compact.py), `RESEARCH_STATUS.md`.

[R5] Supplied `partition-scale-improved(4).zip`: `SCALE_REPORT.md`, `model.py`, `staged.py`, `search.py`, `hybrid.py`, `evidence/sparse_default_measurement.json`, `evidence/sparse_30s_measurement.json`, `evidence/sparse_regression_checks.json`. Historical measurements and newer sparse contraction path.

[R6] Supplied `partition-part1-planted-benchmark(2).zip` and `partition-part2-planted-benchmark(2).zip`: merged `ALL_MEASUREMENTS.csv`, `planted_results`, `planted_extra`, `planted_30s`, `planted_high_memory`. Historical evaluation data; reference answers reserved for evaluator.

[4] R. D. Nowak, “The Geometry of Generalized Binary Search,” *IEEE Transactions on Information Theory* 57(12), 7893–7906 (2011). https://doi.org/10.1109/TIT.2011.2169298 ; https://arxiv.org/abs/0910.4397 . Conditional query geometry, not a theorem for partition lattices.

[5] K. Chaloner and I. Verdinelli, “Bayesian Experimental Design: A Review,” *Statistical Science* 10(3), 273–304 (1995). https://doi.org/10.1214/ss/1177009939 . General expected utility/design perspective.

[6] A. Guillory and J. Bilmes, “Interactive Submodular Set Cover,” ICML (2010). https://arxiv.org/abs/1002.3345 . Interactive coverage under hypothesis uncertainty.

[7] D. Golovin and A. Krause, “Adaptive Submodularity: Theory and Applications in Active Learning and Stochastic Optimization,” *Journal of Artificial Intelligence Research* 42, 427–486 (2011). https://doi.org/10.1613/jair.3278 ; https://arxiv.org/abs/1003.3967 . Conditions for greedy adaptive guarantees, not established here for full closure.

[8] D. Golovin, A. Krause and D. Ray, “Near-Optimal Bayesian Active Learning with Noisy Observations,” NeurIPS 23 (2010). https://arxiv.org/abs/1010.3091 . Decision/equivalence-class identification and cost-sensitive tests; timeout treatment here is distinct from label noise.

[9] D. Blackwell, “Equivalent Comparisons of Experiments,” *Annals of Mathematical Statistics* 24(2), 265–272 (1953). https://doi.org/10.1214/aoms/1177729032 . Classical information/value-of-information perspective; not a claim that one query dominates another without a valid experiment model.

[10] W. Hoeffding, “Probability Inequalities for Sums of Bounded Random Variables,” *Journal of the American Statistical Association* 58(301), 13–30 (1963). https://doi.org/10.1080/01621459.1963.10500830 . Concentration result used only with stated independence/boundedness assumptions.

[11] F. Labbaf, J. F. Groote, H. Hojjat and M. R. Mousavi, “Compositional Learning for Interleaving Parallel Automata,” FoSSaCS (2023). https://doi.org/10.1007/978-3-031-30829-1_20 . Active-learning context with access assumptions different from this passive setting.

**Evidence audit:** main manuscript and both prior reports were read; the pinned implementation was inspected through GitHub and the newer local archive separately. Both benchmark parts were merged; measurement records were inspected. Literature [4]–[10] was checked against online academic/bibliographic records; [11] is cited in the supplied main paper. The proposed code is pseudocode and interface specification, not an applied repository patch. The real external black-box transport was not available, and its concrete wire format beyond the paper is not assumed. No planted solution was used to build or score a proposal. No repository changes were made.
