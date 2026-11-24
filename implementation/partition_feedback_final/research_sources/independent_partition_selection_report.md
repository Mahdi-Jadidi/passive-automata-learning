# Independent algorithmic analysis: partition selection from traces

## Executive conclusions

1. Raw traces can produce **zero regions** and **deletion witnesses** before any query. A zero region is a symbol set on which a negative and some positive have equal projections; every sub-block is therefore unable to reject that negative. Deletion witnesses turn this observation into a hitting-set lower bound on the number of symbols—and hence merges—needed in a rejecting block.
2. A `NO` response certifies the submitted partition incompatible. Its fixed-zero table columns also rule out exactly the partitions for which **one same negative** has every candidate block contained in some evidenced zero region. The regions may come from different blocks, tables, or raw witnesses. They may not be unioned, and zero evidence for different negatives may not be mixed to make one negative fail.
3. A `NO` does not rule out coarsenings. A verified `ACCEPT` incumbent permits cost-based branch cutoffs; without that incumbent the same cutoff is unsound. A canonical parent rule can omit redundant immediate merge edges while preserving a path to every partition.
4. Under the stated input model, query responses add no semantic facts that are unknowable from the raw traces: projections determine compatibility and every local rejection bit. Queries are valuable as paid evidence production or independent checks when raw analysis is deliberately bounded. That distinction should be explicit in any query-efficiency experiment.

This report assumes finite words over a declared finite alphabet and the compatibility rule in the problem statement. An empty positive list makes every partition compatible. If a negative word is identical to a positive word, no partition is compatible; otherwise the one-block partition is compatible, since its projection is the full word. These are inexpensive raw-trace checks.

## Notation and proof boundary

For negative trace `y_i`, define `Z_i(U)` to mean that some positive trace `x` has the same projection on `U`:

$$
Z_i(U) \iff \exists x\in S^+ : \pi_U(x)=\pi_U(y_i).
$$

If `Z_i(U)` holds and `B` is contained in `U`, projecting the equality again shows that `B` cannot reject `y_i`. The positive witness can be named and independently replayed. A raw witness, or a fixed-zero column for block `U` in a returned table, is an evidence item for `Z_i(U)`.

For an evidence ledger, let `Z_i` be the collection of evidenced zero regions for negative `y_i`, including raw regions and table regions. The precise zero-region exclusion closure is:

$$
\mathcal E_Z = \left\{P : \exists i\;\forall B\in P\;\exists U\in Z_i\text{ with }B\subseteq U\right\}.
$$

Every partition in this set is incompatible. This is the exact family licensed by this particular rule. It is not a claim that no other incompatibility follows from the raw words or the full table contents. In particular:

- all blocks must be covered for the **same** negative `y_i`;
- different blocks may use different zero regions and different positive witnesses;
- regions from different query tables may be combined;
- replacing two regions by their union is not licensed;
- a zero in one feasible table row is not a fixed zero and supplies no zero-region evidence.

A complete-partition query `Q` returning `NO` directly supplies a failing negative `y_i` and a matching positive witness on every block of `Q`; consequently every block of `Q` is a zero region for that negative. In addition, inspect every returned table column, not just the column for the failing negative. A column fixed at zero on a block adds a zero region for that column's negative.

## Analyze traces

### Raw zero regions and deletion witnesses

A particularly useful way to discover zero regions is to find symbol sets retained after deletion. If deleting `T` makes a positive `x` and negative `y_i` identical, then `U=Σ\\T` is a zero region. Any block that rejects `y_i` must intersect `T`; otherwise the block is contained in `U` and the matching projections survive.

For each negative and positive pair, collect the inclusion-minimal deletion sets witnessed this way. Equivalently, enumerate the inclusion-maximal retained sets `U` for which the projections are equal, and take their complements. Call the resulting family for negative `y_i` `H_i`. Every block `B` that rejects `y_i` must hit every set in `H_i`.

If `H_i` contains the empty deletion set, the full positive and negative words are equal, so that negative can never be rejected. Otherwise let `τ(H_i)` be the size of a minimum hitting set. A compatible partition must contain a block of size at least `τ(H_i)`, and therefore:

$$
c(P)=\sum_{B\in P}(|B|-1)\geq \max_i\max(0,\tau(H_i)-1).
$$

This is a lower bound, not a sufficiency test: hitting every deletion witness does not guarantee that the projections actually differ.

