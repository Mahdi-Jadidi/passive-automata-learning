# Toward total Split / Global cost selection

## 1. Contract and three distinct goals

The input is a pair of finite disjoint sets S+, S- of finite character strings
and a known ordered partition B_1,...,B_k of a finite alphabet into nonempty
disjoint blocks, k >= 1. Every observed character belongs to the partition.
Empty words and empty sample sets are allowed. Duplicate input records are
normalized to sets, as in the reference. The learner, ordering and negative
allocation are exactly those in `rpni_work_reference.py`: shortlex red/blue
choice, canonical smallest representatives, highest-index negative witness.
Local DFAs have no state bound. Composition uses inverse projections and AND.

W_G and W_S denote the declared reference loop-event costs; Split includes
projection and negative allocation but excludes product construction. H counts
static-selector loop events. Sorting, hashing, set normalization, allocation,
string-copy internals, constant control and arithmetic, including integer bit
complexity, are excluded. These are mathematical event counts, not elapsed time,
RAM-model instruction counts or bounds for arbitrary RPNI implementations.

We distinguish:

1. A total exact comparison: determine W_G < W_S, W_G = W_S, or W_G > W_S.
2. A static winner certificate: establish that relation without executing RPNI.
3. A net saving: prove H + W_chosen < W_other.

The implementation now provides (1) on every valid feasible input, using exact
execution only when static certificates fail. It expands (2), and claims (3)
only under an explicit strict gap test. It does NOT solve universal cheap
pre-training selection. No impossibility theorem for that problem is asserted.

## 2. Feasibility and input classification

Let P_i = pi_i(S+). A sample-consistent regular AND decomposition exists iff
each w in S- has an i with pi_i(w) outside P_i.

Proof: accepting all positives forces P_i subset L_i for each i. A negative
whose projections all belong to their P_i must then be accepted by all factors,
a contradiction. Conversely, if every negative has such a witness, use the
finite regular languages L_i=P_i; they accept all positives and reject every
negative. Allocating a negative only to its highest witness gives disjoint
local positive/negative sets. Any consistent local learners then yield a
sample-consistent product. Empty words are included in this argument. QED.

Accordingly, a well-formed but infeasible input receives GLOBAL_ONLY, not a
claim about the cheaper of two admissible consistent pipelines. Malformed
partitions, out-of-alphabet words and contradictory labels receive INVALID.
Both are separate from UNKNOWN and TIE.

The new early rules below are also feasible without constructing witnesses:
one block is identity; no positive letters gives empty or epsilon-only local
languages; in the unary-inert family an outside symbol supplies a witness in
its own block (a nonempty projection in an inactive block, or an outside symbol
in the active block). Thus early returns do not bypass an infeasibility risk.

## 3. Exact pre-training rule: one block

For k=1, all projections are identity and every negative is allocated to that
factor because S+ and S- are disjoint. Global and local learner inputs and their
deterministic execution orders coincide. Therefore

    W_S = W_G + Pi,
    Pi = M + M_minus + k(p + 2z).

Here p=|S+|, z=|S-|, M=sum positive lengths and M_minus=sum negative lengths.
The winner is Global if Pi>0 and TIE if Pi=0. Language equality follows from
identical inputs/executions. Net Global is claimed only if H<Pi. This does not
require knowing either absolute learner cost. QED.

## 4. Exact pre-training rule: no positive letters

Assume the positive support is empty. Then S+ is either empty or {epsilon}.
The global trie has one root, no edge and no candidate; initialization costs
1+p and the terminal fringe costs two. Write g=3+p, where p is zero or one.
All k local positive sets have the same form. Assigned negatives cannot cause
a candidate or change the output, so each factor costs g. Thus

    W_G=g,    W_S=Pi+kg,
    W_S-W_G=Pi+(k-1)g >= 0.

Both languages are empty when p=0, and {epsilon} when p=1. Their AND product
has the same language, because the blocks cover the alphabet. Net Global
requires H<Pi+(k-1)g. Equality of costs is reported as TIE. QED.

## 5. Unary first-fold cost and a lower bound with arbitrary negatives

Let the positive support be exactly {a}; at least one positive is nonempty.
Let r=max{|w|:w in S+} >= 1, m=sum positive lengths, s=|S+|. The trie is the
entire chain epsilon,a,...,a^r regardless of missing positive lengths.
Let d_r=1 for r=1 and d_r=2 otherwise. Define

    V(m,s,r)=m+s+r^2+(9+d_r)r+10.

