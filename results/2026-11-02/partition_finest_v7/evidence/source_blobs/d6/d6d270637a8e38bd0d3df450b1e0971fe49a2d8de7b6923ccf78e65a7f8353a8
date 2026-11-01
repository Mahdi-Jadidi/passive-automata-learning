# C007-T001: finest compatible partitions and certified adaptive separation

Scope: finite known nonempty alphabet A, exact consistent finite whole-word P,N,
disjoint nonempty blocks and arbitrary regular local languages. No known k,q or
state bound. One-block models are permitted. Empty alphabet/contradictory labels
are invalid. Write pi<=rho iff pi REFINES rho, equivalently E_pi subset E_rho.
All claims concern sample compatibility, not hidden architecture recovery.

## T1. Feasibility, coarsening and infinite witnesses

For any partition pi set P_B={projection_B(p):p in P}. Feasibility is equivalent
to every negative n having at least one B with projection_B(n) outside P_B.
Necessity follows from positively forced local acceptance; sufficiency uses
regular finite factors P_B. The single-block partition always satisfies this
criterion for consistent labels. No positives or no negatives makes EVERY
partition feasible. Epsilon and unused alphabet symbols are retained.

If feasible pi refines rho, a negative's unseen fine projection remains unseen
on its containing coarse block: equality with a coarse positive would project
to the forbidden fine equality. Thus feasibility is coarsening-closed. For
whole-language exact products, merging factors uses the intersection of inverse
projections on the merged alphabet; this preserves regularity and the exact
global language. This is a different argument from finite-sample closure.

Finite witnesses impose no finite-language target assumption. Let L be maximum
observed word length (zero if none). For each B choose b in B and extend P_B by
b^(L+1)b*. Added words are longer than every observed projection. All seen/unseen
tests remain identical, while every factor is regular and infinite. Thus every
feasible partition has an all-infinite-factor explanation too.

## T2. The binary meet equals the all-partition meet

Let F be all feasible partitions and B its bipartitions. F is nonempty. Define
M by E_M=intersection_{beta in B} E_beta; an EMPTY intersection means A x A,
so M is ONE BLOCK, not singletons. Intersections of equivalences are equivalences.

Since B subset F, the all-F intersection is contained in E_M. Conversely, if
a feasible pi separates letters a,b, group its a-block against all other blocks.
This is a feasible bipartition by T1 separating a,b. Hence any separation in F
already occurs in B. Both intersections coincide. In particular M refines every
feasible partition, but M itself need not be feasible. No binary answers means
no nontrivial feasible partition, by grouping any >=2-block model into two sides.

## T3. Finest-existence test and nonunique maximal refinements

M feasible iff a unique finest feasible partition exists; then it is M and F
consists exactly of its coarsenings. Forward: M refines every F member; reverse:
a finest member belongs to F and its equivalence is exactly the intersection.
Coarsening closure proves the characterization of F in the feasible case.

If M fails T1, the finite nonempty poset F has >=2 incomparable members with no
strictly finer feasible refinement. Otherwise its sole such member f is reachable
by refinement from every pi (finite ascent in refinement), hence is finest,
contradicting infeasibility of M. These are maximal REFINEMENTS, not a promised
enumeration of frontier elements or maximizers of block count. The implication
does not by itself compute kmax.

## T4. Cheap must-link certificate WITHOUT known k

Suppose every edge of graph G is independently validated to force common
ownership in EVERY feasible partition, for arbitrary k. Then its component
partition C refines every member of F: a connected component cannot split.
If C itself passes T1, C belongs to F and is its unique finest member. No binary
enumeration, no r=k assumption, and no known k are needed. A spanning forest of
replayable sound edges is enough to certify the components; omitted inferred
edges do not matter if those supplied prove the stated components.

If C is infeasible, this shortcut merely fails; there may still be a unique
finest feasible COARSENING or multiple maximal refinements. Do not conclude
nonexistence, ambiguity, irreducibility or decomposability from C failure alone.
Connected C is one-block and therefore feasible, proving unique finest one-block
and no nontrivial model. C singleton with T1 passing certifies singleton finest.

Sound examples: adjacent positive/negative swaps and insertion-rescue contexts
proved in C006, replaying exact labels/positions. Any enhanced edge rule needs
its own universal-k proof AND implementation/verifier support. No heuristic
"same label means independent" step is justified. C006's enhanced A/B were
dormant there; availability in C007 must be explicitly versioned, not assumed.

## T5. Adaptive separation invariant and termination

Start M0=one-block, and maintain Mt as the meet of compatible bipartitions
actually returned so far. Maintain/prove each returned partition is feasible.
Then E_M subset E_Mt always. Ask the oracle for ANY feasible bipartition beta
splitting a current Mt block (some co-owned a,b have different beta sides).
Replace Mt by Mt meet beta, deleting empty intersections and canonicalizing.
This is a strict refinement: the split block contributes at least two blocks,
and no previous blocks merge. Thus at most |A|-1 successful refinements occur.

