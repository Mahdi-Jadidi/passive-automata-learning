# Mentor handoff | Exact alphabet partition selection

## 1. Objective and results

Given ordered positive and negative traces over a declared alphabet, find **one compatible partition with the maximum number of blocks** and provide a certificate of optimality that can be replayed independently from the raw traces. The final algorithm combines singleton and pair analysis, exact witness-rank optimization for small problems, and a general merge search.

Two cases that exceeded the baseline's five-second budget completed through independent verification in **all three hybrid trials**:

| Case | Certified optimum | Merge cost | Median time through verification |
|---|---:|---:|---:|
| HDFS-1024 | 27 blocks | 2 | 1.189 seconds |
| Eight-vertex path | 12 blocks | 4 | 0.005 seconds |

HDFS holdout-1024 remained incomplete within five seconds. Diagnostic probes reduced paid queries in the controlled example. The holdout comparison did not meet the criterion for enabling them by default. [HDFS certificate](evidence/hdfs_1024.json) · [Path certificate](evidence/cover_path_8.json) · [Timing records](evidence/timing.json)

## 2. Problem contract and research changes

The input $D=(S^+,S^-)$ consists of finite words over the declared alphabet $\Sigma$. The projection $\pi_B(w)$ deletes symbols outside block $B$ and preserves order and multiplicity. For example, projecting $abaca$ onto $\{a,c\}$ gives $aaca$. With unbounded local states, a sufficient language for block $B$ is $K_B=\pi_B(S^+)$. A negative whose projection equals a positive projection must be accepted on that block. Choosing $K_B$ lets us reject all other local images. Thus a partition $P$ is compatible exactly when

$$
\forall y_i\in S^- \quad \exists B\in P \quad
\forall x_j\in S^+ \quad \pi_B(y_i)\ne\pi_B(x_j).
$$

Maximizing $|P|$ is equivalent to minimizing $c(P)=|\Sigma|-|P|$. Every merge costs one unit. The algorithm retains all declared symbols, including unused symbols, and the original IDs of the negative traces. The result establishes compatibility with the sample. Inferring physical ownership would require additional assumptions. [Notation](../../docs/ALGORITHM_NOTATION.md)

The baseline provided layered merge search, reusable zero regions, mandatory contractions, counting bounds, and independent replay. The hybrid version adds five pieces:

1. **Targeted analysis.** The earlier singleton precheck stopped at the first unresolved negative. The final version records partial coverage for every negative ID and focuses expensive witness extraction on unresolved negatives.
2. **Direct low-cost certificates.** Pair projections can certify costs one and two or supply a compatible incumbent to general merge search.
3. **Bounded exact witness rank.** Complete unary and binary discrepancy families give an independent exact optimization method when the comparison and choice counts fit the limits.
4. **A disjoint-support root bound.** The search can prove that disjoint sets of hitting obligations charge distinct merges. This closes the eight-vertex path at the root.
5. **Rule-level evidence audit.** Each PDF rule has a checked event, target, and input fingerprint. The audit checks the rule application as well as the solution certificate. [Baseline guide](../partition_feedback_paper/MENTOR_AGENT.md) · [Rule index](evidence/rule_index.json)

## 3. How the algorithm uses evidence

| Evidence | How it is used | What replay checks |
|---|---|---|
| Positive counts for each singleton | Record singleton separation and carry it forward under merges | The negative's count occurs in no positive for that symbol |
| Pair projections | Cover unresolved negatives, prove failure of a cheaper pair, or assemble an incumbent | Full compatibility and the recorded negative–positive matches on failed pairs |
| Complete discrepancy family for each negative–positive comparison | Choose one discrepancy per comparison and minimize the number of required merges | Reconstruct the options from the raw sample and independently compute the minimum rank |
| Projection equality between a negative and a positive on a region | Infer rejection, derive mandatory contractions, keep sufficient merge edges, and compute lower bounds | Original trace IDs, projection equality, and containment |
| Complete-partition query table | Register fixed zeros, free projection groups, and acceptance or rejection | Reconstruct the table when a transcript is supplied |
| Compatible incumbent and certified lower bound | Close branches that cannot improve the incumbent | Compatibility and the lower-bound proof for each closed branch |

The implementation encodes symbols as bits and blocks as masks. A query supplies a table for each block of a complete partition. The table represents a fixed zero when a negative projection matches a positive. A free group collects negatives that share an image outside the positive projections. This representation avoids enumerating possible table rows. The search keeps inclusion-maximal known zero regions per original negative because smaller regions inherit their equalities. [Model and oracle](model.py) · [Selection and evidence](search.py)

## 4. Overall pseudocode

