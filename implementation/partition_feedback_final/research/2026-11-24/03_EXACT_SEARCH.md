# 03 — Exact partition search and certified lower bounds

**Research assignment:** 03 · Exact combinatorial optimization engine  
**Framework:** *Passive Compositional Automata Learning from Global Logs* (supplied manuscript)  
**Repository revision requested:** `7c90eb59561bd25ec4fdca5ac08b0e5d60d17fd`  
**Scope:** partition selection only; the automata learner and evaluator remain external black boxes.  
**Status:** research design with proofs and small reference checks, not a deployed solver or a claim of publication novelty.

## Executive decision

Replace the breadth-first merge DAG with an **evidence-directed disjoint-region branch-and-bound (EDR-BB)** engine. A search node is not just a partition: it is a *family* of partitions represented by mandatory equalities and branch-local disequalities. When an evidence-backed conflict implies that at least one of several component pairs must be joined, partition the family according to the first pair joined. Implement these disjoint branches lazily using rollback union-find and sparse disequality constraints. Do not combine the previous canonical merge-parent rule and conflict-only branching without a new coverage proof.

Use a portfolio of certified lower bounds, from mandatory contractions and inexpensive deletion-witness packings to **localized joint rank bounds with fractional packing**. The latter is the principal new mathematical candidate in this report: it accounts for sharing between negatives while safely combining overlapping subproblems. A proof of the bound and a strict-improvement example are given below. The earlier witness-rank theorem is retained as a reference relaxation, not claimed as new.

The main architecture is a lazy structural relaxation followed by a complete-partition external query. A structural proof can exclude a family without invoking the evaluator. An actual accepted candidate is required to establish the operational incumbent. Preserve an explicit `UNKNOWN` frontier for interrupted queries. In bounded mode the same structural constraints remain necessary, but an unexplained bounded failure excludes only that exact partition; no coarsening/refinement monotonicity is assumed.

At large scale, first eliminate the representation bottleneck: integer IDs rather than one-hot big integers, sparse projections in the **raw-analysis/checking** module, endpoint-based mandatory-union proofs, and streaming independent replay. This is not a request to modify the external evaluator. The black box's actual serialization, latency, and table volume remain potential bottlenecks even if the selector is fast.

### Evidence and scope of the audit

- Read the supplied 31-page main paper, including Sections 2–5 and Appendix B, and both full previous Markdown reports: *Independent algorithmic analysis: partition selection from traces* (R1) and *Choosing an optimal alphabet partition from trace evidence* (R2). References to those documents below use their actual section headings.
- Accessed the GitHub revision through the repository connector and inspected the relevant directory tree and `README.md`, `model.py`, `search.py`, `staged.py`, `hybrid.py`, and `verify.py` at the requested ref. The recursive repository tree was marked truncated; this is not a claim of a complete audit of every repository file. The standalone archives contain the relevant code and benchmark results used for deeper inspection. The tree response normalized the SHA to `7c90eb59561bd25ec4fdca5ac08b0e5d60d17fd6`; file reads used the user-specified ref. No GitHub write was made.
- Extracted both planted benchmark archives into one directory, separately from `partition-scale-improved(3).zip`. Inspected the benchmark reports, CSVs, measurement JSON, source and certificate replay records. The scale archive is **not byte-identical to the pinned code**: `hybrid.py` matches its Git blob, but `model.py`, `staged.py`, `search.py`, and `verify.py` differ. The scale archive adds the sparse reverse-contraction fast path and verifier improvements. Results are attributed to the archived variant, not silently to the commit.
- Ran independent small reference checks and sparse raw projection/contraction probes on selected benchmark inputs. These are not external evaluator calls and are not an end-to-end timing of EDR-BB. Historical results are distinguished from new observations in §12. The actual external transport/API and state-bound configuration have not been supplied; the paper establishes semantic inputs and outputs, not a JSON wire protocol.

## 1. Formal model and the black-box boundary

Let `Σ = {0,…,n−1}` be the finite **declared** alphabet, indexed in the declared order. Let `X=(x_0,…,x_{p−1})` and `Y=(y_0,…,y_{q−1})` be lists of finite words. Retain original IDs even if duplicate words are internally interned. Projection `π_B(w)` is the subsequence of `w` consisting of all occurrences with symbol in `B`, in original order. Neither sorting nor set conversion of a trace is allowed.

A complete partition `P` is a collection of nonempty, disjoint blocks with union `Σ`. Let `P ≤ Q` mean refinement, so `Q` is a coarsening. Objective:

```
c(P) = n − |P| = Σ_{B∈P} (|B|−1).
```

Write `Sep(i,B)` iff for all `j`, `π_B(y_i) ≠ π_B(x_j)`, and `Dead(i,B)` iff there exists a matching positive. Structural compatibility is

```
F∞(P) := ∀i ∃B∈P Sep(i,B).
```

This is exactly paper Lemma 1, equation (5), in the unrestricted model. With finite state bounds `m(B)`, define `Fm(P)` to mean existence of a tuple of complete local DFAs within those fixed bounds, accepting every positive projection, and collectively rejecting every negative. `Fm ⇒ F∞`, but not conversely. Paper Example 15 demonstrates individually possible rejections that cannot be realized jointly; Example 5 shows that bounded feasibility is not upward-monotone. The assignment's mathematical model is `F∞`, not the bounded model. All structural lower bounds below also hold for `Fm`, since they are necessary conditions. Completeness of an unrestricted search shortcut is not automatically transferable to bounded mode.

The paper assumes nonempty alphabet and disjoint positive and negative sets. For defensive implementation, accept a finite alphabet including empty only if an extended local contract explicitly allows it: if `n=0`, the empty partition satisfies the conjunction exactly when `q=0`; otherwise infeasible. With `n>0`, if `q=0` or `p=0`, singletons are structurally optimal. If an identical word occurs on both sides, every partition is infeasible in either regime. Otherwise `Σ` as a single block is feasible in the unrestricted model (finite language of positives). This is not guaranteed in the bounded model. A raw proof of structural feasibility is not an external ACCEPT receipt; maintain separate labels for both.

### 1.1 Documented interface, not guessed API

Paper §5.1 and Fig. 2 (pp. 12–14) specify the following semantic contract:

| Outcome | Documented information | Valid inference |
|---|---|---|
| Projection failure | Submitted partition, ordered negative indices, one failed negative, one positive witness on every block, local unrestricted rejection tables `R_B^∞` | Exact structural NO; all refinements fail; named zero regions and all valid fixed-zero columns can be reused. |
| Unrestricted success | Complete local DFA witnesses and partition | Compatible; receipt (and independently checkable returned witnesses) establishes incumbent. Paper does not require success tables. |
| Bounded success | Joint feasible rejection assignment and complete DFA witnesses; final return is partition and DFAs | Compatible under the configured capacities. No automatic monotone inference. |
| Bounded failure | `FAIL` for that exact sample, partition and capacity regime; richer failure interface remains open | Exact partition exclusion only, unless a separate structural proof is supplied. |
| Timeout, malformed, interrupted response | No mathematical conclusion; these are operational statuses, not paper's conclusive FAIL | Defer or retry; do not close candidate unless separate evidence suffices. |

For unrestricted tables, paper equation (23): `r_i=1` means rejection, `r_i=0` acceptance; a matching positive forces zero and identical negative projections force equal bits. Every assignment satisfying these constraints is realizable. Represent the relation by fixed zeros and equivalence groups of negative indices. If there are `f` free groups, there are `2^f` feasible rows; never enumerate them merely to detect fixed zeros. A complete all-zero column is exactly structural deadness; a 1 in any feasible row implies structural separation. A zero in a single row, or in a truncated collection of rows, proves neither. Fixedness in bounded tables or tables reduced by joint global conditions is **not** necessarily structural deadness. Do not promote such a column to a reusable zero region. For a bounded fixed zero, one can independently check whether a raw positive match exists; only that match licenses structural reuse.

The pinned local `ProjectionOracle` computes `row(block)`, caches positive projection witnesses and free negative groups, and returns `status`, `blocks`, `tables`, `failed` on both ACCEPT and NO. It decides projection compatibility only. `search.check_reply` checks that zero/free indices form a complete disjoint cover and that the verdict agrees with the union of free columns. That interface is convenient for a simulator, but **not the paper's external success/failure protocol**. In particular, a bounded failure can occur when every negative appears free somewhere, and an external ACCEPT may contain no tables at all. `search.select` assumes a `NO` supplies a usable common-negative region and otherwise raises an assertion; it needs a different search-side adapter to handle bounded and incomplete responses. The scale fast path in `staged.solve` is gated off for custom or query-limited oracles, so benchmark timings do not establish external performance.

Proposed adapter on *our* side, not a modification of the black box:

```python
@dataclass(frozen=True)
class EvaluationRequest:
    sample_digest: str
    regime_digest: str             # includes capacities/admissible family, if any
    request_id: str
    blocks: tuple[tuple[int, ...], ...]  # full declared alphabet, original IDs

@dataclass(frozen=True)
class NormalizedResponse:
    request_id: str
    sample_digest: str
    regime_digest: str
    partition_digest: str
    kind: Literal['ACCEPT','PROJECTION_NO','BOUNDED_NO','UNKNOWN']
    failed_negative: int | None
    named_positive_by_block: object | None
    unrestricted_tables: object | None
    tables_complete: bool
    external_receipt: object | None
    dfa_witnesses: object | None   # opaque payload; read-only validation if supplied
```

The adapter maps documented fields to this internal type; it does not demand these fields from the external API. If the paper's semantic distinction cannot be established for a received NO, store exact rejection only if a complete authoritative NO is confirmed; otherwise UNKNOWN. A malformed table does not invalidate a separately authentic conclusive exact verdict, but its table facts must not enter the structural ledger. Bind every receipt to the exact sample, order of negative columns, partition and regime. Check label ranges, coverage, membership and equality of explicitly supplied witnesses before use. A named raw equality can be verified independently even if other feedback is truncated; interruption itself licenses no verdict. Preserve raw payload/digest. Do not access local DFA internals except public returned witnesses for validation. Do not invoke a block-only query. All external requests contain every symbol, including unused ones.

## 2. Previous work: retain, extend, replace

| Source / implementation | Established contribution | Limitation addressed here |
|---|---|---|
| Main paper §§3–5 | NP-completeness, exact structural test, unary/binary atoms, disjunctive separator conditions, increasing-cost exhaustive search | Cost layers still grow like Stirling numbers; no general feedback-driven partition selection design. |
| R1, “Analyze traces”, “Select partition after NO” | Deletion witnesses, hitting-set bound, joint subset DP, same-negative zero-region exclusion, canonical parent | Per-negative bound can miss interactions; DP exponential in symbols and negatives; canonical parent cannot be blindly combined with conflict pruning. |
| R2, §2 and §4 | Complete discrepancy atoms, exact witness-rank formulation, path-preserving conflict merges, raw/table proof rules | Naive alternative enumeration exponential; retained paths can overlap; no efficient certified fractional combination of localized subproblems. |
| Pinned `hybrid.py` / `staged.py` | Singleton coverage; pairs, disjoint pairs, triples; optional full rank optimization; fallback exact search | Large scans exhaust resources before discovering easy contractions; default uncapped is not a scalability guarantee. |
| `search.py` / `verify.py` | Evidence antichains, same-negative region partitions, greedy support/rank bounds (including overlap correction), incumbent repair, deduplicated cost-layer DAG, proof replay | Keeps frontiers and generated partitions; crossing children still duplicate across parents; branch replay and mask representation expensive. |
| Improved archive | Sparse length-two reverse detection, quotient root ACCEPT shortcut, faster projection replay | Despite DSU, one-hot masks remain quadratic in aggregate bit width; complete projection oracle and replay still expensive. |

The current `supports` routine projects deletion obligations onto current atoms, groups intersecting supports, and derives a lower bound on the hitting number using `ceil(number_of_obligations / maximum_degree)` in each component. Its `lower_bound` greedily combines supports, discounting an overlap of `s` vertices by `max(0,s−1)`, or using disjoint supports. The new fractional certificate in §6 should complement, not erase, that valid rule. The existing `choose_region` groups current atoms into larger witnessed dead regions, and `select` only branches across groups; this is path-preserving for unrestricted coarsenings, but a deduplicated DAG still stores many complete partitions. The current verifier replays contraction and branch records and validates raw compatibility independently of the selector. Preserve this separation of trust.

