# B independent static review: fixed-word certificate

Decision: no substantive correctness blocker found in the reviewed code/proof.
Independent empirical verification and master acceptance remain pending. This
review ran no tests and changed no runtime, structural or audit source. Exact
source snapshots/hashes are in manifest.json; later A revisions are outside scope.

Reviewed fixed_word_solver.py SHA256:
110fa33dd42e43ab57ee4e255e0d19bb82a43495e43f82c21723ebea69d4aa2a

Reviewed PROOFS.md SHA256:
469c5ffd37bee9c3d8e1f1fffcd102aa99e24e2e8c0a509a6885708c80eda86b

The proof became available during review preparation and is included. The initial
live read preceded a minor source revision; conclusions here refer to the saved
12531-byte snapshot, including unique_positive_partition_up_to_swapping_sides,
not the earlier live text. No missing proof or intermediate file is fabricated.

## Model and necessary opposition constraints

The singleton-word factor assumption is explicit in code and P1/P2. With a
positive, a partition fixes both local words as that positive's projections.
Every positive must consequently have equal symbol counts. The code normalizes
samples then checks these counts, including repeated occurrences, before using
opposition. Positive pair variation implies different owners ONLY in this
singleton-factor class; the implementation never applies this opposition rule
to unrestricted regular factors. Comparing each positive to one reference is
equivalent to detecting any variation, and each edge records its differing
positive index in the sorted unique input order.

## Reconstruction, sufficiency and uniqueness

P3 correctly combines equal singleton counts with constant pair projections for
symbols inside each color block. The singleton/pair reconstruction lemma then
fixes the whole projected word; a singleton block follows directly from counts.
Repeated symbols do not break this argument. The code independently verifies all
whole positive projections instead of merely assuming the lemma in its output.

Every class-compatible partition is a proper two-coloring of the opposition
graph. A connected bipartite graph has one coloring up to global complement,
and at least one edge for alphabet size >=2, so both color blocks are nonempty.
The BFS color anchored at the smallest symbol therefore produces the sole
possible unordered fixed-word partition. The implementation does not require
enumeration to certify search_exhausted=true in this specific structural case.

P6's uv/vu construction is valid: each cross-block pair appears as a^r b^s
versus b^s a^r with r,s>=1, while within-block order is unchanged. The resulting
complete bipartite graph is connected even with singleton blocks and arbitrary
repetitions. This proves a sufficient sample-coverage construction, not that
passive sampling supplies those traces and not that connectedness is necessary.

## Negative validation and infeasibility scope

The code checks EVERY negative against BOTH forced local words. A matching
negative rules out the sole positive-compatible structural partition. The result
assumption_violation, exhausted=true, decision_complete=true, uniqueness=unknown
is class-specific and consistent with P4. No infeasible conclusion is exported
for the unrestricted general_regular_product class. Accepted negative conflicts
are retained in the certificate; valid negative witnesses list each possible
unseen side, and their chosen projection actually differs from its singleton
local language. Odd-cycle certificates and count inconsistencies likewise refute
this model class, not the general model.

The odd-cycle helper follows both BFS parent chains to a common ancestor, joins
the tree path with the conflicting same-color edge, and closes the cycle. Since
the endpoints have equal parity, that closed cycle has odd length. The stored
opposition graph allows independent verification of its edges.

## Missing/empty/absent observations and unsupported enumeration

No positive yields insufficient_coverage because the local words are not fixed.
After consistent counts, an absent symbol has no opposition edge: its pair
projection is just the other symbol's constant unary projection. It is isolated,
so the route reports insufficient_coverage rather than inventing its owner.
All-epsilon positives, one unique positive or disconnected evidence receive the
same conservative unresolved status. Such cases can have zero, one or multiple
class-compatible partitions once negatives are considered. The code does not
assert ambiguity or infeasibility from disconnectedness alone.

P7 explicitly gives connectedness-nonnecessity and class-versus-general uniqueness
counterexamples; both are mathematically sound. max_solutions=None is accepted
only for the documented certificate route: disconnected cases remain unresolved,
not falsely reported as a complete enumeration. There is no silent claim that
all fixed-word solutions were listed in those unresolved cases.

Input validation accepts at least two distinct one-character symbols without a
ten-symbol cap, deduplicates/reorders observations and rejects contradictions or
unknown letters. Empty local words are permitted by the model; observed support
is an extra sufficient-coverage condition, not a universal model axiom.

## Deadline and result-state review

Deadline checks occur during validation, counts, projections, pair construction,
BFS and final candidate checks. A partially built graph can be returned on an
incomplete result and must not be used as a completed uniqueness certificate.
construction_complete becomes true only after pair processing; coloring_complete
only after BFS. An expired deadline can prevent invalid-input diagnosis, which
is explicitly documented. Built-in sorting/set/join and serialization are not
hard-preemptible; external process limits remain necessary.

The solution is appended only after all positives and negatives are validated.
If the subsequent deadline check interrupts, the saved solution remains with
status=incomplete, decision_complete=true for existence, search_exhausted=false
and uniqueness=unknown. Without an appended answer, interruption decides neither
existence nor uniqueness. The code does not turn a partial graph or partial
negative scan into a unique/exhausted result.

## Remaining validation boundaries

This is a static implementation/proof review, not a literature novelty review
or an empirical audit. I did not re-open primary references from SOURCES.md.
Independent checker coverage should verify edge-index witnesses, odd cycles,
count certificates, class-conditional uniqueness, accepted-negative conflicts,
absent/empty cases and deadline states against the exact frozen runtime version.
No practical scaling or timing win is inferred from the polynomial certificate
construction or from this review.