~~~text
SOLVE(D, budget)
    Validate the sample and construct the declared singleton partition P0
    Record a separating singleton for every negative that has one
    U = original IDs of the negatives with no singleton witness

    If U is empty:
        Return OPTIMAL(P0, singleton certificate)
    If one full word has opposite labels
       or the alphabet is empty and a negative exists:
        Return INFEASIBLE(raw witness)

    seed = none
    If pair scanning fits its work limit:
        For each pair J:
            H[J] = unresolved negatives separated on J from every positive
            If H[J] covers U:
                Return OPTIMAL(one-pair partition, evidence the root fails)
            Record a failure witness for J

        If two disjoint pairs together cover U:
            Return OPTIMAL(two-pair partition, all one-pair failure witnesses)
        If a greedy collection of disjoint pairs covers U:
            seed = resulting compatible partition

    If complete discrepancy families and their choice space fit the rank limits:
        Return OPTIMAL(minimum-rank witness partition, rank certificate)

    Mine and check projection equalities for unresolved negatives
    Record unused symbols and mandatory contractions
    Return MERGE_SEARCH(reduced root, evidence, seed, budget)

    On exhaustion of the time or query budget, return INCOMPLETE

MERGE_SEARCH(root, evidence, seed, budget)
    best = a compatible initial partition, improved by seed if applicable
    If a certified root bound reaches the cost of best:
        Return best with the root certificate

    Visit layers in increasing merge cost
    For each candidate P that could improve best:
        If every negative has a known separating block in P:
            Record P as a better answer and finish its layer

        R = a witnessed incompatible coarsening of P, if available
        If no such R is known:
            Query the complete partition P and record its evidence
            If the result is ACCEPT:
                Record P as a better answer and finish its layer
            Recover a witnessed incompatible coarsening R

        If the one-merge bound closes this branch:
            Record the cutoff and continue

        If diagnostics are enabled, query eligible proposals and store evidence
        Confirm any proposed better incumbent before using it

        If cost(P) plus the certified additional bound reaches cost(best):
            Record the cutoff
        Else:
            Retain merges whose inputs lie in different blocks of R
            Send distinct children to the next layer

    Restore unused singleton symbols
    Return best and the evidence covering all cheaper alternatives
~~~

The pair precheck uses an estimated work cap of ten million projection units. The rank stage allows up to 4,096 distinct comparisons and 4,096 witness-choice combinations. The general analyzer examines up to 12,000 distinct negative–positive pairs for deletion witnesses. These limits govern which stages run. The exact search continues when a preliminary stage yields no complete proof and the overall budget permits it. [Solver](staged.py) · [Hybrid analysis](hybrid.py)

## 5. Why the algorithm is correct

### Separation persists upward, and equality persists downward

For $A\subseteq B$, projecting first to $B$ and then to $A$ is the same as projecting directly to $A$. If a negative differs from every positive on $A$, it also differs on any $B$ containing $A$. If a positive and a negative agree on $B$, their projections agree on every subset $A$. In particular, a singleton count absent from all positives establishes separation in every subsequent block containing that symbol.

### Cost-one and cost-two certificates

Every cost-one partition consists of a pair and singleton blocks elsewhere. To refute it, find an unresolved negative whose projection on the pair matches a positive. A compatible cost-two answer is optimal once the singleton root and every cost-one partition have been refuted. A triple block can also realize cost two. For example, with singleton positives $a,b,c$ and the empty negative, every pair fails while $abc$ succeeds. The search continues beyond the two-pair test when necessary. [Triple-block evidence](evidence/rank_triple.json)

### Completeness of unary and binary discrepancies

Label each occurrence with its symbol and occurrence number. Counts determine the set of labeled occurrences. Binary projections determine their relative order across different symbols, and occurrence numbers determine the order within a symbol. Therefore agreement on every unary and binary restriction of a block implies equality on that block. For instance, $aba$ and $aab$ have the same counts and different ordered projections on $\{a,b\}$.

For one negative, choose one discrepancy from the family for each positive. All chosen discrepancies for that negative must fit inside one final block. A compatible partition always supplies such choices inside a separating block. Given any selection, connect the atoms touched by the choices for each negative. If there are $k$ atoms and the connections leave $h$ components, every realizing partition needs at least $k-h$ merges. Forming those components realizes exactly that cost. Minimizing across every choice gives the exact optimum and counts shared connections once. A partial family can establish a particular separation. An exact rank certificate requires the complete alternatives.

### Mandatory contraction, rejection, and preserving a route

If the complement of atom $a$ is a zero region for $y_i$, any separating block for $y_i$ must contain $a$. If this holds for multiple atoms and the same negative, those atoms must lie together.

To reject a whole candidate, **one common negative** must have every candidate block contained in an evidenced zero region. The matching positives and source tables can differ from block to block. Suppose $R$ is a witnessed incompatible coarsening of the current $P$. Every compatible continuation above $P$ has a block crossing a boundary of $R$. Two atoms of $P$ in that block on opposite sides of the boundary can be merged first. Thus the retained edges give a route to each compatible continuation. For positives $ab,cd$ and the empty negative, the child “ab | c | d” fails, while “abc | d” is compatible and remains reachable by merging “ac” first. [Worked transcript](evidence/example.json) · [Combining two tables](evidence/mixed_sources.json)