The paper and R2 already prove unary/binary completeness; the following is a compact restatement for integration. For each `(i,j)`, let `A_ij` be the inclusion-minimal discrepancy atoms: unary count differences and binary order differences with both unary counts equal. Equal unary projections identify the same occurrence labels `(a,k)`; equal binary projections fix the relative order of each pair of different-symbol occurrences. Thus equality on every atom-sized restriction entails equality of the projected word. Therefore

```
π_B(y_i) ≠ π_B(x_j)  iff  some A∈A_ij is contained in B.
```

This includes empty projections and repeated symbols. Full atom discovery is polynomial in input and alphabet but can be prohibitively expensive; minimal *separators* can be exponential (paper Example 12). A found atom is sufficient evidence of difference, but an incomplete list of found atoms is not a necessary disjunction. This distinction drives the lazy relaxation.

## 3. Proof-carrying evidence and contraction

### 3.1 Typed evidence ledger

For each original negative `i`, maintain:

- `DeadRegion(i, U, positive_id, proof_id)` with `π_U(y_i)=π_U(x_j)`. Store `U` as sparse included set or complement, not a full mask; an authentic fixed-zero table may be converted to a replayable positive ID by raw matching.
- `Deletion(i,T,j)` is the same equality with `U=Σ\T`. A block rejecting `i` must meet `T`.
- `CompleteAlternatives(i,j,A)` contains **all** discrepancy alternatives (or a verified superset). Missing alternatives are not allowed for necessity. A known partial atom list belongs in `PositiveWitness` instead.
- `Separating(i,B,proof)` proves one block rejects against all positives. Valid for every superset structurally, not for arbitrary bounded local DFA rejection.
- `ExactNo(P, receipt, regime)` and `Accepted(P, receipt, regime)`. Only complete accepted responses count as operational incumbents; a raw structural incumbent can be used as a separate provisional bound in unrestricted mathematical optimization, but the recommended engine waits for external acceptance before pruning on its cost.

For one negative, a family of dead regions excludes precisely the partitions whose every block is contained in some known dead region. Combining different tables is allowed only within the same negative ID, and does not justify union of regions. The ledger is append-only logically; antichain indices are caches, not proof storage. Store evidence by stable IDs and version; coarsening or refining a branch changes its view of evidence, not the raw facts. Negative coverage by an actual separating block is a fact about the structural model only.

### 3.2 Mandatory contractions

**Lemma 1 (forced pair).** If for one negative `i` there are witnessed deletions `{a}` and `{b}`, `a≠b`, every structurally compatible partition joins `a,b`. The two matching positives may differ.

*Proof.* Any separating block for `i` must intersect both singleton deletion sets, hence contain both symbols. ∎

Use DSU with compact parent/size arrays over original IDs. Add only certified successful unions. A proof record `(i, j_a, a, j_b, b)` suffices; the verifier checks equality after deleting each endpoint from the indicated pair of words and performs the union itself. For adjacent swapped words `u a b v` and `u b a v`, `a≠b`, the same proof follows by deleting either endpoint; an alternate record contains the two word IDs and the exact swap position. Detect the length-two special case by dictionary lookup as in the improved archive, then extend discovery by bounded enumeration of adjacent swaps, indexed deletion signatures, and raw known witnesses. For count controls, an equality after deleting one symbol from negative `ab` to positive `b`, and one after deleting `b` to positive `a`, prove the same merge. Index short words first; for arbitrary long words the naive generation of all swapped/deleted strings costs quadratic in length, and must be budgeted. Hash filters are not equality proofs; replay the matched words exactly. No planted grouping is used.

For branch-local constraints, if the set of current atoms intersecting a deletion is a singleton, any rejecting block must include that atom. Two such singleton obligations for the same negative imply a forced union of their atoms within that branch, even if original `T` was not singleton. A forbidden union gives immediate branch infeasibility. Do not require same-block from a singleton obligation of one negative and a singleton obligation of another negative.

Let mandatory closure be `M` with `k` atoms. Every feasible `P` coarsens `M`; quotient partitions correspond bijectively to original coarsenings and

```
c(P) = n−k + (k−|P|).
```

Atom size is irrelevant to **additional** merge cost: merging two current atoms costs one even if one contains 50,000 original symbols. Keep original symbol IDs inside each atom for projection; replacing an entire trace by quotient labels can destroy discrepancies (`ab` vs `ba` becomes the same label twice).

Unused declared symbols are singleton in every optimal unrestricted partition whenever the active alphabet is nonempty: splitting off such a symbol preserves all nonempty active block projections and cannot destroy structural separation. Handle empty active alphabet separately (identical empty words or no label class). In bounded mode removing an unused letter can change `m(B)` and admissibility; therefore do not fix it singleton unless monotone capacity/admissibility and a constructive preservation proof are supplied. For the assignment's unrestricted, all-partitions contract, fix unused singleton atoms as an independently verified reduction; the proof checker may exclude non-singleton placements only as a dominance rule, not declare them incompatible. Restore them on every external query. For a restricted partition family, dominance requires that the refined solution remains admissible.

## 4. Search representation and duplicate-free branching

### 4.1 Region semantics

Let `E` be the equivalence closure of mandatory and branch equalities; `D` a set of original representative-ID pairs constrained unequal. A node denotes

```
R(E,D) = { P : E ≤ P and ∀(a,b)∈D, a and b are in different P-blocks }.
```

Intersect with the admissible family if relevant. The minimum-cost member before any other constraints is `E` (unless a disequality is internal to one E-atom). Every completion has cost at least `n−|E|`. Store the global root `M` and a rollback DSU for branch merges; branch disequalities are sparse adjacency lists between representatives or immutable original endpoints. A union is illegal if it joins a prohibited pair. Query `E` only as a complete original-alphabet partition. It is not a partial partition in the external interface; it is the finest representative of this region.

Contrast with a canonical parent tree: the R1 rule splits the largest symbol from the first nonsingleton block, uniquely reaching all partitions from singletons. This removes duplicate edges but conflict-selected immediate merges need not coincide with the canonical child. Example: alphabet `a<b<c`, positives `a,b,c` as three separate words, negative `ε`. The unique compatible partition is `abc`. The witnessed dead partition `ab|c` (positive `c` matches on `ab`, positive `a` matches on `c`) gives a conflict allowing only `ac` or `bc` as first merges. But the canonical parent of `abc` is `ab|c`, so its unique canonical path first joins `ab`. Combining the two rules loses even the unique optimum. Do not conflate paths and entire cones.

### 4.2 Conflict extraction

A **pair conflict** is a set `C` of currently distinct atom pairs for which every compatible completion in the region must satisfy at least one same-block predicate. The following sources are sound:

1. **Dead partition:** if `E` is structurally NO on negative `i`, group its atoms into disjoint regions `G_1,…,G_r`, each contained in a known dead region for `i`. Any compatible completion must join a pair crossing two groups. Derive a pair conflict consisting of all allowed cross-group pairs. Regions may be the current atoms themselves. For a previously failed partition `Q`, an analogous clause requires crossing its blocks; if current E already crosses Q, the clause is satisfied and cannot branch.
2. **Disjoint deletion obligations:** for one negative, take `H_1,H_2` = the sets of current atoms touching two witnessed deletion sets. If they are disjoint, the negative's rejecting block includes one atom in each, so at least one pair in `H_1×H_2` must join. Filter pairs already prohibited by `D`.
3. **Complete discrepancy alternatives:** for a particular `(i,j)`, if no available unary/atom-contained alternative exists and all alternatives are binary across distinct atoms, at least one such pair must join. Complete alternatives can also be relaxed to a verified superset of pairs. Do not derive a necessity conflict from an incomplete discrepancy list. For general selected obligations with larger supports, derive a pair disjunction by a proved implication, not by assuming every alternative pair is required.
4. **Localized rank constraint:** if a support `S` requires restricted rank at least one, some distinct atoms of `S` must be joined. Larger rank can be retained as a numerical bound; an optional first-pair conflict is the complete pair set on `S` minus prohibited pairs.

An empty unsatisfied conflict proves the region infeasible. Unit conflicts force a union. Exact bounded NO, with no structural witness, does not supply a conflict required in other regions, but at this node it excludes `E`; every *other* completion is a strict coarsening and must join at least one currently distinct atom pair. A generic all-pair split therefore covers every remaining completion. The same generic split can be used after a structural pass that has not received a definitive external response, but the exact representative `E` must be retained as a pending leaf (or later excluded by a new valid bound). This fallback is slow but correct.

### 4.3 The disjoint first-satisfied-pair theorem (new integration design)

Let `C=(e_1,…,e_t)` be a reproducibly ordered list of distinct allowed cross-atom pairs at node `(E,D)`. For each index `j`, define

```
child_j = ( closure(E ∪ {e_j}), D ∪ {e_1,…,e_(j−1)} ).
```

Here each pair is represented by original stable representative IDs as they were at the parent. The residual branch has all `e_j` unequal.

**Theorem 2.** Children are pairwise disjoint as families. Their union equals the members of `R(E,D)` satisfying the pair disjunction. If `C` is a certified necessary conflict, every compatible member belongs to exactly one child. If the residual is not known incompatible, retain it (or the pending exact representative in the all-pair fallback).

*Proof.* Any member satisfying the disjunction has a unique least true pair `e_j`. It satisfies all earlier disequalities and the `j`th equality and therefore belongs to `child_j`. Conversely any member of the child has that least true pair. Two distinct least true indices are impossible. If an equality closure contradicts an earlier disequality, that child is empty; no completion is lost. The argument is independent of heuristic ordering. ∎

**Implementation.** Do not materialize all `t` children. A binary continuation first explores the equal branch for the next pair, and the unequal branch continues the list. Store prefix position and proof of the original disjunction. This has the same disjoint semantics, with one additional merge on every equal descent. For a large cross-product, represent pair families by two sorted atom sets or group membership arrays and use a deterministic pair iterator, skipping prohibited pairs with recorded checks. A resource-limited iterator must checkpoint its unconsumed suffix. A verifier regenerates the iterator from the proof and checks that the residual was closed only by a conflict or retained. Never use an unrecorded top-K pair list as the entire conflict.

This is a region-based adaptation of equality/disequality branching familiar in set partitioning (Ryan–Foster style, see [L3]), with necessary disjunctions generated from trace evidence. The adaptation and proof above are proposed contributions; generic branching itself is established technique.

### 4.4 Dominance and search order

Use depth-first search with an incumbent and certified bounds as default (bounded memory), optionally best-bound selection on a disk-backed frontier. Sort candidate conflicts by small `t`, lower-bound potential, repeated support, or expected feedback benefit; these are heuristic preferences, not exclusions. If a verified external ACCEPT for `E` arrives, its cost is the minimum possible in `R(E,D)` and closes that region for strict improvement. If the engine wants *all* optimal solutions, equality pruning must change to strict `>` and all tie branches must be retained.

A full partition may be rejected by a previously recorded exact NO. That does not imply its coarsenings fail. A structurally known ACCEPT can seed a query proposal; with a true external ACCEPT incumbent, no node of cost at least that incumbent needs querying. For the all-partitions unrestricted objective, the one-block partition is a useful early external query when no better seed is available. A repair heuristic can construct promising blocks by uniting alternatives chosen to reuse current components; the complete candidate must be checked externally. If the external evaluator times out at the one-block candidate, retain the pending state; do not invent an upper bound.

## 5. Witness-rank optimization: exact reference and relaxation

Work on current quotient atoms `V` of size `k`. For each negative `i`, keep a list of necessary alternative families `F_ij`. A family may contain singleton sets (deletion obligation) or unary/binary discrepancy atoms after mapping endpoints to current atoms. The constraint for a negative requires **one common block** containing one alternative from each family. If a family has no alternative, infeasible; if there are no families, it imposes no requirement. Partial deletion witnesses are necessary; partial atom lists must either be omitted or expanded to a verified superset. The exact full-atom model uses every `(i,j)`.

Given one chosen alternative per family, form `H_i` as the union of its choices. All vertices of `H_i` must be co-blocked. Let `r(H)=k−components(H)` be the graphic rank of the union of stars connecting each hyperedge, with isolated vertices counted. This is independent of which star tree is used within each edge. The previous report R2 proves that the minimum additional cost for all obligations is `min_choices r(H)`.

