# Extending pre-training RPNI certificates

## 1. What is proved and what is preserved

This extends `output/defense` without replacing its files. The old single-active-block and complete balanced-marker certificates are retained. New results cover incomplete and unbalanced positive samples, additional marker negatives, and some genuinely merge-rejecting negatives.

All claims concern the exact sparse, sequential implementation in `rpni_work_reference.py` and its declared W_ref loop-event count. Each union scans every original state record retained during that candidate. No union-find or wall-clock bound follows. Sorting, hashes, set normalization, string-copy internals, allocation, constant control and integer bit arithmetic are excluded from W_ref and H. Split preparation is included; explicit product construction and minimization are excluded. H includes the new selector's prefix extraction, projections, negative attribution and local feature loops. Learning is never invoked by the selector.

Input: finite disjoint sets of words S+, S- over a known finite character alphabet Sigma, and an ordered partition into nonempty disjoint blocks B_i. Epsilon is retained. Composition is inverse projection followed by AND. Local DFA sizes are unrestricted. Let p=|S+|, z=|S-|, M=sum positive lengths, M-=sum negative lengths. Split preparation is exactly

    Pi=M+M-+k(p+2z).

Let P_i=pi_i(S+). For each negative w, choose the highest i for which pi_i(w) is not in P_i, adding that projection to N_i. No such i means INFEASIBLE: a product accepting the positives must accept that negative. Conversely, if each negative has a witness, choosing finite languages P_i proves feasibility. The allocation makes every P_i,N_i disjoint; any consistent local learners then give a sample-consistent product. This is sample consistency, not target recovery.

## 2. Static first-candidate lower bound for arbitrary samples

Let Q be the set of positive prefixes including epsilon, N=|Q|, E=N-1, and A the characters occurring in positive words. If N>1, let x be the least character starting a positive word. The first blue state of the reference is x; its first candidate identifies epsilon with x. Define

    T = |{t in Q : xt in Q}|.

**Theorem A (prefix forest).** The first candidate performs at least T successful class unions, regardless of whether its negative test accepts or rejects the candidate.

**Proof.** For every counted t, both the original paths t from epsilon and t from state x exist: their endpoints are the named prefix states t and xt. Any deterministic quotient identifying epsilon with x must identify these endpoints. Put an undirected edge between t and xt for each obligation. A vertex has at most one outgoing extension and one incoming extension; lengths strictly increase by one on a directed extension. Hence each component is a path (isolated vertices allowed), with no cycle. The obligation graph is a forest with T edges. Its equivalence closure therefore requires exactly T class reductions. Any coarser partition requires at least as many. A successful union reduces the class count by one, so there must be at least T such unions. Each visits all N retained records, costing at least NT. The quotient is constructed before negative testing, so rejecting it does not undo the incurred work. QED.

Initialization costs exactly

    I=M+p+2N-1.

The initial fringe costs 2N+E. Separate from union visits, fold map initialization and state reconstruction cost 2N, and one closure pass plus edge reconstruction cost at least 2E. The candidate event costs one. Set delta=0 if S- is empty, delta=1 if epsilon is negative, and delta=2 otherwise. At least delta events occur in the first negative scan: with epsilon, at least one word; otherwise at least one word and one symbol. No red remap is assumed. Thus

    L0 = I+NT+4N+3E+1+delta <= W_G.

At termination there is a distinct final fringe, since N>1 guarantees the first fringe has a blue state. Every positive edge label survives in at least one quotient edge; every model retains at least one state. The terminal fringe therefore costs at least 2+|A|, independently of all preceding counted events. Consequently

    LG = L0+2+|A| <= W_G.                       (1)

When the quality condition in Section 4 holds, the first global candidate is kept and remaps the singleton red set, permitting one more event in LG. All these event classes are disjoint. For N=1, use initialization as a lower bound and I+2 as the exact total work: no candidate exists.

The selector builds a prefix set and counts pairs. It builds no transitions, quotient, hypothesis or red/blue trajectory. This is an O(number of explicitly visited feature records) event-count computation, not a claim about total machine time or string-copy cost.

## 3. Local upper bounds and exact unary work

For any local data let m be its positive symbol volume, s its number of positives, q its positive-prefix count, e=q-1, and d=sum_{w negative}(|w|+1). A fold costs at most

    F(q,e)=qe+q^2+3q+e.