Overlapping witnesses matter. For example, the family `{a,b}`, `{b,c}` has a size-one hitting set `{b}`. Counting one merge per witness would overstate the necessary cost. In contrast, `{a}`, `{b}` forces a rejecting block to contain both `a` and `b`, so at least one merge is required. With `{a,b}` and `{c,d}`, a minimum transversal chooses one symbol from each set: it proves one merge is needed but forces no particular cross-pair merge.

The bound can be strengthened across negatives without incorrectly charging a separate block to every obligation. For any proposed block `B`, define `J(B)` to be the set of negatives whose every witness set in `H_i` is hit by `B`. A single block may cover several negatives. The following finite dynamic program finds the minimum cost of a partition satisfying these **necessary** witness-cover conditions; it is therefore a lower bound on the true optimum. Let `R` be the remaining symbols and `C` the negatives already covered. Choose the least remaining symbol `s` to avoid duplicate block orderings:

$$
F(R,C)=\min_{\substack{B\subseteq R,\;s\in B}}
\left(|B|-1+F(R\setminus B,\;C\cup J(B))\right),
$$

with `F(∅,C)=0` when all negatives are covered and `F(∅,C)=∞` otherwise. Every real compatible partition is among the partitions permitted by this relaxed recurrence, so its cost is at least `F(Σ,∅)`. This is a custom subset dynamic program, not a SAT/SMT formulation or external solver. Its state count is at most exponential in the alphabet and negative count; branch-and-bound can be used instead when the witness families are sparse.

### Discovering witnesses without hidden groups

A transparent, deliberately conservative witness-discovery procedure is:

1. For each negative trace and each positive trace, enumerate all subsets `U` of the declared alphabet.
2. Project both words onto `U`; retain `U` if the projections are equal.
3. Discard any retained set strictly contained in another retained equal-projection set. The complements of the remaining sets are inclusion-minimal deletion witnesses.
4. If a complement is empty, record immediate impossibility. Otherwise, add the witnesses to that negative's family, removing duplicates and supersets that are redundant for hitting.
5. Run a hitting-set branch-and-bound search. At each step choose an unhit witness set, branch on selecting each of its symbols, and keep the best transversal found. Preserve the search tree (or a dynamic-programming table) if an exact minimum transversal is used in the certificate. For a short certificate, a pairwise-disjoint subfamily of size `k` proves the lower bound `τ≥k`; exhibit a size-`k` transversal to prove equality.

The naive projection scan costs `O(2^|Σ| (|x|+|y|))` per positive-negative pair, plus the cost of retaining and reducing the witness sets. Exact hitting set and the joint block-cover recurrence are also exponential in the worst case. This cost is intentional and must be reported: the hidden construction is not needed, but discovering its witness structure may be expensive. A cheaper partial analyzer can return only some witnesses; its lower bound remains sound, though possibly weaker.

### Strong result: witness-cover lower-bound theorem

**Theorem.** For each negative `y_i`, let `H_i` consist of deletion sets `T` for which a positive `x` satisfies `π_{Σ\\T}(x)=π_{Σ\\T}(y_i)`. If a partition `P` is compatible, then for every `i` it has a block that intersects every member of `H_i`. Consequently its cost is at least `τ(H_i)-1` for each `i` with a finite, nonempty witness family. More generally, `F(Σ,∅)` from the joint recurrence above is a lower bound on the cost of every compatible partition.

**Proof.** Fix a compatible partition and a negative `y_i`. By compatibility there is a block `B` whose projection of `y_i` differs from the projection of every positive. Consider any `T∈H_i`, witnessed by some positive `x` with equal projections after retaining `Σ\\T`. If `B∩T=∅`, then `B⊆Σ\\T`; projecting the witnessed equality down to `B` gives `π_B(x)=π_B(y_i)`, contradicting the choice of `B`. Thus `B` hits every `T∈H_i`, so `|B|≥τ(H_i)`. The block contributes `|B|-1` merges to the partition cost, proving the per-negative bound. For the joint recurrence, assign each negative to one block that witnesses its compatibility. Each such block belongs to the recurrence's permitted cover because it hits all the corresponding deletion witnesses. The actual blocks therefore form a feasible solution of the relaxed recurrence with the same cost. The recurrence minimizes over all such relaxed covers, so its value cannot exceed the actual optimum. ∎

### Worked search transcript for the theorem

Use `Σ={a₁,a₂,b₁,b₂,c₁,c₂}`, positives `{a₁a₂,b₁b₂,c₁c₂}`, and negative `{ε}`. The subscripts distinguish symbols; each positive word has length two.

