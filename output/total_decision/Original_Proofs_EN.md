# Certified Split or Global decisions before RPNI

## 1. Contract and claim ledger

Input consists of finite disjoint sets S+ and S- of words over a known finite character alphabet Sigma, together with an ordered partition into k nonempty pairwise disjoint blocks B_i. Empty words are retained. Projection pi_i erases characters outside B_i and preserves the order of remaining characters. Global acceptance of local hypotheses is AND. The comparison returns either a sparse global automaton or a factorized collection. Explicit product construction, minimization and prediction over future traces are outside the cost comparison.

The fixed reference learner uses a positive partial trie, undefined transitions reject, final states are precisely positive words initially, and state names are prefixes. It selects blue and red states in shortlex order. A proposed merge forms the least deterministic quotient and takes the union of old final states. The candidate is kept exactly when every negative rejects. Otherwise the next red state is tried, or blue is promoted. Red states are mapped to canonical classes after a kept quotient. Canonical representatives are the least shortlex prefix in each class.

The fold uses a flat map over all q original state records of that candidate. Each successful class union scans all q records. Records remain until reconstruction. This implementation detail is essential to the global lower bound. These are not union-find lower bounds.

W_ref charges: positive word and symbol visits, created states and edges, two state passes and one edge pass per fringe, one event per attempted candidate, fold-map initialization, union-map visits, closure edge visits, state/edge reconstruction, tested negative words and attempted/traversed negative symbols, and red entries remapped on kept candidates. Sorting, hashing, set construction, string copying, allocation internals, integer bit arithmetic, diagnostics, constant control and returning existing objects do not add separate events. This is an explicit reproducible event functional, not RAM time, total CPU instructions or wall-clock time. H charges the selector's explicitly specified block, alphabet-character, word, character, active-block, histogram and cardinality visits under corresponding exclusions.

The splitter uses a configured character-to-block lookup and one character pass per word, one block-slot pass per positive or negative word, then another block-slot pass per negative for witness selection. Positive projections and selected negative projections are deduplicated. Preparation has exact charged cost

    Pi = M + Mminus + k(p + 2z),

where M and Mminus are positive and negative character volumes, p=|S+| and z=|S-|. The lookup is fixed alphabet configuration for the pipelines; H conservatively also charges validating/building its own lookup. Thus W_S=Pi+sum_i W(P_i,N_i), and W_G=W(S+,S-). Pipeline costs are sequential sums, not parallel elapsed times.

| Claim | Premises | Proof | Boundary |
|---|---|---|---|
| Feasible AND decomposition | Fixed partition, finite consistent labels, unrestricted local DFA sizes | Section 2 | Sample feasibility, not recovery of a target |
| Safe local negatives | Highest-index available witness | Section 2 | Chosen sufficient constraints, not true causal labels |
| Static cost intervals | Fixed learner and event model | Section 3 | General feature-extraction overhead not certified |
| Global pipeline advantage | k>1, S+ nonempty, all observed characters in one block | Section 4 | Net advantage additionally requires H below the gap |
| Split net advantage | Exact balanced family, ordered singleton marker block last, n>=1 | Sections 5--8 | Specific flat-map implementation and event model |
| Equal output languages | Either specialized rule | Sections 4 and 9 | Does not imply target recovery |
| Exact certificate-status boundary | Sound intervals and, for net tests, a sound H | Section 10 | Sufficient certified regions, not universal winner classification |

All proofs below are mathematical arguments, not proof-assistant verification or peer review. Finite checks in Section 12 supplement the proofs. No novelty claim is made.

## 2. Feasibility and local data

Let P_i=pi_i(S+) and V(w)={i:pi_i(w) not in P_i} for w in S-. Let D be the class of languages intersection_i pi_i^(-1)(L_i), with regular L_i and no state bound.

**Theorem 1.** An S-consistent language in D exists iff V(w) is nonempty for every negative w.

**Proof, necessity.** For any product accepting every positive, each L_i contains P_i. If V(w) is empty then every local L_i must accept pi_i(w), forcing acceptance of w, a contradiction.