**Extension (disequality-aware rank).** Restrict choices to those for which the components induced by all `H_i` contain no prohibited pair in `D`. Then `min_choices r(H)` remains the exact minimum additional cost of a partition satisfying the necessary obligations and `D`, with infinity if no choice remains.

*Proof.* Any feasible completion admits a choice of alternatives within its designated witness blocks. Their union components refine that completion, hence contain no prohibited pair and cost no more. Conversely take any permitted choice and make exactly its induced components into blocks, including isolated vertices. Every negative's selected alternatives lie in one component; all disequalities hold. Cost equals rank. ∎

This is exact for the *relaxation*, not for bounded DFA compatibility. With full atoms it exactly optimizes `F∞` under E and D (assuming no additional admissible-family restriction). A minimizer can serve as a proposal, but still submit it externally. If no external confirmation is obtained, report structural optimum separately from operational result. A partial-rank optimum certified by complete choice enumeration is a valid lower bound, whereas the cost of a heuristic chosen witness assignment is an **upper bound on the relaxation's optimum**, not a lower bound.

Use rollback DSU search over alternative families, with a per-negative anchor for already selected atoms. Union chosen atoms with its anchor (choose the first nonempty alternative as anchor if necessary). Any new union raises rank; reject forbidden pair, stop at threshold `U−c(E)` when proving no improvement. Canonicalize equivalent alternatives at the current quotient and deduplicate. If a smaller alternative is contained in another, the larger is dominated for this relaxation because selecting the smaller requires fewer equalities. This dominance is not a direct deletion of complete partitions; it preserves minimum relaxation cost. A choice-tree certificate covers every alternative or provides the containment dominance proof. It does not require every combination of alternative choices to lead to a distinct partition.

## 6. Certified lower-bound portfolio

All bounds in this section are on **additional** cost from `E`. Add `c(E)` once; do not charge mandatory unions twice. For any actual completion `P`, write `P_V` for its partition of current atoms, and

```
r_P(S) = |S| − |{ B∈P_V : B∩S≠∅ }|    for S⊆V.
```

For `S=V`, this is additional cost. For a subset it is rank of the restriction, not the number of selected pairs. The bounds may be combined by `max` unless an explicit sum/packing inequality justifies addition.

### 6.1 Cheap per-negative bounds

For a deletion `T`, quotient support `H={v∈V : v∩T≠∅}`. A rejecting block for that negative must meet all such supports. If a deletion is empty, raw words match globally and the sample is infeasible. Remove duplicate supports and supersets (hitting a subset hits the superset). For any subset of witnesses of negative `i` whose union is `S`, a transversal of its supports must be present inside one block, yielding

```
r_P(S) ≥ max(0, τ(H_i|S)−1),
```

where `H_i|S` here denotes only selected supports **fully contained in S**, not their intersections with S. Truncating a support to S can make the relaxation stronger than the truth and is unsafe. A single large support is no proof of a merge. Compute bounds on `τ` via:

- pairwise-disjoint support packing: each selected support requires a distinct vertex;
- degree bound `ceil(h/Δ)` for `h` supports and maximum vertex frequency `Δ`;
- sum across disjoint incidence components of the hitting problem; all selected witnesses for the same negative still require one common block, so subtract one after summing their hitting bounds;
- rational dual weights `α_T≥0`, `Σ_{T∋v} α_T≤1` for each vertex. Every hitting set has cardinality at least `ceil(Σα_T)` by charging each chosen vertex at most one. Verify every rational inequality exactly. An approximate LP solver may suggest weights, but cannot certify them without exact rational repair;
- exact bounded-width hitting set search, with a covering branch tree proving no transversal below a claimed size. Choose an uncovered support, branch on every vertex of it; selection search need not be duplicate-free for validity, but can use first-choice exclusions. An exhibited transversal alone provides only the opposite inequality.

If pair constraints prevent a common block, local hitting may be impossible even though a cheap bound is finite; ignoring disequalities is always a safe relaxation. Conversely, a branch-level separation already established does not mean its obligation contributes extra merge cost; quotient mapping handles it (e.g. all supports hit by one atom, bound zero).

### 6.2 Localized joint rank bounds (principal proposed extension)

Choose a support `S⊆V` and select a subset of the necessary alternative families for each negative, retaining only families for which **every alternative lies in S**. Keep any branch-local disequalities on S if desired. For negative `i`, all selected families still require one common block. Compute a certified lower bound `l_S` on the minimum rank of this localized problem; use §5 exact rank, subset DP, or a sound lower relaxation. Then every true compatible completion satisfies `r_P(S)≥l_S`.

*Proof.* Restrict any compatible partition to S. For each retained family, a chosen alternative from its original witness block lies wholly in S. All retained alternatives for that negative lie in the same restricted block. The restriction also satisfies the retained disequalities. Its rank is precisely `r_P(S)` and cannot be lower than a certified bound of the localized relaxation. ∎

This captures interactions between negatives without enumerating all partitions of the full alphabet. It can prove stronger bounds than considering each negative independently: take positive `abcdef`, negatives `bacdef` and `abcdfe`. Each has a unique order atom (`ab` and `ef` respectively); on the joint support `{a,b,e,f}`, rank is at least two, not one. A shared atom between negatives, conversely, should be charged once. Exact local optimization can combine alternative choices rather than force a particular pair. Use only small supports (for example ≤12–20 atoms after quotient, with explicit budgets); if interrupted, retain only the lower bound already proved by its own frontier. Do not return an unfinished minimum as a valid lower bound.

### 6.3 Fractional restricted-rank packing theorem

Let a collection of proved local rank constraints `r_P(S_h)≥l_h` be given. Choose nonnegative rational weights `λ_h` with vertex capacities

```
∀v∈V: Σ_{h:v∈S_h} λ_h ≤ 1.
```

**Theorem 3 (fractional rank packing).** Every compatible completion satisfies

```
r_P(V) ≥ ceil(Σ_h λ_h l_h).
```

*Proof.* Fix a block `B` of `P_V` and choose an anchor `a_B∈B`. For each support, `( |S_h∩B|−1 )_+ ≤ |(B\{a_B})∩S_h|`: if the anchor belongs to S the two quantities are equal; if not, the right side is at least the left. Thus

```
Σ_h λ_h (|S_h∩B|−1)_+
 ≤ Σ_{v∈B\{a_B}} Σ_{h:v∈S_h} λ_h
 ≤ |B|−1.
```

Summing over blocks gives `Σ λ_h r_P(S_h)≤r_P(V)`. Substitute the local lower bounds and use integrality. ∎

This includes ordinary disjoint-support summation (weights 1), yet permits overlap without double charging. It applies to any verified localized lower bound, not just hitting-set witnesses. The LP is a **maximization of a provable lower bound**, with variables per support and capacity constraints per atom. Any feasible rational solution is enough; optimality of the LP is not required for certification. Greedy weight assignment, exact rational simplex on small support families, or rationalized floating LP output are implementation options. To repair proposed weights, set negative values to zero, round nonnegative weights down to rational numbers, and scale by `max(1, max_v load(v))`; then check exactly. Round the final objective upward, not the weights upward. Do not substitute a primal LP solution for a verified dual lower bound.

**Strict example versus greedy overlap correction.** Let `x=abcdef` be the only positive; three negatives are `badcef` (swap `ab` and `cd`), `abdcfe` (swap `cd` and `ef`), `bacdfe` (swap `ab` and `ef`). Every negative requires one of its two pair atoms to be joined. Supports are `S1={a,b,c,d}`, `S2={c,d,e,f}`, `S3={e,f,a,b}`, each with local rank floor 1. Every pair of supports overlaps in two vertices, so the old greedy overlap rule on these three primitives can add only one unit initially (subsequent overlap penalty is at least 1). Each vertex belongs to exactly two supports: choose weights 1/2, giving `ceil(3/2)=2`. This matches the true optimum, since joining `ab` and `cd` covers all three negatives. This comparison is specifically against those three rank primitives, not a claim that the full previous solver cannot find the same bound by other analysis. The example is a trace-realizable strict improvement over those local floors and that combination rule.

### 6.4 Existing overlap rule and stronger exact local bounds

For two supports A,B, the inequality `r_P(A∪B)≥r_P(A)+r_P(B)−r_P(A∩B)` follows from counting intersections of each final block. This restricted rank function is **supermodular** on vertex subsets: rank is cardinality minus the number of touched blocks, and the latter is submodular. Explicitly for each final block the inequality `r(A∪B)+r(A∩B)≥r(A)+r(B)` holds, with possible strictness if the block touches both A and B but misses their intersection. Since `r(A∩B)≤max(0,|A∩B|−1)`, the previous correction is sound. Use the maximum of that bound, fractional packing, exact localized rank, and simple global bounds. In particular the fractional result need not dominate the overlap correction; a sequence of supports with one-vertex intersections can be charged more strongly by the latter.

One may also derive moved-vertex bounds: any required pair disjunction forces at least one selected same-block pair and hence two nonsingleton vertices in its endpoint support. If an independent certified relaxation proves at least `m` atoms must belong to nonsingleton blocks, then `r_P(V)≥ceil(m/2)` because a nontrivial block of size `s≥2` contributes `s−1≥s/2`. For instance, formulate a minimum union of endpoints of selected conflict pairs; a lower bound on the number of selected vertices gives a valid moved-vertex bound. This is optional, may be weaker, and does not authorize counting all candidate endpoints as moved.

### 6.5 Local DP and set-partition LP

For small supports, precompute `cover(B)` as the set of negatives whose retained alternative families can all be satisfied inside block B. Discard blocks violating a retained disequality. On remaining set `R`, with already covered negatives `C`, choose its least vertex `v` and enumerate all nonempty `B⊆R` containing v:

```
F(R,C) = min_B [ |B|−1 + F(R\B, C∪cover(B)) ]
F(∅,C) = 0 if C contains every required negative; +∞ otherwise.
```

The block of v is unique, giving a duplicate-free recurrence and exact optimum of this localized relaxation. R1 introduced the joint DP; here it operates on quotient supports with branch disequalities and feeds the fractional bound. Complexity `O(3^s 2^h · poly(s,h,e))` time and `O(2^(s+h))` memo states for `s` vertices, `h` relevant negatives, and explicit evidence size `e`, excluding block preprocessing. A full DP table or recursively checked transition minima are certificate options. A bounded partial DP may provide only a certified floor, not an arbitrary current best value.

A block-set LP uses all admissible nonempty subsets as columns, `z_B≥0`, exact symbol coverage `Σ_{B∋v}z_B=1`, and negative coverage `Σ_{B:cover_i(B)}z_B≥1`. Minimize `Σ (|B|−1)z_B`. LP dual feasibility over **all** columns proves a lower bound. A restricted master containing only generated columns can overestimate the true relaxation optimum, hence is not a valid lower bound unless exact pricing verifies no violating omitted column. For dual variables `u_v` free and `t_i≥0`, require `Σ_{v∈B}u_v+Σ_{i∈cover(B)}t_i≤|B|−1` for every permitted block. Pricing itself may be exponential. Use only when a small support makes all columns checkable or a pricing proof is supplied.

### 6.6 Bound algorithm and proof format

```
compute_lower_bound(node, evidence):
    assert node has consistent E,D
    base = n - number_of_E_atoms
    constraints = []
    for selected negative and retained deletion supports:
        map to current E-atom IDs, dedup, minimize
        certify packing/degree/dual transversal floors
        emit LocalRank(support, max(0,tau_floor-1), proof)
    for selected complete-alternative families or clusters:
        choose supports S and retain only complete in-S families
        run budgeted local rank/DP proof; keep certified floor only
        emit LocalRank(S, floor, proof)
    prove optional forced-union or impossible-family implications
    combine = max(single floors, existing overlap proof,
                  rational fractional packing certificate,
                  other verified rank bounds)
    return Bound(base + combine, proof_refs, evidence_version)
```

