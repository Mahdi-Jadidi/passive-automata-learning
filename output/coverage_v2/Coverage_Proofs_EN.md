# Extending static coverage and complete finite-domain selection

## 1. Precise scope

Inputs are finite disjoint positive/negative sets of finite character strings
over a known ordered nonempty partition into nonempty disjoint alphabet blocks.
Composition is inverse projection followed by AND. The fixed shortlex reference,
canonical representatives and highest-index negative-witness policy are supplied
in `rpni_work_reference.py`. Local state counts are unrestricted. Empty words,
empty samples, inactive blocks and ties are included.

W_G/W_S are reference loop-event counts. Split includes preparation, but not
an explicit product or minimization. Selector/compiler/setup/query events are
declared record visits with unit weight. Sorting, hashing, normalization,
allocation, serialization, constant arithmetic/control and integer bit costs
are excluded, as are diagnostic assertions. No wall-clock or general RAM-model
complexity/speedup follows. In particular, hashing a string is not claimed to
take constant machine time merely because its internals are outside this metric.

There are two new results:

1. An exact pre-training comparison for arbitrary positive samples whose
   prefix trie has at most one edge of each observed label, with no negatives;
   plus sound extensions with arbitrary or inert negatives.
2. An exact pre-training lookup for ALL consistent labelings over ANY fixed
   finite vocabulary and partition, after explicitly charged exhaustive offline
   compilation. This is total on its declared domain, not on unbounded strings.

The unrestricted cheap exact pre-training selector remains unproved. The
existing total exact comparator uses reference execution on unresolved inputs;
its execution fallback is not renamed as static prediction.

## 2. A decidable structural class beyond one positive word

Let Q be the positive-prefix set including epsilon, N=|Q|, E=N-1, A the
positive symbol support, m the total positive length and p its cardinality.
Each observed label appears on at least one prefix-trie edge, so E>=|A|.

**Recognition lemma.** E=|A| iff every observed symbol labels exactly one
positive-prefix-trie edge.

Proof: map each edge to its character label. This map is surjective onto A.
It is injective iff the finite domain and image have equal cardinality. QED.

Shared positive prefixes and multiple terminal nodes are allowed. For example,
{a,ab,ac} has one a-edge, one b-edge and one c-edge. Counting total character
occurrences in sample records would incorrectly reject it. The selector counts
distinct prefixes, so it tests the actual structural property.

**Projection lemma.** Every local positive-prefix trie also has one edge per
observed local symbol.

Proof: if a in block B_i occurs on the unique global edge u --a--> ua,
every positive occurrence of a has precisely the global prefix u before it.
After projection, every such occurrence has the same local prefix pi_i(u),
so it creates the same local edge pi_i(u) --a--> pi_i(u)a. Thus a cannot label
two local edges; each observed local symbol still labels at least one. QED.

## 3. Exact no-negative cost

Define

    B(m,p,E)=m+p+(11E^2+25E+6)/2.

**Theorem 1.** For a unique-edge-label positive trie, W=B(m,p,E) when the
negative sample is empty, independently of its branching and terminal pattern.

Proof: every candidate identifies two distinct states. Every label occurs on
only one edge, and quotienting cannot create a second edge with that label.
Hence no deterministic target conflict exists. A fold performs exactly one
union and one stable closure pass. At q current states its work is 3q+2E:
q map-initialization visits, q union visits, q state-reconstruction visits,
E closure visits and E edge-reconstruction visits. The edge count stays E.

With no negatives every first candidate is kept. Red remains the singleton
root; each iteration removes exactly one state. All quotient states stay
reachable. If blue were empty while a nonred state remained reachable, the
first edge on a root path leaving red would give a blue state. Thus termination
occurs exactly at one state, after E iterations with q=E+1,...,2.

Initialization costs m+p+2E+1. Each iteration costs fringe 2q+E, candidate one,
fold 3q+2E and one red-remap event. The terminal fringe costs 2+E. Therefore

    W=m+p+2E+1 + sum_{q=2}^{E+1}(5q+3E+2) + 2+E
     =m+p+(11E^2+25E+6)/2.