**Proof, sufficiency.** Choose L_i=P_i. Each is a finite regular language. Every positive passes every factor. Each negative has a witness i with pi_i(w) outside L_i and therefore fails the product. This also covers S+ empty (P_i empty) and an empty negative set. Epsilon is never discarded. The constructed product is contained in every product accepting S+, by P_i subset L_i. QED.

Assign each negative only to max V(w), yielding N_i. Then P_i and N_i are disjoint. Any local learner consistent with (P_i,N_i) produces a sample-consistent product: every positive passes all factors, and every negative fails its assigned factor. QED. This is not a claim that all other projections are positive or that the selected factor is the true cause of rejection.

Example: positives={ab}, negatives={ba}, blocks={a},{b} are infeasible because both words have the same projection tuple. Treating ab and ba differently would contradict the AND contract.

## 3. Learner correctness and general static intervals

Every quotient maps existing positive paths to paths ending in a final class. The initial trie rejects all negatives because S+ and S- are disjoint. Every kept quotient explicitly rejects the negatives. Hence each intermediate kept model and the final model are sample-consistent.

Let q be current states and r current red classes. Initially q-r=N-1, where N counts positive prefixes including epsilon even if S+ is empty. Promotion decreases q-r by one. Merging a nonred blue class into a red class decreases it by one. Further red/red identifications decrease q and r equally, while red/nonred or nonred/nonred identifications can only decrease q-r. Thus a kept quotient decreases q-r by at least one. There are at most N-1 main iterations and at most N fringe computations including termination. In zero-based iteration t, at most t+1 red classes exist. Therefore at most B=N(N-1)/2 candidates are attempted. This proves termination as well as the candidate bound.

Let E=N-1, Dminus=sum_{w in S-}(|w|+1), and I=M+p+2N-1. Trie initialization costs exactly M+p+N+E=I. For one fold with q states and e edges, there are at most q-1 successful unions, each costing q. Every productive closure pass performs at least one further union, followed by one final nonproductive pass, so at most q closure passes scan e edges. Initializing and reconstructing states costs 2q and reconstructing edges costs e. Thus

    fold work <= q(q-1)+qe+2q+e
              <= F(q,e)=qe+q^2+3q+e.

Quotients never increase the number of states or edges. All fringes cost at most N(2N+E), all red remaps at most N^2, and each candidate at most 1+F(N,E)+Dminus. Consequently

    I <= W_ref <= U,
    U=I+N(3N+E)+B[1+F(N,E)+Dminus].

All features are available without training. For local samples use the same bounds and add Pi. Their computation has overhead: the current general branch does not certify that full overhead. Nor does raw Global generally satisfy the decomposed hypothesis-class restriction. General intervals compare sample-consistent outputs and do not claim language equality. QED.

## 4. Global rule, including its exact limitations

**Theorem 2.** If k>1, S+ is nonempty, and every character observed in S+ union S- belongs to a single block B_j, then

    W_S-W_G=Pi+4(k-1)>0,

and the output languages are identical members of D.

**Proof.** Projection on B_j is the identity. Other blocks have P_i={epsilon}; all negative projections there are epsilon, which cannot be assigned as a negative. For each negative, the active block is a witness by disjoint original labels and is its unique available witness. If there are no negatives the allocation claim is vacuous. The active learner therefore receives exactly the original data. Unused alphabet characters generate neither edges nor extra reference visits, so its run, order and event cost equal Global. An inactive learner on ({epsilon},empty) costs two initialization events and two terminal-fringe events: exactly four. Add Pi. Global never invents edge labels absent from its positive input, so its language contains no characters outside B_j. Intersecting with inactive epsilon languages imposes precisely that same restriction. QED.

For this selector branch

    H=|Sigma|+2k+p+z+M+Mminus.

A net advantage over always running Split follows exactly when H<Pi+4(k-1). The pipeline advantage alone does not imply this inequality. In particular positives={epsilon}, negatives=empty, blocks={a},{b} give W_G=4, W_S=10 and H=7, so H+W_G=11>10. The presentation-facing selector reports COST_ONLY here, not NET_GLOBAL.

Subtracting H gives the exact input-only margin

    W_S-W_G-H = (k-1)p+(2k-1)z+2k-4-|Sigma|.