A `LocalRank` proof carries support atom representatives, chosen raw evidence IDs, theorem code and specific packing/DP/choice-tree proof. Fractional packing proof carries exact rational numerator/denominator and verifies capacity using *current* atom IDs. A disjoint packing at the root may cease to be disjoint after contractions; a previously valid **absolute** bound remains valid for descendants, but its decomposition into additional cost must not be reused unchanged. Inherit the absolute bound with `max(parent_absolute, newly_computed_absolute)`. Infinity requires a checkable contradiction, not a failed optimization attempt.

## 7. Decomposition, alternative solvers, and parameterized complexity

### 7.1 Exact independent components: when it works

Build an incidence hypergraph over quotient atoms. For each negative i, put **all** endpoints of **all** its necessary alternative families in one hyperedge `U_i` (ignore vacuous negatives). Add other genuine coupling constraints, e.g. cross-component exact NOs if they cannot be handled separately. Compute connected components of the structural incidence hypergraph. For a complete atom model, if each negative's nonvacuous constraints are wholly in one component, and there is no nonseparable admissibility restriction, the structural optimum is additive over components.

**Theorem 4.** Under these conditions, with only equality/disequality restrictions and unrestricted projection semantics, there exists an optimal partition whose blocks stay within components. Its additional optimum is the sum of the component optima. Cross-component disequalities do not impede splitting; within-component disequalities must be retained.

*Proof.* Restrict any feasible partition to each component. Each negative's witnessing choices are confined to its component, so the restriction to that component still satisfies all its obligations. The union of the restrictions is a refinement, hence costs no more; it preserves disequalities. Conversely, concatenate component solutions. Each negative is covered in its component; all components partition the quotient, so cost adds. With full atoms, obligations are exactly the structural predicate. ∎

For partial evidence, the same proof gives exact additivity for the **relaxation only**, hence an additive lower bound on the true optimum. It does not justify excluding cross-component completions of the true sample. When later evidence joins two components, recompute the affected relaxation; keep globally valid past absolute bounds and proofs. If the full structural component solution is confirmed by the external evaluator and the component cost proof matches it, stop. Otherwise, a structural decomposition alone cannot license pruning bounded candidates: an optimal bounded solution may join structurally independent pieces to realize local languages with a different capacity profile. Exact NOs are not monotone structural constraints, and a proof for a projected subsample is not an external query for the actual sample. **Never submit only one component to the external evaluator.**

**Counterexample to decomposition by positive pair families.** For positives `ab,cd,ef` and negative `ε`, the three support groups are disjoint, but a common rejecting block must meet all three; the optimum has rank two. Independently solving the three hit constraints with a singleton choice each and adding zero costs is invalid. The negative vertex connects all those groups in the incidence hypergraph. Likewise, a graph of only currently discovered discrepancy edges is not a complete independence certificate.

For small separators between incidence components, a tree-decomposition DP can track the equality pattern on the bag, disequalities, and witness-responsibility state (including which selected alternatives must share a common block across the bag). A plain graph-connectivity state is not enough. A naive bag state count includes `Bell(w+1)` possible partitions for width w plus responsibility bits, with further growth for obligations crossing the separator. Generic bounded-treewidth CSP methods [L4] motivate this, but an FPT theorem for this particular partition encoding requires an explicit decomposition of the full incidence structure and a proof of the state transitions. Treat as future work rather than deploy an unproved DP.

### 7.2 Formulations to benchmark

**Exact set-partitioning / ILP.** Use the columns in §6.5 with binary `z_B`, not continuous, and full structural coverage. This model is exact for unrestricted partitions and has up to `2^k−1` columns. Singleton columns can be implicit. Add disequalities by banning blocks containing prohibited endpoints. Structural relaxation columns may cover negatives only by necessary conditions; they cannot certify ACCEPT without checking. Branch-and-price [L3] is viable for medium decomposable kernels, but exact pricing is nontrivial and a restricted master optimum is not a global lower bound. In bounded mode the structural model is only a master problem; exact external NOs add no-goods for complete partitions, not monotone cover cuts. Avoid redesigning the external DFA solver.

**SAT / MaxSAT / pseudo-Boolean / ILP with equivalence variables.** On quotient atoms define `e_ab` for each unordered pair (`e_aa=1`). For all triples impose `e_ab ∧ e_bc ⇒ e_ac` and its permutations. These ensure an equivalence relation. For each atom v define `z_v` iff some smaller u has `e_uv=1`; encode both directions (or `z_v≥e_uv` suffices when minimizing only). Then `Σ_v z_v=k−#blocks` exactly, since one least representative per equivalence class contributes zero. Do **not** minimize the number of equal pairs; that counts a size-s block as `s(s−1)/2`, not `s−1`.

To encode full or relaxed obligations without enumerating minimal separators, for each negative i select exactly one anchor atom with variables `a_iv`. Introduce optional selection variables for every alternative of each required family. Require at least one alternative selected in each family, and for every selected alternative A and every possible anchor v enforce `a_iv ∧ select_A ⇒ e_vu` for all u∈A. This forces the same block across all its families. If all families are complete, this is exact for `F∞`; with necessary partial families it is a relaxation. For a candidate Q that is structurally NO, add `∨_{a,b in distinct Q blocks} e_ab`. More compact conflict clauses use deletion cross-products or complete atom alternatives. To exclude only a bounded NO, add the exact no-good `∨_{a<b} (¬e_ab if Q joins a,b else e_ab)`. A proof of unsatisfiability with `Σ z_v ≤ U−1−(n−k)` excludes strict improvement. A MaxSAT soft clause `¬z_v` of unit weight is equivalent to minimizing merge rank; proof logging [L5,L6] is important.

The dense encoding requires Θ(k²) equivalence variables and Θ(k³) triangle implications. For k=100,000, nearly five billion variables are unacceptable. Sparse pair variables with only observed endpoints are **not** automatically an equivalence relation and missing equality variables cannot be fixed false without a dominance proof. Options: lazy triangle separation (with complete verification on each returned assignment), a representative-based label encoding, or restriction to a certified kernel/component. An incomplete SAT encoding is safe for UNSAT if it is a relaxation and objective is encoded correctly, but a satisfying assignment may be spurious. Use proof-logged solving only with a verified translation from original evidence and checkable UNSAT/PB proof; a solver's `OPTIMAL` string or floating gap is not an independent certificate.

**CP with restricted growth strings (RGS).** For k ordered quotient atoms, variables `g_0=0`, `0≤g_i≤1+max_{j<i}g_j`. This defines a unique numbering of every partition. Maximize `1+max g` (k>0). Mandatory unions and disequalities translate to equal/unequal labels; anchor selections impose a common equality. RGS is an excellent universal fallback and small exact comparison oracle. It can be memory-efficient with depth-first traversal but may enumerate Bell(k) leaves. Do not confuse value symmetry breaking with elimination of partitions. CP propagation or CP-SAT performance is an empirical question; a separately checked proof of optimality is still needed.

| Architecture | Strength | Main drawback | Recommended role |
|---|---|---|---|
| Cost-layer merge DAG (previous) | Simple minimum-level stopping; existing verifier | Repeated paths, large frontier, mask and proof overhead | Regression baseline |
| Canonical merge tree / RGS | Unique paths or encodings, simple coverage | Weak conflict guidance unless proven; potentially Bell-sized | Universal reference/fallback |
| EDR-BB (proposed) | Disjoint regions, lazy conflicts, bounded frontier, strong rank proofs | Disequality propagation and dense conflict tails can still dominate | Default exact engine |
| Witness-rank DFS | Exact with complete atoms; compact choice proofs | Alternative product explosion and duplicate rank states | Local bounds, incumbent proposal, exact small kernels |
| Subset DP | Exact joint coverage, simple replay | `3^s 2^h` growth | Small localized supports |
| ILP/set-partitioning, SAT/PB, CP | Strong mature propagation and relaxations | Dense representation, proof translation, external no-goods | Optional kernel backends; ablation |

### 7.3 Complexity limits and parameterization

The paper's Theorem 1 proves NP-completeness even with length-two traces via Vertex Cover. A different simple reduction clarifies why merge-budget parameterization alone is difficult. Let `(U,H,k)` be a Hitting Set instance with nonempty universe and nonempty hyperedges, k≥1. Declare alphabet U, create one positive word listing the distinct vertices of each edge in any fixed order, and take the sole negative `ε`. A rejecting block is exactly a hitting set, because its projection of every positive must be nonempty. If minimum hitting-set cardinality is τ, a block of size τ with singleton leftovers is compatible and costs τ−1; any compatible partition contains a hitting block and costs at least τ−1. Thus optimum equals τ−1, and the merge-budget b=k−1 question is equivalent to Hitting Set with budget k. This is a parameter-preserving reduction from the classical W[2]-complete problem [L7]. Hence general structural partition optimization parameterized by merge cost is W[2]-hard, unless the standard parameterized hierarchy collapses; no generic `f(b)·poly(input)` guarantee should be claimed. This proof concerns unrestricted trace lengths, not the paper's specific length-two reduction. Empty edges correspond to an identical positive and negative and can be handled separately.

An XP algorithm enumerates at most `Σ_{j=0}^b (k choose 2)^j = O((k²+1)^b)` merge sequences, with polynomial raw tests at each partition; an RGS or first-pair traversal removes duplicates. At most 2b current atoms belong to nonsingleton final blocks of a cost-b completion, another XP enumeration bound, not FPT because selecting the atoms costs `k^{2b}`. For bounded conflict width `w`, if every incompatible representative has a sound conflict with ≤w possible pairs and conflicts can be generated in polynomial time, EDR-BB has at most `1+w+…+w^b` equal-branch nodes before budget exhaustion (ignoring deterministic propagation and polynomial per-node work); each branch consumes at least one merge, and the unequal continuation processes at most w alternatives per parent. This is a conditional FPT bound in `(b,w)`. It requires a conclusive structural test and efficient conflict generation; bounded black-box failure can produce a quadratic all-pair conflict and violates the assumption. For Hitting Set with maximum edge size d, the elementary `d^k` branching applies to the transversal subproblem, not automatically the full partition problem.

No algorithm can guarantee polynomial external calls for arbitrary opaque nonmonotone black-box verdicts without further structural information. In a worst case with only exact candidate NOs and no stronger deductions, every cheaper unresolved candidate may need testing. Under unrestricted semantics raw traces determine the answer entirely; calls add independent confirmation or expensive-to-compute evidence, not intrinsically unknowable facts. Do not conflate this observation with permission to replace the external evaluator.

## 8. Lazy constraints and incremental search protocol

Maintain an append-only `EvidenceStore`, a versioned frontier of disjoint region descriptors, and an exact-partition response cache keyed by `(sample_digest, regime_digest, canonical_partition)`. Each version only adds certified constraints. No-good evidence can never make an earlier valid lower bound unsound. An ACCEPT incumbent remains valid while sample/regime are fixed; if either changes, start a new proof session.

The master loop proposes the cheapest representative of a region (or a heuristic/relaxation minimizer in it). Analyze using budgeted trace evidence. If necessary evidence proves a structural conflict, branch without an external call. If no proof decides the representative, submit the complete partition. If raw evidence establishes structural compatibility but the external result is required, still submit that partition unless its cost cannot improve the accepted incumbent. Prefer a quotient-root proposal first after mandatory contractions, including the zero-cost singleton special case. Exact structural analysis is separate from external evaluation; it can generate and validate proofs from the given traces without building any local DFA.

Upon a NO, ingest all usable structural facts, not just those of the failed negative. A newly proved global forced union can be added to the evidence store. **Do not restart the tree**: on each open region, intersect E with the new global equality; if this contradicts D, close that region with the union proof; otherwise rebase its quotient and recompute bounds lazily. Parent disjointness remains because intersecting disjoint sets with the same constraint preserves disjointness. For a lazily generated conflict iterator, retain the original parent-pair descriptors and prefix decisions; evaluate them under the new quotient when resumed. If a pair is already joined or forbidden, the implied branches can be closed with the appropriate proof; never regenerate a different list and silently discard the remaining suffix. Old pruned regions stay pruned under stronger evidence. A new lower cost incumbent only tightens pruning. Persist query attempts and complete receipts; an UNKNOWN is not cached as a definitive verdict.

