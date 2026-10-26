# C003-S001: recovery from positive opposition in the fixed-word class

Scope: known finite alphabet A, |A|>=2, two nonempty disjoint blocks B0,B1.
The local languages are exactly {u0},{u1}, with ui in Bi*. Empty local words are
allowed; support coverage is an additional sufficient hypothesis, not a model
axiom. Positives are complete traces, not prefixes. Labels are exact and finite.
Repeated occurrences of a symbol are permitted. Partitions are unordered.

## P1. A fixed-word product is a shuffle with disjoint support

For disjoint blocks covering A, w belongs to the product iff pi_B0(w)=u0 and
pi_B1(w)=u1. This is precisely an order-preserving shuffle of u0,u1: each event
has a unique block owner. If at least one positive p exists, the local words for
a proposed partition are forced to pi_B0(p),pi_B1(p). No freedom to enlarge these
languages remains, unlike C002's general regular factors.

Every positive therefore has the same occurrence count for every symbol. A
count inconsistency is a complete proof that this class cannot fit the positives.
It says nothing about feasibility with unrestricted regular local languages.

## P2. Pair-variation forces opposite ownership

Define the opposition graph G on ALL declared symbols, including absent ones.
There is an edge {a,b}, a!=b, iff two positive words have different projections
onto {a,b}. If a,b belonged to one block in a fixed-word explanation, both pair
projections would be pi_{a,b}(ui), which is identical on every positive. Hence
every edge forces different block owners. This direction depends on singleton
local languages: different local executions of a general regular factor may
produce different pair projections without implying different owners.

Comparing every positive to one reference is sufficient: variation somewhere
exists iff at least one differs from that reference. Each stored edge records
the index of such a differing positive in the sorted unique positive list.

## P3. Sufficiency of equal counts and a proper coloring for positives

Suppose the positive counts agree and a proper two-coloring of G determines two
nonempty blocks. For symbols a,b in the same block, no edge exists, so their
pair projections are identical across positives. On a block of size at least two,
binary-projection reconstruction implies that the WHOLE block projection is
identical across positives. On a singleton block, equal counts give the same
unary word. Thus the projected positive languages are singletons. This uses the
known reconstruction lemma, not an original combinatorial result [S1].

Repeated symbols do not change the argument: projections retain all occurrences
and their order, not merely the first occurrence or symbol presence. The code
also checks the whole projected words directly instead of trusting the lemma
as a substitute for runtime validation.

## P4. Connected bipartite opposition certifies a unique partition

Every class-compatible partition is a proper two-coloring by P2. A connected
graph has at most two proper two-colorings: once the first vertex's color is
fixed, a path forces the color of every other vertex. The two colorings are global
complements and represent the same unordered partition. A connected graph on at
least two vertices has an edge, so both sides are nonempty. A BFS constructs the
canonical coloring with the smallest symbol on side zero. If G is bipartite and
positive counts agree, P3 proves positive compatibility of that sole partition.

Check EVERY positive projection and EVERY negative against the two fixed words.
If each negative differs on at least one block, the output is a valid explanation
and the unique unordered partition WITHIN THE FIXED-WORD PRODUCT CLASS. If some
negative matches both words, the only possible positive partition rejects none
of that negative's local components. Hence no fixed-word explanation fits all
labels. The API labels this assumption_violation with the exact conflicting
negative, never general-regular infeasibility. No second candidate is needed to
set search_exhausted=true: P2 and connectedness prove exhaustion structurally.

## P5. Odd cycles and count contradictions

An odd cycle cannot be properly two-colored; P2 rules out every fixed-word
explanation. The BFS returns a closed odd cycle made of a conflicting edge plus
the parent-tree path between its endpoints. The result is assumption_violation,
search_exhausted=true, decision_complete=true, uniqueness=unknown (there is no
compatible partition whose uniqueness could be asserted). Count inconsistency
has the same class-conditional decision semantics via P1.

Example: A={a,b,c}, positives abc,bca,cab have equal counts but all three pair
edges, an odd cycle. General regular factors can nevertheless fit these positives
with no negatives, e.g. projected finite positive languages on {a}|{b,c}.
Likewise positives a,aa violate the fixed-word counts but are general-feasible.

## P6. Constructive two-positive recovery with repeated symbols