| Evidence ID | Source and fact | Consequence |
|---|---|---|
| `R1` | Raw projection: the positive `a₁a₂` and negative `ε` agree after deleting `{a₁,a₂}`. | Any rejecting block for `ε` must hit `{a₁,a₂}`. |
| `R2` | Raw projection: the positive `b₁b₂` and negative `ε` agree after deleting `{b₁,b₂}`. | Any rejecting block for `ε` must hit `{b₁,b₂}`. |
| `R3` | Raw projection: the positive `c₁c₂` and negative `ε` agree after deleting `{c₁,c₂}`. | Any rejecting block for `ε` must hit `{c₁,c₂}`. |
| `R4` | The three witness sets are pairwise disjoint; choosing `{a₁,b₁,c₁}` hits all three. | A rejecting block needs at least three symbols, and the witness transversal has size three. Thus the cost lower bound is two. |
| `Q1` | Fresh complete-partition query of `{a₁b₁c₁}|{a₂}|{b₂}|{c₂}` returns `ACCEPT`. | The queried partition is compatible and has cost two. |

**Transcript conclusion.** The singleton partition is **inferred incompatible** from `R1`–`R3`: no singleton block can hit all three disjoint witnesses. Every partition of cost zero or one is **inferred incompatible** from `R4`, since a cost-one partition has no block of size three. The partition `{a₁b₁c₁}|{a₂}|{b₂}|{c₂}` is **queried**, and `Q1` verifies compatibility. Its cost equals the raw lower bound, so it is optimal. The optimality certificate is the three raw witness equalities, their disjointness, the explicit compatible partition and its `ACCEPT` response.

No particular symbol pair is co-blocked in every compatible solution: for any two symbols, choose a size-three transversal that avoids selecting both, then make every unselected symbol a singleton. The resulting partition remains compatible. Thus raw traces prove a cost threshold without forcing a fixed pair merge in all solutions. The support sets above were discovered by projection enumeration; they were not supplied as hidden groups.

### Decision table: Analyze traces

| Rule ID | Observed pattern and evidence source | Action or next complete query | Exactly which partitions are ruled out | Short proof | Example |
|---|---|---|---|---|---|
| `A1` — **incompatibility deduction** | Raw full-word equality between a positive and a negative. | Stop: report no compatible partition; no query can repair this. | Every partition. | Projection onto all of `Σ` is equal, so every block projection is equal as well. | A positive and negative both equal `abc`. |
| `A2` — **incompatibility deduction** | Raw zero regions `U∈Z_i`, possibly with different positive witnesses. | Mark a candidate incompatible when each of its blocks is contained in an evidenced zero region for the same negative. | Exactly the raw-data portion of `𝓔_Z`. | Each candidate block has a matching positive projection for that negative, so that negative has no rejecting block. | For negative `ε`, positive `ab`, and positive `cd`, `ab` and `cd` are zero regions witnessed by the opposite positive. |
| `A3` — **incompatibility deduction** | Equal projections after deleting sets `T`; source is raw traces. | Add each `T` as a hitting obligation. If the required block-size or merge lower bound exceeds a candidate's cost, rule it out; query a minimum-cost candidate only after lower-cost alternatives are accounted for. | All partitions below the certified witness-cover cost bound; optionally all candidates failing a stronger joint cover bound. | A rejecting block must intersect every deletion witness. A disjoint witness packing gives a checkable lower bound; a hitting set gives a matching upper bound when tight. | Three disjoint two-symbol supports force a block of size at least three, hence cost at least two. |
| `A4` — **incompatibility deduction** | Equal singleton-symbol counts, repeated-symbol differences, or order differences in raw projections. | Treat these as projection witnesses; compute maximal retained equal-projection sets and their complements rather than assuming symbols are interchangeable. | The same zero-region and witness-cover families as above. | Counts decide singleton projections; joint projection order decides larger blocks. Any retained set with equal projections supplies a complement witness. | `abc` versus `bac` has equal singleton projections but equal projections on `{a,c}` and `{b,c}`, forcing a rejecting block to contain both `a` and `b`. |
| `A5` — **incompatibility deduction** | Witness families from several negatives overlap, or one possible block hits witnesses for several negatives. | Use the joint block-cover recurrence or an explicit disjointness/cover certificate; do not add one merge per witness or per negative automatically. | All partitions whose cost is below the joint witness-cover lower bound. | A shared block can satisfy multiple negative obligations; the recurrence permits this and therefore remains a valid relaxation. | Witnesses `{a,b}` and `{b,c}` can both be hit by `{b}`. |
| `A6` — **query-ranking heuristic** | Raw scan is partial or expensive; unresolved candidates remain. | Rank a complete candidate partition by likely zero-region coverage, cost relevance, and chance of a useful `ACCEPT`; state that estimates are heuristic. | None before the response. | A predicted table is not evidence. Only a returned table or raw witness can exclude a partition. | Prefer a query whose expected fixed-zero blocks cover many blocks of low-cost candidates, rather than one that only repeats a known singleton result. |

