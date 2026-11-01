# C006-T003 static peer review: stable solver_v3

Scope: stable READINESS_V3, solver_v3 and its frozen C005 graph helper. Exact
bytes/hashes are in MANIFEST.json and snapshots/. No experiment, module import,
runtime edit, benchmark or Git action in this review. Independent gates remain
required. Initial READINESS_V2 advertised a different source; PEER_REVIEW_WAIT_001
records why this review waited for V3 rather than accepting changing bytes.

## Conclusion

No blocking mathematical defect found in old-rule quotienting, contextual
orientation repair or complete collision-cover logic. Unknown-k existence is
correctly reduced to bipartitions under theory T1-T4; no finite q cap is used.
The following API/schema/reporting findings should be handled explicitly in the
independent gate/integration. They are static deductions, not observed test runs.

### F1: verify_solution silently normalizes duplicate block members

solver_v3:246 maps each block list to set before comparing partition coverage.
It never rejects len(block)!=len(set(block)). Repeating a symbol in a block of
an otherwise valid returned solution leaves every later expected language and
witness unchanged, so the duplicate-bearing representation is accepted. The
solver itself emits sorted sets without duplicates; this is a verifier schema
gap, not an invalid language model produced by solve. If canonical partition
records require exact one-occurrence ownership, the verifier must reject such
records, not silently interpret them as sets. Also a nested list/object member
can raise TypeError in map(set, blocks), instead of returning valid=false.
The gate should check malformed JSON-compatible block records explicitly.

### F2: all/uniqueness refer to bipartitions, not all unknown-k partitions

max_solutions=None enumerates every canonical component BIPARTITION. It does
not compute kmax or the maximal-refinement frontier. The result's explicit
uniqueness_scope says two-block partitions, correctly. README's unqualified
"all compatible partitions" wording should be read/qualified accordingly.
Do not compare its output list directly to an all-k oracle without filtering
k=2; compare existence using T3 and all-k counts/frontiers separately if supplied.
Even uniquely identified nontrivial architecture does not eliminate the trivial
k=1 explanation or identify the declared hidden k without a convention.

### F3: interruption/partial status requires reading complete as well

After one solution is saved, a later deadline/KeyboardInterrupt leaves exhausted
false, but line 378 returns status=found rather than incomplete. This is sound
as an existence answer and keeps uniqueness unknown (or ambiguous for >=2), but
it does not mean an all/second-answer request completed. Consumers must inspect
complete/enumeration_complete and number of solutions. The status formula does
not distinguish deliberate answer-limit stopping from a later interruption.

Validation and some certificate replay/finalization are outside caught deadline
loops. For example KeyboardInterrupt in _validate or connected certificate replay
can propagate. Large cover replay has no cooperative deadline parameter. The
external supervisor remains necessary; provider deadline is not a strict hard
wall guarantee. The one-symbol alphabet branch can decide structurally before a
deadline check. These do not invalidate its proof of no nontrivial split.

## Checked proof obligations

1. The frozen helper's _components uses only swap/rescue contexts; its known-k
   validation/q-exact routines are not called. Hashes filter swap/deletion
   candidates and exact string checks guard every inferred edge. No probabilistic
   hash collision can itself create a must-link. Both rules are necessary for
   every k. Enhanced A/B are intentionally NOT active in this version.
2. _replay_must_link_edge requires distinct alphabet symbols, actual labels,
   exact adjacency swap or exact deletion-to-base plus adjacent insertion. In the
   rescue branch it derives the deleted role from the indicated negative offset
   and the inserted role as the other endpoint. Sorted symbol order no longer
   fixes semantic roles. Repeated occurrences are allowed but the claimed offset
   must match. This repairs the recorded orientation failure.
3. _union_components reconstructs components over EVERY alphabet symbol, so
   omission of unused symbols cannot shorten the cover. Claimed components must
   equal that result. A connected graph is accepted only with its correct
   obstruction kind and independently replayed edge witnesses.
4. _canonical_masks fixes atom zero in the left side: masks (tail<<1)|1 with
   tail from zero through 2^(r-1)-2. These are exactly all nonempty two-side
   unordered assignments, excluding the all-left mask. Solver and verifier use
   the same orientation. For r=1 graph soundness is the certificate; an empty
   bare cover is not accepted as an obstruction for a disconnected graph.
5. Every cover record must have a distinct integer (not bool) mask, and the mask
   set must equal all expected canonical masks. Each collision must name a real
   negative and two real positives with the appropriate side projections equal.
   Thus no compatible quotient split survives; sound graph contraction rules out
   every split discarded by the quotient. T3 lifts this to all nontrivial k.
6. Positive languages and every negative rejection in solution verification are
   recomputed directly, without calling solve or the parent feasibility routine.
   This is replay code sharing validation/project helpers, NOT the independent
   audit oracle. Strong independent all-k checking is still needed.
7. Search appends only fully validated solution records. Early found implies
   existence, not uniqueness; exhaustion plus zero answers is required for the
   collision-cover obstruction. The solver self-replays that certificate before
   reporting not_decomposable. Two answers establish ambiguity; one with actual
   exhaustion establishes uniqueness in the stated bipartition scope.
8. For no negatives every tested partition passes, and no old graph edge can
   be inferred. With no positives, all negative local projections are unseen,
   so every bipartition passes. k1 is never counted as a candidate split and
   not_decomposable must retain its NONTRIVIAL convention in the root UI.

Both full enumeration and explicit obstruction size can be exponential. Verifier
expected-mask materialization is exponential too; no claim of short universal
non-decomposability certificates or polynomial decision follows. Preservation
of V1/V2 failures and V3 fixes is reported by implementation READINESS; those
captured smokes were not rerun by this static reviewer.