For E=0, positives are empty or {epsilon}, and the same formula gives p+3,
the exact one-root cost with no candidates. QED.

**Corollary 1 (complete comparison on this class).** With no negatives, both
global and local costs are exact before training:

    W_G=B(M,p,E),
    W_S=Pi+sum_i B(m_i,p_i,E_i),
    Pi=M+k*p.

Here local positives are SETS of projected words; m_i and p_i are computed
after deduplication. They must not be replaced by the raw projected-record
volume/count. Projection preserves the structural property by the lemma.
The sign of the exact gap decides Global, Split or TIE for every member of
this class, under every ordered partition. Net saving additionally requires
the gap's absolute value to exceed the charged static selector work H.

Example: positives {a,b,c,d,e,f,g,h}, no negatives, blocks {a,b,c,d},{e,f,g,h}.
Global has m=p=E=8, so W_G=471. Each factor has four one-letter positives and
epsilon, giving m_i=4, p_i=5, E_i=4 and cost 150. Pi=24, so W_S=324. H=109;
109+324=433<471 proves net Split before learning. The earlier selector returns
UNKNOWN on this input. The branching trie is not a single positive word.

For positives {a,b}, no negatives, blocks {a},{b}, the exact costs tie at 54.
No selector can produce a strict cheaper pipeline on that input.

## 4. Lower bound with arbitrary consistent negatives

**Theorem 2.** For the same positive structure and ANY consistent negative
sample, W>=B(m,p,E).

Proof: folds still have one union and one stable pass, regardless of rejection.
Let R be red. A kept merge reduces q by one and preserves |R| because it joins
one nonred state to one red state with no additional unions. A promotion raises
|R| by one and preserves q. Thus q-|R| decreases exactly once per nonterminal
iteration, from E to zero. Reachability and the blue-path argument establish
that the terminal potential is zero, so there are exactly E iterations.

Before iteration j, at most j-1 kept merges have removed states. Its state
count q_j is at least E+2-j. It pays a fringe 2q_j+E and at least one candidate
plus its fold 1+3q_j+2E. If an attempted candidate is kept, red remapping costs
at least one. If all candidates are rejected, at least one negative-word event
was paid instead. Hence in either case the iteration costs at least
5q_j+3E+2, the no-negative expression at a state count no smaller than baseline.
The terminal fringe costs at least 2+E. Add the unchanged initialization and
sum to obtain B. For E=0, no candidate exists and B is exact. QED.

This proof does not infer that informative negatives preserve the same execution
or output. It only gives a lower bound. It can tighten global and local bounds
even if their negatives reject merges.

## 5. Tighter bounds and exact subcases with inert negatives

A negative is inert here if it contains a label outside the positive support A.
For each such w let j(w) be its first outside-label position, one based, and
D=sum_w(1+j(w)), z=|S-|.

**Theorem 3.** If all negatives are inert and E>=1,

    B+2(E-1)z+D <= W <= B+E*D.

Proof: quotient edges retain only labels in A, so every negative is rejected
under every candidate. All first candidates are kept, and the structural
execution is exactly the no-negative execution with E attempts. In any attempt,
each negative costs at least one word and one symbol event, and at most
1+j(w), because an outside label has no edge. The last candidate has one final
state with loops on all A, so it reads each negative exactly through its first
outside symbol and costs D. The preceding E-1 attempts cost between 2z and D
each. Add their costs to B. QED.

For E=0 there are no attempts and W=B, regardless of negatives. With no
negatives D=z=0, the interval collapses to B. If every negative begins outside
A, D=2z and W=B+2Ez exactly. The same theorems apply independently to every
local factor after the fixed negative allocation, even when only some factors
have the special positive structure. The selector intersects these bounds with
the previous valid intervals. Intersections remain sound and cannot remove an
already certified direction, since H is unchanged.