First the root is red and a is the first blue state. Their proposed merge
forces all r+1 states into one class: root~a implies a~a^2, and so on.
There are exactly r successful unions, each scanning the original r+1 records.
The first union is outside the closure passes. For r=1 the closure's first
pass is already stable. For r>=2, source-length ordering collapses a^2,...,a^r
in the first closure pass, and the second pass is stable. Thus fold work is

    2(r+1) + r(r+1) + d_r*r + r
    = r^2 + (4+d_r)r + 2.

The terms respectively count map initialization/state reconstruction, union
record visits, closure edge visits, and reconstructed edge visits. Initialization
is m+s+2r+1. The initial fringe is 3r+2, the candidate costs one. If there are
no negatives, the fold is kept, remapping the sole red root costs one, and
the one-state/one-edge terminal fringe costs three. Summing gives V exactly.

**Lemma (arbitrary consistent negatives).** For these same unary positives,
every reference execution costs at least V, even if some negative rejects the
first candidate.

Proof: initialization, initial fringe, candidate and entire first fold precede
negative testing; their total is V-4. If the candidate is kept, its red remap
and terminal fringe cost four, with nonnegative additional negative-test cost.
If rejected, there was only one red candidate. The blue state is promoted and
the next fringe scans the unchanged r+1-state, r-edge trie, costing 3r+2 >= 5.
Already this is more than the four still needed. Later work is nonnegative.
Hence W>=V in both cases. QED.

If every negative contains a symbol outside {a}, the first folded candidate
rejects every negative and is kept. Write j(w) for the one-based position of
the first such outside symbol. The only candidate tests every negative exactly
once; each test costs one word event plus j(w) attempted symbol events. Thus

    W = V + D,    D=sum_{w in S-}(1+j(w)).

This also gives an exact local-factor cost whenever its positives are unary
and every assigned local negative contains a symbol outside that local support.

## 6. New infinite Global region, allowing informative local negatives

**Theorem.** Assume support(S+)={a}, with a nonempty positive, and every global
negative contains a symbol different from a. The partition is otherwise
arbitrary. Then Global is strictly cheaper than Split in W_ref.

Proof: the preceding lemma gives W_G=V+D. Let j be the block containing a.
Its positive set is exactly S+, so the active local learner costs at least V,
even when allocated negatives reject its first merge. Every other local factor
has positive set {epsilon}, no positive edge and exact cost four. Therefore

    W_S >= Pi + V + 4(k-1),
    W_S-W_G >= K := Pi + 4(k-1) - D.

Since j(w)<=|w|, D<=M_minus+z. Consequently

    K >= M + kp + (2k-1)z + 4(k-1) > 0,

using M>=1, p>=1 and k>=1. This proves a strict Global winner for every member
of this infinite family, independently of positive completeness, balance,
maximum length, block ordering or which local merges are rejected. QED.

The selector computes the maximum positive length and all first-outside
positions during its already charged input visits: positives are scanned before
negatives, so their support is known. No prefix trie, transitions or merge
trajectory is constructed for this rule. The same per-record arithmetic/control
exclusions as the previous selector apply. If this branch is reached, its H is

    H=|Sigma|+2k+p+z+M+M_minus.

It returns NET_GLOBAL_COST precisely when H<K, otherwise PIPELINE_GLOBAL.
Language equality is not asserted. The early one-block or single-active-block
rules may instead return first with their separate equality proofs.

Example: S+={aa}, S-={ba}, ordered blocks {b},{a}. The active a-factor receives
negative a, which really rejects the all-states merge. Statically V=39, D=2,
Pi=10, W_G=41 and W_S>=53. Thus Global wins without learning. Measured costs
are W_G=41, W_S=83. H=12 and K=12, so the strict net guard correctly declines
to promise net savings from this conservative lower bound.

For a net Global example, take S+={aa}, S-={bb,bbb}, blocks {a},{b}.
Here V=39, D=4, Pi=17, W_G=43, W_S=60, K=17 and H=16.
Thus H+W_G=59<60, certifying net Global before learning.

## 6A. Exact comparison for a single repetition-free positive word

Assume S+={w}, S- is empty, and every symbol occurs at most once in w. Write
r=|w| and l_i=|pi_i(w)|. Define

    F(r)=(11r^2+27r+8)/2, including F(0)=4.

**Theorem.** For every ordered partition,

    W_G=F(r),
    W_S=r+k+sum_i F(l_i),
    W_S-W_G=r+5k-4-11 sum_{i<j} l_i*l_j.