There are at most q-1 main iterations: the potential current states minus red classes decreases on promotion and on every kept merge. In zero-based iteration t there are at most t+1 red classes, so at most q(q-1)/2 candidates in total. At most q fringes cost q(2q+e), at most q^2 red-remap events occur, and a candidate costs at most 1+F(q,e)+d. Thus

    U(m,s,q,d)=I(m,s,q)+q(3q+e)
               +q(q-1)/2 * [1+F(q,e)+d].       (2)

The fold bound follows from at most q-1 unions of q visits, at most q closure passes of e visits, and 2q+e initialization/reconstruction. Quotients cannot increase states or edges. For q=1 the exact work is I+2, independent of negatives, since no candidate is attempted.

If local positives are nonempty and unary, with maximum exponent r>=1 and no negatives, we can do better than (2). The first candidate identifies root and its child and collapses the whole chain. In the sorted edge scan, all remaining chain conflicts are resolved in one productive pass, followed by one unproductive pass for r>=2; for r=1 there is only one unproductive pass. Define d_r=1 for r=1 and d_r=2 for r>=2. There are exactly r unions over r+1 original records. Fold work is

    2(r+1)+r(r+1)+d_r*r+r
      =r^2+(4+d_r)r+2.

Initialization is m+s+2r+1. Initial and terminal fringes total (3r+2)+3. There is one candidate and one red remap. Hence the exact cost is

    V(m,s,r)=m+s+r^2+(9+d_r)r+10.              (3)

For the sole positive a^n this becomes v(1)=23 and v(n)=n^2+12n+11 for n>=2. The formula permits other unary positive lengths and epsilon as additional positives.

Use (2), or the exact cases just proved, for each factor; let the resulting bounds be l_i,u_i. Then

    LS=Pi+sum l_i <= W_S <= US=Pi+sum u_i.      (4)

Global also satisfies (2). Therefore H+US<LG proves a net Split advantage, and H+UG<LS proves a net Global advantage, for any feasible input for which these strict inequalities hold. No statement about equal output languages follows from (1)--(4) alone. Both outputs remain sample-consistent.

## 4. An equality certificate without complete or balanced positives

**Theorem B (inert assigned negatives).** Suppose S+ is nonempty and every assigned local negative contains a character absent from that factor's positive support A_i. Then both outputs equal A*, where A is global positive support. This does not require balanced histograms or a complete family.

**Proof.** An assigned local negative has a character outside A_i=A intersection B_i, so its original global negative has a character outside A. Quotients invent no labels, so every candidate globally rejects all negatives; the same is true locally by the condition. Every proposed merge is kept and no blue state is promoted. The red set remains the root class. Every quotient class is reachable from the root by an image of an original trie path. If a nonroot class remained at termination, the first edge exiting the root on a path to it would target a blue state, contradicting termination. Thus each automaton has one reachable state. It is final because its positive set is nonempty; the global and all projected positive sets are nonempty. All and only observed labels become loops. Global accepts A*, and factor i accepts A_i*. Their inverse-projection AND accepts exactly A*. QED.

This also justifies the extra first-red-remap event mentioned after (1). With no positives both global and local products accept the empty language, separately proving equality. A failing inert-negative test does not prove inequality; it simply provides no equality certificate.

For example, arbitrary nonempty incomplete subsets of the old balanced family, with negative c in the last singleton block, satisfy this equality condition. So do many unbalanced positive sets and several negative words containing c. They can receive NET_SPLIT_EQUAL whenever the new cost inequality succeeds.

## 5. Removing positives one by one: universal deletion certificates

Fix ordered blocks {a},{b},{c}, S-={c}, and C_n the complete balanced family with n>=1. Remove any r distinct positives, 1<=r<P, where

    P=C(2n,n),  p=P-r,  M=2np,
    N0=C(2n+2,n+1)-1,
    T0=C(2n+1,n)-1.

T0 counts all pairs t,xt for either balanced character x: sum_{i=0}^{n-1} sum_{j=0}^{n} C(i+j,i)=C(2n+1,n)-1 by the two hockey-stick sums. Every resulting positive still has n occurrences of each character, so some first symbol exists even if all a-starting positives have been deleted.

