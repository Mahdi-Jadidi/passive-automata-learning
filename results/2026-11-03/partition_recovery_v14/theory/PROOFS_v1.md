# C014 — exact fast path and qualified ownership recovery

Direct proofs ready for independent review. No code runs or historical edits.
Model: known nonempty disjoint Σ, independent arbitrary regular acceptors,
exact complete-word P/N, default no-K. Named physical IDs are not inferred.
An optional trusted count variant is explicitly separate. No noise, state
bound, prefix closure or prime restriction is silently introduced.

## T1. Exact unary-count / all-Bell fast path

For each a∈Σ put C_a={|p|_a:p∈P}. Then the following are equivalent:

1. For every n∈N there is a∈Σ with |n|_a∉C_a.
2. The singleton partition is sample-compatible.
3. Every unordered partition of Σ is sample-compatible.

Proof. A singleton factor must accept each a^c for c∈C_a. If one negative
has all its unary counts in the respective C_a, every singleton factor is
forced to accept it. Conversely F_a={a^c:c∈C_a} are finite regular witnesses
when condition1 holds: every positive passes all factors, every negative
fails at least one. Finally every partition is a coarsening of singletons;
merge these regular witnesses to preserve the global language. Thus2⇒3;
3⇒2 is immediate. ∎

This is an exact result, not a heuristic or assumption of absent dependence.
The same criterion is proved in C013 theory/ALL_PARTITIONS_CONDITION_FA_v1.md.
An unsuccessful fast-path test means only “use the exact fallback,” not
inconsistency or successful ownership recovery. Distinct positives can supply
the unary images for distinct symbols; do not require one matching Parikh
vector or exchange the negative/block/positive quantifiers.

With m=|Σ|, total Z=Bell(m), count at k=S(m,k). For each symbol pair i,j,
same count q=Bell(m−1), different count d=Z−q, for m≥2. Contracting that
pair to a single object proves the q formula bijectively. All pairs are
ambiguous when m≥2. One-block and singleton partitions give shared same and
different witnesses respectively. Use direct factors H(B)={π_Bp:p∈P} to
produce the existing projection-witness records; no hidden DFA size limit.

Boundary cases: m=1 has Z=1 and no pairs; N=∅ satisfies condition1 vacuously;
P=∅ gives C_a=∅ and empty-language factor witnesses. Contradictory labels
cannot satisfy the condition. Any empty version space/invalid input remains
distinct from identified ownership. Test labels are not created by absence
from a positive log.

### Existing C010 expanded output semantics

The exact fast path can populate every required total/per-k/pair/witness
field without listing Bell(m) partitions by default. It establishes a
feasible singleton atom partition: any valid adjacent-swap edge between
opposite labels would contradict singleton feasibility, so such edges
cannot exist here. A sound C010-compatible atom representation is therefore
the singleton partition with empty swap witnesses, both k upper bound and
exact sample kmax equal to m. For m≥2 status is multiple compatible answers,
not unique recovery; at m=1 it is uniquely one-block.

Shared witness objects must be immutable/read-only (or copied on exposure).
Ordinary JSON still expands every pair row and full witness: internal sharing
does not remove serialization costs. Registry-only or omitted pair fields
would require a new output contract, not this fast path. --enumerate, if
requested, still owes the complete family or an incomplete result.

A literal scalar-count preprocessing can use O(T+(P+N)m) work under standard
set/integer accounting, where T is total characters, including zero counts
for absent symbols. No measured dominance is claimed. Projection records
and output cost remain. The fast path proves uninformative ownership data
quickly; it does not make the data informative.

### Optional trusted K variant

If explicitly using a nonempty allowed set K⊆{1,...,m}, restrict the family:

    Z_K=Σ_{k∈K}S(m,k),   q_K=Σ_{k∈K}S(m−1,k),   d_K=Z_K−q_K.

Each pair is forced same/different/ambiguous according as q_K=Z_K, q_K=0,
or 0<q_K<Z_K. Same witnesses exist whenever some k∈K has k≤m−1: place the
pair together, then partition the resulting m−1 units into k groups.
Different witnesses exist whenever some k∈K has k≥2: keep the pair in
different groups and distribute others to achieve k. These choices always
fit because all partitions fit. The two globally shared no-K witnesses need
not satisfy K; construct permitted witnesses instead. For m=1 no pair
formula is applied. Empty/malformed K is handled explicitly, never vacuously.

## T2. Adjacent positive/negative swaps force coownership

If p=u x y v is positive and n=u y x v negative, x≠y, then x,y coown in
every compatible model. If separated, any block sees either x alone, y
alone or neither from the swapped part; all block projections of p,n are
identical. Independent factors accepting p would accept n, contradiction. ∎