Indeed Pi=M+Mminus+k(p+2z), so the M and Mminus terms cancel, the p coefficient becomes k-1, the z coefficient becomes 2k-1, and the constant k term is 4(k-1)-2k=2k-4. Thus, *within the single-active-block premises*, strict positivity of this integer expression is necessary and sufficient for this branch's net Global advantage. Zero means a tie after selection; negativity means its selector plus Global is more expensive than always Split. This is not a necessary condition for Global to win on general inputs.

A positive net example is positives={a,aa}, negatives={aaa}, blocks={a},{b}. Pi=14, pipeline gap=18, H=15. Hence H+W_G<W_S before training. Reference costs 93 and 111 subsequently confirm the identity. Removing inactive factors as a pipeline optimization changes this theorem's cost contract and requires reanalysis.

## 5. Split family and exact recognition

Use ordered singleton blocks {a},{b},{c}, with distinct characters and marker block last. For n>=1 let C_n be all words over {a,b} with n occurrences of each. Take S+=C_n and S-={c}. Relabeling the two balanced characters, including exchanging their lexical order, preserves the argument by symmetry.

There are P=binomial(2n,n) distinct positives, each of length 2n, so M=2nP. A set S+ equals C_n iff each positive has the required counts and p=P. The checks imply S+ subset C_n, and equal finite cardinalities imply equality. A missing member or an additional outside word fails this exact premise. Failure does not establish that Split loses.

The selector validates three blocks and three alphabet characters (six visits), input words and characters (M+P+2), active-block tests (three), positive histogram checks (P), and one cardinality test. Thus H=M+2P+12. It constructs no global trie, invokes no learner and attempts no quotient. Constant arithmetic and library internals have the same declared exclusions as W_ref.

## 6. Prefix count and forced global work

A positive prefix with i a's and j b's, 0<=i,j<=n, has binomial(i+j,i) possible words. Distinct character labels make these schedules distinct, and every such word extends to a positive. Therefore

    N=sum_{i=0}^n sum_{j=0}^n binomial(i+j,i)
     =sum_{i=0}^n binomial(i+n+1,i+1)
     =binomial(2n+2,n+1)-1.

The first sum identity is hockey-stick in j, and the second in i after including and subtracting its missing i=-1 term. The global trie has E=N-1 edges. Each unary local positive trie has n+1 states.

Assume a is the smaller balanced character. The first blue state is a and the first candidate merges epsilon with a. For every t with n-1 a's and n b's, both t and at are trie states: t extends by a, and at is a positive. Right-congruence along the defined original paths forces these states to coincide. There are T=binomial(2n-1,n-1)=P/2 such pairs. Their endpoints are all disjoint: lengths are 2n-1 and 2n, and both endpoint maps are injective. An equivalence relation containing T disjoint pair obligations needs at least T class reductions. Indeed a resulting class containing s such pairs has at least 2s members and requires at least 2s-1>=s reductions, and summing over classes proves the bound. Each successful flat-map union visits all N retained records. Consequently

    W_G >= L_G=I+NT.

No candidate can accept c since quotients invent no c-edge. In particular the first candidate is kept. This is a bound for the specified flat relabel implementation; a union-find implementation need not pay N visits per union.

The initial fringe costs 2N+E. Separate from NT union visits, the first fold initializes and reconstructs N states each, makes at least one closure pass over E edges, and reconstructs E edges. Attempt, negative-word test, missing c-symbol test and red remap cost four. None of these events overlaps I or the union visits. Hence the stronger lower bound is

    Lprime_G=I+NT+4N+3E+4=L_G+7N+1 <= W_G.

## 7. Local cost and the all-n>=3 inequality

Learning ({a^n},empty) merges a into epsilon on its first attempt. Determinism collapses the whole unary chain, yielding one final state with an a-loop. It has one candidate, two fringes and one red remap. Using I_local=3n+2, F(n+1,n)=2n^2+7n+4, fringe bound 3n+2 each and remap bound n+1 gives

    W_unary <= (3n+2)+2(3n+2)+1+(2n^2+7n+4)+(n+1)
            =u(n)=2n^2+17n+12.