Let u in B0*, v in B1*, alph(u)=B0, alph(v)=B1, where both blocks are nonempty.
Include the two COMPLETE positives uv and vu. For a in B0, b in B1, set
r=|u|_a>=1, s=|v|_b>=1. Their pair projections are a^r b^s and b^s a^r,
respectively, and differ. Within one block, both positives project to the same
local word, so within-block pairs never vary. Thus G is exactly K_{|B0|,|B1|},
connected and bipartite, including when either block is a singleton. Arbitrary
repetitions and arbitrary order WITHIN u and v are allowed. Extra positives that
are genuine shuffles preserve all within-block invariance; the complete cross
edges already exist. Negatives must be genuine rejections for successful recovery.

This is an existence/coverage construction, not an active-query algorithm or
a claim that arbitrary passive sampling will deliver uv and vu. The solver is
given only its labeled sample; it never receives the hidden words or partition.
The planned independent auditor, not this proof, establishes empirical scaling.

## P7. Coverage failures and boundaries of identification

If some declared symbol is absent from all positives, its pair projections are
just unary projections of the other symbol. Once P1 counts agree, these do not
vary, so that vertex is isolated. Connectedness cannot hold. Its owner might be
constrained by negatives, but this structural algorithm does not search those
possibilities and returns insufficient_coverage, decision_complete=false,
search_exhausted=false, uniqueness=unknown. It does NOT assert multiple solutions.
The same conservative status applies with no positives or only one unique
positive. Duplicated positives do not add coverage.

Connectedness is sufficient, NOT necessary. A={a,b}, positives={ab}, no negatives:
there is only one nonempty unordered two-block alphabet partition, but G has no
edges. Our conservative coverage route still returns insufficient_coverage.
Disconnected graphs can also have their orientations restricted by negatives;
that stronger algorithm is not implemented or claimed here.

Class-conditional uniqueness is NOT general uniqueness: A={a,b,c}, positives
abc,cab, no negatives produces connected G with edges ac,bc and unique fixed-word
partition {a,b}|{c}. All three unordered nonempty partitions fit these positives
with unrestricted regular local factors (choose finite projection languages).
Thus this very small witness refutes promoting this certificate to the general
regular-product model. More globally, finite samples alone do not identify an
unrestricted true factorization merely because we constructed one explanation.

Count-only reasoning is also inadequate: abc and cba have equal symbol counts,
yet all pair edges form an odd cycle, precluding a two-fixed-word explanation.
And two positives without support coverage need not suffice: for declared
{a,b,c}, ab and ba leave c isolated. Neither graph connectedness nor sample
coverage may be replaced by an unproved heuristic.

## API, interruptions and resource bounds

solve(data, *, deadline=None, max_solutions=1) validates and normalizes observations
independently; malformed input raises ValueError. All positive int limits and
None are accepted because the route emits at most one STRUCTURALLY UNIQUE answer.
It does not enumerate disconnected cases for max_solutions=None: the explicit
insufficient_coverage result is an unresolved decision, not a silently truncated
enumeration. A connected certified answer has decision_complete=true,
search_exhausted=true, uniqueness=unique with an explicit class scope.

Deadline is an absolute perf_counter value. Periodic checks occur in validation,
counting, pair projections, BFS and full label checking. Deadline/KeyboardInterrupt
returns incomplete and preserves any already fully validated solution, with
search_exhausted=false and uniqueness=unknown. If such a solution exists,
decision_complete=true only certifies existence, not uniqueness. There is no
claim of strict preemption inside Python's built-in sort/set/join or final JSON
serialization; the external capture runner supplies its wait cap. Invalid input
may remain undecided if an already-expired deadline prevents validation.

Let m=|A|, q=#distinct positives, P total positive length, N total negative length.
Naive per-pair filtering costs O(m^2 P) character inspections in the worst case,
plus O(P+N+m^2) for graph and full candidate validation (and normalization costs).
The graph and edge witnesses occupy O(m^2) memory; working projected strings
take at most the maximum input-word length. The API includes normalized solution
words/witnesses and graph evidence, whose output cost must also be paid.
There is no exponential partition search in this certificate route. This bound
is not a claim of practical performance or superiority over the general method.

References: [S1] and related shuffle-decomposition distinctions are in SOURCES.md.