## Select partition after NO

### The exact zero-region closure of a response

For each returned table block `U` and each negative column `i`, inspect the whole column. If every feasible row has zero, record `U∈Z_i`. A single zero in one row is insufficient. If the column is not fixed zero, that table does not supply a zero region for that block and negative. The equality constraints between negative columns may explain why bits move together, but they do not turn one zero row into a fixed-zero column.

For an unqueried partition `P`, the response evidence rules it out by this rule **if and only if** the evidence ledger contains a single negative `y_i` such that every block `B` of `P` is contained in at least one recorded zero region for `y_i`. This is precisely membership in `𝓔_Z` above. For one `NO` response whose only zero regions are its queried blocks, this includes every refinement of the queried partition. The count of those refinements is the product of the Bell numbers of its block sizes:

$$
\prod_{U\in Q}\operatorname{Bell}(|U|).
$$

The count includes the queried partition itself. It does **not** include coarsenings, unless separate evidence covers their larger blocks. With multiple responses, take the union of their zero-region closures. A candidate may be covered by regions from different responses, as long as all of its blocks are covered for the same negative.

A fixed-zero table column for some negative other than the one causing the query's `NO` is useful. For example, if one table fixes negative `y_j` to zero on one block and a later table fixes `y_j` to zero on another candidate block, those two facts can exclude a candidate for `y_j`. Zero columns for `y_i` and `y_j` cannot be mixed to show that either one has no rejecting block.

### Four distinct decisions and their proofs

1. **Declare the queried partition incompatible.** The response names a failing negative and a matching positive on each queried block. Every block therefore fails to reject that negative. This is the direct certificate for that one partition.
2. **Rule out an unqueried family.** Use fixed-zero regions and the containment test above. The proof is blockwise and uses one common negative. In the special case of a single query's block regions, all refinements are ruled out. No coarsening follows from this argument.
3. **Close a search branch using an incumbent.** First obtain a verified compatible incumbent `P*` of cost `C`. If every completion in a branch has a proved lower bound at least `C`, the branch cannot improve the incumbent and can be closed. The simple bound is the current node's cost, since merges only increase cost; a stronger admissible completion lower bound may be used. The incumbent must be verified, and the lower bound must apply to every completion in that branch.
4. **Omit a redundant immediate child but preserve every target partition.** Use a canonical search tree, not an outcome-based guess. Order symbols. For any nonsingleton partition `R`, find its first nonsingleton block `D` (by least block minimum), split the largest symbol of `D` into a singleton, and call the result the parent of `R`. This is a unique one-merge parent. Repeating the operation reaches the singleton partition. Generate from a node only those one-merge children for which it is the canonical parent. Every partition has exactly one such path, so omitting the other immediate merge edges preserves a path to every optimum. This rule removes duplicate search paths; it does not claim that a particular merge is irrelevant to compatibility.

The dangerous confusion is treating a `NO`-excluded refinement family as a whole upward branch. In the required four-symbol example below, `ab|cd` is `NO`, but the coarsening `abcd` is compatible, and the optimum is a cross-pair merge of cost one. Treating the `NO` as an incumbent cutoff or as evidence against coarsenings would lose the optimum.

Compatibility is monotone under merging blocks: if a block rejects a negative, any larger block containing it also rejects that negative, because equality on the larger block would imply equality on the smaller one. Thus every coarsening of an `ACCEPT` partition is compatible, though it cannot improve that partition's cost. This is a safe ancillary inference; an `ACCEPT` does not make finer partitions compatible.

### Decision table: Select partition after NO