**Theorem C (loss bounds).** Let N,T be the actual prefix and pair counts for that first symbol. Then

    NL=max(2n+1,N0-2nr) <= N <= NU=N0-r,
    TL=max(1,T0-4nr) <= T.                    (5)

**Proof.** Deleting one word removes at most its 2n nonempty prefix nodes; the union bound over r words gives N>=N0-2nr. At least one length-2n word remains and supplies 2n+1 prefixes. Each removed word's unique length-2n leaf disappears, giving N<=N0-r. In either complete-symbol obligation forest, a deleted node is incident to at most two edges. At most 2nr nodes are lost, so at most 4nr pair edges are lost. At least the root/first-child edge remains, hence T>=1. The complete a and b forests have equal size T0, so the same bound holds for whichever symbol is first after deletion. QED.

For a proper nonempty subset, the actual selector pays the failed complete-family histogram/cardinality test before taking the static branch. Counting its real event increments gives exactly

    H=2M+6p+2N+4n+32
      <= HU=2M+6p+2NU+4n+32.                  (6)

The counts are: initial validation/input/active checks plus balanced tests plus singleton gate, M+2p+13; global prefix creation N; projection word/character/slot and witness passes (p+1)+(M+1)+3(p+1)+3; pair tests N; local factor/prefix/word/character visits 3+(2n+3)+3+2n+1+1. Summing yields (6). No projection or feature-building pass is omitted.

Split work is exact, independent of which r words were removed:

    WS=M+3p+11+2v(n).                         (7)

Indeed preparation is M+3p+7, unary factors cost v(n) each and marker costs four. Equations (1) and (5), including the terminal fringe and first remap, give

    LB=M+p+2NL-1+NL*TL+7NL+5 <= W_G.          (8)

Every expression is monotone increasing in N,T on the nonnegative domain. Consequently

    HU+WS<LB                                  (9)

certifies net Split for **every choice of r deletions**, with equal output languages. This is a theorem about all subsets satisfying (9), not an inference from a deletion experiment.

Some uniform budgets obtained from (9) are:

| n | Complete positive count | Any deletions up to R | At least this many remain | LB-HU-WS at R |
|---|---:|---:|---:|---:|
| 3 | 20 | 2 | 18 | 426 |
| 4 | 70 | 7 | 63 | 2085 |
| 5 | 252 | 22 | 230 | 12597 |
| 6 | 924 | 71 | 853 | 17263 |

For completeness, these budgets guarantee all r=1,...,R, not just the endpoint. For the displayed R, NL=N0-2nr and TL=T0-4nr are unclamped throughout that range. The margin in (9) is

    D(r)=C + [-4nN0-2nT0-14n+10]r + 8n^2 r^2,
    C=N0T0+7N0-(4n+8)P-4n-39-2v(n).

Since r<=T0/(4n), D'(r)<=2nT0-4nN0-14n+10<0, using T0<N0 and n>=1. Therefore D(r)>=D(R)>0 for 1<=r<=R. Direct integer substitution gives the displayed positive endpoint margins. `deletion_budget.py` reproduces them and larger n. The exact-prefix selector can certify much sparser instances than these uniform worst-case budgets. A zero budget for n=1,2 from this conservative bound does not prove that all deletions fail.

No monotonic winner assumption is valid. Already for n=1, full positives {ab,ba} and negative c have WG=103, WS=67, while deleting one positive leaves WG=57, WS=62. The pipeline winner reverses. These exact finite counts are checked against the reference and independent quotient oracle. The new selector returns UNKNOWN on the singleton example because its own overhead is not covered. A threshold observed along one deletion order cannot be applied to all deletion orders.

## 6. A new equal-output Global family with effective negatives

**Theorem D.** Let k>1, S+={a} for one character a, and epsilon in S-, with any further valid negatives anywhere in the alphabet. Then

    WG=25,  WS=25+Pi+4(k-1),
    L(Global)=L(Split)={a}.