The two balanced factors have positive sets {a^n},{b^n} and no negatives. All negatives assign to marker factor because it is the last witness; that factor learns ({epsilon},{c}), costing four. Preparation is Pi=M+1+3(P+2)=M+3P+7. Therefore

    W_S <= U_S=Pi+2u(n)+4=M+3P+4n^2+34n+35.

For n>=3, subtract using the weaker global bound:

    L_G-H-U_S=P(N/2-2n-4)+2N-4n^2-34n-48.

We have P>=2n^2: the base binomial(6,3)=20>=18 holds, P(n+1)/P(n)=2(2n+1)/(n+1)>=3, and 3n^2>=(n+1)^2 for n>=2. Also N=(4-2/(n+1))P-1>=3P for n>=3 (the coefficient is at least 3.5 and P>=20). Substitution yields the lower bound

    3P^2/2-(2n-2)P-4n^2-34n-48.

This polynomial increases for P>=2n^2: its derivative 3P-(2n-2) is positive there. Substitution gives at least 6n^4-4n^3-34n-48. For n>=3,

    6n^4-4n^3=2n^3(3n-2)>=14n^3,
    14n^3-34n-48=n(14n^2-34)-48>=3*92-48>0.

Thus H+W_S<=H+U_S<L_G<=W_G for every n>=3. The stronger Lprime_G is also valid. This proves a family-wide net advantage, not merely the tested cases.

## 8. The remaining n=2 and n=1 cases

For n=2, P=6, M=24, N=19, I=67, T=3. The stronger lower is 67+19*3+7*19+1=258. H=48 and U_S=161, so H+W_S<=209<258<=W_G.

For n=1, positives={ab,ba} and negative={c}. The initial trie states are epsilon,a,b,ab,ba. The first quotient identifies epsilon with a and b with ab, yielding classes R={epsilon,a}, B={b,ab}, C={ba}, edges R-a-R, R-b-B, B-a-C, and finals B,C. The second candidate joins R with B, and the two outgoing a obligations also join C. Both candidates reject c and are kept. The resulting one-state final automaton has a,b loops.

The original ordered edge scan requires exactly two closure passes in each fold: the first pass makes the stated additional union and the second finds no conflict. With q states, e original edges, u successful unions and d closure passes, fold cost is 2q+uq+de+e. Thus fold costs are

    2*5+2*5+2*4+4=32,
    2*3+2*3+2*3+3=21.

Initialization is 15. Three fringes on (q,e)=(5,4),(3,3),(1,2) cost 14+9+4=27. Two attempts, four negative word/symbol events and two red remaps add eight. Hence W_G=15+27+32+21+8=103.

Each unary local run has initialization five, fringes 5+3=8, fold 2*2+1*2+1*1+1=8, one attempt and one remap, totaling 23. Marker costs four. Pi=4+1+3(2+2)=17, so W_S=17+23+23+4=67. H=4+2*2+12=20. Therefore H+W_S=87<103=W_G.

The n=1 result is a direct structural proof. The pre-run selector recognizes the data and applies the proved constants rather than running a learner. Combined with Sections 7 and 8, all n>=1 have a net Split certificate. Three traces is the smallest member of this defined family, not a universal minimum.

## 9. Equality of output languages

Global begins with only a,b labels. All candidates reject c, so none fails and no state is promoted. The red set stays the image of the singleton root. Every quotient class remains reachable by mapping an original trie path. On termination, if a reachable state differed from the root class, a shortest path to it would first leave the root on an edge to a nonred state, creating a blue state, a contradiction. There is thus one reachable state. It is final because some positive is accepted. Both a and b occur in positives, their edges persist as loops, and no c-edge appears. The output language is exactly {a,b}*.

Local outputs are a*, b*, and {epsilon}. Their inverse-image AND product is exactly {a,b}*. This establishes equality on all words, not bounded test words. It also places both hypotheses in D.

It does not prove target recovery. The finite language {ab,ba} is a valid decomposed target using local languages {a},{b},{epsilon}; it agrees with the three training traces, but both learned outputs accept epsilon, which this target rejects. The marker negative never rejects a candidate, so the Split family is a restricted structural result, not evidence of coverage for informative negative samples.

## 10. The precise boundary and the meaning of UNKNOWN