| Rule ID | Observed pattern and evidence source | Action or next complete query | Exactly which partitions are ruled out | Short proof | Example |
|---|---|---|---|---|---|
| `N1` — **incompatibility deduction** | `NO` response with failing negative and one matching positive witness per submitted block. | Mark only the submitted complete partition incompatible; retain all witness IDs. | The queried partition itself. | No block of that partition separates the named negative from all positives. | Query `ab|cd`; `ab` matches positive `cd` on `ε`, and `cd` matches positive `ab` on `ε`. |
| `N2` — **incompatibility deduction** | A returned table column is fixed zero on a block; source is that table. | Add the block as a zero region for that negative. Apply the same-negative containment test. | Exactly the newly covered candidates in `𝓔_Z`; with only query blocks, all refinements of the query. | Equal projections on a region remain equal on every sub-block. | From `ab|cd` with negative `ε`, infer the refinements `ab|c|d` and `a|b|cd` are incompatible. |
| `N3` — **incompatibility deduction** | Two or more raw/table/query evidence items give zero regions for one negative. | Combine by block containment, allowing different evidence IDs for different blocks. | Every candidate for which all blocks are covered by the union of that negative's zero-region evidence; no others by this rule. | Each block separately has a matching positive projection for the same negative. | `ab` covered by one table and `cd` by another rules out `ab|cd`, though neither table alone does. |
| `N4` — **incumbent-dependent cutoff** | Verified `ACCEPT` incumbent of cost `C`, plus a branch lower bound `L≥C`. | Close that branch; otherwise keep searching. | Only descendants covered by the proved lower bound. | No completion can have cost below the verified incumbent. A `NO` response alone is not such a lower bound. | A node already of cost `C` cannot produce a strictly better solution by further merges. |
| `N5` — **path-preserving branching rule** | Canonical parent relation on partitions; source is the search-tree definition, not a query table. | Generate only canonical children. | No partition is ruled out; only duplicate edges are omitted. | Every partition has a unique parent chain to the singleton partition. | Split the largest symbol from the first nonsingleton block to define each unique parent. |
| `N6` — **query-ranking heuristic** | Unresolved candidate set and a predicted distribution of `ACCEPT`, `NO`, and `INCOMPLETE`; estimates may use raw summaries. | Submit one complete partition maximizing expected weighted candidate elimination plus incumbent value per query cost. If probabilities are uncalibrated, use robust bounds or report a heuristic score. | None until a response arrives. | A forecast is not evidence; only the actual `NO` tables or `ACCEPT` response change the proof ledger. | Query a partition whose blocks are expected to become broad zero regions for negatives shared by many low-cost candidates. |

### What to do after each outcome

- **`ACCEPT`:** record the submitted partition and its cost as a verified incumbent. Its coarsenings are also compatible, but have no lower cost. Close only branches whose admissible lower bounds cannot beat the incumbent. To certify optimality, account for every lower-cost candidate by a raw witness, a table closure, or a valid lower-bound certificate.
- **`NO`:** store the failing negative, its positive witness for each block, and all table rows. Mark the queried partition incompatible, extract every fixed-zero column on every block, add those regions to the evidence ledger, and recompute the containment closure. Do not infer anything about a candidate block that crosses all known zero-region boundaries.
- **`INCOMPLETE`:** add no incompatibility or compatibility facts and do not close a branch. Choose a different complete query if it is more informative; retry only under a separately justified operational policy. An incomplete result is not a weak `NO`.

### Counterexamples to plausible but unsound rules

- **Unsound:** “A zero in one feasible row means fixed zero.” **Why it fails:** the supplied semantics explicitly allow a column to be zero in one feasible row and one in another. Only all-zero across every row proves a fixed zero. This distinction is essential when reading tables for negatives other than the one that caused the `NO`.
- **Unsound:** “A `NO` at `Q` rules out every coarsening of `Q`.” **Counterexample:** with positives `{ab,cd}` and negative `{ε}`, `ab|cd` is `NO`, but the one-block partition `abcd` is compatible: both positive projections are nonempty and differ from `ε`.
- **Unsound:** “Close a branch as soon as its current cost reaches a guessed target.” **Why it fails:** without a verified compatible incumbent, there is no upper bound to compare against. A branch may contain the optimum. Even with an incumbent, the cutoff must be a lower bound on all completions, not a guess.
- **Unsound:** “Every witness obligation costs one separate merge.” **Counterexample:** witness sets `{a,b}` and `{b,c}` share `b`; a block containing only `b` hits both. The transversal number, not the number of witnesses, is the relevant basic bound.
- **Unsound:** “Discard every merge that immediately separates zero additional negatives.” **Counterexample:** for positives `{ab,cd,ef}` and negative `{ε}`, every compatible solution needs one block intersecting all three disjoint supports. A size-two merge hits at most two supports and rejects no negative; adding a third selected symbol creates a size-three block that does. Discarding all zero-immediate-gain merges destroys every optimal path of cost two.