Thus a graph of independently replayed exact swap witnesses has no edge
crossing a true ownership block, provided labels and model assumptions hold.
Its connected components refine the true partition and every compatible
partition. An absent edge is not evidence of separate owners.

## T3. Recovery with explicit block coverage

Let Π_true be the actual partition and G the sound witnessed graph on all
known symbols, including unobserved/isolated ones. Suppose, as an explicit
additional coverage premise, G restricted to each true block is connected.
Then G's connected components are exactly Π_true.

Proof. Soundness excludes cross-block paths. Connectivity puts every symbol
of a true block in one component. Both inclusions give equality. ∎

This is a recoverability theorem, not a guarantee that arbitrary passive
traces contain the necessary witnesses. If exact true K is independently
trusted and G has exactly K components, equality already follows: the true
partition is a coarsening of components, and a proper merge reduces count.
Indeed there is then exactly one sample-compatible partition with that K,
because the actual model proves existence and no split/merge is possible.

When coverage holds but K is not supplied, the unrestricted sample version
space still contains all coarsenings of Π_true. Since Π_true is itself
compatible, the feasible family is exactly those coarsenings: Bell(r) answers
and S(r,k) at each k, for r graph components. Reporting graph components as
unconditionally identified physical truth would therefore be wrong for r≥2.

An externally justified coverage promise restricts candidate truths: a larger
merged “actual block” would have disconnected observed graph and violate
that promise. Within that restricted class the components are identified.
The promise is not verified merely by graph construction or a successful
atom-projection test. “Actual factors are prime” by itself is also different:
unseen long couplings can make finite-sample alternative prime factors;
C008's finite prime counterexamples remain relevant. Define any “true atomic”
assumption precisely as a coverage/minimality restriction before using it.

## 4. Concrete recovery world, correct labels and remaining ambiguity

Take Σ=abcd with true devices ab and cd. Each has states0,1, start/accept0
and reject1. Device ab sets state1 on a and state0 on b, irrespective of
the previous state; device cd sets1 on c and0 on d. These are complete,
strongly connected two-state DFAs. Their acceptance depends on local order.

P={ε,ab,cd}, N={ba,dc} are correctly labelled: ab/cd leave the respective
device accepting, while ba/dc leave it rejecting. Positive ab versus negative
ba witnesses edge ab, and cd versus dc witnesses edge cd. The graph is
connected inside each actual block with no cross edge. Its components are
ab|cd. Exactly two unrestricted partitions remain, ab|cd and abcd.

With trusted K=2, the actual ownership is uniquely recovered. With no-K,
components equal the actual world in this example, but the sample does not
prove nature chose it rather than one device accepting the same global
language. Claim uniqueness only with the additional trusted information or
explicit coverage restriction on candidate truths. These are mathematical
world tables and words, not claimed executed/saved sample files.

## 5. Concrete failures and limits

**Commutative world.** Let each actual pair block ab,cd accept exactly when
both of its symbol counts are even. A four-state parity DFA is complete,
strongly connected and has accepting start/nonempty rejection. Adjacent
swaps never change the global label, so no positive-to-negative swap edge
can exist even with the full language. Grouping instead ac|bd gives exactly
the same complete language. Count K=2 alone cannot distinguish these truths.

**Uninformative finite data.** On that parity world choose
P={ε,aa,bb,cc,dd}, N={a,b,c,d}. Each negative has an odd unary count unseen
in the positives; T1 applies and all15 alphabet partitions fit. The actual
ab|cd is compatible, but not recovered. All seven K=2 partitions also fit.
Longer arbitrary words do not automatically repair this lack of coverage;
C013's fixed-world arbitrary-length example establishes that separately.

**Graph incompleteness.** P={ε,aabb,ccdd}, N={bbaa,ddcc} has no adjacent
swap edge yet forces ab and cd semantically. Equal-count binary reversal
is not a single adjacent swap. Failure of this graph certificate is not
failure of exact feasibility search or proof that recovery is impossible.

## 6. Passive boundary and decisions

A passive solver reads a fixed collected P/N sample. It must not relabel an
unobserved swapped word as negative. A separate simulator/oracle collector
may deliberately evaluate calibration words and then provide their actual
labels; that collection is an additional intervention/active acquisition
step. Its cost, queried word policy and world access must be declared and
kept out of the passive inference input. The recovery theorem concerns the
resulting witnessed coverage, not guaranteed passive acquisition of it.

Rejected conclusions: “all-Bell fast path recovers ownership”; “no swap edge
means independence”; “known count alone always recovers”; “successful graph
components are physical truth without coverage/count information”; “prime
real factors certify sampled minimality”; “oracle calibration is free passive
data”; “more length ensures informative labels.” None follows from the proofs.

No implementation or timing claim accompanies this note. Mathematical and
source-review statuses remain separate; future code needs frozen readiness
and independent exact-count/witness verification.
