# Passive discovery of a disjoint alphabet partition: formal baseline

Date: 2026-10-26. Scope: finite, noise-free labeled traces; unknown disjoint alphabet partition; initially exactly two nonempty blocks. This note concerns partition discovery before local passive DFA learning. It does not cluster complete traces, use an active oracle, or claim general passive recovery.

## 1. Model and the actual identification question

Let Sigma be a known finite alphabet, m = |Sigma| >= 2. A partition Pi = {B_1,...,B_k} has nonempty, pairwise disjoint blocks with union Sigma. For B subset Sigma, pi_B deletes all symbols outside B, preserving order. The unknown system has a declared partition Pi* and regular local languages L_i subset B_i*, with

    L* = intersection_i pi_Bi^{-1}(L_i).

Equivalently, a global trace is accepted exactly when every local DFA accepts its projection. Events from several blocks can occur within a single trace. There is no state bound or prefix-closure assumption. Initially k = 2 is supplied and correct. Component names are irrelevant, so recovery means equality of unordered partitions.

Each local DFA can equivalently be extended to the full alphabet Sigma by making every symbol outside its assigned block a self-loop at every state. Intersecting these extended DFA languages gives the same global language. Conversely such self-loops erase outside events, yielding the projection model. Thus this model is a constrained subcase of a conjunction of arbitrary full-alphabet DFAs: only one assigned component can react to a symbol. It is not a claim that ordinary DFA conjunction is new. A symbol assigned to a block may still have no effect there; no minimal-support or irreducibility assumption is implicit.

The input is a fixed finite S = (S+, S-), with S+ subset L*, S- disjoint from L*, and S+ intersection S- empty. The representability assumption above and correctness of k are substantive assumptions. The observation regime supplies no additional labels.

A partition is **sample feasible** if some regular local factors over its blocks accept all S+ and reject all S-. Define F_k(S) to be all feasible partitions with exactly k blocks. Distinguish three outputs:

1. A member of F_k(S): a sample-consistent explanation.
2. All of F_k(S), or an explicit ambiguity certificate: the finite-data uncertainty.
3. Pi* itself: recovery, justified only by an additional identification condition.

Partition recovery does not identify the local languages. Even after Pi* is known, finitely many projected examples generally admit multiple regular local languages.

## 2. Exact finite-sample feasibility

For a candidate Pi and B in Pi, put P_B = {pi_B(p): p in S+}. Define

    C_Pi(S+) = intersection_{B in Pi} pi_B^{-1}(P_B).

**Proposition 1 (feasibility criterion).** The following are equivalent:

(a) Pi is sample feasible with unrestricted regular local factors.

(b) For every n in S-, there is B in Pi such that pi_B(n) is not in P_B.

(c) S- intersection C_Pi(S+) is empty.

**Proof.** In any consistent product model, each local factor on B must contain P_B, because every positive trace is globally accepted. If a negative n has pi_B(n) in P_B for every block, every factor accepts its projection, a contradiction. This proves necessity. Conversely, choose the local factor on B to be exactly P_B. This language is finite and therefore regular. Every positive projects into each P_B. Condition (b) gives a rejecting factor for each negative. The equivalence with (c) is its definition. QED.

