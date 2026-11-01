# C006-T001: unknown number of unrestricted regular factors

Scope: finite known alphabet A, |A|=m>=2; disjoint nonempty blocks; complete
words with exact finite positive P and negative N, P intersect N empty. Arbitrary
regular factors, including empty and infinite languages, are allowed. No finite
word-cardinality q bound and no known k. A partition is unordered. "Nontrivial"
means at least two alphabet blocks, not two nonempty accepted languages.

## T1. Exact finite-sample criterion for every partition

For partition pi, define P_B={projection_B(p):p in P}. Then pi is feasible iff

    for every n in N, some B in pi satisfies projection_B(n) not in P_B.

Necessity: every positive forces its local projection to be accepted on EVERY
block. A negative cannot have all projections positively forced. Sufficiency:
choose each local language equal to finite P_B, a regular language. This is an
existential witness, not an assumption that true factors are finite. With P empty,
all local languages can be empty, so every partition is feasible. With N empty
the condition is vacuous. Epsilon is a word like any other. Contradictory labels
and outside-alphabet symbols are invalid input, not non-decomposability evidence.

## T2. Coarsening closure, both semantic and sample-level

If pi is feasible and rho coarsens pi, choose n and its rejecting fine block B.
Let C in rho contain B. If projection_C(n)=projection_C(p) for some positive p,
projecting further onto B contradicts the rejecting witness. Thus C rejects n
under T1 and rho is feasible. The witness can be transported to its containing
coarse block. No auxiliary queries, hidden target or state bound is needed.

For a globally decomposed language, merging blocks also preserves the exact
global language: on C take the intersection of inverse projections of its
original local languages. Inverse images/intersections preserve regularity.
This grouped factor may be infinite. Its acceptance is exactly conjunction of
the grouped factors, so merging changes architecture, not the global language.

## T3. Existence reduces EXACTLY to bipartitions

Every feasible partition with k>=2 can have its blocks grouped into two nonempty
unions. T2 gives a feasible bipartition. Conversely a feasible bipartition IS a
nontrivial partition. Therefore no bipartition iff no nontrivial partition.
This is a decision reduction, not a claim that bipartitions identify hidden k.
There are 2^(m-1)-1 canonical bipartitions (fix the smallest letter on side zero,
exclude empty side one). Exact exhaustion of these suffices for an impossibility
certificate; there is no need to enumerate Bell(m) partitions to decide existence.

## T4. Feasible cardinalities form an initial interval

The one-block partition is ALWAYS feasible: projection_A is identity and P,N
are disjoint. Let kmax be the maximum feasible block count (finite, <=m).
Repeated merging gives feasible counts exactly {1,...,kmax}. Nontrivial feasible
counts are {2,...,kmax}, empty when kmax=1. Do not report "no model" when this
set is empty: the trivial model still exists. Individual partitions at a given
count are NOT all necessarily feasible. Computing kmax/frontiers remains a
separate search task; the bipartition existence reduction does not compute it.

Every sound must-link component is indivisible, so component count r bounds
kmax<=r. Connected sound graph (r=1) proves kmax=1. r>1 is not evidence that
kmax>=2, nor that kmax=r. Edge absence does not assert independence.

## T5. Hidden k is not identifiable without a convention

For each feasible partition T1 supplies a regular-factor generator consistent
with all observed labels. Different feasible counts therefore give different
possible hidden architectures with the identical input. In particular k=1 is
always possible. Even complete knowledge of a decomposable global language does
not separate an architecture from its coarsenings: T2 preserves the language.
Choosing max k, irreducible factors or an external architecture is an ADDITIONAL
target convention, not an inference of the originally declared hidden k.

The hypotheses do not even identify whether factors are finite: set
L=max{|w|:w in P union N}, taking L=0 for no words. On each nonempty B choose
a letter b in B and let K_B=P_B union b^(L+1)b*. This language is regular and
infinite, and its added words are longer than ANY observed local projection.
It preserves every local seen/unseen test, so every feasible partition also has
an explanation with ALL factors infinite. This covers empty P as well. There
is no finite q restriction hidden in the proof or algorithm.

## T6. Maximal refinement need not be unique

