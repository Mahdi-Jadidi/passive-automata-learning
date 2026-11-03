# C013 — product labels, bounded repair and honest evaluation

Direct proofs awaiting source review and independent audit. No experiments,
source model execution, old-cycle edits or new acceleration. Default inference
is exact C010 no-K; an explicitly authorized count-known variant would use
the separate declared model class, not silently reveal the true count.

## 1. World model and product-label correctness

Device i owns nonempty disjoint alphabet Σ_i and complete deterministic DFA
(Q_i,δ_i,0,F_i). Every transition is saved. Assume 0∈F_i, Q_i\F_i nonempty,
and the directed transition graph is strongly connected. Let s_i=|Q_i|,
s=max_i s_i. The true global label of w is

    accept(w) iff for every i, δ_i*(0,π_{Σ_i}w)∈F_i.

This is precisely independent interleaving semantics: events not owned by i
do not change its state. Induction over w proves that global execution ends
with these local projected states. Hence independent replay from world.json
can validate every saved word without any inference algorithm.

The world and ownership are audit truth only. solver_input contains the
known full alphabet and exact P,N, never transition tables, true partition,
repair annotations, acceptance targets or generator state. Fitting the truth
to the sample does not validate the solver's complete answer family.

## 2. Strong connectivity gives bounded repairs

Every state can reach every nonempty target set. A shortest path to the set
has no repeated state before its first target: remove the repeated-state
cycle to shorten it. Therefore its length is at most s_i−1. This applies
to both F_i and Q_i\F_i, including a zero-length path when already there.

Draw a prefix w₀ of length b by the declared sampling rule; let A be devices
that occur in it. Then |A|≤min(K,b). Compute q_i after the prefix projection.
An inactive device has q_i=0 and is accepting, so it needs no positive repair.

Positive construction: append to each active device's local prefix a shortest
continuation to F_i. Negative construction, requiring |A|≥1: choose one
active device j and continue it to Q_j\F_j; continue every other active
device to its accepting set. Leave inactive devices untouched. The final
product is positive in the first case and negative in the second (indeed
exactly the selected device is rejecting in the latter).

The sum of suffix lengths is ≤Σ_{i∈A}(s_i−1)≤min(K,b)(s−1). Thus

    b + min(K,b)(s−1) ≤ L

guarantees length at most L for either construction. There is no exponential
positive-rejection sampling step: acceptance is enforced constructively.
An implementation should record actual repair lengths and final acceptance
states; a reserve bound is not a replacement for replay.

Two valid output schemes differ in distribution: keep w₀ as a global prefix
and shuffle only the suffixes, or shuffle all repaired local words from
scratch. Both preserve local orders and labels; the second does not retain
w₀ as an actual global prefix. Source/protocol must identify which is used.

## 3. What uniform interleaving really means

For fixed local words of lengths l₁,...,l_K, the number of order-preserving
device schedules is M!/∏l_i!, M=Σl_i. To sample schedules uniformly, select
the next device with probability remaining_i / remaining_total and emit its
next symbol. Any fixed schedule then has probability ∏l_i!/M!, since its
numerators multiply to the local factorials and denominators to M!.
Disjoint alphabets make different schedules different global strings for
these fixed local words, so uniform schedules are uniform interleavings.

Choosing uniformly among currently nonempty devices is NOT this distribution.
For words aa and b it gives aab,aba,baa probabilities 1/4,1/4,1/2 rather
than 1/3 each. Shuffling suffixes uniformly establishes only conditional
uniformity of suffix interleavings, not uniformity over all accepted words.

## 4. Feasibility, tiny lengths and uniqueness shortfalls

With all starts accepting and L=0, ε is the only word and no negative exists.
At most one distinct positive can be returned. More generally there are only
Σ_{ell=0}^L m^ell global words, with possibly far fewer of either label.
Any requested unique per-label sample count can exceed the available set.
Bound attempts, preserve raw counts/duplicates and report shortfall; do not
loop forever or silently reduce counts while reporting full success.

The reserve may admit no b≥1 for a small L, making the proposed active-prefix
negative construction unavailable. This is NOT a proof that the DFA product
has no negative of length≤L: a rejecting state might be one transition away
even when worst-case reserve s is too large. Distinguish:

* proved label impossibility (e.g L=0 under accepting starts);
* unsupported conservative repair budget / construction failure;
* uniqueness shortfall after bounded attempts, not proof of exhaustion.

Possible future exact feasibility check: find each device's shortest rejecting
word from its start. Other devices remain inactive/accepting. The minimum of
these lengths is exactly the shortest negative global length: any negative
global word has a rejecting device and is at least its shortest rejecting
projection length, and a shortest local rejecting word realizes the minimum.
This theorem need not introduce a new feature; review whatever the frozen
generator actually promises. Requests must not be labelled mathematically
impossible on reserve failure alone.

