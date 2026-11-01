# C006 implementation protocol v3

This version documents `solver_v4.py`. It preserves the v1/v2 protocol source;
the provider fixes sorted insertion-rescue symbol roles and reports an
interrupted partial enumeration as `incomplete` even after retaining a valid
answer. A normal `max_solutions` stop remains `found` with `complete=false`.
The certificate verifier checks the expected cut count before replaying masks.

## Scope

The public provider accepts a known finite alphabet and exact positive/negative
complete words. It decides existence of an **unordered two-block** compatible
partition, with both blocks nonempty and factors ranging over all regular
languages. It does not infer the hidden number of factors. Input fields `k`,
`q`, and `local_word_cap` are rejected.

For a fixed block B, let P|B be the set of projections of positive examples.
The least factor language needed to accept every positive is P|B. Therefore a
cut is compatible iff each negative has at least one side whose projection is
outside that side's P projection set. This is necessary and sufficient; the
finite witness languages do not constrain a potentially infinite target.

## Algorithm and outputs

1. Validate and normalize the data; a one-symbol alphabet has no nontrivial
   decomposition by convention.
2. Obtain only sound contextual must-links from the frozen C005 v2 helper,
   checked against its recorded SHA256. Each edge is either an adjacent-swap
   witness or an insertion-rescue witness. The result embeds all edges and
   their source words. The verifier replays every edge.
3. Contract must-link components. A connected graph is a sufficient
   non-decomposability certificate. Otherwise enumerate all canonical
   nonempty cuts of components (component zero stays on side zero).
4. Directly check every candidate. A feasible cut returns exact positive
   projections and one rejecting side per negative. A failed cut stores a
   negative whose projections collide with an explicit positive on **both**
   sides. If every cut fails, the certificate contains every cut mask exactly
   once plus those collisions. `verify_certificate` checks graph evidence,
   component reconstruction, exact cut coverage, and both collisions.

`solve(data, deadline=None, max_solutions=1)` uses an absolute
`time.perf_counter()` deadline. `max_solutions=None` enumerates every
compatible bipartition. A returned first solution establishes existence, not
uniqueness. Any truncated/interrupted enumeration has `complete=false`; a
negative conclusion is emitted only with a replayed complete obstruction.
`verify_solution` independently rechecks partition coverage, positive
projection sets, and rejection of every negative.

Statuses: `found` (at least one witness; `complete` separately states whether
enumeration ended), `not_decomposable` (complete obstruction), `incomplete`,
`invalid_input`, or `runtime_error`. With no positives, every bipartition is
compatible: empty local languages accept no negative projections. The
provider consequently returns the canonical first cut in decision mode, or
all cuts in all-solutions mode. One-symbol alphabets return structural
`not_decomposable`, not invalid input.

## Proof obligations / limits

Adjacent-swap: if the swapped symbols were assigned to different blocks,
each projection of the negative equals the projection of the positive; hence
the negative would be accepted. Insertion-rescue: deleting `a` from the
negative yields one positive and inserting `b` next to that same `a` yields
another. If a and b were separated, the negative's a-side projection equals
the rescued positive's projection, while its b-side projection equals the
base positive's projection. Thus each edge is a necessary same-block relation.

For each fixed cut, positive projections are forced in any consistent local
factors. If a negative collides with a positive on each block, every possible
factor language containing those positives also contains both negative
projections, so the product accepts the negative. Complete coverage of all
canonical cuts proves no nontrivial compatible partition exists. A timeout or
incomplete cut set proves nothing about non-decomposability.

The algorithm is exact but can take exponential time in the number of
contracted components and its complete obstruction can be exponential in
size. Must-links can miss useful structure; a disconnected graph is never a
decomposability claim. The API only addresses existence/compatibility of a
two-block cut. Coarsening closure can connect this result to unknown-k
existence only after the separate theory proof is accepted; no hidden-k
recovery claim is made here.

## Frozen runtime dependency

`results/2026-10-31/partition_coverage_v5/general/known_k_qexact_v2.py`
SHA256 `9f08dd645e7fcccbe8ea8022c758b7cf3277a5f01b6533fb9c1ad0cf08b6c84d`.
Only `_components` is invoked. It is immutable and uses Python standard
library only. No local word cap or known k is passed.