In particular, if both the global and all assigned local negatives begin
outside their respective supports, all costs are exact and either sign or a
tie is decidable. A global outside symbol alone does not imply that its assigned
local projection is inert: allocation can select another block. This condition
must actually be checked locally. General output-language equality remains
separate, using only the previously proved equality certificates.

## 6. Complete finite-domain compilation

Fix an ordered partition and a finite vocabulary V=(v_0,...,v_{d-1}) of distinct
valid words. The domain consists of all disjoint pairs S+,S- subset V.

**Theorem 4.** There are exactly 3^d such samples, in bijection with ternary
keys t=sum_i label_i*3^i, label_i in {0,1,2} meaning absent, positive, negative.
An exhaustive compiler produces a table that exactly classifies every sample
in this domain as GLOBAL, SPLIT, TIE or GLOBAL_ONLY. A lookup executes no RPNI.

Proof: each vocabulary word has exactly three mutually exclusive statuses.
The product rule counts 3^d assignments, and base-three representation makes
their keys unique and exhaustive in [0,3^d). For every assignment the compiler
forms its finite positive/negative sets. The witness criterion proves whether
an AND decomposition exists: each negative needs a projection outside that
factor's positive projection set. Necessity follows since every accepting
factor contains all its projected positives; sufficiency follows by choosing
the finite languages of those projected positives. If feasible, highest-index
allocation makes every factor sample consistent. Global and local reference
executions terminate, so their integer costs including preparation can be
compared exactly. The compiler writes the corresponding row at its unique key.
If infeasible it records GLOBAL_ONLY, not a cost comparison to an inadmissible
consistent Split model. The query reconstructs the same unique key and reads
that row. No learning routine is imported by `compiled_selector.py`. QED.

Reference consistency follows directly from its update rule: the initial prefix
trie accepts exactly S+, hence rejects disjoint S-. Quotienting preserves each
positive path and uses the OR of old final-state flags, so it preserves positive
acceptance. A candidate is kept only after every negative is rejected; a rejected
candidate changes no current transition, state or final flag. Promotion changes
only the red set. This invariant proves sample consistency of every returned
global/local model, including empty samples. It is not target identification.

Reference termination: each nonterminal iteration reduces q-|R| by at least
one; a promotion adds a red state and a kept fold initially joins a nonred
blue state to a red one, so its state reductions exceed its red-image reductions
by at least one. The potential is a nonnegative integer initially N-1. A fold
has finitely many class-reducing unions and every nonfinal closure pass makes
a union. All other scans are finite. Thus every sample used by compilation
has a terminating reference computation.

Contradictory labels are INVALID. A word outside V is OUT_OF_DOMAIN, never
silently truncated or predicted from a neighboring row. The CLI also rejects
a query partition different from the compiled partition. The class instance's
partition is fixed by its table. The table loader checks completeness, numeric
signs and a digest; the digest is an integrity check, not a mathematical proof
of compiler correctness. The exhaustive audit verifies all generated costs.

## 7. Offline, setup and query costs are not free

Compilation actually executes learners on all assignments; this is not a
universal cheap analytic formula. Its declared total C includes domain
validation, vocabulary index visits, d label visits per assignment, preparation
on every assignment, every global run, local runs on feasible assignments,
local dispatch visits and table-row emission. Preparation always scans all
negative witnesses, even when an infeasible one exists, so it costs exactly

    Pi=M+M_minus+k(p+2z)

per assignment. Table loading/setup S includes domain/index checks and one
validation visit per row. Lookup Q_work=1+p+z counts initialization and one
visit per distinct labeled word. Library parsing/hash/serialization/bit costs
are excluded, as stated in the metric. Allocation and storage are substantial:
the implementation retains 3^d rows. This exponential storage cost belongs to
THIS method, not an established lower bound for every possible selector.

For a stream of queries compared with always rerunning Global, let
Delta_j=W_G,j-W_chosen,j >=0. Full strict net saving requires

    sum_j Delta_j > C+S+sum_j Q_work,j.