Given sound intervals L_G<=W_G<=U_G and L_S<=W_S<=U_S, U_S<L_G proves Split cheaper by W_S<=U_S<L_G<=W_G. The symmetric inequality proves Global cheaper. For a sound selector overhead H, H+U_S<L_G proves net improvement against always Global, and H+U_G<L_S proves net improvement against always Split.

The two strict net regions cannot overlap: H>=0 implies U_S<L_G<=U_G<L_S<=U_S if both held, a contradiction. Negating both tests defines their unresolved complement. This is an exact classification of the status of these particular interval tests. Overlapping intervals do not prove equal actual work or impossibility of a better test. Infeasible inputs are a separate outcome under Theorem 1.

The current implementation's general branch has no certified H and no general all-word quality equality. It can certify pipeline cost comparisons only. `defense_selector.py` therefore distinguishes NET_SPLIT, NET_GLOBAL, COST_ONLY, UNKNOWN and INFEASIBLE. A NET outcome additionally requires equal-language evidence and the appropriate overhead inequality. It never imports or invokes the learner. Complete trace-content winner prediction is not claimed solved or impossible.

The specialized branches do not first execute the general projection-based feasibility test. Feasibility is already implied by each branch's structural premises and disjoint input labels, so no separate generic feasibility pass is part of their H. Applying such an extra pass in a different pipeline would require adding its work before claiming the same net inequalities.

### The two questions, stated as one precise theorem

Fix all contracts in Section 1. Let X be the finite, valid, consistently labeled inputs with a known ordered alphabet partition. Define the following subsets of X:

* G: k>1, p>0, all observed characters belong to one partition block, and (k-1)p+(2k-1)z+2k-4>|Sigma|.
* S: the ordered partition consists of exactly three singleton blocks {a},{b},{c}; for some integer n>=1, S+ is exactly C_n (Section 5), and S-={c}.
* C=G union S.

**Two-region theorem (answer to Question 1 and Question 2).** Membership in C is decidable using only the input before any learner invocation. G and S are disjoint. The selector `choose Global on G, choose Split on S` satisfies, for every input x in C:

    x in G  =>  H(x)+W_G(x)<W_S(x),
    x in S  =>  H(x)+W_S(x)<W_G(x),
    L(Global(x)) = intersection_i pi_i^(-1)(L(local_i(x))).

**Proof of recognition (Question 1).** Check the validity premises first. For G, scan the finite words to collect observed characters, p and z; test containment in each known block and evaluate the displayed integer inequality. These operations terminate and are equivalent to G's definition. For S, inspect the three singleton blocks and negative set; derive n from any positive and check n>=1, that each positive has n a's and n b's and no other symbols, and that there are binomial(2n,n) distinct positives. Section 5 proves that these tests are equivalent to the exact family, rather than merely necessary tests. No trie, quotient or learned hypothesis is used. An S input observes a and b in distinct blocks (and c as a negative), whereas G observes symbols in at most one block, so G and S cannot intersect. Section 1's H counts these exact selector loops; normalization and integer/library exclusions are explicit. Recognition accuracy here is a deterministic equivalence, not a statistical confidence level. QED.

**Proof of the choice (Question 2).** For x in G, Theorem 2 supplies the exact identity W_S-W_G=Pi+4(k-1) and equality of the output languages. The defining inequality for G is exactly H<Pi+4(k-1), by the cancellation in Section 4, proving the first implication. For x in S, Sections 6 and 7 show H+U_S<L_G<=W_G for all n>=3, with W_S<=U_S. Section 8 covers n=2 with H+U_S=209<258<=W_G and covers n=1 with H+W_S=87<103=W_G. Section 9 proves all-word equality of the outputs. These cases cover every allowed n, proving the second implication and the equality conclusion. QED.

The boundary is exact for membership in the defined sufficient domain C. It is not a necessary-and-sufficient characterization of the true cheapest pipeline over X. Outside C, this theorem asserts neither a net winner nor that prediction is impossible. The presentation-facing wrapper now permits NET_GLOBAL only for the single_active_block rule with its strict guard, and NET_SPLIT only for the complete_balanced_interleavings_with_marker rule. The lower-level research module also contains a positive-only balanced rule; its evidence is retained as COST_ONLY in this presentation wrapper because it is outside the two admitted regions. A rule that is mathematically related must not silently enlarge the theorem's stated domain.