A useful hybrid is to compute a minimum-cost partition of a small necessary-relaxation kernel and submit it. If accepted and its cost equals the certified global relaxation lower bound, optimality follows immediately. If rejected structurally, use its witnesses to strengthen the relaxation. If bounded NO, exclude precisely that partition. This is analogous to logic-based Benders / constraint generation [L2], with a fixed external evaluation interface and proof-backed cuts. Finite convergence holds if conclusive queries and exact master optimization are available and each unsuccessful proposal adds a valid constraint excluding it. A master objective lower bound cannot be derived from a heuristic feasible solution. Do not run both a global master and a search tree as independent overlapping proof universes unless their respective coverage is explicit; use one as the authoritative proof spine and the other for bounds or proposals.

## 9. Implementation-ready interfaces and pseudocode

### 9.1 Data structures

```python
@dataclass(frozen=True)
class Sample:
    symbols: tuple[str, ...]            # declared order, distinct names
    positives: tuple[tuple[int, ...], ...]
    negatives: tuple[tuple[int, ...], ...]
    digest: str

@dataclass(frozen=True)
class SearchNode:
    node_id: int
    parent_id: int | None
    decisions_ref: int                  # persistent prefix or checkpoint
    equality_delta: tuple[int, int] | None
    disequality_delta: tuple[int, int] | None
    conflict_cursor_ref: int | None     # immutable conflict + prefix index
    inherited_absolute_lb: int
    evidence_version: int
    pending_exact: bool = False

@dataclass(frozen=True)
class Bound:
    absolute_cost: int | float         # integer or +infinity with proof
    proof_ref: int
    evidence_version: int

@dataclass(frozen=True)
class Incumbent:
    blocks_ref: int
    cost: int
    acceptance_ref: int                # genuine external response
    validation_ref: int                # raw check, returned DFA check or trust profile

@dataclass
class SearchState:
    sample: Sample
    regime: object
    evidence: object
    frontier: object                    # DFS frames / disk-backed priority queue
    incumbent: Incumbent | None
    pending: object
    proof_log: object
    query_cache: object
    counters: object
```

Use arrays of 32-bit or 64-bit atom IDs for parent, size and membership; a rollback DSU uses union-by-size without path compression (depth O(log k)), logging each mutation. Global preprocessing may use path compression separately. On DFS backtrack, undo union and disequality changes to a saved checkpoint; representative membership lists can be merged small-to-large, or reconstructed for external materialization. Store original endpoint pairs in immutable proof records so verifier never depends on ephemeral representative labels. A naive DSU union scans all D pairs; optimize via sparse incident lists updated small-to-large, and log changes for rollback. All optimizations need stress tests for rollback consistency. For very large/dense D, switch to compressed conflict clauses, disk storage or a kernel backend; no silent dropping of constraints.

Represent a partition by `block_of_symbol[n]` plus a CSR-style offset array and concatenated members if needed. To emit complete blocks, scan original IDs once, assign deterministic representative order, group in O(n) expected time (or O(n log n) sorting). Store unchanged unused singletons implicitly in search, not as 100,000 Python big integers. Encode dead-region complements by excluded IDs or interval/bitmap formats chosen by density. A single high-index singleton must occupy O(1) words, not Θ(n) bits. Use compact IDs and sparse occurrence postings. Avoid dense atom-by-negative arrays unless measured manageable. Cache only verified evidence and bounded-size hot projections; cache eviction loses performance, not correctness. Persist proof payloads even if derived indices are evicted.

### 9.2 Required APIs

```
initialize_search(sample, evidence) -> SearchState:
    validate declared alphabet, trace IDs, and fixed regime
    initialize append-only ledger and validate supplied evidence
    if identical positive/negative: close root with global equality proof
    handle n=0 under explicit extended contract
    find proved global contractions (budgeted, never guessed)
    apply safe unused-singleton dominance only in appropriate regime
    root = all coarsenings of certified quotient respecting fixed singleton rule
    frontier.push(root, lower = mandatory cost)
    optionally enqueue root and one-block proposals (full original partition)
    return state

compute_lower_bound(search_node, evidence) -> Bound:
    reconstruct node's quotient and D; apply §6.6
    return max(inherited_absolute_lb, newly_proved_absolute_lb), with proof

generate_canonical_children(search_node) -> iterator[SearchNode]:
    # 'canonical' means disjoint first-satisfied-pair regions, not old merge parent.
    derive and record an unsatisfied necessary conflict or generic all-pair split
    for each original pair in deterministic ordered iterator:
        if pair already forbidden in residual: record skip and continue
        if pair already joined in residual: yield entire residual; end iterator
        yield residual plus equality(pair), unless closure contradicts D (log proof)
        residual = residual plus disequality(pair)
    if conflict proved necessary: close residual with conflict proof
    else: retain residual, or exact pending representative as appropriate

prune_with_certificate(search_node, evidence, incumbent) -> Proof | None:
    if E violates D: return CONTRADICTION proof
    if certified structural obligation has no possible completion: return INFEASIBLE proof
    bound = compute_lower_bound(node, evidence)
    if bound is +infinity with proof: return INFEASIBLE proof
    if incumbent exists and bound.absolute_cost >= incumbent.cost:
        return COST_CUTOFF(bound, incumbent.acceptance_ref)
    return None

update_search_after_feedback(response) -> Update:
    validate identity, regime, candidate and completeness
    append raw receipt; normalize using §1.1
    if UNKNOWN: store attempt; leave exact partition unresolved
    if ACCEPT: validate and update incumbent if cheaper
    if PROJECTION_NO: store exact NO; validate named witness for every block
                      ingest other independently justified zero/separation facts
                      queue newly proved global contractions and ledger version bump
    if BOUNDED_NO: store exact NO only, unless independent structural proof supplied
    mark affected frontier indices stale; re-evaluate lazily when visited
    return updated state/version, never delete pending candidates without proof

construct_optimality_certificate() -> Certificate:
    freeze sample/regime digest, ledger, root contractions and dominance proof
    serialize accepted incumbent and disjoint covering proof tree or proof DAG
    include explicit frontier records and certified bounds if interrupted
    do not mark OPTIMAL unless strict-improvement region is entirely closed
    return certificate

verify_optimality_certificate(certificate) -> VerificationResult:
    independent verifier described in §10; no imports from selector
```

`generate_canonical_children` must not return an unchanged residual forever in the already-joined case; it resumes the child search with the conflict marked satisfied and a new conflict selected. In the ordinary fresh parent case, every listed pair is distinct and unsatisfied under E, and successive false prefix constraints cannot force equality, so each emitted child strictly raises cost. Rebased iterators may have satisfied pairs due to newly added global contractions; replay shows progress by cursor consumption or new global facts.

### 9.3 End-to-end scheduler

```
solve(sample, evidence, evaluator, budgets):
    S = initialize_search(sample, evidence)
    while S.frontier not empty and resources remain:
        N = S.frontier.pop_or_resume()
        # transaction: N remains open until prune/children/pending committed
        refresh_global_evidence(N)
        if proof := prune_with_certificate(N, S.evidence, S.incumbent):
            commit_closed(N, proof); continue
        P = full_original_partition(N.E)
        # if P is outside admissible family, no query; use generic strict-coarsening split
        if not admissible(P):
            commit_generic_split(N, exact_leaf='outside-family'); continue
        if evidence proves structural NO(P):
            commit_conflict_split(N, proof); continue
        R = cached_conclusive_response(P)
        if R is None:
            R = evaluator.submit_complete_partition(P)
            update_search_after_feedback(R)
        if R is ACCEPT and validated:
            # P is minimum cost in N, hence region cannot improve it
            commit_closed(N, proof='accepted-minimum-member')
        elif R is PROJECTION_NO with certified conflict:
            commit_conflict_split(N, proof)
        elif R is complete NO for exact P:
            commit_generic_split(N, exact_leaf='exact-NO')
        else:
            # generic split separates exact P from all its strict coarsenings
            commit_generic_split(N, exact_leaf='pending-UNKNOWN')
        schedule bounded retry or new structural analysis of pending leaves fairly
        persist checkpoint and counters
    # Prune any remaining nodes/unknowns by independently checkable final bounds.
    return construct_result_and_certificate(S)
```

`commit_generic_split` uses every allowable distinct current-atom pair. Its residual all-unequal branch contains only E, so exact NO, outside-family, or pending status applies exactly there. If E is a leaf with no allowed pairs, a pending leaf is retried according to policy rather than generating children. Retry must be fair if claiming termination conditional on eventual conclusive replies; if the budget is exhausted, keep the leaf and return INCOMPLETE. For an authenticated ACCEPT but unavailable independent validation, do not close as verified unless the selected trust profile explicitly treats evaluator receipt as an axiom and reports that limitation.

Proof-generating optional proposals outside the current region can be evaluated for incumbent improvement and feedback only; they do not close the current node. Each external attempt is accounted before submission, even if it times out. A new query never uses hidden black-box state or planted metadata.

### 9.4 Global bound and incomplete output

For every unresolved frontier region and pending exact leaf, store a certified absolute lower bound. Closed nodes have either infeasibility proofs or cost floors no lower than their closing incumbent, which is ≥ the current incumbent. If U is the cost of the best accepted incumbent (∞ if none), set

```
L = min(U, min_{open regions or pending leaves} certified_LB(region)).
```

For no open regions, min over empty is infinity. If U is finite, `L≤OPT≤U`; equivalently `n−U ≤ maximum_blocks ≤ n−L`. If U is absent, L is a lower bound only conditional on feasibility. When L=U with finite verified incumbent, return OPTIMAL, even if nominal pending regions exist whose cost bounds exclude improvement. When no incumbent and every region is proved infeasible, return INFEASIBLE. Otherwise return INCOMPLETE with exact unresolved frontier accounting, any accepted incumbent, certified interval (or unknown upper endpoint), query attempt counts, resource limit reason, and checkpoint. A timeout after a candidate has been proposed but before its transaction commits must restore the parent to the frontier. A memory kill may prevent output; record the last atomic checkpoint, not an invented result. Incomplete proof verification itself returns INCOMPLETE, not VERIFIED.

## 10. Optimality, termination, and certificate verification

**Theorem 5 (global correctness).** Under the fixed unrestricted all-partitions model (or bounded variant with its guarded rules), assuming valid initial evidence, all proof rules above are checked, and external conclusive responses are authoritative for the specified sample/regime, a finite accepted incumbent U returned after closing all regions of possible cost <U is optimal. If every region is closed by genuine infeasibility and there is no incumbent, the instance is infeasible. Otherwise any reported interval from §9.4 is sound.

*Proof.* The mandatory quotient and allowed dominance reduction retain at least one optimal completion if any exists. Initially the root covers this reduced universe. A structural conflict split preserves every feasible member by Theorem 2; an all-pair split plus residual partitions the entire region. Propagation intersects with independently justified constraints and cannot remove a feasible member. A local rank bound applies to every completion by §§5–6, and a cutoff removes only members of cost ≥ a verified incumbent. Exact NO removes only the exact candidate, unless a separate structural proof licenses more. All retained regions are disjoint by induction; updates intersect them with common valid constraints and preserve disjointness. Thus every potential strict improvement is either open or correctly excluded. If none remain, no better compatible partition exists. The infeasibility claim uses only infeasibility leaves, not incumbent-dependent exclusions. The same invariant proves the stated lower bound under interruption. ∎

**Termination.** For finite n, each fresh strict coarsening reduces number of atoms, and each disjoint branch makes a new pair decision. A finite RGS fallback can cover every partition. Under finite raw-analysis routines, conclusive/terminating external tests on every queried candidate, and fair processing, the finite tree is exhausted or cut off. There is no unconditional completion guarantee under perpetual UNKNOWN or external timeouts. Optional bound computations must be interruptible so that they do not starve the exact fallback. In unrestricted mathematics with complete raw analysis alone, a structural optimum can always be established, but the operational contract requiring external acceptance may still be incomplete.

### 10.1 Certificate schema (`partition-region-v2`, proposed)

