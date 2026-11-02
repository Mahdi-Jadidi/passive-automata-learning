# Final cost certificates with potential and amortized bounds

## 1. Contract and definitions

The fixed reference and all previously stated input conventions remain in
`rpni_work_reference.py` and the bundled earlier proofs. Samples are finite,
disjoint sets of strings over a known ordered partition. Local acceptance is
AND after erasing outside symbols, epsilon is retained, and each negative is
assigned only to its highest-index witness outside the projected positive set.
An absent witness proves sample-AND infeasibility. Consistency follows from
the initial exact positive trie, preservation of positive paths/final flags
under quotient, and checking every negative before keeping a candidate.

Let p be the positive count, M its symbol volume, Q its prefix set including
epsilon, N=|Q|, E=N-1, A its observed alphabet and s=|A|. Initialization costs
I=M+p+2N-1. Costs count declared loop events in this sparse flat-parent
reference. Sorting, hashing, normalization, allocation, serialization, constant
control/arithmetic, bit complexity and diagnostic assertions are excluded.
Split includes projection/allocation, not explicit product construction.
These are not elapsed-time claims or results for all RPNI implementations.

Write J(n)=n(n+1)/2-1 for n>=1. In particular J(1)=0. When N>1, x is the first
blue label (the least first symbol of any nonempty positive) and
T=|{t in Q:xt in Q}|. Then 1<=T<=N-1. The prefix-forest proof in the earlier
report forces at least T unions in the first candidate, even if rejected.
Each union visits every q retained state record of its candidate.

## 2. Universal union-record lower bound, including rejected candidates

**Theorem 1.** On EVERY valid consistent reference learner input, the total
union-record work over all attempted candidates is at least J(N).

Proof. Every current state remains reachable from the root, since quotienting
preserves every original prefix path. The root remains red. Let v=q-|R| be
the number of nonred states. Initially v=N-1. Termination with no blue state
implies v=0: a path from the root to a nonred state would have a first edge
leaving red and hence a blue target.

If a kept fold has u successful class unions, q drops by u. Red-image count
drops by some h with 0<=h<=u-1, because the initial union joins a nonred blue
state to a red state. Thus the potential drop is d=u-h, with 1<=d<=u.
That candidate incurs q*u union-record visits. Since q>=v+1,

    q*u >= (v+1)d >= sum_{j=v-d+1}^v (j+1).

If an iteration promotes its blue state instead, d=1 and at least one attempted
candidate has at least one union, costing q>=v+1. The same charge applies.
Other attempted folds only add nonnegative work. The potential intervals of
successive iterations partition {1,...,N-1}, so summing charges gives
sum_{j=1}^{N-1}(j+1)=J(N). This argument charges trial unions even when their
quotient is rejected. It never assumes that all states actually merge. QED.
The same proof applies to any later reachable configuration of potential v:
its remaining union-record work is at least J(v+1).

**Theorem 2 (first-candidate refinement).** For N>1, total union-record work
is at least

    C(N,T)=N*T+J(N-T)=J(N)+T(T-1)/2.

Proof. The initial red set contains only the root. Let its only first candidate
perform u>=T unions. If kept, the next potential is N-u-1 and Theorem 1's
rank-charge proof bounds future union work by J(N-u). Therefore total work is
at least f(u)=Nu+J(N-u). Its integer increment f(u+1)-f(u)=u>=0, so the minimum
over u>=T is f(T)=NT+J(N-T). If rejected, the blue state is promoted, the next
potential is N-2, and total work is at least Nu+J(N-1)>=NT+J(N-T). QED.

This applies to arbitrary negative samples and does not assert unchanged
execution, equal outputs or target recovery. It strengthens the older first
candidate NT bound without constructing a later quotient or running RPNI.

## 3. Complete mandatory-work lower bound

For N>1 set delta=0 for no negatives, 1 if epsilon is negative, and 2 otherwise.
The initial fringe costs 2N+E. First-fold map initialization and state
reconstruction cost 2N; at least one closure pass plus edge reconstruction
cost 2E. The first candidate costs one, its negative scan costs at least delta,
and the distinct terminal fringe costs at least 2+s. Labels on positive edges
persist under quotient, so at least s edges survive in every output.

All these events are disjoint from UNION record visits. Hence for arbitrary
consistent samples:

    L_any=I+C(N,T)+4N+3E+3+s+delta <= W.

Using T=1 gives a local lower bound without paying to count local prefix pairs.
The global selector already counts T. For N=1 no candidate exists and W=I+2
exactly, regardless of consistent negatives. The code treats this case directly.

## 4. General upper bound when all negatives are inert