## 5. Random does not mean uniformly random DFAs or accepted words

Constructing a spanning cycle then randomizing other transitions ensures
strong connectivity but favors DFAs containing the constructed cycle.
Rejection sampling unrestricted transition tables until strong connectivity
would be a different conditional distribution. Accepting start and at least
one reject, randomized ownership sizes/assignment, target K selection, seeds,
tie-breaking shortest paths and frequency distribution all need declaration.
Do not claim uniformity over all DFAs without a proof of that sampler.

Repair biases output toward states with short chosen paths; near-max length
and reserve selection bias prefix/final lengths; choosing a rejecting device
biases negative structure. Deduplication conditions on earlier samples.
Any resampling of invalid/unavailable worlds further conditions the world
distribution. Record attempts and conditioning, not only retained successes.
Uniform event sampling and uniform device sampling differ when alphabet sizes
differ. Event frequency and number of samples are distinct experimental axes.

## 6. Evaluation: separate four questions

1. Label correctness: every P/N replayed against saved transitions agrees.
2. Truth compatibility: the actual ownership satisfies the projection
   criterion on these samples and is inside the declared inference class.
3. Ownership recovery: a completed solver has exactly one compatible partition
   and it equals truth. With no-K, only uniquely-one-block can occur; true K>1
   necessarily leaves the one-block merge as a distinct explanation.
4. Ambiguity/censoring: completed multiple answers mean unresolved ownership;
   incomplete/timeout means no exact count or universal recovery conclusion.

For a completed result, every forced same/different relation must match saved
owners if the true model is admissible. This is necessary but not sufficient:
a solver can omit valid alternative partitions while retaining truth and all
its relations. Small independent full-set RGS/count/pair/witness comparison
is required. On large cases, truth compatibility and witness replay must not
be relabelled a complete-family oracle. No-K consistent results cannot force
different, because the one-block model always exists.

If count-known inference is explicitly chosen, the true count belongs only in
the declared allowed_k field, and guarantees become conditional on that count.
It changes the version space; comparisons with no-K must say so. Knowing K
alone need not identify the ownership. Pending clarification is not permission
to select whichever variant produces a nicer recovery result.

## 7. Separate generator cost from exact C010 inference cost

The sweep uses m=40 for K=1,...,20, at least two symbols/device. Thus m is
fixed while ownership blocks and observed must-link atoms r≤40 can change.
Actual local alphabet sizes, states and transition counts should be reported;
K alone does not specify them. Equal world per K across length/sample cells
reduces one source of confounding but does not create a uniform distribution.

World tables have Σ_i s_i|Σ_i| entries. BFS to targets and paths, prefix
simulation, suffix construction, interleaving, deduplication, saved-model
replay, JSON writing and world-generation rejection/conditioning contribute
to generation cost. With precomputed state-to-target path choices and fixed
world, successful per-word construction/replay is linear in generated length
up to device-choice/data-structure cost. Raw retries, duplicate checks and
serialization must also be included; no blanket total-linear claim.

C010 must not be credited with C011 RLE/index improvements. Its positive×negative
adjacent-swap scan has O(PNL) character-work upper bound; projections cost
O(T) per evaluated block, up to O(2^r T) under ordinary set/hash accounting.
Exact DP has at most (r+1)2^r2^n states and O((r+1)3^r2^n) branch work,
with pair-vector and big-integer factors; n is unique negatives. Witness DFS
can backtrack separately. Default counts do not enumerate every Bell partition;
optional full enumeration and expanded pair witnesses can dominate output.

For m,P,N fixed, length growth increases string work polynomially, not 2^L;
the parameter-separated caveats are in C012 theory/COMPLEXITY_FA_v1.md.
Larger P/N can alter coverage states and caching; larger K can alter r even
when m is fixed. Timing a finite grid establishes observed costs/censoring,
not an asymptotic exponent or a general worst-case theorem. Include failed,
unstarted-budget and incomplete cells rather than filtering them out.

## Source-review checklist / preserved false ideas

Reject claims that reserve failure proves label impossibility; random accepted
output is uniform over accepted words; uniform active-device choices give
uniform interleavings; correct labels certify full solver answers; truth-in-set
means unique recovery; hidden K can be fed silently to a no-K evaluation; or
empirical timing proves asymptotic complexity. These are mathematical review
decisions, not failed executable runs. Upcoming generator source/readiness must
be inspected before execution; this note itself is not source clearance.