Proof: subtract C+S+sum_j(Q_work,j+W_chosen,j) from sum_j W_G,j. QED.

For a constant cost profile with Delta>Q_work, the least integer query count
meeting this inequality is floor((C+S)/(Delta-Q_work))+1. This is an accounting
example assuming each query's learner is rerun. Repeated identical samples
could instead reuse previously trained models; no superiority over such caching,
optimal amortization or practical runtime benefit is claimed. In fact, compiling
every possible labeling is often a poor acceleration strategy. Its value here
is a complete and auditable bounded-domain baseline.

For d>=1, independent counting checks total preparation across compilation:
each word is positive in 3^(d-1) assignments and negative in as many, hence

    sum_assignments Pi = 3^(d-1)*(2 sum_{w in V}|w|+3kd).

## 8. What "all inputs" means and does not mean

For ANY predeclared finite V and partition, compilation covers EVERY consistent
labeling over V. If the alphabet is {a,b} and the maximum trace length is two,
V={epsilon,a,b,aa,ab,ba,bb}, d=7 and the table covers all 2,187 cases. Results:
754 GLOBAL, 493 SPLIT, 15 TIE and 925 GLOBAL_ONLY. No UNKNOWN remains within
this domain, including the 714 cases still unresolved by current static bounds.

The full compiled-domain event costs are C=405,921 and S=2,215. The largest
per-query gain over Global after lookup work is 302 events in this table:
positives {ab,ba}, negatives {epsilon,a,b,bb}, W_G=387, W_S=78, Q_work=7.
The constant-profile break-even count is 1,352 under the preceding accounting
assumptions. A per-query saving excluding compilation is not a total net saving.

There is no finite maximum-length vocabulary equal to all finite strings over
a nonempty alphabet. The quantifiers are

    for every finite V, there exists a complete table for samples over V;

not "one supplied finite table covers all unbounded inputs." Compiling a new
table after seeing an out-of-domain query is expensive instance-dependent work,
and must not be presented as having a preexisting cheap decision. No
impossibility theorem for a compact general exact predictor follows. Full
unbounded pre-training winner prediction remains a research objective.

## 9. Attacks and reproducible checks

- The structural property concerns distinct trie edges, not positive-record
  occurrences. Shared prefixes and prefix-positive words are tested.
- With {ab,ba}, E=4 but |A|=2: blindly applying the unique-edge formula is
  invalid. The selector checks E=|A| before using it.
- An inert negative need not begin outside the support: early undefined
  transitions can shorten its scan. Such costs receive an interval, not an
  unjustified exact 2Ez formula. For one repeated-free word abc and negative
  cz, the actual cost is 102, whereas the unjustified leading-outside shortcut
  would give 100. Its last test still reads through the outside symbol.
- Informative negatives can reject candidates: Theorem 2 remains a lower
  bound, while no-negative equality is not reused as an exact cost.
- Infeasible AND decompositions, epsilon labels, inactive blocks, duplicate
  projections, changed partitions and true ties are handled separately.
- Domain lookup rejects aaa for the length-two table. Increasing a trace bound
  without recompilation is not allowed. An entry-resource limit prevents the
  compiler from emitting a partially populated table as if it were complete.

Four audits pass: 12,866 general/static cases; 3,119 prior regressions; 738
targeted tree cases; and all 2,187 compiled-domain cases. These are 18,910 case
executions (not necessarily distinct inputs), with 78,927 independent candidate
quotient checks. The targeted tree audit resolves 484 previous UNKNOWN
executions statically; the broad previous suite resolves another nine on its
own tested cases. No universal coverage percentage follows from these biased,
overlapping suites. Audits verify all reported intervals and exact costs,
every declared net guard, independent saturation and independent learner models.
Finite tests supplement the infinite-family proofs and do not certify code
infallibility. Prior assumptions/proofs remain available in the bundled reports.