Call a negative inert when it contains a symbol outside A. Every quotient has
only labels in A, so all such words reject under every candidate. If all
negatives are inert (including the empty negative set), every first candidate
is kept, red remains just the root, and the output has one final state with
loops on A when positives are nonempty. For N>1, let

    D=sum_w(1+j(w)),

where j(w) is the one-based first position outside A. Every attempted negative
scan costs at most D; the final candidate's scan costs exactly D.

**Theorem 3.** For arbitrary positive tries under this inert-negative condition,

    I+C(N,T)+4N+3E+4+s+D <= W
    <= B(M,p,E)-E+s+E*D,
    B(M,p,E)=M+p+(11E^2+25E+6)/2.

Proof of lower bound. Use Theorem 2's total union work and all mandatory
nonunion work. The first kept candidate remaps the singleton red set, adding
one. Charge the entire negative work by the final scan D, rather than charging
delta on the first scan; do not add both. The terminal fringe is exactly 2+s.
This yields the stated lower expression. QED.

Proof of upper bound. Consider a kept candidate at q states and e<=E edges,
performing u unions. Its closure has at most u passes: its initial union is
outside the closure, at most u-1 subsequent passes can be productive, and one
final stable pass remains. Its fold costs at most

    2q+q*u+e(u+1).

Including fringe, candidate, red remap and negative testing gives at most

    c(q,u)=4q+q*u+E(u+2)+2+D.

Let F(1)=0 and F(q)=sum_{r=2}^q(5r+3E+2+D). A kept candidate reduces q to q-u,
where 1<=u<=q-1. Direct subtraction gives

    F(q)-F(q-u)-c(q,u)
      =(u-1)(4q-5u/2+2E+2+D) >=0,

since q>=u+1, E,D>=0. Thus all candidate/fringe costs telescope to at most F(N).
Add initialization and the final fringe 2+s. Expanding I+F(N)+2+s yields
B(M,p,E)-E+s+ED. This bound permits arbitrarily repeated labels and arbitrary
branching; it does not use the unique-edge-label property. QED.

For N=1 use exact W=I+2. The selector intersects these bounds with earlier
bounds and exact unary/unique-label formulas, globally and for each applicable
local sample. All extra arithmetic/control lies within the already declared
exclusions, and no new sample/feature loop is needed, so its charged H stays
the same. No optimality of these bounds is asserted.

The upper bound's premise matters: positive {a}, negative {epsilon} gives
W=25, whereas inserting a generic word-scan bound D=1 into the inert upper
formula would give 24. Epsilon is not inert. The implementation checks the
premise before applying this bound. The universal lower bound still applies.

## 5. An infinite two-trace family newly receiving net Split certificates

Fix exactly two singleton blocks {a},{b} over Sigma={a,b}, distinct characters,
no negatives, and n>=2. Define

    S+={ b a^n b^(n-1),  b a b^(n-1) a^(n-1) }.

Both words have length 2n and contain n copies of each character. They share
exactly the prefix ba, so p=2, M=4n, N=4n-1 and E=4n-2. The only first blue
label is b. Every nonempty prefix begins with ba (except b itself), so bb is
not a prefix and T=1: only t=epsilon has bt in Q.

Each local positive set is the singleton a^n or b^n. The proved exact unary
cost for n>=2 is v(n)=n^2+12n+11. Preparation costs 4n+4. Therefore

    W_S=2n^2+28n+26.

Theorem 3's lower bound specializes to

    L_G=8n^2+38n-6.

The actual selector's H is exactly 20n+19. Event accounting:

| Event group | Count |
|---|---:|
| Configuration, input and active-block scan | 4n+8 |
| Singleton gate | 1 |
| Global prefix creation | 4n-1 |
| Projection words, characters and slots | 4n+6 |
| Prefix-pair tests | 4n-1 |
| Local factors, prefix creation, positive words/characters | 4n+6 |
| Total | 20n+19 |

No full-balanced-marker scan runs because there are no negatives. The sample
uses both blocks, so the single-active shortcut does not run. It has two
positives, so the single-word shortcut does not run. Global support has two
symbols and E>2, so the early unary and unique-edge exact shortcuts do not run.

Consequently

    L_G-(H+W_S)=6n^2-10n-51.

At n=4 this is five. Its increment from n to n+1 is 12n-4>0 for n>=4.
Thus every member with n>=4 has a pre-training NET_SPLIT certificate.
This is a sufficient threshold for this certificate, not a necessary length
or sample-count threshold for every algorithm/input.

At n=4 the positives are baaaabbb and babbbaaa. The certificate is

    H=99, W_S=170, L_G=274,
    H+W_S=269<274<=W_G.

The previous selector's global lower bound is 44n-6, and
(44n-6)-W_S=-2(n-4)^2<=0. Its split cost is exact, and its global upper bound
cannot certify Global because the new proof gives W_G>W_S for n>=4.
Its early families do not apply, so it returns UNKNOWN for ALL n>=4 here.
The new result is an infinite strict coverage extension, not merely a finite
test-set improvement.