| Record | Required data / independently replayed assertion |
|---|---|
| Header | Version, sample digest incl. original trace order, regime digest, admissible-family identifier, declared objective and trust profile |
| Raw evidence | `(negative_id, positive_id, retained/deleted descriptor)`; exact projections compared by verifier; complete atom family independently recomputed or verified via coverage proof |
| Root | Original IDs, mandatory-union endpoint records, unused-symbol dominance proof when applicable |
| Accepted incumbent | Complete partition, cost, external receipt; direct raw structural compatibility and, if bounded, validation of supplied complete DFAs and bounds |
| Conflict | Proof source and original parent quotient; iterator specification; same-negative dead grouping, deletion support pair, complete alternatives, or proven rank conflict |
| Split | Pair decision or deterministic cursor; both children represented or an independently checkable contradiction; any skipped pair justified |
| Bound | Current atom map, selected obligations, local proofs, rational weights/capacities or existing overlap derivation, inherited bound and incumbent reference |
| Exact NO | Partition/regime/receipt, structural witness proof if projection NO; bounded NO external trust dependency explicitly recorded |
| Pending | Exact candidate or region, current certified floor, reason, checkpoint cursor |
| Footer | Result status, cost interval, record count, final frontier digest and certificate hash |

A bounded exact NO without an independently replayable infeasibility witness cannot be independently *mathematically* certified from a mere status string unless one reruns the documented black box or treats its authenticated verdict as an explicit trust axiom. The paper does not promise a richer bounded failure certificate. Distinguish `VERIFIED_STRUCTURAL`, `VERIFIED_RELATIVE_TO_EVALUATOR`, and `INCOMPLETE_VERIFICATION`; do not promise unconditional independent verification of opaque bounded decisions. Returned bounded success DFAs can be checked by simulating original projected words, checking all transitions are total over their block, initial/final states and the bound. That is witness validation, not replacing the learner.

### 10.2 Independent verifier procedure

1. Parse with strict types; validate sample/partition identity, all IDs, declared coverage, no duplicates, regime and objective. Recompute digest using a versioned encoding. Do not use a producer cache or solver as proof authority.
2. Replay raw equalities, deletion and discrepancy proofs with literal ordered projections; independently reconstruct global DSU closure. Check unused dominance rule conditions. For complete alternatives, absence claims need proof of full enumeration or an equivalent verified necessary superset; merely listing some true atoms fails.
3. Check accepted incumbent and cost. For unrestricted structural compatibility, sparse verification in §11 is exact. Validate external receipt separately. A claimed incumbent with no authentic acceptance cannot certify operational OPTIMAL.
4. Traverse proof tree from root. Reconstruct E,D at each node, validate each conflict derivation, regenerate its exact ordered alternatives (or check a fully covering compact binary split), and ensure no missing child. Recompute each lower-bound primitive and rational arithmetic. Confirm cutoff threshold against an accepted incumbent whose cost is at least the final best cost, or directly against the final incumbent. Exact leaves must match the exact candidate and regime. For a DAG sharing local proofs, validate all references and acyclicity; never equate nodes with same E but different D.
5. Verify frontier closure and stated interval. No absent leaf is implicitly pruned. Recompute aggregate L from open leaves, not just the last visited node. Return VERIFIED only after coverage, proofs and incumbent validation succeed. If verification budget expires, report incomplete with verified prefix only.

Compactness is a goal, not a theorem that every optimality certificate is polynomial. NP-hardness makes short general certificates for lower bounds unlikely without additional structure. Proof logging in PB/SAT [L5,L6] can replace some local tree records, but the independent front end must still verify semantic translation of the constraints and objective. Store binary or JSONL records with bounded sizes, exact rational strings, stable references and checksums; avoid decimal serialization of huge one-hot integers. A verifier must reject missing children, wrong table column IDs, fabricated ACCEPT, invalid rational weights, wrong support quotient, corrupted contraction endpoint, forged sample digest, and changed regime.

## 11. Scalability and complexity engineering

Let n be declared alphabet size, a active symbols, p/q trace counts, T total trace occurrences, k mandatory quotient atoms, e explicit evidence incidences, d stored disequalities, and J number of visited search nodes. Bound all arithmetic in ordinary machine-word IDs (unless explicitly using rational proof arithmetic).

| Operation | Time / storage and caveats |
|---|---|
| Input encode and exact duplicate detection | Expected O(n+T+p+q) time and storage with exact tuple equality/hash table; worst-case adversarial hashing needs mitigation. Preserve IDs. |
| Reverse length-two mandatory DSU | O(n+p+q+r α(n)) expected index/union work; O(n+p+r) words; endpoint proof per successful union. Long-word discovery separately budgeted. |
| General pair atom extraction | Naive O(n²(qT_+ + pT_- + pq)); full atom lists O(pq n²), not acceptable at full scale. Restrict active supports and targeted pairs; full completeness must be proved whenever used. |
| Raw sparse projection compatibility for a complete partition | Expected O(n+T+p+q) time and O(n+T_+ + max_y length(y)) working words, under exact hashing; optional positive-match witnesses and full tables may cost much more. |
| Dead-region ledger | Sparse incidence and containment checks; cost proportional to actual stored supports and comparisons, can grow exponentially in maximal regions. Budget optional discovery and retain proofs. |
| Rollback DSU | O(log k) find with union-by-size; additional disequality checks cost O(d) naively per merge, or incident-list update. DFS snapshots use O(k+d+mutations along current path) plus proof storage. |
| Conflict generation | Cross-product size up to Θ(k²); stream pairs and certify residual coverage; never allocate all pairs for a huge dense conflict. |
| Rank alternative search | Worst-case product of alternative-family sizes, times DSU/disequality work; exponential; localize. |
| Outer search | O(J·(node work + bound work + branch work)) plus external query/evaluation and verification; J exponential and no general improvement over Bell-order leaf counts. Depth can be O(k²) pair decisions for binary continuations; equal descent ≤ k−1. |
| Certificate replay | At least linear in proof bytes and input; raw witness comparison cost, branching regeneration and independent local proofs can dominate; replay large contractions incrementally rather than rebuild entire partition. |

The total size of a one-hot Python integer for symbol i grows as Θ(i) bits. n distinct singleton masks require Θ(n²) bits in aggregate, even if almost all symbols are unused. The previous benchmark calculates ~638 MiB of digit payload at n=100,000 for one set of masks, before object overhead or duplicate root/DSU allocations. Eliminate these, not just their copying. The large-root certificate can use O(r) endpoint records plus O(n) partition IDs; verifier performs one DSU union per certified edge. Verifying each equality may still cost O(length(x)+length(y)) per edge; for adjacent swap or length-two witnesses this is cheap. Large connected contraction components need no all-pairs closure materialization; membership and rank depend on the representative. If the quotient has thousands of blocks, don't build a dense block×trace projection matrix merely to check raw compatibility.

### 11.1 Sparse ordered projection checking (raw analysis and independent verifier only)

The planted checker already implements the core idea; this report adopts and formalizes it rather than claiming novelty. For each positive word, group its occurrences by current `block_of_symbol[a]`, appending original symbol a to that block's temporary list. Only touched blocks appear. Insert each nonempty ordered projected tuple into its block's positive set `U_B_nonempty`; count the number `touch_pos[B]` of positive IDs touching it. Then `ε∈π_B(X)` iff `touch_pos[B]<p`. For each negative, build its touched projections in the same one-pass way. A nonempty projection is separating iff missing from the corresponding positive set; an empty projection is separating iff the block was touched by **all** positives. Maintain `full_touch={B:touch_pos[B]=p}` for p>0; if `len(full_touch)>number_of_touched_blocks_in_full_touch`, there is an untouched block whose empty projection separates. If p=0 and at least one block exists, all negatives are structurally rejected by any block. If n=0 handle explicitly. This avoids iterating over every empty image and preserves repetitions/order.

Proof: every block either contributes the exact nonempty subsequence constructed by the scan or the empty word. The positive sets plus the exact empty-membership criterion represent every positive projection; the algorithm tests all possible separating cases, so it is equivalent to paper Lemma 1. The existential test needs only coverage; full named table generation may require Ω(kq) output indices if explicitly enumerated. The external evaluator's documented table format may indeed be large. **Do not implement an alternative teacher or request undocumented compressed replies.** If it supports references or compact fixed-zero/free-group semantics as documented, consume them as given. Otherwise charge parsing, payload bytes, and black-box time; keep incomplete verdict separate. Query-side complete partition serialization is at least Ω(n) symbols regardless of internal sparse state.

### 11.2 Dense and sparse operating policy

Use sparse support incidences and targeted deletion/adjacent-swap discovery by default. Dense constraints on a small quotient can benefit from bitsets indexed by *local* dense IDs; choose based on measured density, not original index width. Dense constraints at k≈100,000 may not fit; choose a proof-producing subset to derive safe partial bounds, avoid full pair enumeration, and return INCOMPLETE if budget is insufficient. The absence of discovered evidence never proves absence of constraints. Prefer small local joint rank supports and rational packing over global LP/SAT at large k. If a dense mandatory component makes k small, expensive exact optimization becomes more plausible even though original traces remain long. If k stays huge with few constraints, implicit isolated atoms and lazy branching are crucial. Time and memory budgets must include proof construction, I/O, and independent replay, not just search.

## 12. Benchmark audit and reproducible validation

### 12.1 Historical results — supplied artifacts, not new timings

The merged archives contain 33 independent inputs, with 41 solver runs including eight reruns at different limits (`PLANTED_REPORT_FA.md`, `ALL_MEASUREMENTS.csv`, `planted_*/summary.csv`). At the initial 5-second / 1,536 MiB address-space budget, 17/33 solver runs returned OPTIMAL, 10 returned INCOMPLETE, and 6 hit MEMORY_LIMIT. Of the 17 solver-optimal runs, 16 passed the general verifier; the large dense reverse case did not complete that verifier, but a separate specialized raw-A07 root replay subsequently verified it. A 30-second rerun solved `small_count` with general verification, giving 18 distinct solved inputs and 15 remaining unsolved according to the archive. Reference partitions have independent generator-side proofs; they were not given to the solver. Alternate optimal partitions exist (`planted_alternate_optimum.json`); partition identity with the reference is not the optimization criterion.

Selected individual historical measurements (seconds, MiB). `—` means unreported or unavailable, not zero. All cases below have initial 5-second limits except those explicitly marked; the archive's RSS includes process baseline, while the limit is address space. These are single recorded runs, some overlapping, not controlled speedup measurements.

| Case | n / p / q | Reference cost | Solver status; worker s | Peak RSS | Last stage | Independent verification |
|---|---|---:|---|---:|---|---|
| tiny_choice | 6 / 2 / 2 | 2 | OPTIMAL; 0.00048 | 96.90 | digest | VERIFIED; 0.00055 s |
| small_choice | 12 / 4 / 4 | 4 | OPTIMAL; 0.00183 | 96.89 | merge_selection | VERIFIED; 0.00047 s |
| small_count (5 s) | 100 / 100 / 100 | 40 | INCOMPLETE; 5.004 | 100.77 | pair_triple_scan | — |
| small_count (30 s) | 100 / 100 / 100 | 40 | OPTIMAL; 8.769 | 102.26 | oracle_partition | VERIFIED; 0.00875 s |
| medium_choice | 1,000 / 1,000 / 1,000 | 300 | INCOMPLETE; 5.004 | 104.51 | pair_triple_scan | — |
| medium_reverse_dense | 1,000 / 1,000 / 1,000 | 990 | OPTIMAL; 0.0754 | 101.39 | digest | VERIFIED; 0.316 s |
| medium_reverse_pairs | 1,000 / 1,000 / 1,000 | 500 | OPTIMAL; 1.874 | 152.14 | digest | VERIFIED; 0.984 s |
| large_reverse_dense (5 s) | 10,000 / 10,000 / 10,000 | 9,990 | OPTIMAL; 0.612 | 344.95 | digest | General INCOMPLETE; 6.658 s |
| large_reverse_pairs (30 s) | 10,000 / 10,000 / 10,000 | 5,000 | INCOMPLETE; 30.255 | 809.35 | oracle_partition | — |
| large_singleton | 10,000 / 10,000 / 10,000 | 0 | INCOMPLETE; 5.006 | 282.78 | singleton_scan | — |
| huge_reverse_unused | 100,000 / 10,000 / 10,000 | 10,000 | MEMORY_LIMIT; 0.615 | 1,222.49 | sparse_contractions | — |
| huge_sparse_small | 100,000 / 10 / 10 | 1 | MEMORY_LIMIT; 0.664 | 1,222.02 | sparse_contractions | — |
| huge_singleton_active | 100,000 / 10,000 / 10,000 | 0 | MEMORY_LIMIT; 0.831 | 1,222.31 | sparse_contractions | — |
| extra_interleaved | 200 / 200 / 200 | 60 | INCOMPLETE; 5.001 | 106.40 | pair_triple_scan | — |
| extra_long_1024 | 30 / 20 / 20 | 10 | OPTIMAL; 2.078 | 98.89 | oracle_partition | VERIFIED; 0.0730 s |

