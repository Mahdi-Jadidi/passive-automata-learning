# 01 — Sparse raw-trace analysis for exact alphabet partition selection

**Research assignment 01 · 24 November 2026**  
**Status:** mathematical design with a measured reference prototype of the central fast path; not a production solver or an external-oracle implementation.  
**Proposed module name:** Sparse Deletion-Join and Implicit Discrepancy Analysis (SDJ-IDA).

## Executive summary

The highest-return change is to stop representing a symbol, a partition block, or the complement of a small deletion as an alphabet-wide Python integer. The second change is to replace the Cartesian raw-trace scan by an **indexed join of single-symbol (or current-component) deletion signatures**. Unlike the current short-reversal special case, the join discovers mandatory contractions from arbitrarily long words, repeated symbols, interleavings and distinct positive witnesses. A signature is only a retrieval key; literal projection equality is the proof.

For comparisons that cannot be solved by this join, represent the discrepancy graph *implicitly* by occurrence ranks. A linear scan recovers all count discrepancies, detects order disagreements, finds the support of all minimal atoms, and supplies a witness of an order discrepancy. A greedy ordered-set procedure computes an inclusion-maximal equal-projection region in near-linear time in the compared word lengths without constructing the potentially quadratic graph. Combine these regions, singleton deletions, and disjoint weighted supports into reusable, independently replayable constraints; generate further evidence only when the search requests it.

The central fast path was prototyped during this assignment. With only the supplied `input.json` as input, it discovered 10,000 mandatory unions and a structurally compatible 90,000-block quotient on **both** 100,000-symbol / 20,000-trace target cases. It also obtained the correct structural optimum on seven further targeted fixtures. Its contraction edge certificates were checked by literal erasure and graph traversal; the returned quotient was independently checked using the supplied benchmark's sparse compatibility checker. All nine structural optima match the recorded references. No external black-box calls were made. In the intended workflow, send the complete quotient to the unchanged external service for final acceptance; a local structural check is not an external response.

The unrestricted optimization remains NP-complete (main paper, Theorem 1). There is no claim that sparse discovery is complete for all global constraints or that all 100,000-symbol instances can be solved efficiently. The single-deletion join is complete for that particular witness class when fully exhausted; budgeted results are merely sound. Dense or exponentially large evidence families are kept implicit or generated lazily.

## 1. Problem, semantics and scope

Let the declared alphabet be a finite nonempty set `Σ`, with a stable mapping to integer IDs `0..n-1`. The sample comprises positive words `x_j`, `0 ≤ j < p`, and negative words `y_i`, `0 ≤ i < q`. Store ordered token sequences; identical words within one class may share storage, but each original index remains addressable. Opposite-label duplicates are inconsistent. The paper assumes disjoint sample sets and nonempty alphabet; the implementation also handles duplicate IDs and an empty alphabet. Define `π_U(w)` as literal erasure of all tokens outside `U`, preserving repetitions and order, and `del_T(w)=π_(Σ\T)(w)`.

A complete partition `P` consists of disjoint nonempty blocks with union `Σ`. Define

\[
 Z(i,j,U) \iff \pi_U(y_i)=\pi_U(x_j),\quad
 R_i(B)\iff \forall j\;\neg Z(i,j,B).
\]

Structural compatibility is `C∞(P) ⇔ ∀i ∃B∈P R_i(B)`. The objective is `min c(P)=n-|P|`, equivalent to maximizing block count. The same block must defeat *all* positive words for a given negative, but different negatives may use different blocks. A block may defeat multiple negatives. In this report the admissible family is all complete partitions; if an external run restricts that family, objective-preserving reductions must separately preserve admissibility.

**Established result (paper Lemma 1):** `C∞` is exactly feasibility with arbitrary finite local DFA state counts. A finite language of positive projections can always be recognized by a complete DFA. This is an existence argument, not a proposal to build or modify any DFA. Equality on a larger block implies equality on its subsets; hence `C∞` is upward monotone under coarsening. The main paper also considers independent finite bounds `m(B)` and a supplied admissible family. Under bounds, `C∞` is only necessary, and coarsening need not preserve feasibility (paper Example 5). All raw *necessary* constraints below remain valid with bounds, but structural acceptance, optimization-preserving unused/inert-symbol reduction and monotone acceptance inference require the unrestricted regime (and appropriate admissible family). Do not apply them to bounded `FAIL`.

### 1.1 Actual external interface, as specified by the paper

Source: supplied `main (1).pdf`, *Passive Compositional Automata Learning from Global Logs*, §§2, 4.2–4.5, 5.1–5.5, Figure 2 and Appendix B.

- Input to selection is the labeled global sample. A proposal is one **complete partition**. On projection failure, §5.1 returns the partition, ordered negative indices, one failing negative, one matching positive per block for that negative, and an unrestricted rejection table `R_B^∞` for every block. These may be passed by reference. Bit `1` denotes rejection, `0` acceptance.
- The unrestricted table is defined by Eq. (23): a negative projection matching a positive forces zero; equal negative projections have equal bits. Fixed zeros and groups of identical projections specify every row, without listing all `2^k` choices for `k` free groups. A fixed-zero unrestricted column is exactly a dead block for that negative. A single zero entry in one row does not establish deadness. Free groups encode eligibility to reject, not a compulsory rejection or a selected responsibility.
- On unrestricted success the paper returns `P` and complete local DFA witnesses. With state bounds, projection success may proceed to exact `CheckPartition(D,P,m)`, returning a joint row and DFA witnesses on success or `FAIL` on failure. The paper explicitly leaves richer bounded-failure interfaces open. An arbitrary bounded fixed-zero column is not in general a raw projection equality. A branch-reduced bounded relation is not an unrestricted base table.
- The paper does not define a wire protocol, literal `ACCEPT`/`NO` JSON values, timeout schema, or extra explanation query. These names are integration-level normalized statuses from the assignment. Obtain a documented adapter for the actual service. Keep `PROJECTION_NO`, `BOUNDED_NO`, `INCOMPLETE`, and `ACCEPT` separate. A timeout, truncated response, invalid schema, missing table or ambiguous completeness must never manufacture a complete `NO` or a fixed-zero fact. If a partial response contains a separately replayable raw equality, it may be retained as that equality only, not as a verdict.

The local Python `model.ProjectionOracle` is **not the external interface**: it takes `(partition,purpose)` using integer masks and returns a dictionary with `status`, `blocks`, `tables`, `failed`; its tables contain `zeros` as `[negative_id,positive_id]` and `free` as groups of negative IDs. It also returns tables on ACCEPT and caches individual block rows. It does not return local DFAs or bounded feasibility. The analysis module must not access its cache, row methods, teacher internals, hidden responsibilities, or planted metadata. Our optional raw structural checker uses the original words independently; it is not a replacement service. Under the assignment's operational contract every reported final answer should be confirmed by an external complete-partition ACCEPT. With an indefinitely inconclusive external service one can still prove structural optimality, but cannot claim service acceptance.

### 1.2 Degenerate cases

Validate declarations, tokens, IDs, and ordering. For nonempty `Σ`: no negatives implies singleton optimal; no positives implies singleton structurally compatible; exact opposite-label word equality refutes every partition, even with bounds. Otherwise the one-block partition is structurally feasible. With empty `Σ` (extension beyond the paper), the empty partition is compatible iff there are no negatives. Certificates: original word IDs for a conflict; declared size and class sizes for degeneracy. Full-word deduplication is sound within a label class; dedup must not renumber the external columns. Counterexample to prefix-label inference: positive `ab` need not imply positive `a`. Counterexample to using one-block success under bounds: one-state DFAs cannot distinguish two differently labeled words. These checks are complete for the stated degeneracies, not for bounded feasibility.

## 2. Audit of prior work and code

### 2.1 Previous reports (both read)

`independent_partition_selection_report.md` (§§Analyze traces, Select partition after NO) establishes zero-region inheritance, complement-deletion hitting obligations, the per-negative hitting-set floor, a joint block-cover subset DP, and same-negative region coverage. Its exhaustive discovery enumerates retained subsets for each cross-label pair. Its proposed packing floor is sound but incomplete unless all deletion witnesses and exact transversals are available. Its empty-positive statement needs the paper's nonempty alphabet convention. It correctly separates query-derived evidence from raw information and refuses to prune all coarsenings of a NO.

`Alphabet partition research report.md` (§§2–4, 7) already proves the unary/binary atom characterization, the witness-rank theorem, singleton-deletion mandatory classes and safe branch ordering. It explicitly treats partial atom lists as insufficient necessity evidence, establishes exact rank optimization with full alternatives, and discusses duplicate IDs and unused symbols. It scans all cross-label word pairs and all stable symbol pairs inside each comparison. Its full atom list and exact rank search can be huge. Its finite-rank compression theorem for *table-history model existence* does not license dropping arbitrary occurrences from the actual input. The prior experiments are reported small exhaustive checks, not evidence of large-scale performance.

The main paper itself already states the small-projection lemma (Lemma 2), necessary structural conditions (Prop. 2), adjacent-swap forced pairs, NP-completeness, and reference search. **None of these is a novelty claim here.** New candidate contributions relative to those reports are the complete sparse deletion-signature join, extension to quotient components, occurrence-rank implicit graph operations, support/weighted certificates with inexpensive complete verification, and a resource-bounded evidence API. Their mathematical proofs are given below; publication-level originality has not been established.

### 2.2 Pinned GitHub versus uploaded package