## Required examples

### 1. Four symbols: singleton query, then `ab|cd`

Let `Σ={a,b,c,d}`, positives `{ab,cd}`, and negative `{ε}`. Write partitions in the stated block notation.

**First query.** Query `a|b|c|d`. It returns `NO`. On block `a` and block `b`, positive `cd` projects to `ε`; on block `c` and block `d`, positive `ab` projects to `ε`. Thus all four singleton table columns for the only negative are fixed zero. The first response certifies only the singleton partition by direct query and its refinement closure, which has no other partition.

**Second query.** Query `ab|cd`. It returns `NO`: on block `ab`, positive `cd` projects to `ε`; on block `cd`, positive `ab` projects to `ε`. Both block columns are fixed zero for the negative.

The second response certifies exactly these partitions by its own zero-region closure:

| Partition | Status with respect to the second response | Evidence |
|---|---|---|
| `ab|cd` | Queried and incompatible. | `N1`: `ab` matches positive `cd`; `cd` matches positive `ab`. |
| `ab|c|d` | Inferred incompatible; unqueried. | `N2`: `ab` lies in zero region `ab`; `c` and `d` lie in zero region `cd`. |
| `a|b|cd` | Inferred incompatible; unqueried. | `N2`: `a` and `b` lie in zero region `ab`; `cd` lies in zero region `cd`. |
| `a|b|c|d` | Already known incompatible from the first query; also a refinement inferred from the second. | First query's direct witness; second query's containment closure. |

There are no other refinements of `ab|cd`: a refinement independently partitions its two-symbol blocks, giving four total partitions. Under a **query-only evidence ledger**, the two proper refinements and `ab|cd` itself were not certified by the first singleton response and remained conjectures until the second response. Under a **full raw-analysis ledger**, they need not remain conjectures: raw projections already give zero regions `ab` (positive `cd`) and `cd` (positive `ab`), which cover all three. This distinction is important because Analyze traces has access to the raw words.

**Optimal answer and certificate.** Choose `ac|b|d`, of cost one. Its block `ac` projects the positives to `a` and `c`, while the negative projects to `ε`; hence that single block separates the negative from every positive. For a lower bound, the positive `ab` and negative `ε` agree after deleting `{a,b}`, and positive `cd` and negative `ε` agree after deleting `{c,d}`. These two disjoint witnesses require a rejecting block to contain at least one symbol from each set, so every compatible partition has cost at least one. The candidate attains the bound. A fresh query of `ac|b|d` may provide an independent `ACCEPT`; otherwise the projection witnesses themselves are directly checkable from the raw traces.

### 2. Same singleton tables, different order witnesses

Compare positives `{abc}` with either negative `bac` or negative `acb`. On every singleton block, the positive and negative projections are the same one-symbol word. Thus the singleton query's rejection tables are identical: all three columns for the sole negative are fixed zero, with the same positive trace ID as witness. Select partition, given only those tables and IDs, cannot distinguish which pair merge is useful.

Raw order does distinguish them:

- For `abc` versus `bac`, the equal retained sets `{a,c}` and `{b,c}` have complements `{b}` and `{a}`. A rejecting block must hit both singleton witnesses, so it must contain `a` and `b`. The merge `ab|c` separates: `ab` projects to `ab` versus `ba`.
- For `abc` versus `acb`, equal retained sets `{a,b}` and `{a,c}` have complements `{c}` and `{b}`. A rejecting block must contain `b` and `c`. The merge `bc|a` separates: `bc` projects to `bc` versus `cb`.

The distinguishing extra fact is the raw order (or the complement-witness sets derived from it). A complete query of `ab|c` also distinguishes the instances: it is `ACCEPT` for `bac` and `NO` for `acb`. Three symbols are minimal for this type of different-pair example: with two symbols there is only one possible pair merge.

Repeated occurrences fit the same framework. Singleton projections compare counts, so a count mismatch can immediately separate a pair on a singleton block; equal counts do not imply equal multi-symbol projections. For example, `aa` and `a` differ on `{a}`, while `abc` and `bac` have equal one-symbol counts but differ on `{a,b}` by order.

### 3. No-immediate-gain merges can be necessary