Three 100,000-symbol reruns at 3,072 MiB / 10 seconds got past initial mask construction, but remained incomplete: `huge_reverse_unused` at oracle (~2,304 MiB RSS), `huge_sparse_small` at oracle (~2,032 MiB), and `huge_singleton_active` at singleton scan (~2,045 MiB). Long and choice families with 100,000 active symbols also hit the original memory limit. The `extra_imbalanced_positive` and `extra_imbalanced_negative` cases (100 versus 10,000 traces) stopped at oracle; long-word costs and trace imbalance matter independently of alphabet size.

**Interpretation by family.** Reverse instances expose mandatory pair contractions. Count instances need two singleton deletion witnesses, potentially from different positives. Long instances include a shared suffix around a swap: the general proof is unchanged, but the length-two index misses those words. Choice instances require disjunctive constraints rather than mandatory pairs, so localized rank and conflict branching are the meaningful algorithmic test. Mixed instances can reject the first reverse-only quotient, so the fallback must search coarsenings. Singleton and unused cases mainly test representation and sparse raw checking; their solved performance is not evidence for general NP-hard instances. Interleaved and imbalanced traces reveal hidden repeated-scan costs. All new proposals should receive **input.json only**, not the family name, reference partition, generator seed/spec or reference proof. Use these metadata after solving for analysis only.

The large dense case (`planted_results/large_reverse_dense/measurement.json`) shows why phase separation matters: input 0.113 s, contractions 0.154 s, one completed local quotient-teacher call 0.288 s for 200,000 projections, certificate assembly 0.051 s, merge search skipped. The saved JSON result was 92,228,343 bytes. `root_replay_results.json` reports a specialized A07/no-search-record replay of 0.187 s plus 1.580 s loading, while the original general verifier timed out. This is evidence of certificate-format/replay overhead, not combinatorial difficulty. In `large_reverse_pairs` at 30 seconds, 5,000 quotient blocks imply 100 million block/trace images if fully built; the saved stage log shows 29.773 s in the unfinished local oracle. Its completed-call counter is zero, which must not be mistaken for zero attempted calls. The new instrumentation records attempts before evaluation. None of these archived teacher timings are measurements of the actual external evaluator.

The earlier scale package (`SCALE_REPORT.md`) separately reports the 1,000-symbol, total-10,000-trace stress case: old 30-second run spent 2.571 s in singleton analysis and 27.429 s in pair scan; new sparse reverse pass found 986 mandatory unions, quotient 14 blocks, one local query, no merge search. Recorded default run 0.109 s producer and 0.319 s independent verifier; 30-second-budget run 0.120 s producer and 0.337 s verifier. These are historical single runs, not a same-host controlled experiment. `RESEARCH_STATUS.md` also records HDFS-1024 and holdout (29 symbols, 27 blocks each) and eight-vertex path (16 symbols, 12 blocks). The HDFS holdout needed a triple rather than two disjoint pairs and all 406 cost-one alternatives were excluded by witnesses. Retain them as non-planted regression cases.

### 12.2 New observations in this research session

A small stand-alone reference check, `03_reference_checks.py` (companion to this report), used a restricted-growth enumerator and direct literal erasing projections, independent of the previous solver/teacher. It tested 100 seeded random corpora per n=1,…,6 (600 total; positive and negative lists of lengths 0–3, words of lengths 0–5, including repetitions, duplicates, empty words and overlap). It compared sparse and literal projection compatibility on every partition: **27,800 comparisons**, no discrepancy. A reference region traversal explicitly filtered the enumerated candidate universe by first-true-pair decisions, verifying disjointness and coverage at each split and comparing the minimum compatible cost against full enumeration: **3,705 visited reference nodes**, no disagreement. It uses enumeration intentionally to validate the rule, not as a scalable implementation of EDR-BB. All **203** six-symbol partitions satisfied the fractional packing inequality for the three overlapping supports in §6.3; a direct test also found optimum 2 for the stated trace example. These are finite sanity checks, not a replacement for the proofs.

Separate raw-only probes, using original `input.json`, indexed length-two reverse words, ordinary integer-ID DSU and sparse ordered projection checking. Results below are **structural proof ingredients only**; no external evaluator was contacted, no external incumbent was certified, no new full solver/certificate replay was benchmarked. The probes used the original trace lists and no reference labels/partitions. A successful quotient plus forced-union count is mathematically enough for the unrestricted structural optimum, if the recorded unions are independently verified; an operational result still requires external confirmation. Timing values are single-process observations, rounded; peak RSS is cumulative across cases, not isolated per-case memory. Encoding excludes JSON load. Raw checking is charged separately from contraction discovery.

| Raw-only probe | Successful mandatory unions | Quotient blocks | Structurally compatible? | Encode s | Contractions s | Raw check s | Cumulative peak RSS MiB |
|---|---:|---:|---|---:|---:|---:|---:|
| huge_reverse_unused | 10,000 | 90,000 | yes | 0.03464 | 0.02984 | 0.02302 | 128.14 |
| huge_sparse_small | 1 | 99,999 | yes | 0.05924 | 0.00765 | 0.00006 | 132.91 |
| large_reverse_pairs | 5,000 | 5,000 | yes | 0.02557 | 0.00629 | 0.02979 | 145.43 |
| large_reverse_dense | 9,990 | 10 | yes | 0.00980 | 0.00911 | 0.01196 | 145.43 |
| huge_singleton_active | 0 | 100,000 | yes | 0.02392 | 0.00901 | 0.31704 | 179.47 |

The probe demonstrates that the raw representation and compatibility check can be inexpensive at these particular scales. It does **not** imply an end-to-end speedup factor, especially if the external evaluator still constructs explicit per-block tables or times out. Certificate assembly/verification timings for the proposed engine and its external evaluation time are not measured. Do not compare the raw-only probe time directly against the historical end-to-end worker time as a solver speedup. The 100,000-symbol choice, count, and long cases require additional algorithm implementation and validation. No benchmark artifact was modified.

### 12.3 Reproduction and experimental protocol

From a clean working directory:

```sh
mkdir -p audit/bench audit/scale
unzip -q 'partition-part1-planted-benchmark(1).zip' -d audit/bench
unzip -q 'partition-part2-planted-benchmark(1).zip' -d audit/bench
unzip -q 'partition-scale-improved(3).zip' -d audit/scale
python -B 03_reference_checks.py
python -B 03_reference_checks.py audit/bench
# archived baseline, local simulator only; no external-system changes
cd audit/scale
python -B staged.py evidence/synthetic_10000_traces_1000_symbols.json > fresh.json
python -B verify.py evidence/synthetic_10000_traces_1000_symbols.json fresh.json
python -B scale_regression.py
```

The companion script requires Python 3.10+ and uses `resource` for Linux RSS reporting. Its independent exhaustive check can also be reproduced from this report: enumerate RGS partitions, for each ordered pair of words literally filter by block, evaluate the quantifiers in §1, and compare the first-satisfied-pair split's children as subsets of that finite universe. For the sparse probes, use the algorithm in §11.1 and exact length-two reverse lookup in §3.2. The script has no external evaluator adapter and does not claim to implement the proposed full search.

For a controlled study after implementation, pin the exact code revisions and runtime; record machine, OS, CPU, memory, Python version, hash seed, dataset hashes, sample ordering and external evaluator/version/regime. Use fresh processes for solver and independent verifier and equal wall, CPU, memory, query and proof-size budgets. Repeat at least five times per affordable input; report median/IQR and all failures, not only successes. Separate cold/warm external caches when evaluator supports a documented reset; otherwise record this as a confounder. Run one process at a time. Do not infer exact worst-case complexity from a benchmark.

| Variant | Purpose |
|---|---|
| Literal RGS exhaustive enumeration, n≤8 (extend to 10 where feasible) | Gold optimum and infeasibility, independent raw compatibility |
| Pinned `partition_feedback_final` staged exact solver | Original algorithm baseline; use same evaluator adapter or compare structural-only mode separately |
| Improved scale archive | Isolate prior sparse-contraction optimization |
| New sparse data structures + previous search logic | Isolate representation gain before changing branching |
| EDR-BB, base rank only | Measure branch-family representation and duplicate suppression |
| EDR-BB + previous greedy/deletion bounds | Isolate established deductions |
| EDR-BB + localized rank + fractional packing | Test new bound tightness, overhead and proof cost |
| Optional full-atom/rank, CP/PB, ILP kernel backends | Compare exact architectures under equal evidence and limits |
| Feedback ablations (none / zero regions / full usable tables, same raw budget) | Quantify incremental information and avoided external calls |

For structural-only comparison, use direct raw semantics on all variants or the unchanged historical simulator. For the operational experiment, every variant uses the actual documented evaluator via the same adapter and identical query accounting; no historical simulator result is labeled external ACCEPT. If a baseline cannot consume external responses without semantic changes, report that incompatibility and limit its comparison to the structural regime. Run the paper's bounded examples as a separate guarded-mode suite, not as equivalent unrestricted benchmarks.

### 12.4 Metrics and correctness gates

Record phase-exclusive elapsed seconds (nested instrumentation must not double count), plus total wall time:

- input encoding / raw trace analysis / global contractions and discovery;
- search time excluding raw analysis, oracle waiting and certificate construction; separate bound computation and conflict generation subcounters;
- black-box query attempts, conclusive ACCEPTs, projection NOs, bounded NOs, UNKNOWNs, retries, unique complete candidates, cache hits, and proposals rejected locally before submission;
- external evaluation wall time, transport/serialization and table ingestion separately where measurable; do not estimate unknown internal evaluator phases;
- peak solver RSS, independent verifier RSS, evidence/DSU/frontier bytes, payload and proof bytes; record RLIMIT_AS or cgroup cap separately;
- certificate construction/serialization time, independent verification load and replay time, verification result/trust profile;
- final incumbent cost, certified lower cost bound, integer gap, max-block interval, status, explored region count, excluded-by-proof counts by rule, and saved checkpoint validity.

Count mathematical exclusions and skipped paid queries separately. A family of Bell-many partitions may never have been queried by the baseline anyway. Measure the new lower bound's value `L_new−L_old` on the *same* root or region/evidence snapshot, proof construction time, and reduction in visited nodes/calls. A predicted diagnostic benefit is a heuristic, not actual measured savings. Compare query count at matched final gap and matched verification status, not a partial solution against a completed one. Use the independent reference optimum only in post-run assessment. Acceptance and optimality must be checked by verifier, not by reference-partition equality.

Required validation cases: all samples from prior reports' tests; original `audit.exhaustive_samples()` (2,529 corpora in scale report); n=1…8 random plus exhaustive short words; empty alphabet as explicit extension; no positives/negatives; duplicate IDs and identical oppositely labeled words; repeated symbols and late occurrence-order swaps; sparse/large unused declarations; huge active alphabets, long traces and huge contraction components; choice and overlapping disjunctions; dense/decomposable/nondecomposable constraints; interleaving; multiple equivalent optima. Compare every generated branch against exhaustive compatible completions on small n, not just final objective. Check local rank and fractional bounds against exhaustive node optima with random partial evidence and branch disequalities; check full rank equivalence and decomposition conditions. Property-test incremental evidence replay and checkpoints with arbitrary insertion order, late global unions, timeouts before and after each atomic state transition, incomplete tables, duplicate/late responses, and corrupted proof records. Run exhaustive bounded DFA examples only as documented external conformance tests or using the paper's existing reference outputs; do not create a replacement learner.

## 13. Counterexample checklist and integration recommendations