Proof: first let r>=1. The positive trie is a chain with r+1 states and r
edges, with pairwise distinct edge labels. Since every label occurs on exactly
one edge, no quotient ever has two old edges with the same label. A candidate
therefore has no deterministic target conflict: it performs exactly its initial
one union and one stable closure pass. No negative can reject it. The red set
remains the singleton root. Every nonterminal iteration removes exactly one
state, preserves all r distinct-labeled edges, and is kept. Reachability is
preserved under quotienting. An empty blue fringe while red is just the root
therefore implies that only the root remains. There are exactly r iterations,
with state counts q=r+1,r,...,2.

Initialization costs 3r+2. At each such q, the fringe costs 2q+r; fold map
initialization, the one union and state reconstruction cost 3q; closure and
edge reconstruction cost 2r. The candidate and red remap cost two. The final
one-state, r-edge fringe costs 2+r. Consequently

    W_G=3r+2 + sum_{q=2}^{r+1}(5q+3r+2) + 2+r
       =(11r^2+27r+8)/2.

For r=0 the positive is epsilon and the exact cost is four, agreeing with F(0).
Every projected local word is also repetition-free, including empty words, so
its exact cost is F(l_i). Split preparation is r+k. Summing these exact costs
and using sum l_i=r proves the second equation. Expanding squares gives the
gap equation, since r^2-sum l_i^2=2 sum_{i<j}l_i*l_j. QED.

The models have one final root with loops exactly on their observed symbols
(or a final root without edges for an empty word). Hence Global accepts A*,
each factor accepts A_i*, and their projected AND product also accepts A*.
This proves equality on all words for this family; it does not prove target
recovery or extend the pending general equality question.

The sign of the exact gap decides Global, Split or TIE before learning. Net
savings require its absolute value to exceed H. The selector tracks block
volumes and repeated-symbol flags during its existing positive-character visits,
then pays k factor events for the F sums. If this branch is reached,

    H=|Sigma|+3k+1+r.

For w=abcd, blocks {a,b},{c,d}, W_G=146 and W_S=112. H=15, so
15+112=127<146 certifies net Split, with equal languages.

Ties are not restricted to empty data or one block. For w=abcde, use the blocks
{a,b},{c,d,e} and eleven unused singleton blocks {f},...,{p}, k=13. Then
W_G=W_S=209. Conversely, unused blocks can turn a Split advantage into a
Global advantage; the exact k terms must not be discarded.

The repetition-free premise matters: for w=aa the actual Global cost is 39,
whereas blindly substituting r=2 in F gives 53. Negatives are also outside this
theorem because they can reject candidates and alter the execution.

## 7. Attacks on tempting extensions

**Removing unary support is invalid.** Positives {ba}, no negatives, blocks
{a},{b}: W_G=53 and W_S=50. These exact finite counts are reference executions
checked with independent quotient saturation and an independent learner. They
are a counterexample to extending the theorem to arbitrary positive supports.

**Allowing arbitrary unary negatives is invalid.** Positives {aaaa}; negatives
{aaaaaaaa,ab,aba,abb,b,ba,bb}; blocks {a},{b}. Global costs 316 and Split 315.
The negative aaaaaaaa violates the outside-symbol premise. Hence unary positives
alone do not force Global. The static selector retains UNKNOWN on this input;
the exact fallback correctly reports Split after executing the pipelines.

**A static winner need not pay for selection.** Positives {epsilon}, no
negatives, blocks {a},{b}: W_G=4, W_S=10, H=7. The pipeline winner is Global,
but H+W_G=11>10. No claim about all other possible selectors follows.

**A strict cheaper path does not always exist.** Empty positives and negatives,
one block {a}: W_G=W_S=3. Even a zero-cost selector cannot make either pipeline
strictly cheaper than the other. TIE is necessary for a total comparison.

These counterexamples bound our claims; they are not unresolved counterexamples
to the stated, conditional theorems.

## 8. A total exact comparator exists

**Termination lemma.** Let q be the current state count and R the red set.
Every nonterminal iteration decreases q-|R| by at least one. A promotion adds
one red state without changing q. A kept merge initially joins a nonred blue
state to a red state; if all its unions reduce q by d, they can reduce the
number of distinct red images by at most d-1. Thus q_new-|R_new| <= q-|R|-1.
The potential starts at N-1, is nonnegative, and every inner fold has finitely
many unions, each reducing its finite class count. Every closure pass that is
not final performs a union. All scans and candidate lists are finite. Hence
the reference terminates on every valid consistent finite sample. QED.