Let positives be `{ab,cd,ef}` and the negative be `{ε}`. For the positive `ab`, deleting `{a,b}` makes it equal to `ε`; likewise the other two positives give witnesses `{c,d}` and `{e,f}`. A rejecting block must hit all three pairwise-disjoint witness sets, so it contains at least three symbols and costs at least two merges. A block such as `{a,c,e}` hits all three and rejects `ε` from every positive, so this lower bound is attainable.

Starting from all singletons, no pairwise merge can hit all three witness sets. In particular, the first merge along any path to a size-three transversal block rejects zero additional negatives. Discarding every such merge does **not** preserve an optimal path.

## Diagnostic complete-partition queries

### How to propose and rank them

A query must be a complete partition. A practical ranking procedure is:

1. Maintain the unresolved candidate partitions, their costs, and the current verified incumbent, if any.
2. For each proposed complete partition `Q`, predict possible outcome-specific zero regions from the raw facts already computed. A `NO` response guarantees zero regions for every block for its failing negative and may expose fixed-zero columns for other negatives.
3. For each plausible failing negative, estimate the weighted number of candidates whose every block would be contained in those regions. Count unique candidates in the union, not one count per table cell. Use larger weights for lower-cost candidates if the immediate goal is proving optimality.
4. Estimate the chance that `Q` returns `ACCEPT` and the value of its cost as an incumbent. Include `INCOMPLETE` probability if operationally relevant.
5. Rank by expected weighted eliminations plus incumbent value per query cost. If probabilities are not calibrated, report a range or use a conservative worst-case score. A score is only a query heuristic; do not prune until the actual response arrives.

A good diagnostic query is often one whose blocks are unions of symbols that appear together in many unresolved candidates' possible rejecting blocks. The query's own cost matters: a very coarse `NO` may exclude many refinements but be irrelevant to the lower-cost region being proved. Tables for other negatives can increase value substantially, so estimate the full table outcome rather than only the likely failing-negative column.

### Zero, one, and two query comparison

The following count isolates **table-derived closure**, not the power of full raw analysis. Use six symbols and the two candidate query partitions `Q₁=abc|def` and `Q₂=abcd|ef`. Let `F(Q)` denote the partitions refining `Q`.

- `|F(Q₁)| = Bell(3)·Bell(3) = 25`.
- `|F(Q₂)| = Bell(4)·Bell(2) = 30`.
- `|F(Q₁)∩F(Q₂)| = Bell(3)·Bell(1)·Bell(2) = 10`, from the common refinement `abc|d|ef`.
- Therefore `|F(Q₁)∪F(Q₂)| = 25+30−10 = 45`.

For a concrete input on which both queries return `NO`, take positives `{a,b,c,d,e,f}` as six one-symbol words and negative `{ε}`. Each block of either query is a proper subset of the alphabet; a positive symbol outside that block projects to `ε`, so the negative is not rejected on that block.

| Diagnostic queries paid | Mathematical family excluded by their tables | Queried partitions inside that family | Unqueried candidates actually skipped by inference | Paid diagnostic queries |
|---:|---:|---:|---:|---:|
| Zero | 0 | 0 | 0 | 0 |
| One, query `Q₂` | 30 | 1 | 29 | 1 |
| Two, query `Q₂` and then `Q₁` | 45 | 2 | 43 | 2 |

These are different quantities: the family size includes the queried partition; skipped candidates exclude it; query count is the paid evidence-gathering cost. The second query adds 15 new mathematical exclusions beyond `Q₂`, of which 14 are unqueried candidates skipped.

**Important limitation.** In this particular six-symbol input, exhaustive raw analysis can see that every proper symbol subset has an empty projection for some positive singleton trace. It can therefore rule out every multi-block partition before either query; the one-block partition is compatible. The table counts deliberately measure only the marginal value of the two returned tables in a restricted evidence ledger. If raw analysis has already computed those facts, the queries have no semantic information value and are not worth paying for unless an independent check is itself required. Any experiment comparing zero, one, and two queries should report the cost and coverage of Analyze traces separately.

### Two tables can jointly rule out a partition

Let positives be `{a,b,c,d}` as four one-symbol traces and negative `{ε}`. Consider these two `NO` queries:

- `T1`: query `ab|c|d`. Its table fixes the negative column to zero on all three blocks.
- `T2`: query `a|b|cd`. Its table also fixes the negative column to zero on all three blocks.

The unqueried candidate `ab|cd` is not a refinement of `T1`, because its `cd` block crosses the singleton blocks `c` and `d`; nor is it a refinement of `T2`, because its `ab` block crosses `a` and `b`. Neither response alone rules it out by zero-region containment. Together they do: `ab` is contained in the `ab` region from `T1`, and `cd` is contained in the `cd` region from `T2`, for the same negative. The positive witnesses can differ by region. This is a response-combination proof, though a full raw analyzer could of course find the same matching projections before querying.