| Unsound shortcut | Counterexample / precise failure |
|---|---|
| NO prunes every coarsening | `X={ab,cd}`, `Y={ε}`: `ab|cd` fails, `ac|b|d` is optimum, and `abcd` succeeds. |
| Only merges with immediate new negative coverage | `X={ab,cd,ef}`, `Y={ε}`: every first pair fails to cover the negative; optimum cost 2. |
| Merge all symbols of a deletion set | `X={ab}`, `Y={ε}`: either singleton rejects. A set-valued obligation is a choice. |
| Count one merge per negative | `X={aabc}`, `Y={abac,baac}`: a single `ab` merge suffices for both. |
| Sum all overlapping local costs | `X={abcdef}`, `Y={bacdef,bacdfe}`: both can be satisfied by `ab`; summing one per negative is unsound. Use a proved packing. |
| Drop missing alternatives / truncate to support | `X={ab}`, `Y={ε}`, only atom `a` discovered: requiring `a` excludes the true alternative `b`. |
| Combine zeros from different negatives | `X={ε}`, `Y={a,b}`: singleton partition succeeds; each block has a zero for the other negative. |
| Union dead regions with same positive witness | `X={ab}`, `Y={ba}`: unary projections agree on both, but their union separates. |
| Use a zero row as fixed zero | Free unrestricted group admits both 0 and 1 by paper equation (23). |
| Combine canonical parent and unrestricted conflict branch without proof | §4.1 unique optimum `abc` lost by dead grouping `ab|c`. |
| Assume bounded monotonicity | Paper Example 5: singleton even-length languages fit within two states each, the merged block cannot. |
| Treat relaxed optimum or local heuristic as external ACCEPT | Paper Example 11: two structurally optimal partitions have different bounded feasibility. |
| Treat one-hot masks as constant-size / omit unused declared symbols in query | 100,000-symbol historical memory failures; incomplete partition is not a legal proposal. |
| Treat interrupted oracle/verification as a proof | UNKNOWN may hide the unique better candidate. Keep its exact leaf and certified bound. |

### 13.1 Recommended module integration and implementation order

**Raw analysis module:** provide immutable original-ID evidence records; exact projection comparison, sparse counts/positions, budgeted singleton deletion discovery, adjacent-swap and count controls. Expose a completeness flag only with a replayable proof of alternative coverage. Expose both partial necessary obligations and sufficient separating witnesses, not one ambiguous atom list. Provide compact support descriptors and touched quotient atom indices. No solver should infer absence of a missing atom from preprocessing timeouts.

**Feedback interpretation module:** map paper semantics to `NormalizedResponse`. Independently authenticate sample/partition/regime identity, table column order, zero/free group semantics and named witnesses. Export `DeadRegion`, `Separating`, `ExactNo` or `Accepted`; preserve raw receipts. Report unknown/unavailable tables explicitly. Do not demand modifications to the external automata system. The exact search consumes the facts without needing learner internals.

**Candidate ranking/diagnostic module:** offer ranked conflicts and complete candidate proposals, estimated query latency, information gain, or incumbent potential. It may choose among certified conflicts and ordering of child pairs; it must not prune, change necessary disjunctions, or hide unresolved children. Diagnostic queries may be outside the active region but only add valid global evidence/incumbents. Record their actual costs separately.

**Exact search module (this assignment):** own region coverage, rollback DSU, branch disequalities, evidence versions, certified lower bounds, frontier, incumbents and exact proof spine. The solver never sees the planted reference answer. Suggested new files within `implementation/partition_feedback_final/`: `region_search.py`, `sparse_partition.py`, `rank_bounds.py`, `evidence_store.py`, `external_adapter.py`, `certificate_v2.py`. Keep historical solver untouched as comparison. Maintain a compatibility reader for `partition-v1` or explicitly separate versions. Do not modify the external evaluator.

**Independent verifier:** separate code path and small proof kernel with direct raw checks; implement root DSU replay first, then split/coverage replay, then local bound proofs and rational packing. For bounded black-box NOs document trust assumptions and allow external receipt replay if supported. A shared schema is fine; avoid importing selector heuristics or its projection caches.

Implementation sequence and acceptance gates:

1. Sparse ID representation and endpoint contraction proof. Gate: no O(n²) singleton masks, raw checker agrees with exhaustive literal oracle and handles 100,000 symbols with 10,000+ traces on sparse fixtures.
2. External adapter and query/pending accounting. Gate: paper examples, missing success tables, projection versus bounded failure, wrong IDs and incomplete responses all handled correctly; no undocumented query.
3. Region branching and rollback proof tree, with only base rank. Gate: exhaustive optimum match, every child and residual checked, checkpoint/restart invariant holds.
4. Existing witness packings and disjoint local proofs; add localized rank and fractional packing. Gate: every claimed floor ≤ true exhaustive optimum, rational proof mutation rejected, overlapping example strictly strengthens the old primitive combination.
5. Optional kernel/master backends and diagnostics. Gate: no unverified solver gap used as proof, no loss of candidate coverage, same external query policy in baseline comparisons.
6. Run controlled planted and non-planted suite, record gaps and full phase metrics. Only after independent verifier completes should the operational result be labeled certified.

### 13.2 Open problems and limitations

- The proposed localized-rank/fractional packing bound is mathematically proved here, but its empirical tightness, certificate size and selection overhead beyond the strict example are not yet established. Discovering profitable supports and generating compact local certificates without solving many NP-hard subproblems remains open.
- A disjoint search region avoids duplicate partition *coverage*, not necessarily duplicate proof work or an exponential number of decision nodes. Dense disequality propagation can be costly. A good proof-preserving compressed representation for large cross-product conflicts is an engineering/research problem.
- Complete decomposition from raw trace atoms can require huge preprocessing. A sparse evidence graph is enough for lower-bound decomposition but not for exact structural factorization. Efficient separator DP with shared witness responsibilities remains unproved.
- External transport, actual feedback serialization and capacity configuration are unspecified beyond the paper. External calls may dominate after selector improvements. The benchmark archive measured a local projection simulator. No end-to-end speed or actual external query-count claim is made for EDR-BB.
- Independently verifying opaque bounded NO without a proof or rerunning the external evaluator is not possible from the provided interface alone. The unrestricted target avoids that specific issue, but operational acceptance provenance remains necessary.
- The supplied paper's proof and examples are the model authority; earlier reports use an unrestricted abstraction. Do not claim physical architecture recovery or identification of the underlying automata solely from optimal sample compatibility.
- The prototype checks here validate the two proposed mathematical mechanisms on small enumerated cases and sparse raw representation on selected large cases. The full scheduler, localized LP/DP proof generation, incremental rebasing, external adapter and certificate-v2 verifier are design deliverables, not implemented or benchmarked production components in this assignment.

## 14. Attribution and verifiable references

### Project sources

- **[P]** *Passive Compositional Automata Learning from Global Logs*, supplied `main (1)(2).pdf`, 31 pp. Key references: Lemmas 1–2, Theorem 1, Proposition 1–3, Examples 5/11/15, §5.1 (equation 23), §5.2, Appendix B. The manuscript marks its own evaluation as TODO.
- **[R1]** `independent_partition_selection_report(2).md`, *Independent algorithmic analysis: partition selection from traces*. Deletion witnesses, joint block-cover DP, zero-region closure, canonical parent and diagnostics.
- **[R2]** `Alphabet partition research report(2).md`, *Choosing an optimal alphabet partition from trace evidence*. Discrepancy atoms, witness-rank theorem, path-preserving branching and table semantics.
- **[G]** [Pinned repository directory](https://github.com/Mahdi-Jadidi/passive-automata-learning/tree/7c90eb59561bd25ec4fdca5ac08b0e5d60d17fd/implementation/partition_feedback_final/). Relevant files: `README.md`, `model.py`, `hybrid.py`, `staged.py`, `search.py`, `verify.py`, `RESEARCH_STATUS.md`. Retrieved file blob IDs: `model.py` `ea78e9300efd121ae79441cc46c7062dfee5af9f`; `search.py` `c61b84623ded7325fc7ff154db131d09115120e7`; `staged.py` `51f044a907f7d0d9e4cc3d70b4cca89ac5c5b7a0`; `verify.py` `dd376cae9ba57d75a69d9a1b48c9e2337ce8a40b`; `hybrid.py` `2b02597633f3fda707144029385f6aef09d8cede`.
- **[B]** Supplied `partition-scale-improved(3).zip` and both planted benchmark ZIPs, especially `SCALE_REPORT.md`, `PLANTED_REPORT_FA.md`, `ALL_MEASUREMENTS.csv`, `planted_*/summary.csv`, per-case `measurement.json`, `representation_probe.json`, `root_replay_results.json`, `planted.py`, `benchmark_planted.py` and `root_replay.py`.

### Academic literature and proof tools

- **[L1]** R. M. Karp, “Reducibility Among Combinatorial Problems,” 1972. [DOI 10.1007/978-1-4684-2001-2_9](https://doi.org/10.1007/978-1-4684-2001-2_9). Background NP-completeness; the specific partition reduction is in [P].
- **[L2]** J. N. Hooker and G. Ottosson, “Logic-based Benders decomposition,” *Mathematical Programming* 96, 33–60 (2003). [DOI 10.1007/s10107-003-0375-9](https://doi.org/10.1007/s10107-003-0375-9). Motivation for a master relaxation and proof-backed feedback cuts; not a theorem that the proposed cuts are fast.
- **[L3]** C. Barnhart, E. L. Johnson, G. L. Nemhauser, M. W. P. Savelsbergh and P. H. Vance, “Branch-and-Price: Column Generation for Solving Huge Integer Programs,” *Operations Research* 46(3), 316–329 (1998). [DOI 10.1287/opre.46.3.316](https://doi.org/10.1287/opre.46.3.316). For pairwise same/different branching see also D. M. Ryan and B. A. Foster, “An Integer Programming Approach to Scheduling,” in *Computer Scheduling of Public Transport*, 269–280 (1981), and the [SCIP Ryan/Foster example](https://scipopt.org/scip/doc-8.0.2/html/BINPACKING_BRANCHING.php).
- **[L4]** E. C. Freuder, “Complexity of K-Tree Structured Constraint Satisfaction Problems,” AAAI 1990, 4–9. [Publication entry](https://mlanthology.org/aaai/1990/freuder1990aaai-complexity/). Motivation for decomposition under explicit incidence structure; not a proof of a partition-specific treewidth result.
- **[L5]** J. Berg, B. Bogaerts, J. Nordström, A. Oertel, T. Paxian, and T. Vandesande, “Certifying Without Loss of Generality Reasoning in Solution-Improving Maximum Satisfiability,” CP 2024. [DOI 10.4230/LIPIcs.CP.2024.4](https://doi.org/10.4230/LIPIcs.CP.2024.4).
- **[L6]** W. Koops et al., “Practically Feasible Proof Logging for Pseudo-Boolean Optimization,” CP 2025. [DOI 10.4230/LIPIcs.CP.2025.21](https://doi.org/10.4230/LIPIcs.CP.2025.21); [VeriPB](https://veripb.org/). Proof-logging backends are optional; semantic translation and external receipts still require validation.
- **[L7]** “On Structural Parameterizations of Hitting Set: Hitting Paths in Graphs Using 2-SAT,” [arXiv:1507.05890](https://arxiv.org/abs/1507.05890). Establishes context for the known W[2]-completeness of Hitting Set parameterized by solution size. See also M. Cygan et al., *Parameterized Algorithms*, Springer, 2015, for standard parameterized complexity background.

### Contribution classification

Established in the paper/prior reports: unrestricted projection criterion, NP-completeness, unary/binary discrepancy sufficiency, minimal-separator condition, mandatory merges, witness hitting and rank optimization, canonical parent, same-negative table closure, path-preserving crossing merges, and prior greedy overlap bounds. Established generic literature: pairwise equality/disequality branching, branch-and-price, Benders, hitting-set complexity and proof-logging tools.

Proposed extensions for this project, proved in this report: evidence-directed disjoint first-satisfied-pair search regions with explicit residual coverage; disequality-aware witness rank; localized joint rank floors and fractional restricted-rank packing including a strict example; parameter-preserving Hitting Set reduction for the unrestricted merge budget; guarded incremental region rebasing and global gap accounting. These are candidate contributions to the project, not a claim that no equivalent mathematical technique exists in the literature. A systematic novelty review, full implementation, and controlled evaluation remain required.

**Final recommendation:** prioritize representation and certificate fixes, then the disjoint region proof spine, then localized joint rank and fractional packing. Use external ACCEPT to establish the verified operational incumbent and proof-backed exclusions to establish its optimality. This architecture provides a correctness path even if sophisticated bounds are weak, and a truthful incomplete result if resources or the external evaluator prevent certification.