With no negatives all candidate merges keep in both pipelines, so the previously
proved support-star argument also proves both output languages equal {a,b}*.
This special-case equality does not answer the pending general equality question
or prove recovery of the actual target language.

## 6. Global certificates remain independently available

For unary positive support {a} with a nonempty positive, let r be its maximum
length, m its total length and s_p its positive count. The exact no-negative
cost is V=m+s_p+r^2+(9+d_r)r+10, with d_r=1 if r=1 and 2 otherwise.
Its first fold collapses the whole chain; it has r unions, d_r closure passes,
fold work r^2+(4+d_r)r+2, initial fringe 3r+2, final fringe three, candidate
one and remap one. This proves V by direct summation.

For arbitrary consistent local negatives, cost is at least V: everything
through the first fold costs V-4. Keeping it pays remap+terminal fringe four;
rejecting it causes the next unchanged-trie fringe to cost 3r+2>=5. Hence
either continuation covers the remaining four. If all GLOBAL negatives contain
an outside symbol, W_G=V+D. The active factor costs at least V even with
informative assigned local negatives; inactive factors cost four. Thus

    W_S-W_G >= K=Pi+4(k-1)-D
      >=M+kp+(2k-1)z+4(k-1)>0.

This is the existing infinite Global region. Net Global requires H<K.
It is cost-only unless a separate equality rule applies. For positive aa,
negatives bb,bbb, blocks {a},{b}: H=16, W_G=43, W_S=60, so 59<60.

Counts alone do not select a universal winner: with the same p=2, z=0,
M=16 and singleton partition, positives {a^7,a^9} give W_G=208,W_S=232,
whereas the n=4 two-trace family has W_S=170 and W_G>=274. The individual
lengths and prefix structures differ; no equality of every feature is claimed.

## 7. Total comparison versus total pre-training coverage

`total_selector.py` returns an exact direction/tie on any valid feasible finite
sample, using actual reference runs when static intervals overlap. This fallback
is explicitly marked and costs H+W_G+W_S; it is not a pre-training savings
theorem. Infeasibility and invalid inputs have distinct statuses.

The earlier finite-vocabulary compiler is also retained. For any fixed finite
vocabulary of d distinct words and fixed ordered partition, every word is
absent/positive/negative, giving exactly 3^d datasets. Offline exhaustive runs
fill a complete table, and lookup executes no RPNI. The all-length-at-most-two
binary table has 2187 rows: 754 Global, 493 Split, 15 ties and 925 AND-infeasible.
Its offline event cost 405921 and setup cost 2215 must not be omitted. Its finite
domain and cost proof are in the previous coverage report. It does not cover
all unbounded strings or establish a cheap universal selector.

The certified region is decidable membership in our implemented predicates and
interval inequalities. An UNKNOWN result proves only the absence of a current
certificate. It is not undecidability or an impossibility theorem. General
language equality remains a separate next research question.

## 8. Arbitrary-negative upper bound

The final arbitrary-negative upper bound also tightens the previous generic
upper bound. In a candidate at q states/e edges, u<=q-1 and closure passes<=u,
so its fold costs at most q^2+q+qe. There are at most N-1 iterations and N
fringes. At iteration j the old red count is at most j, since promotion adds
one and a kept merge never increases red count. Thus candidate count is at most
C=N(N-1)/2 and TOTAL red-remap visits across kept iterations are also at most C.
Every fringe costs at most 2N+E, and every negative scan at most
d=sum_w(|w|+1). Consequently, for arbitrary consistent samples with N>1,

    U_any=I+N(2N+E)+C(2+N^2+N+NE+d).

The two C terms outside the fold/negative expression count candidate events
and red-remap visits separately. For N=1 the exact I+2 rule still applies.
All terms are monotonically extended from current q/e to initial N/E. This
upper bound needs no inertness, uniqueness or balanced-data assumption.

## 9. Audit and repair record

The new audit checks ALL 32768 positive subsets of the 15 binary words of
length at most three, all 2187 ternary labelings of words of length at most two,
1500 seeded arbitrary effective-negative samples, 250
inert-negative variants and nine instances of the infinite family. It directly
checks union-record charges on all attempted folds, including rejected folds,
exact fold-event arithmetic, both new bounds and independent partition-saturation
quotients. Finite audits supplement the universal proofs above.

An initial integration of the universal local lower bound double-counted two
terminal events for a one-root local automaton. Exhaustive tests caught the
error. The root case now sets its exact cost directly to I+2; all suites are
rerun after this repair. No failed version is part of the final selector.
This was an implementation error, not a counterexample to the stated theorem.
