# Independent proof audit — C006 T001/T002

Audit date: 2026-11-01. Read-only review of `theory/PROOFS_v1.md` and
`theory/ENHANCED_RULES_PROOFS_v1.md`, plus an independently implemented
all-k direct projection oracle. No candidate source was used by the oracle.

## Decisions

- **T1 direct finite-sample criterion: accepted.** Every observed positive
  forces its projection into each local factor. If all projections of one
  negative occur among those forced positive projections, every candidate
  factor accepts it. Otherwise choosing exactly each finite positive
  projection set gives regular factors that accept all positives and reject
  every negative on a witnessed block. This is an existence argument and does
  not bound or identify true languages.
- **T2 coarsening closure: accepted.** If a fine block rejects a negative,
  equality of the merged negative projection to any merged positive projection
  would imply equality after projecting to the rejecting fine block. Thus the
  coarsened block still rejects. Grouped factors preserve regularity and their
  product language. k=1 is always feasible for consistent exact labels;
  nontrivial feasible k are an initial interval from 2 through kmax.
- **T3 bipartition reduction/T4 cardinality interval: accepted.** Grouping any
  feasible k>=2 partition into two nonempty unions preserves feasibility.
  Therefore nontrivial existence is equivalent to one compatible bipartition,
  while feasible k values do not identify the hidden k.
- **T5 true-k/nonfinite identifiability limit: accepted.** Finite labels support
  multiple regular explanations. Extending each finite projection set by a
  unary tail longer than all observations preserves the observations and makes
  each local explanation infinite. This does not mean the true factors were
  inferred.
- **T7 connected graph obstruction: accepted as sufficient only.** Each
  adjacent-swap and insertion-rescue edge is a same-owner constraint for every
  compatible partition. A connected graph proves no nontrivial split; a
  disconnected graph says nothing by itself.
- **T8 incomplete old graph: accepted and independently checked.** The original
  and reduced examples have no old swap/rescue edges and no compatible
  bipartition. The exact all-k oracle confirms they are non-decomposable.
- **T9 collision-cover certificate: accepted.** For every canonical
  bipartition, a negative whose two projections are each matched by positive
  projections proves that split impossible. Complete cover of all canonical
  splits, plus independently validated must-link edges when contracted,
  certifies non-decomposability. Missing/duplicate splits or one-sided
  collisions are insufficient.
- **T002 alternative insertion/deletion rules A/B: accepted.** For A, with
  positives `xay`, `xby` and negative `xy`, if `a,b` were in different blocks,
  each owner block would match the negative projection against the positive
  with the other inserted symbol; every other block ignores both. For B, if
  `p_a` and `p_b` are the exact words obtained by deleting the stated distinct
  occurrences from one negative, each of the two owner blocks matches the
  negative against the positive deleting the symbol owned by the other block.
  Exact occurrence offsets and word relations are required. The proof survives
  repeated symbols, arbitrary contexts, any k, and unrestricted regular
  factors.
- **T10 genuine exact-language irreducibility vs sample ambiguity: accepted.**
  The exact language `(ab)*` is irreducible over `{a,b}`, but the positive-only
  sample `{ab}` permits a compatible bipartition. Adding negative `ba` gives a
  finite obstruction for that target. These are different claims and must not
  be conflated.

## Independent finite checks

The primary RGS oracle enumerated all set partitions for 135 consistent cases,
including the manager's four-symbol candidate and theory lead's examples. A
second implementation enumerated partitions by recursive block insertion and
recomputed every compatibility set and bipartition collision independently.
It matched all 135 full all-k partition sets, checked the exact bipartition
coverage/collisions for all 134 cases with alphabet size at least two, and
verified sidecar membership before using it.

Ten cases have no nontrivial compatible partition under the all-k oracle. Eight
of those are also disconnected under the old swap/rescue graph: three generated
two-symbol corpus cases; the explicit `mustlink_not_necessary` sample; the
manager four-symbol case; the original/reduced theory graph-gap cases; and the
manager's four-symbol graph-gap example. This confirms that graph connectivity
is sufficient, not necessary. The alternative rules A/B recover the two small
theory gaps, but the manager's equal-length four-symbol case remains a gap even
for their union.

The manager's four-symbol sample was also checked directly from a previously
captured provider output: all seven canonical cuts appear exactly once, every
cut's negative is matched by positive projections on both sides, and there
are no sound swap, rescue, A, or B edges. This confirms the hypothesis without
relying on the provider's `certificate_check` field.

## Limits

This audit approves mathematical rules and the independent oracle/certificate
logic only. It does not certify the implementation's verifier or readiness
hash, establish general polynomial complexity, infer the hidden number of
factors, or authorize performance claims. Implementation source parity,
orientation/deadline behavior, all-k corpus comparison, and mutation controls
remain pending the corrected immutable implementation readiness.