## 11. Why trace quantity alone does not define the winner

Fix blocks {a},{b},{c}, choose n>=3 and P=binomial(2n,n). Sample A is the balanced family with negative c; it favors Split by the proved net theorem. Sample B has positives a,a^2,...,a^P and negative a^(P+1); it favors Global by Theorem 2. Both have P positives and one negative under the same partition, and each comparison has equal output languages. Any function receiving only these counts and partition receives identical inputs for A and B, so cannot label both correctly. P is unbounded, giving arbitrarily large examples. This is not a claim that lengths, prefix counts or all static features are equal, nor an impossibility proof for inspecting full content.

For every r>=1, positives={a^r}, negatives={a^(r+1)} also favor Global, with total character volume 2r+1 unbounded. Thus volume alone cannot force Split to win. These counterexamples do not undermine the existence of the sufficient regions in Section 10.

## 12. Adversarial audit and reproducibility

Run `python -B audit_defense.py`. The reference was extended only with an optional uncharged diagnostic observer, leaving the default algorithm and W_ref event increments unchanged. The observer compares every observed candidate to an independent oracle using explicit set partitions and transition saturation. A second learner uses that oracle to check final automata and candidate counts. Exact equality of promised outputs uses BFS on the reachable product of Global and all local automata with implicit rejecting sinks, including stuttering on symbols outside a local block. This procedure checks all words for the finite tested models.

The audited suite has 2,339 valid labeled samples: 2,187 exhaustive binary samples, 24 renamed balanced families, one n=5 family, 64 subsets of the n=2 positive family, 20 single omissions at n=3, 37 extra-negative cases, three extra-positive cases, one overhead counterexample, and two equal-count Global cases. It additionally checks five invalid inputs and one target-recovery counterexample. There were 14,845 independent candidate quotient checks and no failed assertion. This is finite evidence of code/proof agreement, not an exhaustive check of all possible inputs. Results are in `audit_results.json`.

The audit rejects extrapolations to total machine time, union-find implementations, all negative datasets, arbitrary changes to witness policy, target recovery, and universal cardinality thresholds. No unresolved counterexample to an admitted theorem was found in this suite or mathematical review. This wording does not claim that empirical search alone establishes the theorems.

### Second attack on the explicit boundary

Run `python -B audit_boundary.py`. This adds 2,216 valid case executions and 13,650 independent candidate quotient comparisons. It uses a separate domain predicate (deriving n from length rather than the selector's first-word histogram count), computes the selection before learners, checks exact domain membership against the presentation status, and then checks the promised cost inequalities and exact language equality against the independent oracles from the first audit.

The cases comprise 2,059 samples with a multisymbol active block and varying unused-alphabet sizes, 108 combinations of block permutations and symbol renamings, nine nonstandard character-order cases, three positive-only cases excluded from the admitted net region, 28 omitted-positive cases, three extra-empty-positive and three extra-empty-negative cases, and three explicit strict-threshold cases. Across the single-active cases, the exact margin was positive 977 times, zero 146 times and negative 939 times. Zero and negative margins must not receive a net Global certificate. There was no failed final assertion. The initially drafted threshold fixture used two positives where three were needed; its arithmetic expectation was corrected before the final run. This fixture correction does not change the proved formula or learner code. Detailed evidence is in `boundary_audit_results.json`.

The mathematical review also rechecked the disjoint-pair lower bound, the non-overlap of first-candidate costs, the n=1 direct quotient count, the all-n polynomial inequality, and the all-word equality argument. No unresolved counterexample was found for the admitted statements. These are mathematical proofs plus finite code checks, not a claim of proof-assistant certification or infallibility of human review.

## Sources

The conventional state-merging background appears in Björklund, Björklund and Martens, *Learning Algorithms*, Section 4, Algorithms 6 and 7: https://www.theoinf.uni-bayreuth.de/pool/documents/Paper2011-15/Paper2011/Learning_Algorithms_paper.pdf . The source does not prove the specific reference event bounds or pre-run selection results presented here. Those arguments are supplied above. No characteristic-sample identification theorem or CONCUR completion result is needed for this presentation.