**Proof.** The global trie has root and final a-state, one edge. Its only initial blue/root candidate merges them and accepts epsilon, so the first negative, epsilon in shortlex order, rejects the candidate. No other negative is examined. The blue state is promoted and the next fringe terminates. Initialization costs five, two fringes cost ten, fold costs eight, candidate costs one, and epsilon's word test costs one: total 25. The output is the original two-state partial trie accepting only a. For Split, epsilon has a unique witness: the factor containing a; inactive factors have epsilon as a positive. Thus epsilon is assigned to that active factor, whose only candidate is likewise rejected first, giving work 25 and language {a}. Every inactive factor learns ({epsilon}, some nonempty negatives), attempts no candidate, costs four and accepts {epsilon}. Their product accepts exactly a. Add preparation to obtain WS. QED.

When the new branch is reached its overhead is

    H=|Sigma|+2k+p+z+M+M-+1,

the initial input/active scan plus a singleton-family gate. The complete-balanced branch performs no record scan here because epsilon in the negatives makes its marker condition false. Net Global requires H<Pi+4(k-1), equivalently

    (2k-1)z+3k-6>|Sigma|.

If the old single-active rule returns earlier, it pays one fewer gate event and already supplies its own exact guard. For blocks {a},{b}, positives {a}, negatives {epsilon,b}, the new branch has H=12, WG=25, WS=41. Hence 12+25=37<41, with equal output languages. The negative epsilon actually rejects the attempted merge. This family is outside the previous observed-single-block region because b occurs in the negatives.

## 7. Effective negatives can also receive net Split cost certificates

Theorem A does not require the first candidate to be kept. Equation (2) permits arbitrary valid local negatives. Thus the same static method covers genuinely rejecting negatives when H+US<LG. It must label this NET_SPLIT_COST unless a separate language-equality theorem applies.

A concrete example uses the full n=3 positives and negatives {epsilon,c}. Epsilon rejects a proposed merge that would make the root final. Static quantities are N=69, T=34, H=530, LG=3109 and US=594. Therefore

    H+WS <= 530+594=1124 < 3109 <= WG.

This proves a net cost advantage before learning. Subsequent reference runs give WG=6811, WS=352; those measured counts are checks, not premises of the inequality. Both outputs are sample-consistent. The certificate does not assert equal languages, even if exact checking finds equality for a particular tested instance.

In fact equality cannot be inferred for all newly covered effective-negative inputs. Remove aaabbb from C_3 and take negatives {bbb,c}. The net cost certificate succeeds, but Global accepts epsilon while Split rejects it. The assigned a-factor negative is epsilon and the a-factor must reject it. The global target constraints do not themselves label epsilon. The actual global acceptance is checked by the independent quotient learner and exact product test. The full input and distinguishing word are in `quality_counterexample.json`. Thus a blanket extension of the old equal-language claim would be false. The implementation uses distinct NET_*_COST and NET_*_EQUAL statuses to avoid that error.

## 8. Reproducible experiment and scope of the remaining UNKNOWN cases

`audit_extensions.py` makes each decision before reference training, then checks every candidate quotient against set-partition saturation, checks the final global/local models with an independent learner, checks each displayed bound, and performs exact completed-product equivalence whenever equality is promised. It also attacks the equality extrapolation and retains a concrete distinguishing word.

The final audit has 3119 valid case executions and 13425 independently checked candidate quotients: 2187 exhaustive binary samples, all 64 n=2 positive subsets, all 210 one/two deletions at n=3, 408 full-to-empty deletion-path steps under four orders for n=1..4, 128 effective-negative cases, 48 multiple-negative cases, eight unbalanced cases, 36 block-order attacks, 15 new Global-family cases and 15 unary-formula cases. Five invalid inputs are separately rejected. Counts are executions, not distinct inputs across categories. All final assertions pass. Results and all experiment rows are saved in JSON and CSV. An early test fixture mistakenly used a*a for string concatenation; it was corrected to a*2 before the final audit, without changing a theorem or reference learner.

UNKNOWN remains possible when conservative intervals overlap or selection overhead exhausts the certified gap. Infeasible decomposition is a separate result. Cost-only net certificates deliberately leave language equality unclaimed. None of these statuses proves that a stronger predictor cannot exist. No universal minimum trace count, monotonic deletion threshold, target-recovery theorem, novelty claim or peer-review/proof-assistant certification is made.

Reproduce in this folder:

    python -B audit_extensions.py
    python -B deletion_budget.py
    python -B extended_selector.py incomplete_net_equal.json
    python -B extended_selector.py informative_net_cost.json
    python -B extended_selector.py simple_informative_global.json