Stopping with a COMPLETE proof of NO feasible separator implies Mt=M: every
feasible bipartition keeps every Mt pair together, so E_Mt subset E_M; combine
with the invariant. Now apply T3. Singleton Mt has no splittable pair, so its
no-separator claim is tautological (provided its recorded meet history is valid).
The number of successful calls bounds neither candidate enumeration nor oracle
time: finding a separator, or proving the final no-separator answer, can be
exponential. There may be |A| oracle calls including the final failed search.

Crucially, Mt passing T1 before certified termination does NOT certify finest:
for N empty many partial meets are feasible but more refinement remains possible.
Do not accept an oracle's "none" after timeout as exhaustion. Partial found
separators certify existence and separation only; absent proof of completeness
they do not generally certify forced coownership or finest uniqueness.

## T6. Replayable constrained-search/forced-coownership certificates

Canonical binary masks fix the least letter on side zero and exclude all-zero
second side. For a claimed final Mt, define Q(Mt) as ALL such masks that split
at least one Mt block. A no-separator certificate must independently account
for EVERY mask in Q, not just arbitrary searched prefixes or a chosen pair.
For each mask supply negative n and positives p0,p1 matching n on respective
sides. T1 refutes that mask. Masks outside Q may be omitted because they cannot
refine Mt. Replay computes Q's condition from the supplied valid partition,
checks exact coverage/no disguised omissions, and checks all labels/projections.

If search uses must-link atoms, separately replay those sound edge proofs;
they justify omission of every mask splitting an atom. Then cover all remaining
atom masks in Q. A compatible binary answer cannot split validated atoms. If
Q has no surviving masks, the graph/constraint checks, not an unexplained empty
list, are the proof. Exhausted prefixes may compress the cover only with proved
branch coverage and sound pruning witnesses; a node counter is not a proof.

For a forced pair a,b one can instead certify infeasibility of ALL canonical
bipartitions separating a,b; T2 then proves they co-own in every pi in F. To
certify an entire final Mt by pair queries, cover at least a spanning tree of
pairs inside EVERY Mt block; choosing just one pair per block is insufficient
for blocks of size >2. Each pair query must exhaust its own separating domain.
Do not constrain the oracle by a provisional Mt as if Mt were forced: it is an
UPPER bound on the true meet equivalence, not a validated must-link relation.

These explicit covers can be exponential; a certificate verifier must not hide
that cost. A valid unique-finest certificate combines (1) graph proofs or a
sequence of feasible binary separators with exact meet replay, (2) a valid
no-separator/forced-pair proof as needed, and (3) direct T1 acceptance of the
claimed finest partition and its local projection/negative witnesses.

## T7. A useful early ambiguity certificate (not a production requirement)

If the meet of ANY recorded feasible partitions is already infeasible, no
finest feasible f exists: f would refine every recorded member, thus their
meet, and coarsening closure would make that meet feasible. Contradiction.
Thus feasible separator witnesses plus an infeasible intermediate meet prove
multiple maximal refinements exist via finiteness, WITHOUT claiming this is
the exact final meet or enumerating the frontier. This is a sound early stop.
Its infeasibility witness is a negative whose projection is positively witnessed
on EVERY current meet block; one rejecting or matching side alone is insufficient.

## T8. Examples and target convention

* Unique finest with THREE blocks: A=abcdef, P={epsilon,ab,cd,ef},
  N={a,b,c,d,e,f}. Rescue from epsilon/a/ab and analogous words forces ab,cd,ef.
  C={ab}|{cd}|{ef} passes T1 (unary negatives unseen on their pair block), so T4
  certifies unique finest. Infinite true factors (ab|ba)*, (cd|dc)*, (ef|fe)*
  fit all labels. The input contains no k, q or hidden partition. Merging these
  three true factors into two or one preserves their WHOLE language. Thus even
  this successful finest recovery does not identify declared hidden architecture.
* Multiple maximal refinements: A=abc, P={epsilon,abc}, N={a}. Feasible binaries
  ab|c and ac|b have singleton meet, which fails T1 for a. The third binary and
  singleton partition fail; these two are incomparable maximal refinements.
* Unique finest one-block/irreducibility: A=ab, P={ab}, N={ba}. Swap forces ab
  and the one-block partition passes. Infinite true target (ab)* fits and is
  irreducible over this declared alphabet. Positive-only sample {ab} does not
  certify irreducibility: all partitions then pass T1.
* Empty binary family without connected old graph: A=ab, P={a,b}, N={epsilon}.
  Only one-block is feasible, so the empty binary meet MUST be one-block. Its
  old swap/rescue graph is empty; binary collision cover supplies the proof.

Unique finest is an explicit SAMPLE convention. Its block count need not equal
the hidden count, and finite positive-projection witness languages need not
equal true languages. No RPNI, arbitrary true factor recovery, polynomial oracle
bound, general speed improvement or novelty claim follows.