**Total comparison theorem.** First classify feasibility and try sound static
certificates. If none applies, run Global and all consistent allocated locals,
count their reference events and compare the two integer costs including Split
preparation. Feasibility, termination and finite integer comparison prove that
this procedure returns GLOBAL, SPLIT or TIE on every valid feasible input.
It returns GLOBAL_ONLY for infeasible inputs and INVALID for malformed inputs.
It never returns UNKNOWN when exact fallback is enabled. QED.

This is what `total_selector.py` implements. Its fallback has

    diagnostic_work = H + W_G + W_S.

Therefore its diagnostic work is strictly greater than min(W_G,W_S). It does
not establish useful pre-training prediction or net savings on unresolved
inputs. `training_started=true` and method EXACT_EXECUTION_FALLBACK explicitly
expose this fact. The static-only mode still returns UNKNOWN when appropriate.
Calling the fallback "static analysis" would not change the work it performs.

## 9. A pre-training action for all feasible inputs, with bounded regret

For an UNKNOWN input the static stage supplies sound intervals
L_G<=W_G<=U_G and L_S<=W_S<=U_S. Define

    R_G=max(0,U_G-L_S),    R_S=max(0,U_S-L_G).

Select Global if R_G<=R_S, otherwise Split. This always selects an action
before learning; it does not necessarily select the true cheaper pipeline.
For action A, its excess cost is bounded by

    W_A-min(W_G,W_S) <= min(R_G,R_S).

Proof: for A=G the left side is max(0,W_G-W_S)<=max(0,U_G-L_S)=R_G;
the other action is symmetric. Selection chooses the smaller bound. QED.
Including the selector gives an excess bound H+min(R_G,R_S). The bounds are
attained at opposite interval-box corners when the corresponding difference
is positive. Thus the rule minimizes worst-case regret over the interval box,
not necessarily over the smaller set of realizable RPNI cost pairs.
`bounded_policy.py` marks unresolved actions `winner_certified=false`.
For already certified winners, pipeline regret is zero and total excess is
at most H. GLOBAL_ONLY is handled separately. This is a total action policy,
not a disguised exact pre-training winner theorem.

## 10. What remains open

The universal exact comparator is decidable; inability of our current static
rules to separate intervals does not prove that a cheap exact selector is
impossible. Neither halting-problem undecidability nor a complexity lower bound
has been established or used. General finite tests cannot settle that issue.

The next cost research target is samples with multiple positive symbols and/or
effective global negatives: obtain sound later-attempt bounds, detect additional
exact executions structurally, and account for the extra feature cost. The
seven-negative unary counterexample is a concrete regression target. General
language equality remains a separate future research question, as requested.

## 11. External context, not evidence for our new theorems

- Oncina and Garcia, *Inferring Regular Languages in Polynomial Updated Time*:
  https://doi.org/10.1142/9789812797902_0004
- Rice, *The Algorithm Selection Problem*, author technical report:
  https://docs.lib.purdue.edu/cstech/99/

These establish the learning/selection context. The exact formulas and
conditional certificates here are proved for our supplied program and metric;
they are not attributed to those publications, peer review or formal proof
assistant verification. Earlier proofs and audit reports are bundled separately.

## 12. Reproducible audit results

The main new audit has 12,866 case executions, including exhaustive ternary
labelings of the seven binary words of length at most two under two partitions,
7,936 unary/inert configurations, 300 seeded ternary-alphabet samples, 144 longer
unary attacks, 108 distinct-word partitions and explicit boundary attacks/ties.
It rejects five malformed inputs separately. Previous UNKNOWN counts on this
deliberately targeted suite fall from 10,525 to 805; 9,720 previously unresolved
executions acquire a static winner or tie. No previously decided case becomes
UNKNOWN. This is not a coverage percentage over all finite samples.

The 3,119-case prior regression suite also passes, including balanced examples,
deletion experiments, informative negatives and block-order changes. Together
the audits perform 15,985 case executions and 61,534 independent candidate
quotient checks. Counts are executions and may include duplicate inputs across
categories. Each actual learner model is checked against an independently
implemented partition-saturation learner; stated bounds, exact costs, net guards,
fallback comparison and regret guarantees are checked. Finite checks supplement
the proofs; they do not constitute a universal proof or certify all source code
against every possible implementation defect.