## Challenge cases and limits

### Identical tables do not determine the next merge

The singleton tables for `abc` versus `bac` and `abc` versus `acb` are identical, but the optimal useful merges differ (`ab` versus `bc`). Therefore no rule that chooses an optimal next merge solely from those observed singleton tables and trace IDs can be correct on both inputs. Raw word order or a discriminating complete query is additional information required.

### Why a table row is not a column certificate

A feasible row records one jointly feasible assignment of local bits. A bit zero in that row says only that the negative is not rejected under that assignment. If another feasible row has bit one, the column is not fixed zero. The required proof for a zero region is all-zero across every feasible row, or an explicit raw equality witness. This also explains why table correlations across negative columns must be read exactly rather than interpreted as independent local observations.

### Exclusion and search accounting

For every candidate, record one of these statuses rather than using a generic “pruned” label:

- **Queried incompatible:** direct `NO` witness IDs for every block of the failing negative.
- **Inferred incompatible:** one negative ID plus, for each candidate block, a zero-region evidence ID and containment check.
- **Branch cutoff:** a verified incumbent ID and an admissible lower-bound proof for all descendants.
- **Not generated as an edge:** canonical-parent evidence that another path still reaches the same partition.
- **Unresolved:** no valid proof; keep it or query it.

This ledger prevents an infeasibility fact from being mistaken for an objective cutoff and prevents a duplicate-edge optimization from being mistaken for a compatibility deduction.

## Exhaustive small-instance checks

I checked the witness lower bound and the `NO`-refinement rule by enumerating every partition on small alphabets, independently computing compatibility from projected words.

**Observed results.** Over three symbols, the test set comprised all 8,281 ordered positive/negative trace-list pairs where each list contains one or two distinct words chosen from the 13 words of length at most two. All five partitions were checked for each instance. The per-negative witness lower bound never exceeded the true minimum compatible cost; infeasible instances were also identified by an empty deletion witness. Across the same instances, 33,693 `NO`/refinement pairs were checked and every refinement of a `NO` partition was incompatible. Separately, a seeded random check covered 250 additional three-symbol trace instances and 293 `NO`/refinement pairs over two- and three-symbol alphabets. Exact set-count enumeration confirmed the six-symbol family counts `203`, `25`, `30`, `10`, and `45` used above.

**What these checks do not establish.** They are finite sanity checks, not proofs; they do not test large alphabets, the joint recurrence's runtime, incomplete witness extraction, calibration of query-outcome probabilities, or implementation costs. The theorem and the containment arguments above are the proofs. The query-efficiency comparison is a mathematical prediction conditional on the specified `NO` outcomes, not a measured production workload.

## Result ready to state as a theorem

A concise theorem suitable for discussion is:

> **Projection-witness lower-bound and exclusion theorem.** For every negative-positive pair and every retained symbol set on which their projections agree, the complement is a necessary hitting obligation for any block that rejects that negative against that positive. Consequently, any compatible partition's cost is at least the minimum witness-cover cost obtained by partitioning the alphabet into blocks that collectively hit all witness families for all negatives. Independently, any evidence ledger of fixed-zero regions excludes exactly those partitions for which all blocks are contained in regions for one common negative. A complete `NO` query supplies such regions for its blocks and its fixed-zero table columns, but licenses no conclusion about coarsenings. A verified `ACCEPT` incumbent plus a valid lower bound may close branches whose completions cannot improve it.

## Policy choices for experiments and the main open question

**Policy choices that need experiments:** how many maximal equal-projection sets to enumerate before returning a partial witness family; whether to use exact hitting-set search, disjoint witness packing, or the joint block-cover DP; how to weight low-cost candidates in query ranking; how often returned tables expose fixed-zero columns for negatives other than the failing one; and whether query cost is mostly latency, human review, or compute. Report each separately from the mathematical number of partitions excluded.

**Most consequential open question:** can one compute a compact, independently checkable witness-cover certificate that is usually tight for realistic trace collections, without paying the worst-case exponential cost of maximal-projection enumeration and the joint block-cover search? The theorem provides a sound lower bound, but its practical value depends on certificate size and tightness. A useful next experiment would compare the witness-cover bound, zero-region closure, and actual optimum over structured and adversarial trace families, while charging the raw-analysis and query costs separately.