Pinned source: [repository directory at 7c90eb59561bd25ec4fdca5ac08b0e5d60d17fd](https://github.com/Mahdi-Jadidi/passive-automata-learning/tree/7c90eb59561bd25ec4fdca5ac08b0e5d60d17fd/implementation/partition_feedback_final). The directory and relevant source file inventories were accessed through GitHub; the pinned `model.py` (blob `ea78e9300efd121ae79441cc46c7062dfee5af9f`) has `deletion_candidates` and `analyze` but **no `reverse_contractions`**. Pinned `staged.py` (blob `51f044a907f7d0d9e4cc3d70b4cca89ac5c5b7a0`) is the earlier hybrid. The subsequently uploaded `partition-scale-improved(1).zip` contains that optimization. Do not attribute its measurements to the exact pinned commit. The complete local code paths of the supplied enhanced package and benchmark copy were inspected; the pinned repository review focused on the partition module, not every unrelated repository file.

| Source / symbol | Existing behavior | Limitation and action |
|---|---|---|
| `sample.py:read_sample` | Validates string tokens and declaration; encodes ordered tuples; positional original IDs | Keep API validation; use packed arrays and explicit alias map; avoid dense membership masks. |
| `model.py:analyze` | A01 duplicate conflict, A02 empty-alphabet failure, A03 unused, A04 duplicate metadata, A05 empty words, A06 empty classes | Preserve these semantic checks, not their mask encoding. |
| `model.py:deletion_candidates` | A08 count-different deletion candidate; A09 builds stable-symbol discrepancy graph, greedy independent-set orders; validates equality | Count-different deletion alone need not work; quadratic pair enumeration, repeated rescans, and cross-label Cartesian scan in `analyze`. Replace with implicit operations and lazy scheduling. |
| `model.py:analyze` A07 | Groups zero regions by negative, repeatedly scans all current blocks for complements covered by a region, contracts required blocks | Correct but rescans root and regions; use deletion-to-component mapping and proof-carrying incremental queue. |
| Enhanced `model.py:reverse_contractions` | Indexes positive two-distinct-symbol words, scans reversals in original negative order, union-by-size/path compression; two A09 equalities and A07 per successful union | Only length two, even when a long context is identical. Allocates singleton masks, component masks and dense complement witnesses. Replace with compact IDs and generalized join. |
| Enhanced `staged.py:solve` | Builds singleton root, then sparse probe for default hybrid (not explicit query limit/custom oracle/targeted/order-insensitive/preprocessing-disabled route). ACCEPT gives contracted-root proof; NO falls back to raw/general feedback route | Still allocates mask root before pass. Full quotient check through local `ProjectionOracle` enumerates blocks × traces; broad scans remain if sparse root insufficient. Keep external query accounting and route semantics. |
| `hybrid.py:singleton_analysis` | Positive count sets for every symbol, scans every symbol per positive and at most every symbol per negative | Replace by sparse `(symbol,count)` index plus implicit zero / universal occurrence. |
| `hybrid.py:pair_scan`, `discrepancy_families`, `rank_answer` | Exact cost-one, two-pair/triple cases, optional full atom rank; heuristic disjoint-pair incumbent | Dense pair/triple enumeration and failure arrays. Make these small-instance baselines; do not apply singleton-only `bit_length()-1` extraction to nonsingleton quotient blocks. |
| `search.py:Evidence`, `supports`, `lower_bound`, `select` | Per-negative maximal known zero regions, eligible rejection regions, hitting supports, lower bounds, exact feedback search | Useful consumer architecture. Introduce symbolic retained/deleted sets and group-aware indexes; avoid re-scanning every block for sparse complement witnesses. |
| `verify.py:Replay`, `verify` | Independent raw equality, contraction, coverage/rank/branch replay; modified bit-membership helper in scale ZIP | Dense masks and repeated partition reconstruction. New versioned sparse proof reader and graph/DSU replay are needed. |
| Benchmark `planted.py:compatibility`, `root_replay.py` | Sparse structural compatibility check and restricted independent A07 replay | Already implements important sparse ideas. `root_replay` is not general `verify.py`. Reuse checker concept, not planted construction or expected groups. |

The uploaded `SCALE_REPORT.md` documents 986 unions on the 1,000-symbol / 10,000-total-trace fixture, 14 blocks, 1,972 raw equalities, one local teacher query, no merge records, and independent verification. Reported default producer 0.109 s, peak RSS 104.020 MiB, verification 0.319 s. The prior failed 30 s run used 2.571 s singleton analysis and 27.429 s pair scanning. These are archived single runs, not same-host controlled speedups. The supplied planted benchmark also proposes generalized deletion hashing, sparse quotient checking and compressed proof formats; this report supplies a concrete join, proofs, implementation and new measurements rather than claiming those ideas were absent from the handoff.

### 2.3 Why “sparse contractions” exhausted memory

On the recorded CPython 3.13.5 build an int has 30-bit limbs stored in 4 bytes. `1<<a` requires approximately `24+4(floor(a/30)+1)` bytes. The supplied `representation_probe.json` measured 669,266,680 bytes (638.26 MiB) for one collection of 100,000 singleton integers. The enhanced `staged.py` creates one such collection, and `reverse_contractions` creates another `masks` collection; complements, sorted tuples, facts, union masks, temporary values and Python objects add further memory. Thus a nominally sparse union-find pass still uses Θ(n²) bits even before processing many traces. Its parent and size arrays are not the primary problem.

A07 stores two almost-full complements per union and successive component masks. For `r` successful unions, complement storage alone can be Θ(r n) bits. At n=100,000, masks also exceed CPython's recorded default 4,300 decimal-digit JSON conversion limit. Changing that limit does not fix asymptotics. `large_reverse_dense` has an archived 92,228,343-byte solver JSON and original verifier timeout; the restricted diagnostic replay later verified the contraction-only proof in approximately 0.18–0.19 s of computation (plus 1.48–1.58 s load). The full verifier's status remains INCOMPLETE. The other major bottleneck is the complete quotient oracle with `k(p+q)` images and repeated word scans, followed by `n×p` singleton checks and broad pair/triple scans. None is required to discover the easy raw facts.

## 3. Sparse representation and basic exact indexes

Notation for complexity: `L=Σ_w |w|`, `D=Σ_w |supp(w)|≤L`, `N=p+q`, `Lmax=max |w|`; primed values refer to deduplicated words. Count bytes of variable-length token strings separately. Bounds use a word-RAM with IDs, lengths and offsets fitting machine words; hash-table bounds are expected, unless explicitly stated. In Python use actual integers with no alphabet-wide shifts. Worst-case hash collisions affect runtime, not validity.

Store the original encoded trace array with CSR-style offsets, original IDs / alias groups, and for each distinct trace a sparse mapping `symbol -> (count, positions_slice)`. Inverted postings `symbol -> [(trace_id,count,positions_ref)]` need only nonzero incidences. Optionally store class-specific `(symbol,count>0) -> posting list` and `positive_presence_count[symbol]`. Use packed unsigned 32-bit IDs where valid, 64-bit offsets for large L, and arrays for parent/size. Immutable input has a digest and stable schema version. Build in expected O(n+N+L) time and O(n+N+L) words, or sort records deterministically in O((N+L)log(N+L)+n) time. Empty trace and empty projection are different from missing data.

### Rule R1 — sparse singleton separation (complete)

**Premise and result.** For symbol a, positive possible counts are `C_a={count_a(x_j):j}`. A negative is separated on `{a}` iff its count is not in `C_a`. Construct sets of nonzero counts only, and `U+={a: positive_presence_count[a]=p}` when p>0. Then count zero is absent from `C_a` iff a is in `U+`. For every negative, test its present symbols against the nonzero count sets; also test whether `U+\supp(y)` is nonempty. This gives exactly all singleton-eligible negatives and can emit one separating singleton for each without scanning all n symbols per trace.

**Proof.** A unary ordered word is completely specified by its count. A positive contributes count zero precisely when it lacks the symbol. For the missing-universal test, scan U+ until a missing symbol appears or the scan ends: at most `|supp(y)|+1` membership tests. If p=0, use the degenerate rule. If q=0, stop. For any singleton witness, all coarsenings contain a separating block, so that negative can be omitted from *unrestricted structural search obligations*, but its ID and raw word remain available. For bounded search this means only structural coverage, not global bounded feasibility.

**Certificate.** `(i,a,count_a(y_i),positive-count-index-version)` with a verifier rebuilding the count index from raw positives, or replaying every positive. Missing-universal certificate names a and checks occurrence in every positive. **Counterexamples:** only considering present negative symbols misses `x=ab,y=b` on `{a}`. Only considering maximum counts misses positives `a,aaa`, negative `aa`. Equal counts on every symbol do not imply full equality (`aba,aab`). Expected time O(n+N+L); no dense count vector. A list of all separating singleton/negative combinations can itself be large; emit just one witness or an iterator.

### Rule R2 — sparse structural partition check (complete for fixed P)

**Premise.** A complete partition is represented by an owner array `owner[a]=block_id`. Scan each positive once, append each original token to its block's local ordered sequence, index only nonempty projected words by block and retain first original positive ID. Count how many positive words touch each block. Let V be blocks touched by all positives. For each negative, construct its sparse local sequences, test present sequences against the index, then check for any missing block in V. No positive can have empty projection in V. If no test succeeds, the negative fails on all blocks.

**Proof.** For present blocks, dictionary membership is exactly positive projection equality. For absent blocks, the negative projection is ε, which is absent among positives exactly on V. These exhaust the blocks. The same early-stop argument as R1 bounds the missing-universal scan. Expected O(n+N+L) time and space for one fixed P, with exact tuple/string equality, no full tables. Certificate of structural success: complete partition, one block per negative, and verifier rebuilding its own index. Certificate of failure: negative ID plus per-block match, optionally encoded lazily by nonempty postings and a representative positive missing that block. One may find a missing positive by scanning IDs until a gap in the sorted presence postings; charge the actual search. Counterexample to dropping empty projections: positive `a`, negative `ε` is separated on `{a}`. Counterexample to relabeling local tokens by block ID: `ab` and `ba` become identical if a and b share a block; keep the original tokens within each local word.

R2 is known in the supplied `planted.py` checker, not a new theorem claimed here. Integrate it as a raw evidence service, not as a change to the external oracle. Explicit external tables may still contain kq columns, so the overall workflow can be I/O-bound even with sparse raw preprocessing.

## 4. Complete sparse single-deletion discovery

### Rule R3 — deletion signatures and three-way cross-label join (new candidate algorithm)

For current partition Q, define `erase_g(w)` as removal of **all** occurrences whose owner is g, preserving every other original token. At the singleton root this is ordinary single-symbol deletion. A group g is touched by w iff it has at least one token in w. Define a required group for negative i:

\[
 g\in M_i(Q)\iff \exists j:\operatorname{erase}_g(x_j)=\operatorname{erase}_g(y_i).
\]

**Theorem 1 (complete sparse join).** If no opposite-label words are identical, all pairs `(i,g)` satisfying the displayed predicate can be discovered by the following three joins, each using signatures of *touched* groups only: (i) positive and negative deletion signatures agree on `(g, deleted_word)`; (ii) a negative deletion signature matches a positive full word (group absent from positive); (iii) a positive deletion signature matches a negative full word (group absent from negative). Keep one exact positive witness per `(i,g)`. There is no need to enumerate absent groups in every word or every positive–negative pair.

**Proof.** If g is absent from both words, equality after erasure would mean a full opposite-label duplicate, excluded by premise. If present in both, case (i) covers it. If present on exactly one side, case (ii) or (iii) covers it. Conversely every emitted result is verified by literal erasure and hence satisfies the predicate. Identical original words within one class may use a representative with aliases; a positive witness retains its original ID. This proves completeness for this witness class, not completeness for all mandatory co-memberships. For example, `x=ab, y=ba` is detected by two deletions; `x=abc, y=cba` has no singleton deletion equality and yet needs some merge.

**Fingerprints in O(L) aggregate work per pass.** For a word w of length m, compute prefix polynomial hashes `H[t+1]=(H[t]*b+token[t]+1) mod M` and powers `b^r mod M`. A contiguous interval `[l,r)` has hash `H[r]-H[l]*b^(r-l)` modulo M. Concatenate kept gaps by `h←h*b^gap_length+gap_hash`. For each touched group use its sorted positions to concatenate gaps between deletions. The total number of gaps is at most `m+#touched_groups`; therefore all deletion fingerprints of a word take O(m) time and O(m) scratch space. Fingerprint includes projected length; optional second modulus improves performance against accidental collisions. A signature match only proposes a comparison, and every certificate uses exact ordered equality. Even an adversarial constant fingerprint remains logically sound and complete if all collisions are resolved and the join is exhausted. It can make runtime much worse. The prototype uses one fixed 64-bit modular hash and exact replay, not a probabilistic correctness guarantee. This is a fingerprint-filter application of the established Karp–Rabin technique [4], not a claim of a new hashing primitive.

```
DELETION_JOIN(index, owner, budget):
    # A pass uses a frozen owner snapshot, raw tokens are unchanged.
    F = multimap from full signature -> positive representative IDs
    D = multimap from (group, deletion signature) -> positive representative IDs
    I = multimap from deletion signature -> (group, positive representative ID)
    for positive representative x,j:
        budget.debit(...); build prefix hashes and group positions
        F[signature(x)].append(j)
        for g,sig in all_touched_deletion_signatures(x,owner):
            D[g,sig].append(j); I[sig].append((g,j))
    for negative representative y,i in scheduled order:
        found = map(group -> verified positive ID)
        for g,sig in all_touched_deletion_signatures(y,owner):
            for j in chain(D[g,sig], F[sig]):
                if literal_equal_after_group_delete(x_j,y,g,owner):
                    found[g]=j; break
        for g,j in I[signature(y)]:
            if g not in touched(y) and g not in found:
                if literal_equal_after_group_delete(x_j,y,g,owner): found[g]=j
        emit verified (i,g,j) in found with alias IDs accessible
    return EXHAUSTED only if all entries and collision buckets processed
```

A full-word hash lookup that collides with a word touching g is harmless if literal erasure validates; the proof is always the direct predicate. For a rigorous deterministic alternative, sort deletion signatures and compare actual erased strings in collision buckets; explicit strings may be expensive. For long shared contexts, a suffix-array/LCP structure over raw words could compare kept gaps, but the prototype does not implement it. Keep processing candidates until an exact match is found, not merely the first hash match. Optimize large buckets by exact equivalence classes of deleted words, keeping one representative per `(g,exact projected word)`, not one per unverified hash. Use external sorting or shard by signature if necessary; combine shards only after exact checks. Prioritize the shorter/rarer side when choosing join orientation; orientation changes scheduling, never logical claims.

**Certificate.** For a singleton: `(i,j,a)` and rule `DELETE_EQUAL` with universe implicit. Verifier checks IDs, a∈Σ, then compares literal erasures. For a quotient group: reference a snapshot component representative, membership digest/version and the verified current DSU component; independently recover membership from earlier proof edges (or explicit sparse set). Store an immutable deletion descriptor, never a live mutable DSU reference. **Counterexample to a stronger rule:** equal deletion hashes do not prove equality; and deleting a single *occurrence* rather than every occurrence of a symbol is invalid (`aba` and `ab`: removing the last a from only one trace is not the same operation).

**Complexity.** Let J be the number of candidate bucket entries actually examined, and V the sum of raw comparison lengths for verified or failed equality checks. Build O(n+N'+L') expected time and O(n+N'+L') space, then O(L'+J+V) expected work including negative signatures and bucket probes. Alias expansion is optional and charged by output size. With one witness per negative/group, worst-case output can still be Ω(qn); the join does not promise O(L) total in all corpora. In adversarial collision buckets or genuinely broad matches, J and V can grow far beyond input size. Full-word indexing may avoid many comparisons when there is no shared signature; long equal projected strings still cost replay time. The index can be streamed by shards and released after proof forest extraction. For a bounded run, count actual inspected bucket entries and tokens, not only number of compared word pairs.

### Rule R4 — mandatory contractions from different witnesses (established inference, new extraction)

**Theorem 2.** Suppose every feasible partition coarsens Q. For each negative i, every structurally feasible coarsening has one block containing **all** current groups in `M_i(Q)`. Consequently, union them in a spanning star (or any spanning tree), retaining one proof edge per successful union. Different groups may have different positive witnesses. This remains necessary for bounded feasibility.

**Proof.** If a separating block misses g, it is contained in Σ\g and therefore inherits the corresponding matching positive equality. Contradiction. All groups that are required for the same negative must be in that negative's separating block. If each is a component of the already-mandatory Q, intersecting it means containing it. Transitive closure across negatives gives the necessary quotient. Successful unions r imply every feasible partition has cost ≥r. Certificate edges establish a forest, and graph connectivity independently determines the root. If the root is structurally compatible, its cost r equals this lower bound and is the exact unrestricted optimum. External ACCEPT of the complete root additionally certifies the workflow's required acceptance. If the root is incompatible, this does not refute coarsenings. This is a complete optimality test for the special case of a feasible mandatory root, not a complete global optimizer.

**Counterexamples.** Positives `ab,cd`, negative ε force a separating block to intersect both supports, but no particular cross-pair is mandatory. Positives `ab`, negative ε yield singleton alternative a or b, not a mandatory merge. Requirements from *different* negatives cannot simply be joined: positive ε, negatives `a,b` are handled by separate singleton blocks. Same-positive witness is not required: positives `a,b`, negative `ab` force both a and b via different witnesses. A single singleton deletion witness forces a symbol into a separating block, not a merger by itself.

**Certificate format:** `ForcedEdge(i, a, j_a, b, j_b)` for singleton evidence (5 IDs, O(1) machine words). For group evidence use two prior component references and two raw deletion witness IDs. Replayer starts singleton, checks each prior component at the recorded epoch, independently erases both groups from the negative and respective positives, then unions (or verifies equality if redundant). Store only successful edges in the spanning forest and optional other evidence separately. Cost proof r is independently recovered, not trusted from producer. For singleton edges the verifier can build an adjacency list and compute components in O(n+r), avoiding even DSU dependence. For general group steps use DSU with current membership maps; never trust producer-provided masks. The exact proof-check cost includes all raw erasure lengths (or a separately verified index).

### Rule R5 — closure under component deletions (new candidate extension)

After any mandatory union, a previously non-singleton deletion T may fall wholly inside one new component g. Equality on Σ\T implies equality on Σ\g. Thus an existing witness becomes a required current component without a new pair comparison. Additionally rerun the R3 signature join grouping occurrence positions by current owner. This finds equalities after removing whole components that no earlier singleton deletion exposes. A full round with no unions reaches a fixpoint for the R3/R4 rule relative to its current component partition, not for all logical consequences. All operations preserve mandatory status by induction. Each successful round lowers component count, so at most n−1 successful rounds. A naive fully repeated pass can cost O(n(n+N+L+J+V)) with per-round terms; use lazy scheduling to avoid this in practice.

Example: `Σ={a,b,c}`, positive `ab`, negative `ba` force a,b. Add positive `c`, negative `abc` (same sample). For negative `abc`, deleting c matches `ab`; deleting the component `{a,b}` matches `c`; hence `{a,b}` and c must merge. No singleton-deletion rule on `abc` forces a or b individually. The full singleton pass may obtain other valid evidence, but the quotient join is the direct justification of this step. A budget that stops after the first pass must not call its root the full singleton/component closure. Counterexample to quotient substitution: replacing original tokens by component labels before hashing would falsely equate `ab` and `ba`; group deletion changes only the membership filter, not the retained tokens.

Incremental design: store, for each retained sparse deletion witness, the set of DSU components meeting its deletion. Maintain component-to-witness incidence; merge smaller component into larger and update touched incidences, or mark dirty and recompute when requested. If the set becomes singleton, enqueue its negative for mandatory propagation. On a union of A,B, deletion fingerprints for untouched groups in a word remain unchanged; new fingerprints for A∪B are required only for words touching A or B. Postings enumerate these words. Use snapshot versions and tombstones for old entries. A complete incremental index must process both sides' affected signatures and absent-side joins, including earlier full-word lookups; otherwise declare the pass PARTIAL and run a fresh frozen-epoch join when completeness is needed. Small-to-large membership movement alone is O(L log n) over a union sequence, but rehashing whole words, candidate joins and witness verification have additional costs; no global near-linear claim for incremental closure.

An explicit incompleteness example for the fixpoint: positive `abc`, negatives `bca,cab`. For the first negative only deletion of a gives equality; for the second only deletion of c gives equality. R4 makes no union, so R5 stops immediately. The only compatible partitions are `ac|b` and `abc`: a and c are globally forced together. The two negatives have alternative atom families `{ab,ac}` and `{ac,bc}` respectively; picking different pair alternatives joins all three, and choosing the common pair joins a,c. This shows why a fixpoint of single-group witnesses must not be advertised as all mandatory relations. A complete test of global necessity can search all structural bipartitions keeping two designated symbols apart, as the previous report notes; it is exponential and outside the default preprocessing budget.

## 5. Implicit discrepancy graphs and maximal equal-projection regions

### Rule R6 — occurrence-rank representation of all minimal atoms (established characterization, new representation)

For a cross-label pair x,y let `D={a:count_x(a)≠count_y(a)}`. Call other *present* symbols stable. Remove D from both words. Name each remaining occurrence `(a,t)` with t its rank among occurrences of a. Stable counts guarantee the same set of named occurrences. If `z[0..m-1]` is the sequence of positions in filtered y of the occurrence labels read in filtered x order, z is a permutation of `0..m-1`. Record `sym[k]`, the symbol of the kth occurrence in filtered x. Two occurrences of one symbol never form an inversion because their occurrence ranks are ordered in both words.

**Theorem 3 (implicit exact discrepancy predicate).** For any `B⊆Σ`, `π_B(x)≠π_B(y)` iff either `B∩D≠∅` or the subsequence of z retaining positions k with `sym[k]∈B` has an inversion. Equivalently the minimal discrepancy atoms are the singletons in D and all distinct stable symbol pairs that label an inversion. The representation stores no edge matrix.

**Proof.** A count difference survives retaining the symbol. If no count-different symbol is retained, x and y have the same labeled occurrences in the projection. Their orders coincide iff their y positions in x order are strictly increasing. An inversion gives a binary projection discrepancy and cannot involve two occurrences of the same symbol. Conversely a discrepancy of the restricted stable order entails an inversion, whose two labels are present in B. All singletons in D are minimal. Each discrepant stable pair is minimal because its individual counts agree. No other minimal set can exist, proving the characterization. This is a constructive version of main paper Lemma 2 and the earlier report's occurrence-order proof, not a new structural characterization.

**Operations.** Build D by sparse count comparison, and construct z by walking x with per-symbol occurrence cursors into y position arrays (raw y positions, instead of compressed ranks, also work for order tests). For any chosen B, test B∩D, then find an inversion by scanning z and maintaining the maximum seen rank and its source index; if max > current rank, emit those occurrence labels. The scan is linear, or use sorted position lists / a k-way merge when B is small. `pair_atom(a,b)` can compare the two projected words from their positions in O(count_x(a)+count_x(b)+count_y(a)+count_y(b)); use actual counts, no dense pair cache. `iter_atoms()` may enumerate inversion occurrences using merge-sort-based reporting in O(m log m+I) time (I is occurrence inversion count) and deduplicate symbol pairs. This may report a huge number of duplicate occurrence inversions, so use only when requested and capped; an alternative stable-symbol pair iterator compares ordered postings directly. Do not mistake I for the number of distinct atom edges. In particular, there may be Θ(n²) distinct atoms even for words of length n. For a full reversal with one occurrence per symbol, store x and the reverse rank sequence, not all n(n−1)/2 edges.

**Certificate.** A unary atom names `(i,j,a)` and verified counts; an order atom names `(i,j,a,b,t_a,t_b)` and opposite relative order of those ranked occurrences plus equal individual counts if claiming minimality. For a nonminimal discrepancy witness the order discrepancy still proves inequality when counts are equal for retained symbols; direct two-symbol comparison is the simplest universal checker. Complete implicit descriptor verification rebuilds D and z from original traces; a projected equality certificate can simply replay literal erasure without trusting the descriptor. **Counterexamples:** `aba,aab` have the same counts and order of first appearances but a different rank-2 a position relative to b. An incomplete atom list cannot be used as the only allowable alternatives: `ab` versus ε has two unary alternatives, and finding `{a}` does not force a or invalidate `{b}`. A discrepancy with one positive does not by itself separate a negative from all positives.

Time and space for one descriptor O(|x|+|y|) expected with sparse counters; no scan of n needed. Do not store descriptors for all pq pairs: retain a byte-bounded LRU of hot comparisons, with source IDs and proof references surviving eviction. When a descriptor is complete, its implicit query method is exact for *any* B, even though its enumerated atom list is empty. Mark these two notions separately (`predicate_complete`, `enumeration_exhausted`).

### Rule R7 — exact discrepancy support in linear time (new candidate extraction)

Let G be the symbols that label any inversion in z. Compute `prefix_max[k]=max(z[0:k])` and `suffix_min[k]=min(z[k+1:])`, using −∞ and +∞ for empty ranges. Occurrence k participates in some inversion exactly when `prefix_max[k]>z[k]` or `z[k]>suffix_min[k]`. Add its symbol to G. Set `T=D∪G`. No edge enumeration is needed. Use a forward and backward pass, with O(m) array or O(m) descriptor scratch; no need to retain the extrema after construction.

**Theorem 4.** T is exactly the union of minimal discrepancy atoms for the pair. Deleting T makes x,y equal. If D is empty but G nonempty, a separating block must contain at least two distinct members of G. Otherwise, if T nonempty, a separating block must contain at least one member of T. An empty T proves full-word equality.

**Proof.** The two extrema tests characterize precisely whether an occurrence participates in an inversion. By Theorem 3 the participating stable symbols are exactly the endpoints of binary atoms. All unary atoms lie in D; there are no other minimal atoms. Removing T removes every atom, hence leaves equal projections. Every distinguishing block contains a minimal atom, so the stated cardinality requirement follows. It is exact as a support statement and a sound necessary cardinality relaxation, not sufficient to guarantee distinction. Example: `abc` vs `bca` gives G={a,b,c}; `{b,c}` meets the cardinality demand but is not a discrepant pair. If D≠∅, demanding two from T is unsound: positive `a`, negative `aa` is separated by a singleton. The raw deletion T may not be minimal; e.g. `ab,ba` has T={a,b} but either singleton deletion suffices.

**Certificate.** `WeightedSupport(i,j,T,demand)` with `demand=1` or `2`; verify support inclusion by rebuilding the descriptor or checking `del_T(x)=del_T(y)` plus additional no-cross-inversion condition for demand 2. Specifically for demand 2 require D empty and *all inversion endpoints* contained in T, not merely equality on Σ\T. Equality outside T alone guarantees one hit, not two: `ab` vs `ba`, T={a} is a deletion witness but a separating block contains only one member of T. The complete endpoint scan is a compact check of this stronger premise. A certificate may store a superset of true support, weakening the bound but remaining valid. For the clique-reversal special case, to assert all pairs in G are discrepant, provide one ranked occurrence of each member whose order reverses between words, plus the support check; then every pair has a witnessed inversion. This is a sufficient, not necessary, clique recognition test for repeated symbols. For all-distinct permutations it recognizes reverse-order cliques exactly. A general clique claim requires more work; never assume support is a clique.

### Rule R8 — inclusion-maximal equal-projection region without materializing edges

For a pair, valid retained sets must avoid D and be independent in the implicit stable-symbol discrepancy graph. Include all symbols absent from both words without listing them. Use the following greedy method for an inclusion-maximal region. The symbol order may be deterministic ID order, rarity, high count, or a seeded order; the result remains certified regardless of order.

Maintain an ordered set of occurrence positions in filtered x already retained, with their associated y ranks. Initially empty. For each stable present symbol a, inspect all its occurrence positions k in increasing x order. For each k locate predecessor and successor of k among previously retained positions; require `z[pred]<z[k]<z[succ]` when they exist. If all checks pass, insert all occurrences of a; otherwise reject a and record one violated neighbor as a blocking pair. Check the entire symbol before inserting any of its positions. An order-statistic Fenwick tree over positions supports predecessor/successor by prefix count plus select-by-rank, and updates in O(log m); a balanced ordered tree is an alternative. Python's `bisect` with list insertion is not worst-case logarithmic, so use a Fenwick implementation or a native tree.

```
MAX_EQUAL_REGION(x,y,order):
    D,z,sym,pos = BUILD_IMPLICIT_DESCRIPTOR(x,y)
    F = Fenwick(m)                   # 1 at retained x occurrence positions
    dropped = D.copy(); blockers = {}
    for a in order(stable_present_symbols):
        bad = None
        for k in pos[a]:
            p = predecessor(F,k); s = successor(F,k)
            if p exists and z[p] > z[k]: bad = (p,k); break
            if s exists and z[k] > z[s]: bad = (k,s); break
        if bad is None:
            for k in pos[a]: F.add(k,1)
        else: dropped.add(a); blockers[a] = occurrence_labels(bad)
    return Complement(dropped), blockers
```

**Theorem 5.** The resulting retained set U=Σ\dropped has equal projections and is inclusion-maximal among equal-projection regions for the pair. **Proof.** Inductively the previously retained sequence has increasing y ranks. For a new symbol its own occurrence ranks are increasing. The predecessor/successor inequalities place every new occurrence in the correct gap relative to all old ones, so simultaneous insertion preserves increasing order. If an inequality fails, the named occurrence of an already retained symbol forms an inversion with a; that retained symbol is never removed. D symbols always disagree in count. At the end every excluded symbol has a persistent obstruction to adding it. By Theorem 3 equality holds on U and no excluded symbol can be added while maintaining it. Downward closure makes this equivalent to inclusion maximality.

**Certificate.** Original i,j, sparse deletion T; verify equality of del_T and, for every a∈T, either count discrepancy or an atom `{a,b}` with b∉T. This independently proves maximality without reconstructing the greedy algorithm. If the consumer only needs a valid deletion witness, omit the maximality claims and blockers. Complexity O(|x|+|y|+m log(max(2,m))) time and O(|x|+|y|) space for one greedy region, including blocker checks (verify stored ranks via position index). Repeat under a small budget for alternative regions; every result is maximal, not necessarily maximum cardinality, and the collection may be incomplete. **Counterexample:** x=`abc`, y=`bca` has star discrepancy graph centered at a. Greedy a-first yields retained `{a}`; greedy b-first yields `{b,c}`. Both maximal, only the latter maximum cardinality. A naive strategy of simply deleting D fails on `ab,ba`; count agreement does not ensure word equality.

**Exact enumeration when demanded.** Minimal deletion sets are D plus minimal vertex covers of the stable graph; maximal equal regions correspond to maximal independent sets. Full enumeration can be exponentially large: x=`a1 b1 a2 b2 ... ar br`, y=`b1 a1 b2 a2 ... br ar`, with distinct symbols, has r disjoint discrepancy edges and 2^r maximal equal regions. Thus no algorithm can explicitly emit every maximal region in time polynomial in input alone. For a small graph one can materialize edges and use an established maximal-independent-set enumerator (Tsukiyama et al. [5]). For a large implicit graph, use budgeted exact branch enumeration on the stable symbols, with equality tests and maximality verification at leaves; worst case exponential. A lazy exact iterator must cover both include and exclude possibilities or use a proven maximal-set enumeration rule. Repeated greedy runs alone are not a complete enumerator. The first region and exact support already provide sound obligations; postpone enumeration until exact search needs more.

## 6. Hypergraph obligations and objective lower bounds

### Rule R9 — deletion hypergraph (established, sparse encoding)

For each negative i, store deletion witnesses `H_i={T: ∃j del_T(x_j)=del_T(y_i)}` discovered so far. Every separating block for i must intersect every T∈H_i. This is the prior reports' hitting theorem; the proof is exactly projection inheritance. If H_i contains ∅, full-word equality proves infeasibility. A candidate with no block hitting all H_i is structurally impossible. With all witnesses, hitting is exact: if B fails to distinguish some positive, T=Σ\B is a disjoint witness. With partial H_i, it is necessary only. Store only inclusion-minimal known T for each i for this predicate; if T1⊆T2, hitting T1 implies hitting T2. Keep source facts if referenced by an existing proof. Never intersect deletion sets or union retained regions to manufacture an equality. For x=`ab`, y=`ba` each singleton is equal, but their union is not. Do not combine obligations from different negatives into one required block.

On current mandatory root Q, map each sparse T to `E_Q(T)={g:g∩T≠∅}`. If T is retained as an explicit region U instead, `E_Q(T)` consists of components not contained in U; computing it may be expensive for small retained U. This equivalence follows from disjoint partition membership. Each completion's separating block contains a set of current components hitting every edge of this hypergraph. A singleton edge propagates via R4; an empty edge proves a conflict. Keep large edges as complement descriptors or predicates instead of materializing a dense list. Hyperedges sharing vertices do not imply every endpoint is co-blocked. For positives `ab,bc`, negative ε, the hitting edges overlap and `{b}` suffices: summing one merge per edge is wrong. Exact hitting-set optimization can be NP-hard even for ε negatives (positive supports are arbitrary); do not require it during preprocessing.

**Certificate:** one original witness ID and its compact deletion descriptor per edge, with any component projection replayed from the certified root. For objective floors use a verified disjoint subfamily or a feasible dual, never a heuristic transversal as a lower bound. A proposed hitting set is an upper bound on transversal size, not proof of a lower bound.

### Rule R10 — weighted support packing (new candidate combination with known rank bounds)

A weighted obligation `(i,S,d)` asserts every separating block B for i satisfies `|B∩S|≥d`, where d=1 comes from a deletion witness and d=2 from R7. Other demands may be emitted only with an independent proof (e.g. two disjoint singleton obligations). For one negative, if supports `S1,...,Sr` are disjoint, then one block contains at least `sum d_j` symbols, forcing cost ≥ `sum d_j−1`. More generally choose nonnegative rational weights λ_j with `Σ_{j:a∈S_j} λ_j≤1` for each symbol a. Then

\[
 |B|\geq \sum_j\lambda_j |B\cap S_j|\geq\sum_j\lambda_j d_j,
 \qquad c(P)\geq \max(0,\lceil\sum_j\lambda_jd_j\rceil-1).
\]

**Proof.** The first inequality follows by summing per-symbol capacities over B; the second from each obligation's demand. Disjoint packing sets λ=1 for selected supports, 0 otherwise. The certificate consists of raw witness IDs, integer demands, rational weights and per-symbol capacity checks. It is sound, not necessarily the best possible rank bound. The floor can be used without solving an LP; greedily choose a disjoint support family and/or feasible rational weights. Certify them exactly using integer numerator/denominator arithmetic; floating-point solutions may guide but cannot certify.

**Across negatives:** For each of several negatives choose a local packing supported entirely on a set A_i, and suppose A_i are pairwise disjoint. If local demand is k_i≥1, any global compatible partition restricted to A_i has at most `|A_i|-(k_i−1)` blocks, since one block intersects A_i in at least k_i symbols. For disjoint A_i, extend them to a partition of Σ with singleton leftovers; summing restriction costs gives at most global cost because each global block intersects at least one part. Thus `c(P)≥Σ_i(k_i−1)`. This is the same rank-sharing principle used in the previous reports and planted choice proof, with weighted support certificates derived without full atoms. Without disjointness, take the maximum of individual floors unless a stronger overlap proof is available. Positive `aabc`, negatives `abac,baac` both need the same pair a,b; adding their floors gives a false cost of 2. Negative ε, positives `ab,cd,ef`, needs one block hitting all three, not three independent merges.

**Current-root version:** Use component vertices, not original symbols, and compute demands in component units. For d=1 map S to components meeting it. For an original d=2 support, the component demand is only 1 unless the verifier also proves that no single current component contains a discrepancy atom of that pair. If all single-component projections agree, then any distinguishing block is a union of ≥2 current components; and because there are no unary atoms, its discrepant pair uses two components in mapped S. This verifies demand 2 in component units. Counterexample: a and b are already in one component, x=`ab`, y=`ba`; original demand 2 does not imply an additional merge. A root-level bound must charge **additional** component rank and add it to current cost r only once. Distinct symbol supports that map to overlapping components are not disjoint anymore. Preserve proof context `(sample_digest, root_epoch, scope)`.

**Interaction with exact rank search.** A complete atom predicate `D_{ij}` is an exact OR over all minimal atoms; a deletion witness supplies a necessary OR over singletons from T. For each negative, pick an alternative from every necessary family and co-block their union. The minimum rank of the resulting hypergraph components is the earlier witness-rank theorem: any feasible partition realizes such choices, and merging exactly the connected components of chosen requirements realizes the relaxation. With complete atom families this is exact for the unrestricted structural problem. With partial witnesses it is a lower bound. A restricted atom list is NOT a necessary family unless proved complete or replaced by a proved superset of the alternatives. A feasible rank-relaxation result alone is not ACCEPT. Send the rank solver an implicit alternative iterator and completeness flag; if enumeration is budget-stopped, it must report unresolved states rather than prune unexplored choices. This preserves correctness of the existing exact-search module while replacing eager atom generation.

### Rule R11 — safe compression and its limits

1. **Unused declared symbols:** a symbol absent from every word changes no projection. In any unrestricted feasible partition, split it off as a singleton; projection comparisons on the remaining nonempty part are unchanged, and if the original block was all unused it could not separate a negative when positives exist. With no positives/no negatives handle the degenerate rules. Thus every unrestricted optimum has each unused symbol singleton; internally omit them from branching and expand them on output. Completeness for this reduction is exact in the unrestricted all-partitions case. Certificate: occurrence counts are zero, and the returned full partition includes each declared symbol exactly once. Keep them in the full input digest. For arbitrary block-specific bounds or admissible families, do not assume splitting preserves eligibility or state budgets. Example: positive `aa`, negative `a`, with Σ={a,u}, m({a,u})=3 and m({a})=m({u})=1, can be realized on the merged block but not on the split blocks.
2. **Observed inert symbols:** if I is a set disjoint from every minimal atom of every positive–negative pair, removing I from any tested B preserves projection equality/disequality. The proof is Theorem 3: a discrepancy atom contained in B is contained in B\I and conversely. Thus separating blocks can be retained after splitting I into singletons, subject to the same unrestricted degeneracy handling. This condition is sufficient, not claimed necessary for a symbol to be optimally singleton. Do not certify it from partial atom scans. A useful cheap special case is a fixed common prefix u and suffix v across all original words with *all* occurrences of I confined to these fixed contexts: write each word `u t v` with t containing no I. For any B, equality of the projections is equality of projected t after cancelling the same projected prefix/suffix. Restricting B by removing I changes only the common contexts, not projected t. Certificate names prefix/suffix lengths, I, and checks all words and absence in the middle. Common contexts must be nonoverlapping within each word. A symbol occurring in the middle as well may still be important (`aab` vs `aba` share initial a but a participates in discrepancy). This is a safe special-case structural compression, not a general reason to erase prefixes from the original evidence or external payload.
3. **Equivalent / symmetric symbols:** identical occurrence counts or postings do not establish interchangeability or mandatory merging. Example x=`ab`, y=`ba` has identical counts but forces a,b together; positive `ab`, negative `aabb` also gives identical per-trace count profiles for a,b, yet the singleton partition is optimal. A proved permutation of alphabet symbols preserving the two labeled word sets induces a cost-preserving automorphism of the unrestricted partition problem. It may be used to canonicalize search states if the search module proves orbit coverage; it does not force those symbols into one block. A verifier can apply the permutation to every raw word and compare exact labeled word sets (or multisets if preserving ID-sensitive scheduling); trace-ID aliases and mapping back must be explicit. Do not apply to asymmetric bounded capacities or families. Finding useful symmetries cheaply is heuristic unless verified. Mandatory DSU components are the only default contraction of observed symbols. For common-context or inert compression, retain the full declared alphabet and original traces for all external calls and for proof replay.

## 7. Lazy cross-label comparisons and incremental evidence ledger

The central question cannot be answered by one universal eager scan: the full discrepancy output can be quadratic per pair, the number of pairs pq, and maximal regions exponential. SDJ-IDA separates complete fast paths from bounded discovery and from exact search's coverage obligation.

### 7.1 Targeted matching for an arbitrary block (complete when exhausted)

For a negative i and candidate block B, compute its projection by merging its postings (or scanning the word), retaining actual symbols. If nonempty, any positive match must have the same count for each present symbol of B. Retrieve the rarest posting list `(a,count_a(y_i))` among those symbols, optionally intersect other positive postings and filter candidate counts on all B symbols. Then compare literal ordered B projections of the remaining positive candidates. A match produces a reusable zero region. Exhausting all candidates with no match proves `R_i(B)`. For an empty negative projection, a positive match exists iff at least one positive does not touch any symbol in B; union positive presence postings for B and find a missing positive ID. If p=0 handle immediately. Store sparse touched lists and stop on a concrete witness. The verifier can re-execute the filter and full comparisons or reconstruct R2's projection index. Proof: every possible equal projection satisfies all count filters, and in the empty case it lacks every B symbol; final comparisons decide exactly. Counterexample to treating counts as sufficient equality: `aba,aab` on `{a,b}`. No-match on a budget-truncated candidate list is UNKNOWN, never separation. This index is useful when the search requests a small B or a small number of negatives; for a complete partition with many blocks R2 is better.

### 7.2 Scheduling (heuristics only)

Priority 0: full-word conflict, unused detection, singleton coverage, length-two reverse shortcut (may retain it as a cheap first pass), complete or budgeted deletion join. Priority 1: compatible mandatory-root test; if some negative fails, target that negative first and map all its known deletions onto root components. Priority 2: choose cross-label pairs via shared count-vector hashes, similar lengths, long shared prefixes/suffixes, small count distance, rare supports, previous exact match or feedback IDs. For one pair emit R7 support, one R8 maximal region, and on-demand atom witness; do not eagerly build all atoms. Priority 3: alternate maximal regions for high-value negatives, exact atom family iterator or full pair scans only on residual small problems. Count-vector equality is particularly useful for order-only discrepancies; count-vector *inequality* must not cause a pair to be ignored forever. Near-neighbor ranking and sampling produce no proof of necessity or compatibility.

For exact fallback with no conclusive external response, a deterministic fair enumerator can process all cross-label pairs using the implicit predicate, or the exact-search module can exhaust lower-cost complete partitions with R2. The latter is a local structural proof path only; final operational acceptance is still external. With state bounds a structural fallback cannot decide bounded feasibility. Budgeted preprocessing never needs to complete the whole pair enumeration to preserve an exact solver's completeness: it returns only verified constraints, and search retains every solution not soundly excluded. New evidence may change the frontier, but a heuristic score alone cannot remove a branch.

### 7.3 Ledger data model and update rules

```
SampleId = digest(canonical_original_sample, schema_version)
TraceRef = (label, original_index)
SetRef = SparseSortedIDs | DenseBitmapForDenseLocalSet | Complement(SparseSortedIDs)
RawFact = (id, sample_id, kind, i, j?, region_or_deletion?, payload, verified)
ComponentFact = (raw_fact_id, root_epoch, component_references)
NegativeLedger = {
    deletion_antichain, retained_region_antichain, weighted_supports,
    known_separating_blocks, required_component_witnesses,
    pair_descriptors_LRU, pending_tasks, alias_ids
}
Progress = (scope, epoch, processed_units, pending_cursor, exhausted, reason)
```

Choose one canonical fact descriptor; `Complement(T)` means Σ\T, not `active\T` unless an explicit active universe is attached. Sparse set containment is sorted-list intersection, hash lookup, or a dense bitmap *only when density justifies it*; never make a bitmap per singleton. For complement witness and B, `B⊆Σ\T` iff B∩T=∅. Keep a witness ID for every dominance decision; derived records may refer to raw facts archived on disk. Index obligations by original negative, with aliases sharing immutable facts; never deduplicate columns across labels or reorder original trace IDs. `known_separating_blocks` stores minimal verified sets for a negative (upward-closed semantics). New zero facts remove redundant supersets of deletions / subsets of retained regions for the same negative; dominance does not delete certificates still in use. An index by rare symbols or cardinality buckets can reduce subset-test candidates; worst-case antichain comparison remains quadratic in its size. Set a memory cap, spill append-only facts or discard nonessential cached candidates, never silently discard proof provenance. Do not combine retained regions by union even when they have the same positive witness: `ab` vs `ba` is the counterexample. Complete unary/binary agreements for the same pair can be stitched by Theorem 3, as the previous report showed; avoid anonymous stitching across different positives.

For complete unrestricted feedback, a named positive witness can be replayed as `EQUAL_REGION`. When a fixed-zero column has no positive ID, a raw match can be recovered by targeted matching if needed; otherwise keep the trusted external table fact explicitly marked as external and not independently raw-verified. A free group or an actual feasible `1` establishes separation in the unrestricted base table. Identical free projection groups may share computations, but they do not necessarily have the same negative word or behave identically on another block. A fully fixed-zero bounded column without a raw equality cannot be turned into a structural region. On `BOUNDED_NO`, record tested partition and bounds only, unless a separate structural certificate is provided. On `INCOMPLETE`, retain independent verified facts only and leave the verdict unresolved.

### 7.4 Evidence strength and safe pruning boundary

- Raw equality on U implies deadness on any B⊆U. A partition is proved incompatible by this rule iff one same negative has every block covered by some known dead region. Different positive witnesses per block are allowed. This rule is complete for the *specified region-containment test*, not for all possible deductions.
- A verified raw separating set is upward-valid for unrestricted structural compatibility. An external ACCEPT is separate. Use candidate cost and a lower bound only when the upper bound is verified in the actual regime.
- Required-component contractions and hitting obligations are necessary in both regimes; neither implies that arbitrary coarsenings of an incompatible node are incompatible. Do not combine dynamic merge-order restrictions and a canonical-parent tree unless search proves coverage of each target.
- The ledger never labels a candidate infeasible because a witness scan found nothing, a rank relaxation failed to find a candidate within budget, or a heuristic expects rejection. Proofs refer to the original sample digest and correct root snapshot. External tables carry query IDs and table scope.

## 8. Implementation-ready module and interfaces

Recommended directory: `implementation/partition_feedback_final/sparse_analyze/`, separate from external adapter. Keep legacy mask-based code as a baseline and migration path for small inputs only. Suggested Python protocol (types illustrative):

```python
@dataclass(frozen=True)
class Budget:
    max_tokens: int | None = None
    max_bucket_entries: int | None = None
    max_pairs: int | None = None
    max_witnesses: int | None = None
    max_bytes: int | None = None
    deadline: float | None = None  # monotonic time

@dataclass(frozen=True)
class Witness:
    kind: Literal['DELETE_EQUAL','EQUAL_REGION','COUNT_ATOM','ORDER_ATOM',
                  'WEIGHTED_SUPPORT','SEPARATES','FULL_CONFLICT']
    sample_digest: str
    negative_id: int
    positive_id: int | None
    payload: object  # versioned schema by kind; never arbitrary executable code

@dataclass
class Analysis:
    sample: SampleView
    indexes: SparseIndexes
    ledger: EvidenceLedger
    root: OwnerArray
    mandatory_forest: list[ForcedEdge]
    structural_coverage: Mapping[int, BlockRef]
    lower_bound: BoundCertificate
    candidate: CompletePartition | None
    status: Literal['PARTIAL','FAST_PATH_EXHAUSTED','STRUCTURAL_OPTIMUM','STRUCTURAL_INFEASIBLE']
    progress: list[Progress]

# Required interfaces; names are proposed, not claims of existing APIs.
def build_sparse_indexes(sample: Sample) -> SparseIndexes: ...
def analyze_traces(sample: Sample, budget: Budget = Budget()) -> Analysis: ...
def discover_raw_witnesses(indexes: SparseIndexes, budget: Budget, *,
                           targets=None, root_snapshot=None, cursor=None) -> EvidenceBatch: ...
def derive_mandatory_contractions(evidence: EvidenceLedger, *,
                                  root_snapshot=None) -> ContractionBatch: ...
def update_witness_ledger(new_evidence: EvidenceBatch, *,
                          ledger: EvidenceLedger, sample: SampleView) -> LedgerDelta: ...
def verify_raw_witness(sample: SampleView, witness: Witness, *,
                       verified_root=None) -> VerificationResult: ...
```

`EvidenceBatch` carries facts and `Progress` for each phase, with status `EXHAUSTED`, `PARTIAL_BUDGET`, `PARTIAL_MEMORY`, `ERROR`; progress units are token scans, bucket entries, pair comparisons, bytes and outputs, not a vague percentage. `VerificationResult` is `VALID`, `INVALID` or `INCOMPLETE`; an unfinished verification is never VALID. `ContractionBatch` contains the prior and next epoch, new forest edges, rank increase and affected IDs. `LedgerDelta` lists accepted facts, dominated facts, changed negative obligations, queued propagation and any proof of conflict. Use immutable sample/owner snapshots across workers, and a single deterministic verification/commit coordinator. Workers may produce unverified proposals; only the coordinator commits verified facts. Budget checks occur before allocating buffers, while scanning large buckets, and per chunk of long words. Limit memory by estimated bytes plus measured high-water/allocator telemetry; Python objects have substantial overhead. If an individual trace exceeds the working-memory budget, use on-disk arrays or stop without claiming exhaustion.

```
ANALYZE_TRACES(sample,budget):
    index = build_sparse_indexes(sample)           # streaming validation / budget
    ledger = empty_verified_ledger(index.digest)
    if opposite_label_duplicate: return verified structural conflict
    if trivial_class_case: return verified structural result
    owner = singleton_DSU(n)                      # no one-hot masks
    active,unused = observed_support(index)
    singleton_coverage = sparse_singleton_check(index)
    if all negatives covered: return structural optimum at singleton root

    # Optional old length-two shortcut can emit the same ForcedEdge format.
    while budget permits:
        frozen = snapshot(owner)
        batch = discover_raw_witnesses(index,budget, root_snapshot=frozen,
                                      phase='single_group_deletion_join')
        update_witness_ledger(batch,ledger,sample)
        changes = derive_mandatory_contractions(ledger,root_snapshot=frozen)
        commit_verified_unions(changes)
        propagate_sparse_hyperedges_to_current_roots()
        # R2 is a raw structural test, not the external black box.
        verdict = sparse_root_check(sample,owner,budget)
        if verdict is verified compatible:
            candidate = expand_complete_partition(owner,unused)
            return STRUCTURAL_OPTIMUM with forest lower bound and candidate
        if verdict is verified failure: schedule its negative as high priority
        if no unions in this round: break  # closure only if batch was EXHAUSTED

    for task in budgeted_scheduler(ledger,index,owner):
        if task is pair(i,j):
            d = implicit_descriptor(x_j,y_i)
            emit verified weighted_support(d)
            if budget permits: emit verified greedy_max_region(d)
        if task is target(i,B): emit exact_match_or_separation(i,B)
        update_witness_ledger(...)
        propagate any newly certified mandatory components
        # Every change preserves all feasible completions; update cost lower bound.
    return PARTIAL or FAST_PATH_EXHAUSTED, owner, forest, ledger, proved lower bound
```

This pseudocode separates the recommended production schedule from the measured prototype in Appendix A, which ran only one complete singleton-deletion pass plus a root check and edge replay. The pilot does not implement production resource accounting or incremental closure. In the implementation, root checks should also be triggered after substantial new unions or when a frontier module requests them, subject to budget. `FAST_PATH_EXHAUSTED` does not mean global search complete. If a stage is disabled, record it as skipped, not exhausted.

```
VERIFY_RAW_WITNESS(sample,witness,verified_root=None):
    validate digest, kinds, IDs, label classes, token IDs, set representation
    if DELETE_EQUAL:
        recover immutable deletion set (check root proof if group reference)
        return literal erase(x, T) == literal erase(y, T)
    if EQUAL_REGION:
        return literal project(x,U) == literal project(y,U)
    if COUNT_ATOM: return counts actually differ
    if ORDER_ATOM: return both counts agree and opposite occurrence order
    if WEIGHTED_SUPPORT:
        reconstruct D and inversion endpoint support
        verify support covers all minimal atoms and appropriate demand
    if SEPARATES:
        verify B nonempty and projected y differs from all positives
    if FULL_CONFLICT: return original x == original y
    otherwise: INVALID
```

Actual verifier should independently implement simple exact erasure, projection and occurrence-count operations rather than call producer helper functions. If a root snapshot certificate references other evidence, replay dependencies in order and verify no cycles. No untrusted pickle/eval; check type/range of every ID, reject bool-as-int and invalid duplicate block members. For external facts not independently replayed, separate `TRUSTED_EXTERNAL` from `VALID_RAW` and preserve full provenance. Proof IDs should refer to canonical serializations, not Python process-dependent hashes. Deduplication is by exact canonical payload after validating its scope. Verify forced edges before union; a malformed deletion set or wrong epoch must fail closed. Use original trace IDs in every exported witness.

### 8.1 Versioned proof migration

Propose `sparse-partition-v2`:

```json
{
  "kind": "sparse-partition-v2",
  "sample_digest": "...",
  "regime": "unrestricted",
  "alphabet_size": 100000,
  "forced_edges": [["negative_id", "symbol_a", "positive_a", "symbol_b", "positive_b"]],
  "group_edges": [],
  "additional_bound_proofs": [],
  "answer_owner": "array or content-addressed packed array",
  "external_accept_ref": null
}
```

The example uses descriptive placeholders, not a real proof. A singleton edge is 5 integer IDs, e.g. 20 bytes in packed uint32 fields, plus framing and digest. Derive the mandatory root from the forest, not duplicated component memberships. An owner array of n 32-bit IDs is ~0.38 MiB at n=100,000. Materialize complete external blocks in one pass over the alphabet, grouping by owner in O(n) expected time; sort members by declaration order if required. Unused IDs remain explicit in the output. Large proofs may use chunked JSONL/CBOR/Arrow or fixed-width binary with validated offsets; JSON with small integer IDs works today. Maintain `partition-v1` replay for archived certificates; a conversion must replay the old proof then produce and verify v2, not simply transcode claimed values. For group witnesses, use immutable component references and replay the corresponding membership before erasure. The verifier can stream evidence and retain only dependencies and a DSU, but a general search certificate can still be exponential in size. Do not call an edge forest a complete optimum certificate unless the claimed partition also meets the rank lower bound and has verified acceptance in the relevant regime.

## 9. Complexity summary and scalability limits

Let k be number of current components, r successful mandatory unions, W total stored sparse witness memberships, F number of retained facts, J deletion candidate entries inspected, V total lengths in their literal checks, and A the sum of lengths of pairs actually analyzed implicitly. Space is measured in machine words unless stated. With all traces retained and no external table materialization:

| Operation | Time | Working / retained space |
|---|---|---|
| Validation, encoding, occurrence/count postings | Expected O(n+N+L) | O(n+N+L) |
| Singleton coverage, sparse fixed-partition test | Expected O(n+N+L) per partition | O(n+N+L) |
| Singleton/group deletion signatures | O(L') per frozen pass after encoding | O(N'+L'+Lmax) |
| Exact single-group join | Expected O(n+N'+L'+J+V) plus output | O(n+N'+L'+F+W), or stream facts |
| Union forest | O((n+r+number of union attempts) α(n)) | O(n+r), plus cited facts |
| Complete quotient fixed-point iteration | At most n passes; sum of individual costs | Reuse one pass workspace; retained ledger separately |
| Implicit descriptors / one exact support per compared pair | O(A) expected | O(max pair length) scratch, byte-capped cache |
| One maximal equal region per compared pair | O(A log(max(2,Lmax))) | Same scratch plus blockers |
| Maximal region enumeration | Exponential output in worst case | Can stream; explicit graph baseline may need Θ(n²) edges |
| Antichain insertion | Worst case O(F) set tests per insertion | O(F+W) for sparse facts, plus archive |
| Verify singleton-edge forest | O(n+r+sum of referenced trace lengths) | O(n+r), plus raw input |
| Exact global rank / partition search | Potentially exponential, up to Bell(n) partitions in fallback | Depends on search; no universal polynomial bound |

α is the inverse Ackermann function from classic union-find analysis [3]. For quotient witnesses, erasure membership can be tested from a verified owner snapshot rather than copying a dense complement; use packed component membership maps or replay current DSU roots. Store immutable sparse deletion facts over original symbols where feasible; if the deletion is huge, a reference to a previously verified component plus epoch avoids repeated copies. The table's O(F+W) ledger size is not a bound on the number of discoverable facts, and budgets must control it. For total runtime in the external workflow, add every complete proposal serialization, black-box execution, response transport and verification, as the paper's Eq. (28) suggests. Even a compact table format can have kq entries; the raw module cannot promise to remove that cost or change the external contract.

At n=100,000, a packed owner or parent array takes 400,000 bytes; two uint32 DSU arrays total 800,000 bytes (excluding headers). The occurrence store scales with L, not with n². For 20,000 traces with 220,000 total occurrences, the token array is 880,000 bytes, plus offsets, counts, positions, original token strings, Python overhead, indexes and witnesses. A 10,000-edge forest has 200,000 bytes in five packed uint32 fields per edge. These are illustrative raw-array sizes, **not** process RSS estimates. In CPython the prototype uses dictionaries, lists and tuples, hence substantially more memory. All dense n×n, n×N and p×q default structures are forbidden. Optional local dense bitmaps only for explicitly bounded high-density sets are acceptable.

Worst cases remain: all words very long, nearly every symbol in every trace, adversarial fingerprint buckets, large genuine cross-label joins, expensive exact hitting/rank optimization and external timeouts. For a 100,000-symbol alphabet with every trace containing every symbol, just reading the input is Ω(nN). The paper's Theorem 1 proves NP-completeness even on length-two words; the length-two reverse shortcut does not contradict that result. The draft's total-reduction paragraph uses a fixed YES/NO gadget of mixed lengths despite its uniform-length-two statement; that is a minor proof-presentation issue rather than a reason to claim polynomiality: trivial YES/NO source cases can be mapped instead to fixed uniform-length-two instances, e.g. Σ={a,b}, positive `ab`, negative `ba`, thresholds K=1 and K=2 respectively. The nontrivial Vertex Cover reduction and the complexity warning stand. Neither evidence extraction nor this benchmark demonstrates architecture identification, target-language recovery, or any state-bound feasibility theorem.

## 10. Experimental investigation and measured prototype

### 10.1 Archive provenance and historical outcomes

Both supplied planted ZIPs were extracted into the same directory; the scale package was extracted separately. The benchmark collection reports 33 independent samples, 41 runs, and independent reference checks for all 33. Historical `PLANTED_REPORT_FA.md`, `ALL_MEASUREMENTS.csv/json`, `planted_30s/summary.csv`, `planted_extra/summary.csv`, `planted_high_memory/summary.csv`, `representation_probe.json`, and `root_replay_results.json` were inspected. The 5-second suite solved 17/33, with one dense case verified only by restricted root replay, 10 INCOMPLETE and six MEMORY_LIMIT; one extra case succeeded at 30 seconds. A planted reference proof is not a solver output. The archives record separate solver and verifier status; retain both.

| Fixture | n | p / q | Active | L | Archived outcome / budget | Recorded solver seconds / peak RSS MiB | Main historical issue |
|---|---:|---:|---:|---:|---|---|---|
| huge_long_active | 100,000 | 10,000 / 10,000 | 100,000 | 220,000 | MEMORY_LIMIT / 30 s | 1.360 / 1222.21 | sparse_contractions; long reversal contexts missed by short pass |
| huge_reverse_unused | 100,000 | 10,000 / 10,000 | 10,010 | 40,000 | MEMORY_LIMIT / 30 s | 1.505 / 1222.49 | mask root and complements despite 89,990 unused symbols |
| large_reverse_dense | 10,000 | 10,000 / 10,000 | 10,000 | 40,570 | OPTIMAL / 30 s; general verifier INCOMPLETE | 0.457 / 344.95 | repeated verification / certificate representation |
| large_reverse_pairs | 10,000 | 10,000 / 10,000 | 10,000 | 325,000 | INCOMPLETE / 30 s | 30.255 / 809.35 | oracle_partition with many quotient blocks |
| small_count | 100 | 100 / 100 | 50 | 2,170 | OPTIMAL / 30 s, VERIFIED | 8.769 / 102.26 | count witnesses with distinct positives |
| extra_interleaved | 200 | 200 / 200 | 200 | 57,360 | INCOMPLETE / 5 s | 5.001 / 106.40 | pair_triple_scan |
| extra_long_1024 | 30 | 20 / 20 | 12 | 41,010 | OPTIMAL / 5 s, VERIFIED | 2.078 / 98.89 | repeated long projections |
| extra_imbalanced_negative | 1,000 | 100 / 10,000 | 1,000 | 308,770 | INCOMPLETE / 5 s | 5.027 / 230.65 | oracle_partition |
| extra_imbalanced_positive | 1,000 | 10,000 / 100 | 1,000 | 298,870 | INCOMPLETE / 5 s | 5.001 / 119.46 | oracle_partition |

The recorded 30-second huge runs used 1,536 MiB virtual-address limits, not 1,536 MiB RSS limits. The high-memory rerun of `huge_reverse_unused` under 3,072 MiB and 10 s reached the oracle phase, then INCOMPLETE at 10.145 s, 2303.65 MiB RSS. This independently supports the diagnosis of multiple representation bottlenecks. `huge_sparse_small` likewise failed despite only two active symbols; with the higher limit it stalled at the oracle phase. `huge_singleton_active` stalled at singleton scanning. These are stage-specific outcomes, not proofs that any of these problems is mathematically difficult.

### 10.2 New experiment: actual observed results

A small standalone Python pilot was run in the analysis environment, one process per fixture. It reads **only input.json**, not `spec.json`, `reference.json`, generators, expected block counts, or solver results. It builds positive deletion fingerprints with exact collision verification, scans original negative representatives, stores one raw witness per symbol, unions a spanning forest, performs a sparse raw quotient check, and independently replays each edge by literal erasure plus graph connectivity. A second process reconstructed the resulting complete partition and checked it using the supplied `planted.py:compatibility` function, not its reference/proof checker or generator. Each reference value was compared only after the result was computed. This pilot deliberately omits external calls, general search, component re-indexing, and production budget/certificate I/O; no old/new end-to-end speedup is asserted.

| Fixture | Verified unions | Root blocks | Discovery s | Raw root check s | Edge replay s | Peak RSS MiB | Edge JSON bytes |
|---|---:|---:|---:|---:|---:|---:|---:|
| huge_long_active | 10,000 | 90,000 | 0.7632 | 0.1346 | 0.0578 | 185.66 | 275,561 |
| huge_reverse_unused | 10,000 | 90,000 | 0.1094 | 0.0159 | 0.0300 | 130.06 | 264,473 |
| large_reverse_dense | 9,990 | 10 | 0.1081 | 0.0149 | 0.0108 | 113.14 | 264,185 |
| large_reverse_pairs | 5,000 | 5,000 | 0.2484 | 0.0364 | 0.0078 | 127.86 | 132,132 |
| small_count | 40 | 60 | 0.0016 | 0.0003 | 0.0001 | 93.88 | 653 |
| extra_interleaved | 60 | 140 | 0.0287 | 0.0035 | 0.0002 | 98.64 | 1,080 |
| extra_long_1024 | 10 | 20 | 0.0156 | 0.0020 | 0.0006 | 96.51 | 142 |
| extra_imbalanced_negative | 90 | 910 | 0.1974 | 0.0201 | 0.0003 | 115.63 | 1,661 |
| extra_imbalanced_positive | 90 | 910 | 0.2069 | 0.0246 | 0.0003 | 119.67 | 1,827 |

All nine raw root checks were True, all edge replays passed, and all nine independent benchmark compatibility checks returned True. All nine counts match their recorded structural optima. The mathematical proof does not depend on matching those reference counts: a forest of r verified mandatory unions provides the lower bound r, and the complete compatible quotient has cost r. Discovery emitted respectively 20,000; 20,000; 19,999; 19,999; 199; 120; 39; 1,948; and 199 singleton-deletion witnesses before retaining only successful forest edges. The 30-second dense old solver JSON (92,228,343 bytes in the earlier archived run) is not directly comparable to the 264,185-byte edge list here: the latter excludes the sample digest, final partition, protocol and general search records. It illustrates the magnitude of the representation change, not a measured complete proof-file compression ratio.

Input load/encoding times, in table order: 0.2802, 0.0876, 0.0664, 0.1583, 0.0010, 0.0230, 0.0039, 0.0828, 0.0346 s. Timings are single-run Python process timings using `perf_counter`; RSS is `ru_maxrss` on Linux, includes interpreter and input data; discovery includes DSU forest construction. The separate checker run was not timed. The pilot was not run with the historical RLIMIT_AS configuration; these are not controlled same-host comparisons. No external ACCEPT was observed or claimed. No complete v2 artifact or full search certificate was generated. The proof replayer uses assertions for a trusted experimental harness and must not be used with Python `-O` or as an adversarial-input validator. Production verifier design is in §8.

### 10.3 Interpretation by family

**Long / interleaved.** The generalized deletion join discovers the same mandatory relation when each reversal has an arbitrary common context, even when the swapped symbols are not adjacent after interleaving, as long as deleting either makes the traces equal. Count vectors alone do not find these order-only witnesses. Repeated symbols and long shared context increase verification length but not alphabet-square storage. The observed long and interleaved cases recovered all necessary root unions; no claim is made that arbitrary interleaved patterns force pairs or that all long traces are easy.

**Huge unused.** Its 89,990 unused declared symbols are retained as singleton IDs; the join enumerates only touched groups. The root includes 90,000 blocks, so an external service materializing per-block negative columns could still be very expensive. The local sparse check avoids this, but we cannot replace that service. The active huge case is also solved structurally, showing the result is not merely an unused-symbol shortcut.

**Dense versus pairs.** Both reverse families expose mandatory forests, but one quotient has ten blocks and the other 5,000. The old complete-table local oracle scales with quotient block count; R2 scales with actual token incidences for one candidate. Compact forest replay avoids reconstructing successive full partitions. A dense *discrepancy graph* on a long reversed word is different from a dense *forced contraction path*: the former may force only a disjunction, not all its endpoints. Never union a whole reversal clique without the separate mandatory-deletion proof.

**Imbalance.** A naive pair scan pays pq and a naive singleton scan pays n(p+q), even if one side is tiny. The join builds a posting index on one label class and probes the other; the raw witness relation is symmetric under exchanging the two word arguments but the negative obligations are not. In the prototype positive-heavy input built a larger positive index, while negative-heavy output generated more witness incidences. A production join can build on the cheaper side with a careful original-label mapping, or spill/shard; time depends on shared signature buckets and actual comparison lengths rather than only trace counts. Both pilot roots matched their references with 90 forced edges.

**Choice / count / mixed and nonplanted inputs.** Small count succeeds in the pilot because the two positive witnesses can differ. Choice families such as positive `bca`, negative `abc` may yield a single required symbol but no forced edge; R7 gives a two-symbol demand and R8 yields disjunctive deletion obligations. Do not manufacture the planted grouping. For overlapping choices, rank/search and further lazy witness discovery are essential. The main code audit identifies HDFS traces and an eight-vertex cover path; these should be regression targets, not assumed solved by the new prototype. No full-corpus performance claim follows from the nine targeted successful roots.

## 11. Reproducible validation and experimental plan

### 11.1 Checks actually executed

- All 121 words of length ≤4 over three symbols: 14,520 ordered pairs of **distinct** words. For each, the singleton-deletion join's group set equaled direct literal erasure for every symbol. Opposite-label equal words were excluded from this test because they require the separate full-word conflict check. This includes empty words, repetitions and insertion/deletion cases. The count is 121×120.
- Seed 17, 1,000 random disjoint positive/negative corpora over those words, 1–11 words per class: join results compared against all cross-label singleton-deletion tests; forest edges replayed; root compatibility compared against literal all-block/all-positive projections. No failures observed.
- Nine target benchmark roots and all forced edges replayed as above. Separate checker rebuilt local positive projection sets from the original string tokens and verified each complete partition. All reported new measurements are in §10.2. No timing of R6–R11 was performed; those are proved designs, not tested implementations. The two previous reports' exhaustive results and archive regressions are not new executions in this assignment.

### 11.2 Required production acceptance tests

1. Enumerate small alphabets n≤5 and short words, including duplicates, opposite labels, empty words, unused declarations, repeated tokens and random declaration/ID orders. For each pair check implicit atom predicate on every subset against literal projection; compare R7 support to exhaustive unary/pair atoms; validate R8 region equality and inclusion maximality against subset enumeration. Test all maximal regions on small graphs only. For each small corpus enumerate all partitions independently; verify mandatory DSU coarsening, every reported floor, unused/inert transformations, and exact structural optimum. Use a separate reference algorithm, not production helpers.
2. Reproduce R3 for group deletions on arbitrary current partitions and compare against literal full cross-label deletion tests. Test multi-round R5 example and the global-necessity fixpoint counterexample. Test random sequences of mandatory unions, incremental update versus fresh index, both join orientations, tombstones and alias handling. Test forced-edge permutations and rejection of invalid epoch/component references.
3. Force all fingerprints to collide (including equal lengths), split buckets into shards, inject long collision chains and repeated projected signatures. Results when exhaustive must match exact literal witnesses; budget-stopped results must be subsets of exact evidence. Mutation tests: wrong trace label/ID, off-by-one occurrence rank, wrong digest, missing symbol in deletion, missing compulsory edge, fake support demand, wrong capacity scope, duplicate member, bogus "complete" marker, incomplete free table, mismatched negative ordering. Reject incorrect claims, not merely malformed JSON.
4. For all 33 archived planted inputs, run pinned baseline, enhanced scale baseline, sparse-representation-only variant, R3/R4, R3–R5, R6–R10 lazy evidence, and the full integrated exact solver. Use original `input.json` only; lock reference files outside solver access. Compare reference cost only after verification. Evaluate all achieved optima, not only the nine chosen successes. Include historical `audit.exhaustive_samples()` (2,529 cases), HDFS-1024, HDFS holdout, and path-cover certificates. Add deliberately difficult Vertex Cover reductions, ε negatives with overlapping supports, multi-negative choices, reverse cliques, repeated-symbol nontrivial inversions, many maximal equal regions, common-context compression, count adversaries, 1:100 and 100:1 label imbalance, and scalable random nonplanted corpora. Include cases where mandatory-root check fails but feasible coarsenings exist. Test external mock `ACCEPT`, `PROJECTION_NO`, `BOUNDED_NO`, malformed and `INCOMPLETE` responses separately; never conflate a local checker with the actual service.
5. Run fresh independent processes with identical machine, interpreter, CPU affinity and memory settings. For each case record at least five trials at 5 s, 30 s and uncapped (or a specified upper experimental cap), RLIMIT_AS 1,536/3,072 MiB where supported. Record medians, ranges, counts censored by timeout, and OS/CPU/Python version. Measure input read and encoding; index build; fingerprint generation; join bucket visits and literal token comparisons; DSU and propagation; sparse root check; ledger memory and disk; search runtime and nodes; total external calls, payload bytes and latency; verification and proof bytes; peak RSS and wall time including I/O. Do not count structural raw checks as external calls. Report `OPTIMAL`, `INFEASIBLE`, `PARTIAL`, `MEMORY_LIMIT`, `INCOMPLETE`, service failures and verifier status separately. If only the structural problem is solved, report `STRUCTURAL_OPTIMUM`, not an externally confirmed optimum.

### 11.3 Success criteria

- Zero counterexamples to certified equality, necessary contraction, weighted bound, compression and root-optimality theorems on independent finite checks. Correctness remains proof-based rather than statistical.
- No alphabet-wide one-hot collection or per-edge full complement serialization; show allocations by phase. Verify n=100,000 and at least 10,000 total traces, including all-active cases with 20,000 traces, without quadratic alphabet structures.
- For the nine pilot successes, reproduce equal optimum and compact proof from input alone with production verifier. For other cases measure completion and lower-bound quality without overstating success. Compare partial evidence coverage, number of forced unions, floor gap, maximum live facts and certificate replay time against old `analyze` at equal time/byte budgets. Distinguish exact preprocessing-only improvement from improvements in search and diagnostics.
- End-to-end acceptance criterion: external service confirms the complete candidate, and independent proof covers all cheaper feasible partitions in the intended regime. A root-compatible forest case satisfies the structural lower/upper equality; general cases require search proof. Failure to obtain a complete external verdict is a recorded blocker, not a false infeasibility claim.

## 12. Integration recommendations and open research questions

### 12.1 Other research modules

**Exact search agent:** consume `root_epoch`, verified forest, `structural_coverage`, per-negative deletion/weighted hyperedges, implicit atom families and progress flags. Start at the mandatory quotient, with cost r. Expand unused/inert symbols only under verified objective-preservation rules. Use verified rank floors and admissible branch coverage, not heuristics. A root-compatible candidate can be proposed immediately and, after actual ACCEPT, gives exact optimality; otherwise search all feasible continuations not pruned by proof. Expose a callback requesting `match_or_separation(i,B)` and budgeted next witness. When dynamic root unions are proved, rebase search states or restart with a proved coverage mapping; don't let stale partition IDs corrupt pruning. Partial atom enumeration cannot restrict alternative families. A fully exact fallback may enumerate candidate partitions at increasing cost and use the raw predicate for structural exclusion. It must account for externally unresolved cheaper candidates if the service is authoritative beyond the structural model.

**Feedback and query-selection agent:** accept only complete full-alphabet partitions for external proposals. Use the raw ledger for same-negative known dead regions, verified supports and diagnostic ranking; request additional matching evidence for zero columns without IDs. Track external query count, exact scopes and latency separately. Structural facts may already determine a verdict, making a query useful only for independent acceptance or other table evidence. Do not buy a query that adds no proof or acceptance value unless required by the contract. Store returned table metadata by negative ID, preserve correlations and completeness, and do not infer structural deadness from bounded table restrictions.

**Verification / benchmark agent:** implement `sparse-partition-v2` as independent small-ID forest and literal-erasure verifier, with proof context validation and exact structural compatibility checker. Preserve old v1 archive replay and old results unchanged. Reproduce Appendix A and then add production validation, actual adapter schema tests, collision tests and all adversarial cases. Verify candidate blocks are a true partition of the declared alphabet and preserve original token labels and ordering. The pilot root proof is not a general proof format yet. In particular, only the raw singleton-deletion extraction and root test have a measured prototype.

**Migration order:** (1) replace one-hot representation end-to-end, including output and verifier; (2) generalize reverse pass to R3 and R4 with checked proof edges; (3) integrate sparse raw coverage and root check; (4) implement component rounds and incremental propagation; (5) implement implicit descriptors and maximal regions; (6) integrate rank bounds, search and feedback with unchanged service; (7) run controlled ablations and independently verify every claimed optimum. Each step should be separately testable and preserve old proofs where possible.

### 12.2 Remaining limitations / open problems

- Can all useful component-deletion matches be maintained across mandatory unions without repeatedly rehashing long words or processing huge shared buckets? The frozen-pass method is correct, but its incremental complexity is open here.
- Can exact projected equality classes for all single deletions be built with a deterministic compressed string index with near-input-size verification cost even for adversarial long common contexts? The present hash-filter join is exact but has data-dependent candidate costs.
- Can implicit colored inversion graphs support faster enumeration of diverse maximal equal regions, a strong minimum vertex cover / hitting-set relaxation, or exact atom alternatives without duplicate inversion blowup? Repeated symbols make the graph a quotient of an occurrence permutation graph; general graph structure should not be assumed to retain special permutation-graph algorithms.
- Can stronger global mandatory relations (e.g. the `abc` versus `bca,cab` counterexample) be certified compactly through disjunctive evidence without running an expensive full optimizer? Explore proof-producing small connected support cores and exact restricted bipartition checks.
- Can a reliable evidence-budget policy predict when new raw facts cost less than external diagnostics? Use empirical marginal bound improvements, wall time and oracle response cost, not hidden planted answers.
- The external wire protocol and actual response-volume limits are not supplied. The paper specifies mathematical content, not operational schema. The 90,000-block roots may be hard for the external service despite trivial local structural certificates. No redesign of that service is proposed. A bounded-regime deployment would require separately certified external behavior and must not use unrestricted objective-preserving reductions without a proof.

### 12.3 Contribution classification

**Established:** erasing projections, structural compatibility and monotonicity, minimal unary/binary atoms, deletion hitting obligations, mandatory singleton witnesses, union-find, witness-rank optimization, same-negative region closure, sparse projection checks in the supplied benchmark. **New candidate contributions relative to supplied work:** complete touched-group deletion join with absent-side cases and compact exact certificates, group-epoch closure design, linear implicit inversion support, near-linear greedy maximal regions, weighted support integration and resource-aware evidence interface. **Measured implementation:** one-pass singleton-deletion join, sparse mandatory forest, structural root check and independent edge replay on nine fixtures and finite tests. **Unimplemented / open:** production integration, actual external adapter, component incremental reindexing, implicit graph module performance, full general exact-search proof replay and novelty relative to all published research. The research module should be judged on sound deductions and useful certified preprocessing, not a claim to have solved every instance at scale.

## References and source provenance

1. Supplied draft, *Passive Compositional Automata Learning from Global Logs*, `main (1).pdf`, §§2–5, Lemmas 1–2, Theorem 1, Propositions 1–3, Eq. (23), Fig. 2, Appendix B. No public bibliographic identifier provided. Main source for the external mathematical interface.
2. Supplied `independent_partition_selection_report.md` (288 lines) and `Alphabet partition research report.md` (301 lines). Prior projection-witness lower bounds, discrepancy and rank theorems, examples, finite checks. Both read before developing the new method.
3. R. E. Tarjan, “Efficiency of a Good But Not Linear Set Union Algorithm,” *Journal of the ACM* 22(2), 215–225, 1975. DOI: [10.1145/321879.321884](https://doi.org/10.1145/321879.321884). Established disjoint-set analysis, not a new theorem of this report.
4. R. M. Karp and M. O. Rabin, “Efficient randomized pattern-matching algorithms,” *IBM Journal of Research and Development* 31(2), 249–260, 1987. DOI: [10.1147/rd.312.0249](https://doi.org/10.1147/rd.312.0249). Fingerprint retrieval background; our exact verification is mandatory.
5. S. Tsukiyama, M. Ide, H. Ariyoshi, I. Shirakawa, “A New Algorithm for Generating All the Maximal Independent Sets,” *SIAM Journal on Computing* 6(3), 505–517, 1977. DOI: [10.1137/0206036](https://doi.org/10.1137/0206036). Output-sensitive explicit-graph enumeration background, not a claim that our implicit colored graph enumerator has this bound.
6. R. M. Karp, “Reducibility Among Combinatorial Problems,” in *Complexity of Computer Computations*, 1972, pp. 85–103. DOI: [10.1007/978-1-4684-2001-2_9](https://doi.org/10.1007/978-1-4684-2001-2_9). Standard combinatorial hardness reference, also cited by the main paper.
7. F. Labbaf, J. F. Groote, H. Hojjat, M. R. Mousavi, “Compositional Learning for Interleaving Parallel Automata,” FoSSaCS 2023, pp. 413–435. DOI: [10.1007/978-3-031-30829-1_20](https://doi.org/10.1007/978-3-031-30829-1_20). Related active-learning context as cited by the main paper; not a source of passive raw witness guarantees.
8. [Pinned GitHub source directory](https://github.com/Mahdi-Jadidi/passive-automata-learning/tree/7c90eb59561bd25ec4fdca5ac08b0e5d60d17fd/implementation/partition_feedback_final), relevant source inventory and blob IDs in §2.2; supplied enhanced ZIP and planted archives, `SCALE_REPORT.md`, `PLANTED_REPORT_FA.md`, source code and recorded measurement files. No repository files modified.

References 3–5 were independently checked against online bibliographic/publisher records during this assignment; references 6–7 are taken from the supplied paper's bibliography. This is a focused literature grounding, not an exhaustive novelty search.

Archive SHA-256 values for exact reproducibility:

```
partition-part1-planted-benchmark.zip  e328739aa0ffd4ad8d79792826ded298da38abb32394ee6694e671a4c7b9019e
partition-part2-planted-benchmark.zip  28bd9ec6f109810424e4bd38b48179692d08652f9f7dae5ae4515028800b5d35
partition-scale-improved(1).zip        595f928ef085f8decc9533404eeb3a8b458ff4e82e527e80d889c20fa55946ca
```

## Appendix A — executable reference pilot (the measured subset)

Save the following Python block as `sparse_pilot.py`. It requires only the Python standard library on Linux. This is the code used for the new measurements (filename changed for convenience); it is intentionally a small trusted-fixture research prototype. It handles disjoint positive/negative inputs; for full production edge-case handling and validation see §§1.2 and 8. It does not accept a hidden answer or external teacher. Do not run with assertions disabled. For other OSes adapt RSS measurement. The code has no enforced time/memory limits and should be run under process limits for arbitrary workloads. Hash matches are verified by exact erasure.

```python
import collections as C, itertools as I, json, sys, time, resource, random
MASK=(1<<64)-1; BASE=1000003

def signatures(w,powb):
    h=[0]; pos={}
    for k,a in enumerate(w):
        h.append((h[-1]*BASE+a+1)&MASK); pos.setdefault(a,[]).append(k)
    def cat(v,l,r): return (v*powb[r-l]+h[r]-h[l]*powb[r-l])&MASK
    yield None,(len(w),h[-1])
    for a,pp in pos.items():
        v=l=0
        for r in pp: v=cat(v,l,r); l=r+1
        yield a,(len(w)-len(pp),cat(v,l,len(w)))

def equal_delete(x,y,a):
    return tuple(t for t in x if t!=a)==tuple(t for t in y if t!=a)

def unique(words):
    d={}
    for i,w in enumerate(words): d.setdefault(w,i)
    return d

def deletion_join(xs,ys):
    P=unique(xs); Y=unique(ys); powers=[1]
    for _ in range(max(map(len,I.chain(P,Y)),default=0)): powers.append(powers[-1]*BASE&MASK)
    full=C.defaultdict(list); deleted=C.defaultdict(list); by_image=C.defaultdict(list)
    for x,j in P.items():
        for a,k in signatures(x,powers):
            if a is None: full[k].append(j)
            else: deleted[a,k].append(j); by_image[k].append((a,j))
    for y,i in Y.items():
        seen={}; support=set(y)
        for a,k in signatures(y,powers):
            if a is None:
                for b,j in by_image.get(k,()):
                    if b not in support and b not in seen and equal_delete(xs[j],y,b): seen[b]=j
            else:
                for j in I.chain(deleted.get((a,k),()),full.get(k,())):
                    if equal_delete(xs[j],y,a): seen[a]=j; break
        yield i,seen

def components(n,records):
    p=list(range(n)); size=[1]*n
    def find(a):
        while a!=p[a]: p[a]=p[p[a]]; a=p[a]
        return a
    def union(a,b):
        a,b=find(a),find(b)
        if a==b:return False
        if size[a]<size[b]:a,b=b,a
        p[b]=a;size[a]+=size[b];return True
    proof=[]; witnesses=0
    for i,d in records:
        witnesses+=len(d)
        if not d:continue
        a=next(iter(d))
        for b in d:
            if union(a,b): proof.append((i,a,d[a],b,d[b]))
    return [find(a) for a in range(n)],proof,witnesses

def sparse_root_check(xs,ys,root):
    def images(w):
        d={}
        for a in w:d.setdefault(root[a],[]).append(a)
        return {b:tuple(v) for b,v in d.items()}
    if not root:return not ys
    if not xs:return True
    pos=C.defaultdict(set); hits=C.Counter()
    for x in unique(xs):
        for b,v in images(x).items():pos[b].add(v);hits[b]+=1
    p=len(unique(xs)); universal=[b for b,k in hits.items() if k==p]
    for y in unique(ys):
        d=images(y)
        if any(v not in pos.get(b,()) for b,v in d.items()):continue
        if any(b not in d for b in universal):continue
        return False
    return True

def verify_edges(n,xs,ys,proof,expected):
    # Independent replay: direct erasures and graph traversal, not producer DSU.
    g=C.defaultdict(list)
    for i,a,j,b,k in proof:
        assert 0<=i<len(ys) and 0<=j<len(xs) and 0<=k<len(xs) and 0<=a<n and 0<=b<n and a!=b
        assert [v for v in xs[j] if v!=a]==[v for v in ys[i] if v!=a]
        assert [v for v in xs[k] if v!=b]==[v for v in ys[i] if v!=b]
        g[a].append(b);g[b].append(a)
    seen=set(); count=0
    for a in range(n):
        if a in seen:continue
        count+=1;seen.add(a);todo=[a]
        while todo:
            for b in g.get(todo.pop(),()):
                if b not in seen:seen.add(b);todo.append(b)
    assert count==expected==n-len(proof)

def pilot(path):
    t=time.perf_counter(); D=json.load(open(path)); idx={a:i for i,a in enumerate(D['alphabet'])}; n=len(idx)
    xs,ys=([tuple(idx[a] for a in w) for w in D[k]] for k in ('positive','negative'))
    assert not set(xs)&set(ys)
    t1=time.perf_counter();root,proof,w=components(n,deletion_join(xs,ys)); t2=time.perf_counter()
    ok=sparse_root_check(xs,ys,root);t3=time.perf_counter();k=len(set(root));verify_edges(n,xs,ys,proof,k);t4=time.perf_counter()
    print(json.dumps(dict(name=path.split('/')[-2],n=n,unions=len(proof),witnesses=w,root_blocks=k,raw_compatible=ok,encode_s=round(t1-t,4),discover_s=round(t2-t1,4),check_s=round(t3-t2,4),edge_replay_s=round(t4-t3,4),rss_mib=round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,2),edge_json_bytes=len(json.dumps(proof,separators=(',',':'))))))

def test():
    W=[w for k in range(5) for w in I.product(range(3),repeat=k)]; tests=0
    for x in W:
        for y in W:
            if x==y:continue
            got=next(deletion_join([x],[y]))[1]; want={a for a in range(3) if equal_delete(x,y,a)}
            assert set(got)==want,(x,y,got,want); tests+=1
    rng=random.Random(17);cases=0
    for _ in range(1000):
        x=rng.sample(W,rng.randrange(1,12)); y=rng.sample([w for w in W if w not in x],rng.randrange(1,12)); rec=list(deletion_join(x,y))
        for i,d in rec:assert set(d)=={a for a in range(3) if any(equal_delete(w,y[i],a) for w in x)}
        root,p,_=components(3,rec);verify_edges(3,x,y,p,len(set(root)))
        groups=set(root)
        literal=all(any(all(tuple(a for a in v if root[a]==b)!=tuple(a for a in w if root[a]==b) for w in x) for b in groups) for v in y)
        assert sparse_root_check(x,y,root)==literal;cases+=1
    print(json.dumps(dict(word_pairs=tests,random_corpora=cases)))
if __name__=='__main__':
    if sys.argv[1]=='--test':test()
    else:pilot(sys.argv[1])
```

Reproduce after extracting both planted archives to `bench/` and the enhanced package to `scale/`:

```sh
mkdir -p bench scale
unzip -oq partition-part1-planted-benchmark.zip -d bench
unzip -oq partition-part2-planted-benchmark.zip -d bench
unzip -oq 'partition-scale-improved(1).zip' -d scale
python sparse_pilot.py --test
for name in huge_long_active huge_reverse_unused large_reverse_dense large_reverse_pairs small_count; do
  python sparse_pilot.py "bench/planted_30s/$name/input.json"
done
for name in extra_interleaved extra_long_1024 extra_imbalanced_negative extra_imbalanced_positive; do
  python sparse_pilot.py "bench/planted_extra/$name/input.json"
done
```

Independent compatibility cross-check (the separate run used the same function and inputs, with adjusted local paths). Save as `check_pilot_roots.py`; import the checker only, never read reference or spec data:

```python
import sys, json
from collections import defaultdict
from sparse_pilot import deletion_join, components
sys.path.insert(0, 'bench')
from planted import compatibility

for path in sys.argv[1:]:
    D = json.load(open(path))
    ids = {a:i for i,a in enumerate(D['alphabet'])}
    xs, ys = ([tuple(ids[a] for a in w) for w in D[k]]
              for k in ('positive', 'negative'))
    root, edges, _ = components(len(ids), deletion_join(xs, ys))
    groups = defaultdict(list)
    for a,r in zip(D['alphabet'], root):
        groups[r].append(a)
    ok, failed = compatibility(D, list(groups.values()))
    print(path, ok, len(groups), failed)
    assert ok
```

```sh
python check_pilot_roots.py \
  bench/planted_30s/{huge_long_active,huge_reverse_unused,large_reverse_dense,large_reverse_pairs,small_count}/input.json \
  bench/planted_extra/{extra_interleaved,extra_long_1024,extra_imbalanced_negative,extra_imbalanced_positive}/input.json
```

The reference pilot is deliberately separated from the actual oracle adapter and has no permission to change external behavior. Its measured structural optimum fast path is a concrete implementation of the central sparse analysis contribution, while the rest of this report is the specification for integrating it into a certified exact partition-selection workflow.