### Bounds and independent replay

A zero region gives a hitting obligation on atoms outside it. A separating block for a negative with two disjoint obligations must connect at least two atoms. If the supports used for several deductions are mutually disjoint, their required internal connections give independent edges and the costs add. The implementation also accounts for shared contributions when supports overlap. Once the current cost plus a certified lower bound reaches the incumbent cost, the branch cannot yield a strict improvement.

The verifier checks the input fingerprint, complete answer partition, and compatibility on the raw sample. It then checks all cheaper possibilities using the singleton, pair, rank, or merge-search proof. For general search, it reconstructs the required children independently. Deleting one required record invalidates the optimality proof even if the answer itself is compatible. [Independent verifier](verify.py) · [Missing-child audit](evidence/missing_child_audit.json)

## 6. What the evidence shows

- **HDFS-1024.** The singleton stage leaves 288 original negative IDs, representing 130 distinct words. Each of the 406 possible one-pair candidates has a failure witness. The pairs {E16,E18} and {E20,E4}, together with 25 singleton blocks, cover all negatives. Direct replay checks the failure of all cheaper candidates and the compatibility of the cost-two answer. [HDFS certificate](evidence/hdfs_1024.json)
- **Eight-vertex path.** Negatives 0, 2, 4, and 6 each yield two hitting obligations. The four supports are disjoint and certify at least four merges. The answer realizes that bound with the pairs bj, dl, fn, and gh. Events 58 and 59 record the incumbent and the root cutoff. [Path certificate](evidence/cover_path_8.json)
- **Core and hybrid checks.** The merge-search core recorded 10,211 replays and 5,553 intermediate-node checks. The hybrid evaluation ran 7,587 solves and replays across three settings on 2,529 historical inputs. Exact rank was compared with direct projection and partition enumeration at 4,032 intermediate nodes. [Core checks](evidence/checks.json) · [Hybrid checks](evidence/hybrid_checks.json)
- **Rule citations.** All 27 PDF rules link to observed events. The audit checks the cited target in addition to the answer certificate. For the incomplete event, the audit confirms the incomplete status. [Rule index](evidence/rule_index.json) · [Audit code](check_rules.py) · [English decision rules PDF](../../output/pdf/Partition_Decision_Rules_Final_EN.pdf)
- **End-to-end timings.** The 105 records include the phase timings and verification outcome. HDFS-128 and HDFS-512 each verified in all three hybrid trials, with medians of 0.097 and 0.289 seconds. HDFS holdout-1024 stayed incomplete in all three hybrid trials. Medians include verified runs only. [Timing records](evidence/timing.json)
- **Diagnostics.** In the controlled experiment, the no-reuse, passive, one-probe, and two-probe arms paid 11, 11, 6, and 4 total queries. They skipped 0, 0, 6, and 9 ordinary candidates, respectively. The probes were selected in advance. In the separate hybrid comparison, the runs with and without diagnostics both verified 6 of 9 trials and paid zero complete-partition queries. [Diagnostic experiment](evidence/diagnostics.json) · [Default-policy gate](evidence/timing.json)

## 7. Reproduction

Run the commands from the directory containing this file. On Windows, py can replace python.

~~~text
python -B staged.py example.json --transcript
python -B verify.py evidence/hdfs_1024.json
python -B verify.py evidence/cover_path_8.json
~~~

The verification commands should return VERIFIED. The commands below regenerate evidence files in this package. Keep a copy of the delivered timing.json if comparing recorded times with a new run.

~~~text
python -B audit.py
python -B audit_evidence.py
python -B experiments.py
python -B check_rules.py
python -B experiments.py --timed
~~~

[Solver](staged.py) · [Independent verifier](verify.py) · [Evidence index](evidence/rule_index.json) · [Persian mentor handoff](MENTOR_HANDOFF_FA.md)

## 8. Limitations and follow-up

1. **Investigate HDFS holdout-1024 first.** Test cost-two triple blocks on the unresolved negatives. The existing pair scan found no covering pair of disjoint pairs. A compatible triple plus proof excluding costs zero and one would certify cost two. A lower bound of three requires covering every cost-two alternative.
2. **Measure incomplete runs by phase.** Record raw analysis, table construction, rank, frontier expansion, and replay separately on the holdout data. Prioritize completion rate and end-to-end time through verification.
3. **Explore shorter certificates.** Measure the effect of sharing equivalent rank states and decomposing genuinely independent obligations. Partition search and witness selection have combinatorial worst-case growth. The timing evidence concerns the tested families.
4. **Evaluate the automatic diagnostic policy where it actually proposes probes.** Compare it against passive reuse under matching budgets and candidate order. Record paid calls, the certified incompatible family, skipped candidates, and time through verification.
5. **Separate mathematical and empirical claims in the manuscript.** Present compatibility, path preservation, and optimality with proofs and replayable evidence. Report runtime and query counts with their workload, baseline, and budget. Complete inference from query histories involving several positives and several negatives remains a research question.
