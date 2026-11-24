# Choosing an optimal alphabet partition from trace evidence

**Three answers.** Before querying, compare counts and two-symbol projections. They give a complete description of every positive–negative discrepancy, including discrepancies involving repeated occurrences. Partial comparisons can already force merges or prove a cost floor without forcing any particular pair. After a NO, the key is to keep evidence indexed by the **original negative**, not just by the partition that failed. In isolation, one NO with opaque trace IDs rules out **exactly the refinements of the submitted partition**. With history or raw facts, the exclusion can be strictly larger. For a diagnostic, submit a complete partition whose blocks test several still-relevant candidates; rank it by the ordinary queries it is expected to *replace*, not the number of mathematical refinements it has.

There are two distinct information regimes. If Analyze supplies the complete discrepancy description, Select can solve the problem with **zero oracle queries**. Diagnostics make sense when producing, passing, or using all those facts is more expensive than asking questions. The comparisons below say exactly which regime they use.

## 1. Objects, orientation, and evidence

Let \(n=|\Sigma|\), and let \(P\preceq F\) mean that **\(P\) refines \(F\)**: each block of \(P\) lies inside a block of \(F\). The search moves toward coarser partitions by merging two blocks. Write \(ab/c/d\) for \(\{a,b\}\mid\{c\}\mid\{d\}\); a word such as \(ab\) inside a trace list still denotes an ordered word. Lower cost \(c(P)=n-|P|\) is better.

For negative \(y\), call a set \(B\) **dead for \(y\)** if some positive \(x\) has \(\pi_B(x)=\pi_B(y)\); otherwise it is **separating for \(y\)**. Deadness goes down under inclusion; separation goes up. Thus compatibility goes up under coarsening and incompatibility goes down under refinement. Crucially, a rejecting block must defeat **all** positives for one negative. Rejecting blocks need not be the same across negatives; matching positives need not be the same across blocks.

**Evidence convention.** Raw evidence consists of trace IDs, symbol sets, and a comparison the verifier can repeat. Table evidence names the response, its block, and the original negative column; a reported positive ID gives a direct equality witness. A fresh query is always of a **complete** partition. An inferred verdict is not a paid query. No reasoning below treats INCOMPLETE as NO.

## 2. What to extract before querying

### The small comparison that preserves all order information

For each positive–negative pair \((x,y)\), form its **discrepancy atoms** \(D_{yx}\):

1. Include \(\{a\}\) if the counts of \(a\) differ.
2. For two distinct symbols with equal individual counts in the two words, include \(\{a,b\}\) if their two-symbol projections differ. Pairs already containing a discrepant singleton are redundant.

For every symbol set \(B\), the exact test is:

$$
\pi_B(x)\ne\pi_B(y)\quad\Longleftrightarrow\quad \exists D\in D_{yx}: D\subseteq B.
$$

**Proof.** Further projection proves the reverse implication. For the forward implication, assume no atom is contained in \(B\). Label each occurrence of a retained symbol by its symbol and occurrence number. Unary agreement gives the same labeled occurrences in both words. Two occurrences of the same symbol have fixed order; two of different symbols have the same relative order because their two-symbol projections agree. Hence the entire ordered list of labeled occurrences agrees. This also covers empty projections. For example, \(aba\) and \(aab\) have the same counts and the same order of *first* appearances, but the second \(a\) changes sides of the \(b\). Their atom is \(\{a,b\}\).

A block separates \(y\) precisely when it contains an atom **for every** positive \(x\). This need not be the same atom for every positive. Conversely, if deleting \(T\) makes \(x,y\) equal, then \(T\) meets every atom of \(D_{yx}\), and every separating block must meet \(T\). These are equivalent ways of looking at the same pair of words: if \(B\) contains no atom, \(T=\Sigma\setminus B\) is itself an equality-producing deletion disjoint from \(B\). A *partial* list of deletion witnesses gives necessary conditions only.

### Analyze traces

Rule types: **I** = incompatibility deduction; **C** = incumbent-dependent cutoff; **B** = path-preserving branching rule; **H** = query-ranking heuristic. The action column is operational; the exclusion column is deliberately narrower where an action is not a proof.

| Rule ID | Observed pattern and evidence source | Action or next complete query | Exactly which partitions are ruled out | Short proof | Example |
|---|---|---|---|---|---|
| A1 · I | Raw: counts and ordered two-symbol comparisons for each \((y,x)\). | Test whether any block contains an atom for every positive. | Exactly the incompatible partitions if all comparisons are available: for some \(y\), every block misses every atom of at least one positive. | Occurrence-order proof above. | With positive \(abc\) and negative \(bac\), all partitions keeping \(a,b\) apart fail. |
| A2 · I | Raw: deletions \(T_j\), each with an equality witness for the **same** \(y\); positives may differ. | Require one block to hit every \(T_j\). | All partitions with no such block. Being a hitting block is not by itself a proof of acceptance. | A block disjoint from \(T_j\) inherits its equality. | With positives \(ab,cd\) and negative \(\epsilon\), a block must hit both supports. |
| A3 · I | Raw: deleting each of several individual symbols, separately, gives a match for the same \(y\). | Put all those symbols in the same required block; take the transitive closure of proved co-memberships. | Every partition splitting a required class. | Each singleton deletion forces that symbol into *every* block separating its negative. Co-membership is transitive even when the proofs use different negatives. | Deleting either \(a\) or \(b\) makes \(aba,aab\) equal; both are required. |
| A4 · I | Raw: multiple set-valued obligations, possibly shared between negatives. | Compute the witness-rank lower bound below; use a packing bound if cheaper. | All stipulated coarsenings below the certified cost floor, not necessarily every partition above it. | One must connect a feasible choice of witnesses; shared connections are charged once. | Two disjoint three-symbol reversal groups force three merges without naming one compulsory pair. |
| A5 · B | Raw: for a failing \(y\), two deletion obligations meet disjoint sets of current blocks. | Branch only on merges between a block meeting the first and one meeting the second. | No entire coarsening cone is declared incompatible. Only other **first steps** are omitted here. | A final rejecting block contains a representative from each side; merge those two first. | At singleton resolution for \(ab,cd,ef\) versus \(\epsilon\), one may start between the first two supports. |
| A6 · H | Raw: a cheap subset of comparisons suggests a promising complete grouping, without a proof. | Complete a proposed witness block with singleton leftovers, or pack disjoint suspected dead sets into one diagnostic. | None by the heuristic. | Unchecked positives or order comparisons can reverse the guess. | A likely transversal is worth testing; a partial transversal is not a rejection certificate. |