This criterion is an independently proved specialization of the observation/distribution criterion in Henry, Mousavi, Neele and Sammartino, *A Detailed Account of Compositional Automata Learning through Alphabet Refinement*, arXiv:2504.16624v3, Section 4.1 Proposition 5 and Section 6.1 Corollary 12. It is not a novelty claim. [Primary source](https://arxiv.org/html/2504.16624v3).

The proof also shows that C_Pi(S+) is the least Pi-product language containing S+: any such language must contain it. Thus rejection of a negative whose every projection has a positive witness is impossible under this Pi, independently of DFA-learning heuristics.

**Asymmetry.** A positive global label forces a positive local label in every block. A negative global label forces at least one local rejection, but usually does not identify its location. Let

    W_Pi(n) = {B in Pi: pi_B(n) not in P_B}.

Feasibility says precisely W_Pi(n) is nonempty for every negative. Choosing any w(n) in W_Pi(n) and declaring that selected local projection negative cannot contradict the forced local positives. Finite positive and selected negative sets can be separated by regular languages. This is a consistency construction; it does not establish that the selected component really caused rejection in the unknown system. Labeling every negative projection negative can instead contradict a positive projection.

**Lemma 2 (coarsening).** If Pi is feasible and Pi' is obtained by merging blocks, then Pi' is feasible.

**Proof.** For a negative n, take B in Pi with an unseen positive projection. Let D in Pi' contain B. If pi_D(n) equaled pi_D(p) for some positive p, projecting that equality again onto B would contradict the choice of B. Hence pi_D(n) is unseen, and Proposition 1 applies. QED.

In particular, every noncontradictory finite sample is feasible under the one-block partition, by taking its sole factor to be S+. Without a supplied k or a justified structural target, feasibility alone cannot discover a meaningful number of components.

If S- is empty, every candidate partition is feasible because Proposition 1 has no negative constraints. If S+ is empty, every candidate is again feasible: choose each local language empty, so every global word is rejected. Thus purely positive or purely negative samples cannot distinguish candidate partitions in this unrestricted model. A combinatorially unique partition, such as k = m, is a trivial exception to ambiguity, not evidence learned from such labels. This does not assert that merely having both label classes is sufficient for identification.

## 3. Sound local evidence for common block membership

All contexts x,y below are arbitrary words over Sigma; a,b are distinct symbols. Edges mean "must lie in the same block," never "must be separated."

**Lemma 3 (adjacent swap).** If xaby is positive and xbay is negative, then a,b belong to the same block in every sample-feasible partition.

**Proof.** If they belonged to different blocks, swapping those adjacent events would preserve every block projection: one block sees only a, another only b, and every other block sees neither. The two words would therefore have identical global membership in any product model. Their opposite labels contradict feasibility. QED.

Either orientation of the two labels is valid by exchanging a and b.

**Lemma 4 (insertion rescue).** If xy is positive, xay is negative, and at least one of xaby or xbay is positive, then a,b belong to the same block in every sample-feasible partition.

**Proof.** Suppose a belongs to A and b does not. The A-projection of xay equals the A-projection of the longer positive word, so it must be locally accepted. For every other block D, pi_D(xay) = pi_D(xy), so its projection is accepted because xy is positive. Every block would accept the negative xay, a contradiction. QED.

Construct the undirected graph G_S on all symbols of Sigma using every observed instance of these rules. Include isolated vertices. Let Gamma be its partition into r connected components.

**Theorem 5 (known-k recovery certificate).** Every sample-feasible partition is a coarsening of Gamma. Consequently:

* Under the model assumptions, Gamma refines Pi* and r >= k.
* If r = k, Gamma = Pi*, and F_k(S) = {Gamma}.
* If r < k, at least one of the stated modeling, labeling, alphabet, or supplied-k assumptions is false.

**Proof.** Every edge has its endpoints in one block by Lemmas 3 and 4. Along a path, transitivity of common block membership puts the entire connected component in one block. Therefore every block of Gamma lies inside a feasible block. Pi* is feasible by assumption. A coarsening cannot have more blocks. If both partitions have k blocks, no merge is possible, so they coincide. The same argument applies to every member of F_k(S). QED.

The condition r = k is a sufficient, checkable recovery certificate. It is not necessary. If r > k, the graph alone leaves different k-block coarsenings possible (assuming 1 < k < r); the full labeled sample can still eliminate all but one.

**Successful four-symbol example.** Take Sigma = {a,b,c,d}, k = 2,

    S+ = {abcd},  S- = {bacd, abdc}.

The swaps give edges a--b and c--d. There are exactly two connected components, so the partition is {{a,b},{c,d}}. The model exists, for example with local languages {ab} and {cd}; its accepted global traces are their interleavings. Thus the example satisfies the assumptions rather than merely forcing an inconsistent answer.

## 4. Graph limitations and exact enumeration

**Example A: graph incomplete, full data identifying.** Let Sigma = {a,b,c}, k = 2,

    S+ = {epsilon, abc},  S- = {a,b}.

There is no swap witness and no insertion-rescue witness: all negative words have length one, while the positive lengths are zero and three. Hence Gamma has three singleton blocks. Nevertheless only {{a,b},{c}} is feasible. For {{a},{b,c}}, negative a has all projections seen in positives. For {{a,c},{b}}, negative b has all projections seen. For {{a,b},{c}}, the a- and b-projections onto {a,b} are both unseen among {epsilon,ab}, so both negatives are rejected. The local languages {epsilon,ab} and {epsilon,c} give a compatible true system.

**Example A2: a nonempty generator-valid example without graph edges.** Let Sigma = {a,b,c,d}, k = 2, Pi* = {{a,b,c},{d}}, with local languages {ab,ac,bc} and {d}. Take

    S+ = {abd, acd, bcd},  S- = {abcd}.

Every listed positive is accepted by this generator; the negative projects to abc, which the first factor rejects. There are no swap witnesses (their lengths must agree) or rescue witnesses (a rescue negative must be shorter than a positive), hence the graph has four singleton components. Nevertheless Pi* is the only feasible two-block partition. To see this without enumerating all seven candidates, suppose neither candidate block contains all of a,b,c. For each block B choose a symbol t in {a,b,c} outside B. The positive word obtained by deleting t from abcd has exactly the same B-projection as abcd. Thus every block projection of the negative is positively witnessed, contradicting Proposition 1. Hence some block must contain a,b,c; with exactly two nonempty blocks, the other must be {d}. Pi* is feasible because its abc projection is unseen. This is a concrete case where a multi-symbol constraint proves a whole block although the two local witness rules infer no edges.

**Example A3: structural incompleteness even with complete target labels.** Let Sigma = {a,b,c}, k = 2, Pi* = {{a},{b,c}}, L_a = {a}, and L_bc = {b,c}. The complete global positive language is

    L* = {ab, ba, ac, ca}.

Take S+ = L* and S- = {abc}. This finite sample has exactly one feasible two-block partition: {{a},{b,c}}. In that partition, the negative's bc projection is unseen among the positive projections {b,c}, so it is feasible. For {{a,b},{c}}, the negative's projections ab and c are witnessed respectively by positives ab and ac. For {{a,c},{b}}, the negative's projections ac and b are witnessed respectively by ac and ab. These are all three unordered nonempty bipartitions.

More strongly, neither local graph rule gives any edge even if the labels of *every* word over Sigma are available. For swaps, L* contains both permutations for each of its accepted two-symbol multisets; swapping adjacent events preserves the length and multiset. Thus no swap of any positive can be negative. For rescue, the base positive xy must have length two, so the longer rescued word xaby or xbay would have length four and cannot be positive. Consequently the full-label witness graph is empty although the true block {b,c} has two symbols and the finite sample already identifies it. The witness-tree assumption in Section 5 therefore fails for some perfectly valid regular product systems; missing graph edges are not solely a finite-sampling problem. This strengthens Example A2's finite-observation incompleteness claim without invalidating it.

**Example B: genuine ambiguity and no unique finest sample-feasible partition.** Return to Sigma = {a,b,c} and S+ = {epsilon,abc}, but let S- = {a}. Both

    Pi_1 = {{a,b},{c}},   Pi_2 = {{a,c},{b}}

are feasible, since a is unseen in the two-symbol positive projection set in each case. The remaining two-block partition {{a},{b,c}} is infeasible. The only common strict refinement of Pi_1 and Pi_2 is the singleton partition; it is infeasible because a is seen on {a} and epsilon is seen on {b} and {c}. Thus Pi_1 and Pi_2 are incomparable maximally refined feasible partitions. Both also maximize the number of blocks. They produce two possible target systems agreeing on all observed labels: use the finite projection languages supplied by Proposition 1 for each partition.

This proves non-identifiability even when k = 2 is known. A deterministic tie-break can define a reproducible output, but cannot make that output the recovered unknown partition. The example concerns finite-sample explanations; it does not assert anything about uniqueness of decompositions of a completely known infinite language.

**Exact baseline solver.** Enumerate the k-block coarsenings of Gamma and retain exactly those satisfying Proposition 1. For k = 2, fix one component to side 0, assign the other r-1 components to either side, and exclude the all-zero assignment. There are 2^(r-1)-1 candidates before feasibility pruning. Cache each candidate block's positive projections; for each negative, check for at least one unseen projection. A rejected candidate has a finite certificate: a negative n and one positive p_B for each block with pi_B(n) = pi_B(p_B). A retained candidate has a certificate consisting of a rejecting block for each negative.

**Proposition 6 (solver soundness, completeness and identification).** This solver returns exactly F_k(S). Under the model assumptions, it contains Pi*. It returns a uniquely identified partition iff |F_k(S)| = 1. If |F_k(S)| > 1, no procedure based only on this sample can guarantee the declared target partition over the unrestricted regular-factor model class.

**Proof.** The graph removes no feasible partition by Theorem 5. Proposition 1 decides feasibility exactly for every remaining candidate. For the final claim, construct the finite-factor model of Proposition 1 for each of two retained partitions. Both satisfy every observed label and the supplied k, but have distinct declared partitions. An algorithm receives the same input in both cases and cannot be correct in both. QED.

Exact enumeration can additionally report pairs lying in the same block in every retained partition, or in different blocks in every retained partition. Such conclusions use the complete finite feasible set and are stronger than interpreting missing graph edges as separation. Exponential enumeration is a baseline, not a polynomial-time claim.

## 5. Explicit sufficient sample coverage, without hidden queries

Assume for each true block B that a finite set of true swap/rescue witnesses supplies a spanning tree on its symbols. Singleton blocks need no edges. Let W be the finite union of all words occurring in these witnesses, with their true deterministic labels. If the passive sample contains W with those labels, G_S connects every true block. By soundness no edge crosses a true block. Therefore r = k and Theorem 5 recovers Pi*.

This is a structural assumption on L* and an observational assumption on S. Neither follows merely from regularity, finite state, or noise freedom. Some valid systems admit no such witness tree. The algorithm does not request the missing words when coverage fails.

For an optional probabilistic statement, fix this finite W before sampling. Suppose N independent traces are drawn from a fixed distribution D on Sigma*, each labeled by L*, and every w in W has probability at least p_min > 0. Write q = |W|. Then

    Pr[recovery fails] <= Pr[some w in W is absent]
                         <= sum_{w in W} (1-D(w))^N
                         <= q exp(-N p_min).

The first inequality uses the sufficient coverage event, so it is an upper bound on failure rather than an equivalence. For q > 0 and 0 < delta < 1, N >= log(q/delta)/p_min suffices for probability at least 1-delta. For q = 0 coverage is vacuous. This is not distribution-free, requires positive support on both positive and negative witness words, and does not describe separately sampled positive/negative datasets without modifying the sampling argument.

## 6. A tractable first milestone and staged relaxation

The first milestone is a **certificate-producing passive two-block solver**: implement these witness rules, enumerate component coarsenings exactly on small alphabets, return all feasible partitions, and certify a unique answer only when justified. Validate it against exhaustive enumeration without graph pruning; include the successful example and both failure-boundary examples above. The formal contribution at this stage is a clearly delimited known-k certificate and explicit limits of this particular witness graph, not discovery of the known feasibility criterion or a claimed new general learning theorem.

The accompanying `partition_solver.py` is a bounded demonstrator of that specification. It takes a JSON file with `alphabet` (2--10 distinct one-character strings), `positive` and `negative` (lists of strings; `""` denotes epsilon), and emits JSON containing all feasible bipartitions, positive projection languages, a rejecting projection witness for each negative and feasible partition, graph edges and their observed witnesses, and a separate graph certificate. It rejects contradictory labels and out-of-alphabet symbols. Run `python partition_solver.py INPUT.json`; add `--no-graph-pruning` to enumerate every symbol bipartition as an independent comparison baseline. It has no external dependencies. Four `theory_*.json` files cover graph recovery, recovery beyond the empty graph, genuine ambiguity, and the structural graph gap of Example A3. Initial execution of the first three returned respectively one, one, and two feasible partitions, as proved above; independent auditing is separate from this initial execution.

Suggested assumption ladder:

1. Known Sigma, disjoint blocks, k = 2, exact labels, unrestricted regular factors; solve finite consistency and give coverage-conditional recovery as above.
2. Known general k; replace bipartition enumeration by set-partition enumeration of graph components. The same proofs apply.
3. Seek a stronger, tractable inference method between these local witnesses and full feasible-set enumeration. A completeness characterization, complexity guarantees and meaningful gains over existing alphabet-refinement methods remain unproved.
4. Address unknown k only after defining the target: a declared architecture, an irreducibility criterion, a complexity-optimal partition, or another justified objective. Sample-maximal refinement alone can be nonunique, as Example B proves.
5. Add local DFA state bounds or a complexity objective explicitly; Proposition 1 alone no longer decides feasibility under arbitrary added bounds. Resolve negative-projection responsibility as a joint consistency problem rather than silently treating all projections as negative examples.
6. Treat noisy labels and shared alphabet symbols as new models requiring revised constraints and proofs. The present sound-edge guarantees rely on exact labels and disjoint ownership.

No claim here establishes general passive recovery of Pi*, recovery of true local DFAs, witness-tree existence for all regular product systems, a polynomial exact algorithm, or novelty relative to the full literature. Those are separate research questions.