A={a,b,c}, P={epsilon,abc}, N={a}. Exactly two bipartitions are feasible:
{a,b}|{c}, and {a,c}|{b}. In either, projection of negative a on the two-letter
block is unseen. The third {a}|{b,c} fails: a and epsilon are both seen.
The three-singleton partition fails for the same reason. Thus kmax=2 and the
two feasible bipartitions are incomparable maximal refinements. There is no
unique finest compatible partition. Both can have infinite local factors by T5.
Maximal under refinement also differs from maximum cardinality in general;
do not conflate either convention with true-k recovery. No unique-frontier
theorem is asserted here.

## T7. Sound contextual must-links and sufficient obstruction

A positive w and a negative obtained by swapping adjacent distinct a,b force
a,b to have the same owner: different owners would leave every local projection
unchanged. More generally, ANY proposed must-link rule needs its own soundness
proof for all regular factors; a graph must not contain heuristic equalities.

For insertion rescue, positives xy and xaby (or xbay), negative xay, distinct
a,b imply same owner: if separated, a's owner sees its negative projection in
the rescued positive, every other block sees it in xy. This works for arbitrary
k, arbitrary contexts x,y and repeated symbols, not just two factors. Transitive
closure therefore lies inside every feasible block. A connected such graph
forces all symbols together and proves no nontrivial decomposition. Replay a
spanning tree's labeled contexts and verify every edge; unexplained edges are
not an obstruction certificate.

## T8. This graph obstruction is INCOMPLETE

Original example: A={a,b,c}, P={ab,ac,bc}, N={abc}. For any bipartition, its
two-letter block projection of abc is a listed positive word's projection;
its singleton projection is also seen in positives. All three splits fail.
No adjacent-swap graph edge exists because positive/negative lengths differ.
No rescue edge exists because it requires a positive longer than this negative.
The graph is empty, although nontrivial decomposition is impossible.

Reduced example: A={a,b}, P={a,b}, N={epsilon}. There is only one bipartition;
on {a}, epsilon is seen via positive b; on {b}, it is seen via positive a.
Again no split is feasible, and there are no swap/rescue edges. This is minimal
in alphabet size and, for that alphabet and one epsilon negative, positive
cardinality: deleting either positive makes the split feasible. Alphabet size
cannot go below two in the declared task. We claim this specific minimality,
not minimality among all imaginable contextual proof systems. A stronger rule
may infer a must-link from this collision itself; the counterexample refutes
completeness of the stated swap/rescue graph, NOT completeness of all sound
contextual rules. Both original and reduced cases are retained in examples_v1.

## T9. Complete collision-cover obstruction certificate

For EACH canonical bipartition B|C, give a negative n and positive witnesses
p_B,p_C such that projection_B(n)=projection_B(p_B) and likewise for C. The
two positive witnesses may differ; n may differ between bipartitions. T1 proves
that split infeasible. A verifier checks exact coverage of all 2^(m-1)-1 splits,
no missing/duplicate disguised assignments, the two nonempty blocks, and every
word's label/membership and projection equality. T3 then proves nontrivial
impossibility. A collection with one split omitted, or one offending negative
without BOTH matching witnesses, is not a complete certificate. Interrupted
enumeration never certifies impossibility.

The certificate may be exponential. Graph-component quotienting can reduce it
provided a separate independently replayed sound must-link certificate proves
that all splits which split a component are impossible. Verify BOTH parts:
the graph rules and collision cover over all surviving component splits. If r=1,
the latter cover is empty but the graph itself supplies the proof. Do not accept
an empty cover alone for m>=2. Compressed SAT/proof formats need their own
sound verifier and are not implicitly provided by this conceptual proof.

## T10. Genuine language irreducibility versus observation ambiguity

Relative to A and the disjoint-product operation, a regular language is genuinely
irreducible if no nontrivial exact decomposition exists. A finite-sample
obstruction proves EVERY label-consistent global language has no decomposition
in the declared model: otherwise its partition would pass T1. The converse is
false: L=(ab)* on {a,b} is irreducible, since its projections are a*,b* whose
product contains a, but L does not. Sample P={ab}, N empty still permits a
bipartition. Add negative ba: the swap must-link proves non-decomposability.
This gives an infinite regular irreducible target and a finite obstruction.

"No unique finest sample refinement" concerns competing explanations of finite
data, not necessarily multiple exact irreducible factorizations of ONE completely
known language. Literature uniqueness theorems for normalized word shuffle sets
must not be transferred to this setting. For true unknown regular targets with
insufficient observations, output ambiguity/compatible construction, not a
declaration of genuine irreducibility. Literature scope is in SOURCES_v1.md.