A useful exact special case of A3: symbol \(a\) occurs in **every** separating block for \(y\) precisely when \(\Sigma\setminus\{a\}\) is dead for \(y\). Otherwise the complement itself separates without \(a\). A nonvacuous use requires that separation be possible. A larger deletion set, such as \(\{a,b\}\), forces only a choice, not the merge \(ab\). To test whether two symbols are globally forced together by more complicated evidence, it suffices to test all bipartitions separating them **using complete raw facts**: any compatible partition separating them can be coarsened to such a bipartition without joining them. This tests necessity in *all* solutions, not just in optimal ones.

### Witness-rank theorem: a sharp cost bound that accounts for sharing

Start from any current partition \(P\) with \(k\) blocks. For each negative \(y\), record obligations indexed by \(j\). Obligation \(j\) offers a family \(\mathcal A_{yj}\) of alternative symbol sets. One final block for \(y\) must **contain one alternative from every family**. A deletion witness \(T\) supplies alternatives \(\{\{a\}:a\in T\}\). The full comparison to a positive \(x\) supplies alternatives \(D_{yx}\). These two kinds may be mixed. **Direction matters with incomplete preprocessing:** it is safe for a lower bound to omit an entire obligation or give it a proved *superset* of its alternatives. It is not safe to keep only the atoms found so far and pretend that list is complete. For example, against positive \(ab\) and negative \(\epsilon\), finding the atom \(\{a\}\) proves a way to separate, not that \(a\) is mandatory: \(\{b\}\) works too. A positive containment witness can certify an upper bound; a necessity claim must account for missing alternatives.

**Theorem.** Choose one alternative per obligation. For each \(y\), collect into \(H_y\) all current blocks touched by its chosen symbols. Regard the \(k\) current blocks as vertices and connect the vertices of each \(H_y\) together, counting isolated vertices as components too. The minimum *additional* cost among coarsenings satisfying the written obligations is:

$$
L(P)=\min_{\text{choices}}\bigl(k-\#\operatorname{components}(H_y:y\in S^-)\bigr).
$$

An obligation with no alternative means infeasibility. A negative with no obligations adds no edge and can use any existing block. Here \(k>0\); the empty-alphabet convention is below. For partial obligations this is sharp **for the relaxation**, not necessarily for the original traces. With all \(D_{yx}\) it is the exact additional optimum, or infinity if infeasible.

**Proof.** Given a satisfying coarsening, choose alternatives inside its witnessing block for each negative. All vertices of an \(H_y\) lie in one final block. Intersecting hyperedges must therefore stay together as well. If there are \(h\) components, the coarsening has at most \(h\) blocks, hence costs at least \(k-h\) additional merges. Conversely, for any choice, merge precisely the vertices in each component, using a tree on its vertices. This takes exactly \(k-h\) merges. Each negative's selected symbols now lie in one block; different negatives may use the same or different components. Minimizing proves equality in both directions. With all discrepancy atoms, satisfying the obligations is equivalent to separating every negative, by the occurrence-order proof. ∎

**Why not sum obligations?** For positive \(aabc\) and negatives \(abac,baac\), the sole atom against each negative is \(\{a,b\}\). Each negative alone needs one merge; together they still need only one. Conversely, for *one* negative, if \(r\) deletion witnesses meet pairwise disjoint sets of current blocks, its separating block needs at least \(r\) current blocks and hence at least \(r-1\) additional merges. Disjointness of symbol sets at the root need not survive earlier merges. The rank calculation handles both effects.

**Discovery and optimization pseudocode.** No hidden grouping, partition query, or solver is used here. When a list is claimed complete, retain enough information to verify the *agreements* as well as the discrepancies.

```text
analyze(words, alphabet):
    count occurrences in each word
    for every negative y and positive x:
        atoms[y,x] = all singleton count mismatches
        for every unordered pair a,b with both counts agreeing:
            compare the two projections to a,b in occurrence order
            if different: add {a,b} to atoms[y,x]
        for every deletion T in the chosen cheap scan:
            if the projections outside T agree: emit (y, x, T) as a witness
    return atoms and the chosen deletion witnesses

discover_two_per_group_floor(y, complete_atom_lists):
    groups = empty list
    for each positive x:
        A = complete_atom_lists[y,x]
        if A is empty: return infeasible with equality witness (y,x)
        if any member of A is not a pair: continue
        G = the union of the endpoints in A
        if A consists of exactly all unordered pairs in G:
            record (y,x,G,A) in groups
    select any subcollection with disjoint endpoint sets (greedy is sound)
    if the subcollection is nonempty:
        return a root cost floor of twice its size minus one, with the selected records

rank_search(P, obligations):
    enumerate one alternative from each obligation (an empty family has no choices)
    for each complete choice:
        start a disjoint-set structure on the blocks of P
        for each negative y:
            collect the blocks touching its chosen alternatives
            unite them with one representative, if any
        retain the least merge count and the corresponding component partition
    return the best choice and partition, or infeasible if there was no choice
```

A partial-choice search can stop a branch when its already-required unions reach a verified incumbent's cost: more choices cannot undo a union. To discover the disjoint-group certificate below, for each \((y,x)\) with no unary discrepancies, collect the endpoints of its discrepant pairs, check that **all and only** pairs within that set occur, then check disjointness of the resulting sets. For empty negatives, simply collect positive supports and check whether selected supports are disjoint. These are discovery algorithms, not promises about the input.

**Costs.** Write \(p=|S^+|\), \(q=|S^-|\), and \(L_+,L_-\) for the corresponding total word lengths. A simple exact scan costs \(O((1+n^2)(qL_+ +pL_-+pq)+L_++L_-+n)\) elementary steps using indexed symbols: scan the two words for each restriction, with a precomputed count vector or only counts of the requested symbols. One may precompute per-word data only for nonempty cross-products. The atom lists use \(O(pq(1+n^2))\) space in the worst case, in addition to the words and scratch space. Checking \(d\) specified deletion sets across all word pairs costs \(O(d(qL_++pL_-+pq))\) after preparing their membership masks. Enumerating all deletion sets or all maximal dead regions can be exponential; it is **not** required for the atom representation. Enumerating rank choices costs the product of the alternative-family sizes times polynomial work per choice. This is an exact algorithm, not a polynomial-time claim. Reading explicitly listed local table rows also costs time proportional to the entries read; a complete table with \(f\) free projection groups can have \(2^f\) rows.

### A hidden-group family and a worked rank search

Take \(g\ge1\) disjoint groups of at least three symbols each. The sole negative lists the groups consecutively, in some order within each group. Make one positive per group by reversing just that group's order. Every symbol may instead be a run of the same positive length in all words. Individual counts reveal nothing. Comparing a positive to the negative gives exactly the two-symbol atoms within its reversed group: cross-group order and all other within-group orders agree. Thus the raw discovery procedure recovers the groups from the traces alone.

One separating block must contain **at least two symbols from every group**. Its size is at least \(2g\), so all partitions of cost less than \(2g-1\) are incompatible. Choosing any two from each group in one block, leaving all others singleton, attains the bound. For any proposed compulsory pair, choose the two from the first symbol's group so as to omit that symbol. It stays singleton. **No particular pair is compulsory even among optimal partitions.** The number excluded by the strict cost floor alone is \(\sum_{j=0}^{2g-2}{n\brace n-j}\), where the braces are Stirling numbers of the second kind. This counts partitions, not queries saved.

**Switching the quantifiers changes the optimum.** Instead make the base word the only positive and the \(g\) single-group reversals the negatives. Now each negative requires just one pair from its own group, and different negatives may use different blocks. Any choice gives \(g\) vertex-disjoint pair edges at the singleton root, of rank exactly \(g\). Thus cost \(g\) is necessary and sufficient, strictly less than \(2g-1\) when \(g>1\): make each selected pair its own block. No pair is compulsory, by the same omission argument. This is a multi-negative cost-floor family for which adding the individual one-merge bounds is justified *by disjoint endpoints*, unlike the \(aabc\) example. The groups are again recovered from the complete discrepancy lists.

Worked instance: negative \(y=abcdef\); positives \(x_1=cbadef\), \(x_2=abcfed\). **R1** = complete raw atom list against \(x_1\): \(ab,ac,bc\). **R2** = complete list against \(x_2\): \(de,df,ef\). **R3** = the disjoint-endpoint lower bound from R1 and R2. The following trace materializes the merges of the rank choice \(ab,de\); a cost-level search could bypass both intermediate nodes entirely.

| Complete partition | Status | Evidence and conclusion |
|---|---|---|
| \(a/b/c/d/e/f\) | Inferred NO | R1, R2: a singleton cannot contain even one of either list's atoms. |
| \(ab/c/d/e/f\) | Inferred NO | R2: the only nonsingleton has no second-group atom. R3 excludes this cost level. |
| \(ab/c/de/f\) | Inferred NO | R1, R2: the two comparisons are defeated in **different** blocks, not one block. |
| \(abde/c/f\) | Inferred ACCEPT, optimal; not queried | R1, R2: the same block contains both chosen atoms. Its actual projections are \(abde\) for \(y\), \(bade\) for \(x_1\), and \(abed\) for \(x_2\). R3 proves optimality. |

This transcript pays **zero queries**. The cost floor certifies all 81 partitions at costs zero, one, and two, not merely the three inferred NOs displayed. It does not declare the coarsenings of those three nodes incompatible.

## 3. What a NO licenses

### Read every column, but do not overread a zero

On block \(B\), each distinct negative projection that matches a positive must be accepted locally, so its rejection bit is fixed at zero. For the remaining distinct projections an unbounded DFA can label any chosen subset rejecting while accepting all positive projections: a trie for these finitely many words, completed with a sink, suffices. Identical projections have equal bits. Hence on a **complete feasible table**, a column is fixed-zero **if and only if** \(B\) is dead for that negative; a 1 in even one feasible row proves separation for that negative. The row rejecting all free groups simultaneously suffices if certified as such. An arbitrary sample of all-zero rows does not certify fixedness. If an implementation returns samples, use the failing negative's positive IDs, a fixedness guarantee, or direct raw comparisons instead. Two fixed-zero columns do not by themselves prove their projections identical. In contrast, if two **non-fixed** columns agree in every row of a complete table, their projections on that block must be identical: distinct free projections could have been labeled differently. That supplies an identified equality between two negatives, which may be combined with a named positive equality on a subrestriction.

Let \(\mathcal U_i\) contain all certified dead regions for the **same original negative** \(y_i\). Storing only inclusion-maximal known regions per column is sufficient for the containment test. Its exact exclusion family is:

$$
\mathcal F_{\rm reg}=\bigcup_i\{R:\ \forall B\in R\ \exists U\in\mathcal U_i\text{ with }B\subseteq U\}.
$$

A certificate names \(i\) once and supplies one region ID per candidate block. Those IDs may be from different responses; their matching positives may differ. This is exactly what **this region test** proves, not necessarily all semantic implications of the history. By contrast, if each negative has a known separating set inside some block of \(R\), \(R\) is certified compatible and can give an incumbent. The local all-free choices cause no conflict between negatives.

### Select partition after NO

| Rule ID | Observed pattern and evidence source | Action or next complete query | Exactly which partitions are ruled out | Short proof | Example |
|---|---|---|---|---|---|
| N1 · I | One NO: the named negative and a matching positive ID on each block. | Record the queried partition as incompatible. | That partition by direct witness; no claim about a coarsening. | No block defeats all positives for the named negative. | On \(ab/cd\), the witnesses can be different positives. |
| N2 · I | One NO, with no side information about the words. | Skip every refinement. | Exactly its refinement cone as an unconditional incompatibility implication of this one response; proof below. | Inherit each block's equality; a crossing pair permits a countermodel. | \(ab/cd\) has four refinements, including itself. |
| N3 · I | One table or several: fixed-zero entries, including columns other than the reported failure. | Apply same-column coverage by stored regions. | Exactly \(\mathcal F_{\rm reg}\) by this test, including partitions refining no queried partition. | Subset inheritance needs one negative globally and one match per block. | A zero on \(cd\) from one query and a zero on \(ef\) from another can both certify the first negative. |
| N4 · I | Combined evidence: for one named positive and negative all unary and binary restrictions of a block agree. | Stitch the comparisons; add the block as a dead region for that negative. | Partitions newly covered by N3, including ones whose blocks were never individually queried. | The labeled-occurrence proof reconstructs equality. Positive identity must be justified. | Agreement on \(ab,ac,bc\) with one positive proves agreement on \(abc\). |
| N5 · C | Verified incumbent of cost \(u\) from ACCEPT or raw proof; certified additional lower bound \(L(P)\). | Close the branch for **strict improvement** when \(c(P)+L(P)\ge u\). | No partition here can improve the incumbent; none is declared incompatible on this basis. | The lower bound applies to every coarsening under consideration. | With a cost-one incumbent, a cost-one branch can contain compatible ties or worse solutions. |
| N6 · B | Current \(P\) fails on \(y\); one raw or table region \(U\) is dead for \(y\). | Keep first merges with at least one constituent not contained in \(U\). | No entire cone. Omit only the other immediate moves from this node. | Every final rejecting block includes an outside constituent and at least one other current block. | If \(bc\) is dead, an optimal continuation may start at \(a\) even though \(b,c\) eventually join. |
| N7 · H | History suggests a complete grouping would settle several unresolved, likely-to-be-visited candidates. | Rank by conditional saved work; ask one complete query, then rescore. | None until a verdict or a proof is obtained. | A predicted NO or a guessed failing column is not evidence. | Test \(abcd/e\), then consider \(abce/d\). |

**Sharpness of N2 (one response).** Every refinement is incompatible by the named negative's matches. Conversely, let \(R\) not refine the submitted \(Q\). A block of \(R\) contains two symbols \(a,b\) from distinct blocks of \(Q\). Start with any trace corpus realizing the observed response. Append \(ab\) to **every positive** and \(ba\) to **every negative**, retaining IDs. On each block of \(Q\) these suffixes have identical projections: it contains at most one of \(a,b\). Appending the same suffix preserves both equality and inequality there, hence all local tables and all reported witness IDs. But on the crossing block of \(R\), every positive ends in \(ab\) and every negative in \(ba\); this one block separates all negatives. So no non-refinement is forced incompatible by that single response. This is an indistinguishability proof, **not** an instruction to alter the data. A known literal word, known counts, other queries, or a promise restricting possible inputs can invalidate the countermodel; N2's exactness claim excludes those side facts.

**What multiple tables can prove beyond containment.** In the one-positive, one-negative case with one or more NOs, put an edge between symbols ever tested in one common block. Unary agreement is known everywhere. Then a candidate is forced incompatible **exactly when every one of its blocks is a clique** of this graph, with singletons allowed. For a clique, the *same* positive agrees on all its pairs, so N4 applies. For a nonclique block, its missing pair was never co-tested: the suffix proof preserves *every* observed NO and makes the candidate compatible. For example, the three pair tests \(ab/c,ac/b,bc/a\) jointly certify \(abc\) dead if all return NO for one positive and one negative, even though no queried block contained \(abc\). With several positives, do not stitch anonymous matches as if they were all the same trace. One can safely stitch named equalities and propagate equality transitively for the **same restriction** across trace IDs.

**An exact reference test for arbitrary table histories.** If “exactly” means *all* implications of arbitrary complete tables and opaque IDs, not just N2–N4, there is a finite, if impractical, answer. A candidate is forced incompatible iff **no** corpus consistent with the observations makes it compatible. This need not be left as an unbounded search. For \(N=p+q\) labeled traces it suffices, for table/ID evidence, to enumerate corpora with each word of length at most \(K=\binom N2 n^2\). Recompute the table as a set of feasible rows, the supplied witness equalities, and previous conclusive verdicts; keep only consistent corpora. INCOMPLETE imposes no constraint. If any retained corpus accepts the candidate it is a counterexample to exclusion. This test is also valid with raw **projection equality/disequality** facts; fixed literal words or numerical counts must additionally be preserved.

Here is the bound's proof and a way to discover the small witnesses. Label positions in each word by symbol and occurrence number. For each unordered pair of words:

- For each differing symbol count, mark rank one beyond the smaller count for that symbol.
- For each discrepant binary projection whose two counts agree, find one reversed pair of occurrence labels by comparing their positions in the two words. Mark both ranks, one for each symbol.

Pool marks **globally by symbol**. In each word retain exactly the occurrences with marked ranks. A previously equal projection stays equal because the same rank filter operates on both sides. A count difference persists because the longer prefix of occurrence ranks contains a mark absent from the shorter one. A reversed pair persists with corresponding labels in both filtered words. The atom test now preserves equality and inequality on *every* subset for *every* pair of traces, hence preserves every table, complete verdict, named witness, and target verdict. At most \(n+2\binom n2=n^2\) marks were introduced per word pair. This proves the bound. For supplied literal words, also mark all their occurrences; for a specified count, mark all ranks up to that count. Increase the bound accordingly. This reference test explains what “not proved by my cheap rule” means: it is **not** necessarily “logically unknowable.”

### Four different search decisions, with different proofs

1. **Declare one partition incompatible.** Exhibit one negative and its matching positive on every block, or equivalent fixed-zero evidence. Finding just one dead block, or a different negative per block, is not a proof. For positive \(\epsilon\) and negatives \(a,b\), \(a/b\) is compatible even though each block has a zero for *some* negative.
2. **Exclude an incompatible family.** Give the same-column containment proof for each member, possibly compressed by a cone, the region formula, or the clique test. For a single queried \(Q\), its cone has \(\prod_{B\in Q}\operatorname{Bell}(|B|)\) members including \(Q\). NO is not inherited upward.
3. **Close for objective value.** Given a verified incumbent, if the branch's cost floor reaches its cost, no better partition can be there. Keep the incumbent. Use a strict inequality instead if *all* optimal ties are wanted. For positive \(abc\), negative \(bac\), and incumbent \(ab/c\), the branch \(ac/b\) cannot improve it; the descendant \(abc\) nevertheless **is compatible**.
4. **Omit a first step while retaining a path.** For N6, take any compatible coarsening \(F\) of the failing \(P\) and one of its blocks rejecting the failing \(y\). This block is not contained in \(U\), and cannot consist of just one current block. Merge, inside it, a current constituent not contained in \(U\) with any other constituent. This is a retained child still refining \(F\). Repeating the argument preserves a path to any needed solution (or finds a compatible finer one first). This proof assumes unrestricted merge order below a retained child. Extra canonical-order restrictions require a new coverage proof; do not combine them blindly.

**Confusing omission with exclusion loses the optimum.** With positives \(a,b,c\) and negative \(\epsilon\), the only compatible partition is \(abc\). The region \(bc\) is dead, witnessed by positive \(a\). From \(a/b/c\), N6 may omit the first move to \(a/bc\), keeping moves involving \(a\). But globally deleting the cone of \(a/bc\), or forbidding \(b,c\) ever to join, deletes \(abc\) even along the retained path. Three symbols already suffice for this distinction.

## 4. Search policy, termination, and the certificate

A complete solver needs no external optimizer. With full atoms, run `rank_search` at the singleton partition and return the component partition of a minimum-rank choice. Alternatively, scan complete partitions in increasing cost, testing the exact atom predicate. With partial facts, use the same cost layering: infer NO or ACCEPT only with evidence, otherwise query the unresolved **complete** candidate. Store all columns of a NO. A diagnostic may jump ahead, but a high-cost ACCEPT is only an upper bound until every cheaper possibility is accounted for. A merge-DAG implementation may use N5 and N6 instead of visiting all partitions of a layer. Memoize the complete partition, and any extra branch restrictions if used. Do not equate “already tested and failed” with “its coarsenings need not be searched.”

- **ACCEPT:** save the incumbent if cheaper; coarsenings are compatible but not better. Do not infer the witnessing block from ACCEPT alone. Stop when the verified lower bound meets the incumbent or all cheaper candidates are covered.
- **NO:** file the failure, per-block IDs, and all useful fixed-zero and separating columns; update the covered frontier before choosing another probe.
- **INCOMPLETE:** count the attempt as paid, learn no verdict, and do not close a cheaper unresolved candidate. Defer it, try a genuinely informative different complete partition, or use exact facts supplied by Analyze. For guaranteed termination even if all queries are INCOMPLETE, make the full comparison facts available up front. A table-only algorithm with an indefinitely inconclusive oracle cannot guarantee an optimal answer on indistinguishable inputs.

**Replayable certificate.** The upper part names the returned partition and, for each negative, a block and a discrepancy against every positive; the verifier can simply reproject the words. For the lower part use a proved floor (as in R3), a rank-choice tree that covers all alternatives with verified cost cutoffs, or the following universal fallback: enumerate every cheaper partition canonically and give its failing negative and one matching positive ID per block. The verifier regenerates the cheaper partitions so omissions cannot pass. Compressed region/branch certificates must likewise verify coverage, not just individual leaves. For a table-derived fixed zero with no positive ID supplied, the verifier can find a matching positive in the raw list. Certificate size can be exponential; no succinctness assumption is needed.

**Degeneracies.** If \(n=0\), the unique empty partition is compatible exactly when there are no negatives: there is no block to witness anything. For \(n>0\), no negatives or no positives makes the singleton partition optimal. Otherwise, an identical positive and negative proves infeasibility; in the absence of such a pair the one-block partition is compatible. Thus infeasibility can be certified directly, not mistaken for an unsuccessful search. Duplicate word IDs do not change the criterion. A declared symbol absent everywhere can be left singleton without losing separation.

## 5. Required examples and adversarial checks

### Four symbols: exactly what the second response adds

Positives \(x_1=ab,x_2=cd\); negative \(y=\epsilon\). **E0** is the fresh query on \(a/b/c/d\): NO; the witnesses on \(a,b,c,d\) are \(x_2,x_2,x_1,x_1\). **E1** is the fresh query on \(ab/cd\): NO; \(ab\) matches \(x_2\) and \(cd\) matches \(x_1\). The sole column is fixed zero on both blocks. Here is **every** partition certified incompatible by E1:

| Complete partition | Queried or inferred | Evidence and novelty relative to E0 alone |
|---|---|---|
| \(a/b/c/d\) | Queried NO | E0 already; also a refinement under E1. |
| \(ab/c/d\) | Inferred NO | E1: \(ab\) is dead, and \(c,d\) inherit deadness from \(cd\). New. |
| \(a/b/cd\) | Inferred NO | E1: \(a,b\) inherit from \(ab\), and \(cd\) is dead. New. |
| \(ab/cd\) | Queried NO | E1 itself. Its verdict was not implied by E0 alone. |

There are four members, of which two were queried and two were not. No other partition actually fails: every other one has a block meeting both supports. **E2** (raw): on \(ac\) the negative gives \(\epsilon\) and the positives give \(a,c\). Thus \(ac/b/d\) is **inferred ACCEPT**, cost one; E0 excludes the unique cost-zero partition. E2 plus E0 is an independently replayable optimum certificate.

What was conjectural depends on the information boundary. With **only E0 and opaque IDs**, the three “new” verdicts above were conjectures. For a concrete indistinguishable E0, use \(y=abcd,x_1=dc,x_2=ba\) with the same IDs: both pairs then separate, while every reported singleton witness still matches. If Analyze has supplied the fact **\(y=\epsilon\)**, matching singleton IDs for the same positive *do* combine here: absence of both symbols implies absence on their union. With the full raw supports, all four exclusions follow even before E0. E1 is then corroboration, not new knowledge.

### Same observed IDs and tables, different optimal next moves

Positive \(x_1=abc\); negative \(y_1=bac\) in input A and \(y_1=acb\) in input B. **O0** (fresh singleton query, either input): three identical one-column fixed-zero tables, the same failing ID, and the same sole positive witness on each block. Select knows singleton counts agree. Without a distinctness promise it cannot even infer feasibility; if the words are distinct, the atom lemma implies *some* two-symbol merge suffices, but O0 does not identify it. Under a promise that these are the two possibilities, Select knows the disjunction, not which member holds.

**OA/OB** (raw order): the only atom is \(ab\) in A and \(bc\) in B, respectively. The unique optimum is therefore \(ab/c\) in A, \(a/bc\) in B, both **inferred** with cost one and lower bound O0. **OD** (fresh complete query \(ab/c\)) returns ACCEPT in A and NO in B, distinguishing the promised pair. Without that two-input promise, a NO here does not identify \(bc\) as the answer. The two-symbol example \(ab\) versus \(ba\) is already a minimal counterexample to the rule “singleton matches with the same positive imply a match on their union.”

### Why demanding immediate progress fails

Positives \(ab,cd,ef\), negative \(\epsilon\). **T1–T3** (raw): the three positive supports are disjoint, and a rejecting block must hit all three. Every first merge from singletons creates only a two-symbol block. **All 15 first moves separate zero additional negatives.** Discarding all of them loses every optimal path. For example, \(a/b/c/d/e/f\) and \(ac/b/d/e/f\) are **inferred NO** by T1–T3; \(ace/b/d/f\) is **inferred ACCEPT** by the same witnesses and direct projections. A block hitting three disjoint supports needs two merges; the displayed cost two is optimal. The cost floor alone excludes 16 partitions, not merely the illustrated path.

### Combining responses, including a non-failing column

A small clean combination: positive \(abcd\), negative \(acbd\). **J1** (query \(ab/c/d\)) and **J2** (query \(a/b/cd\)) both return NO. \(ab/cd\) is **inferred NO** using its first block from J1 and its second from J2. Neither alone implies this: with the same positive, negative \(abdc\) preserves J1 but separates on \(cd\); negative \(bacd\) preserves J2 but separates on \(ab\). This is a countermodel argument, not just failure of a particular deduction rule.

A less obvious case uses a column that was **not** the cause of the NO. Positive \(abcdef\); negatives \(y_1=bacdef\) and \(y_2=abcdfe\).

| Complete partition | Status and evidence ID | Useful entries |
|---|---|---|
| \(ab/cd/e/f\) | Queried NO · J3, caused by \(y_2\) | \(y_1\) is separated on \(ab\), **but fixed zero on \(cd\)**. |
| \(ef/ac/b/d\) | Queried NO · J4, caused by \(y_1\) | For \(y_1\), all four blocks are fixed zero; \(y_2\) is separated on \(ef\). |
| \(ef/cd/a/b\) | Inferred NO · J3 + J4 | For \(y_1\): use J3 on \(cd\), J4 on \(ef,b\), and J4's \(ac\) on \(a\). The candidate actually separates \(y_2\). |

In J3 the column for \(y_1\) on \(ab\) can take either value, not just 1. Reading a single feasible zero there as a fixed zero would be wrong. Discarding all non-failing columns would instead lose useful, genuine evidence.

## 6. Which one or two diagnostic partitions to ask

**Propose complete partitions.** Start with the unresolved candidates that the ordinary search is likely to pay for before it finds an incumbent or closes a cost level. Propose blocks that group several of their untested pairs or larger obligations. Pack disjoint proposed blocks together, filling unused symbols by singletons. Include an alternative partition that regroups overlapping suspected dead regions: they cannot both be blocks of the same query. Never ask an isolated block question. Do not pay for a verdict already derivable unless there is a separate reason to acquire its other columns.

**Forecast by outcome, not by cone size alone.** A NO on \(Q\) guarantees its refinement cone. For each plausible failing negative, tentatively add every block of \(Q\) to *its* regions; forecast other fixed columns only under an explicit hypothesis. Recompute covered candidates, subtract those already covered, and intersect with the likely paid frontier. In a one-positive history use the clique update instead. Give an ACCEPT credit only for the search work its verified upper bound would avoid; INCOMPLETE supplies no coverage. Weight candidates by their probability of actually being reached and their check cost. Rank by expected avoided work minus probe and analysis cost. Weights can come from cheap raw features, a specified prior, or measured histories; they are **never** logical exclusions. If historical probabilities are unavailable, report outcome-conditional savings rather than inventing a confidence level. After the first outcome, rescore the second probe; asking neither is a valid choice.

To count mathematical families without double counting, for one negative let \(A(B)\) mean “allowed as a dead block by the chosen test.” Set \(f(\varnothing)=1\), and for nonempty \(S\) use the recurrence:

$$
f(S)=\sum_{\min S\in B\subseteq S,\ A(B)} f(S\setminus B).
$$

The block containing the least symbol is unique. The recurrence takes at most \(O(3^n)\) subset transitions, besides testing \(A\). For several negatives, count the **union** of their partition families by enumeration or inclusion–exclusion, not by adding their totals. To count only a cost layer, retain the number of blocks in the recurrence. For a short explicit frontier it is cheaper simply to test its members.

### Controlled comparison: zero, one, or two paid diagnostics

Five symbols, positive \(abcde\), negative \(abced\). The verifier knows the words; for this experiment Select receives **no raw-order facts**. The common ordinary strategy first queries the singleton partition, then scans the ten one-pair partitions in lexicographic order, skipping certified NOs, stopping at its first ACCEPT. Write \(P_{uv}\) for the **complete** partition with block \(uv\) and every leftover singleton. Ordinary NOs also update the evidence. No top-partition ACCEPT or promise that the words are distinct is given to Select.

The probe pool consists of one-symbol-versus-rest cuts. A ranking model putting equal weight on a possible single discrepant pair ties all five first cuts; break ties by putting the last available letter alone. After the first NO the four still-possible pairs in that model touch \(e\); the four untried cuts tie for incremental coverage. The **experimental budgets** deliberately take zero, one, or two probes so we can compare realized cost. A deployment threshold need not buy the second. The one-pair model affects ranking only, not the certificates.

**D0** = fresh singleton NO, sole witness \(x_1\) on every block. **D1** = fresh NO on \(abcd/e\). **D2** = fresh NO on \(abce/d\). As direct cones D1 and D2 have 15 members each; their intersection is the five refinements of \(abc/d/e\), so their union has 25 members. Combining the actual block evidence does more: any block avoiding the pair \(de\) lies in \(abcd\) or \(abce\). Hence all partitions keeping \(d,e\) apart are excluded. There are \(\operatorname{Bell}(5)-\operatorname{Bell}(4)=52-15=37\), since identifying \(d,e\) counts the partitions putting them together. **Twelve** exclusions are outside the union of the direct cones. For example \(ad/be/c\) is **inferred NO** from D1 on \(ad\), D2 on \(be\), and either on \(c\); neither response alone implies it. It is not an ordinary cost-one candidate.

**Worked transcript.** In the table, “query \(O_{uv}\)” denotes the fresh response on that complete \(P_{uv}\). All such responses below are NO except \(O_{de}\), which is ACCEPT. A dash means not scheduled, **not** inferred. Each inference names sufficient evidence; the single reported negative and sole positive IDs are unchanged throughout.

| Complete partition | Zero diagnostics | One diagnostic | Two diagnostics |
|---|---|---|---|
| \(a/b/c/d/e\) | Query D0 | Query D0 | Query D0 |
| \(abcd/e\) | — | Query D1 | Query D1 |
| \(abce/d\) | — | — | Query D2 after D1 |
| \(P_{ab}\) | Query \(O_{ab}\) | Inferred NO · D1 | Inferred NO · D1 |
| \(P_{ac}\) | Query \(O_{ac}\) | Inferred NO · D1 | Inferred NO · D1 |
| \(P_{ad}\) | Query \(O_{ad}\) | Inferred NO · D1 | Inferred NO · D1 |
| \(P_{ae}\) | Query \(O_{ae}\) | Query \(O_{ae}\) | Inferred NO · D2 |
| \(P_{bc}\) | Query \(O_{bc}\) | Inferred NO · D1 | Inferred NO · D1 |
| \(P_{bd}\) | Query \(O_{bd}\) | Inferred NO · D1 | Inferred NO · D1 |
| \(P_{be}\) | Query \(O_{be}\) | Query \(O_{be}\) | Inferred NO · D2 |
| \(P_{cd}\) | Query \(O_{cd}\) | Inferred NO · D1 | Inferred NO · D1 |
| \(P_{ce}\) | Query \(O_{ce}\) | Query \(O_{ce}\) | Inferred NO · D2 |
| \(P_{de}\) | Query \(O_{de}\): ACCEPT | Query \(O_{de}\): ACCEPT | Query \(O_{de}\): ACCEPT |

The optimum certificate in every column is D0 plus \(O_{de}\): the actual projections on \(de\) are \(de\) and \(ed\), and cost zero was impossible. This certificate does not need the probes that helped find it.

| Paid diagnostic queries | Mathematical NO family after D0 and probes, before ordinary scan | Actually skipped ordinary candidates | Paid ordinary cost-one queries | Total paid, including D0 |
|---:|---:|---:|---:|---:|
| 0 | 1 | 0 | 10 | 11 |
| 1 | 15 | 6 | 4 | 6 |
| 2 | 37 | 9 | 1 | 4 |

For completeness, with the exact clique update, the mathematical family sizes after successive **ordinary** NOs are respectively **2, 3, 4, 5, 9, 13, 17, 27, 37** in the zero-probe run and **20, 27, 37** in the one-probe run. There is no ordinary NO in the two-probe run. A direct cone from one ordinary cost-one NO has just two members; the larger numbers are *accumulated* families.

**When does the second query pay?** Here it skips three *additional* ordinary tests for one extra call, a net saving of two. The first saves five net. These are realized savings, not a distribution-free guarantee. Under the uniform single-pair ranking model conditional on D1, D2 returns NO with probability \(1/4\); counting only its three new cost-one NO exclusions gives expected credit \(3/4\) of a call before even discounting early stopping. A policy using just that credit would decline it. An ACCEPT might also help via its upper bound, depending on the remaining search. If the winning pair were the very first ordinary candidate, a high-cost exploratory ACCEPT could be pure overhead. Finally, if Analyze already supplied the discrepancy atom \(de\), **none** of these paid calls would be necessary. Query and preprocessing costs belong in the same comparison.

## 7. Independent exhaustive checks: observed results

These are results of running a separate enumerator, not projections from the saving formula. Its oracle generated set partitions by choosing the block of the least remaining symbol and recurring on the rest. It computed compatibility by literally erasing symbols in each word, then applying the stated quantifiers. It did **not** use atoms, deletion obligations, graph cliques, rank, or the pruning rules to generate oracle verdicts. For local tables it separately enumerated all labelings of distinct nonpositive projections. Empty words, repetitions, and overlapping positive and negative lists were included.

| Check actually run | Observations |
|---|---|
| All ordered pairs of three-symbol words of length at most four, all eight retained symbol sets | 121 words, 14,641 word pairs, **117,128** equality-versus-atom checks; no discrepancies. |
| All positive and negative subsets of size at most two of the 13 three-symbol words of length at most two; all five partitions as starting nodes | **8,464** inputs, **42,320** nodes. Exactly 6,345 inputs were feasible. Full-atom rank equaled the directly enumerated minimum additional cost at every node, including infeasible nodes. |
| Partial deletion rank on the same inputs | Using only deletions of size at most one, rank equaled the enumerated optimum of the relaxation and never exceeded true cost; it was strictly weaker at **1,044** nodes. Allowing all deletions of size at most two closed that gap on these particular inputs. |
| Tables, coverage, and branching on the same inputs | **155,480** fixed-column checks; **207,855** candidate tests over histories of one or two NOs, yielding **118,913** valid region certificates, counting repetitions across histories. **44,664** failing-node/dead-region/compatible-continuation checks of N6; none lost the continuation. |
| Sharp single-NO countermodels | For **44,377** non-refinement cases on that corpus, appending the crossing suffixes preserved all table rows and all local positive–negative equalities, and made the target compatible. |
| Four symbols, single positive and negative, all-zero NO histories of one, two, or three distinct complete queries | **575** histories, **8,625** candidate comparisons. Against a model bank containing equality and each possible isolated adjacent swap, exactly **4,862** candidates were forced NO across histories; **125** of these were detected by clique stitching but not region containment. The proof in §3 explains why this model bank suffices for this test. |
| Named examples and diagnostic counts | Direct enumeration found exactly four incompatible partitions in the four-symbol empty-negative example; eight optima at cost two for \(ab,cd,ef\); nine optima at cost three for the two reversal groups. The five-symbol run produced the three rows **11, 6, 4** total calls and **0, 6, 9** skipped candidates as predicted. |

As a separate non-exhaustive stress check, the occurrence-rank compression preserved all **19,200** tested pair/subset equalities across 400 generated four-word corpora on three symbols, including shuffled orders and a count perturbation. These checks support the implementations of the rules, not a claim that the diagnostic policy is generally faster.

## 8. What is settled, and what is not

**Ready to state as a theorem.** For finite traces and unbounded local states, unary and binary discrepancy atoms are sufficient for exact partition optimization. The optimum above any current partition is its current cost plus the minimum component rank of a simultaneous witness choice. Partial deletion and discrepancy obligations give certified lower bounds **when used in the necessary direction**. Independently, from one NO with only opaque-ID table evidence the forced incompatible family is exactly its refinement cone; in one-positive, one-negative NO histories it is exactly the clique-partition family of the co-tested-pair graph.

**Policy choices that need experiments.** Compare full raw preprocessing, budgeted deletion scans, and diagnostics at equal *total* cost. Measure reached frontier nodes, conclusive and inconclusive paid calls, time to verify the lower bound, and certificate size. The best probe pool, the probability of an informative NO, and the point at which a second probe pays are properties of the workload and search order, not of monotonicity.

**Most consequential open question here.** For partial histories with multiple positives and negatives, can we obtain a practical, complete implication procedure that returns either a short exclusion certificate or a consistent accepting counterexample, without enumerating bounded corpora or most of the partition lattice? That would tell Select whether to spend its next unit of work on *reasoning from evidence it already owns* or on *buying another complete query*.