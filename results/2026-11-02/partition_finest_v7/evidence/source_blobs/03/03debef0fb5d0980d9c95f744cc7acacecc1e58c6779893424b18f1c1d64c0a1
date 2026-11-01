# C007 independent audit corpus protocol v1

Date: 2026-11-02 (Asia/Tehran)

## Frozen scope

This audit targets the sample-level finest partition: a partition of the known
alphabet whose blocks admit regular component languages that contain every
positive projection and reject every negative trace. A planted generator's
partition is hidden metadata only and is not an identifiability target.
Generator architecture, generator partition, and hidden-factor recovery rates
must be reported separately from the sample-level finest partition. In
particular, positive-only rows trivially admit the discrete sample finest and
do not count as hidden-factor recovery successes. Separator calls are internal
searches over fixed data, not active label queries.

The solver-visible record has exactly `alphabet`, `positive`, and `negative`.
It contains no component count, factor partition, DFA, grammar, sample-size
bound, or generator label. Words are arrays of symbols; `[]` denotes epsilon.
The alphabet is ordered, symbol labels are distinct, and positive and negative
sets are disjoint.

Corpus seed is `20261102`. The main corpus has 210 independently generated
payload rows, 30 for each alphabet size 2 through 8. Each is sampled from a
product of total DFAs whose component languages are all infinite. A separate
hidden sidecar records the planted alphabet partition and each DFA. Input
deduplication is by canonical solver-visible payload, not row identifier.
Generation retries a duplicate rather than counting it toward 210.

Targeted controls are frozen separately and are never counted toward the 210
small generator rows. They cover epsilon, no positives, no negatives,
unused symbols, invalid records, a unique finest partition with at least three
blocks, multiple incomparable maximal refinements, and the one-block-only
case. Deadline, interruption-after-partial-answer, missing/forged proof, and
partial-meet cases are execution/proof controls, not ordinary corpus rows.

## Independent oracle convention

For a partition `P`, compatibility is checked directly: for every negative
word `n`, at least one block `B` must have `n|B` absent from the set of
positive projections onto `B`. This is exactly the finite-sample condition
for existence of arbitrary regular factor languages: each local factor can
be the finite set of observed positive projections. No candidate solver or
planted generator is used by the oracle.

The primary oracle enumerates restricted-growth strings (RGS) for every set
partition for alphabets up to 8 symbols. It stores all compatible partitions,
all compatible binary partitions, their common-equivalence meet, and the
maximal-refinement frontier. A separate implementation enumerates by
recursive block insertion and recomputes each projection test without the
primary oracle's cache. It independently recomputes the meet and frontier.

For valid records, the one-block partition is compatible. The meet is the
unique finest compatible partition iff the meet itself is compatible. If not,
the saved maximal frontier demonstrates ambiguity. A production implementation
may also establish the *decision* `multiple_maximal_exist` early: if the meet
of already found compatible partitions is infeasible, every compatible
partition refines that partial meet, so no unique finest can exist. Such an
early decision does not certify the exact meet or enumerate the maximal
frontier. Audit decision completeness and exact-meet completeness separately.
An incomplete search cannot claim uniqueness or a complete frontier.

## Evidence policy

The generator and each oracle/validator run are executed only through
`../evidence/capture.py` (path relative to this audit folder's parent).
Attempts snapshot this protocol, capture wrapper, source, and every input
dependency. Corpus rows and hidden sidecars are immutable once their manifest
is written. Any correction gets a new source/protocol version and a new
attempt; no failed artifact is overwritten.

Production correctness checks begin only after the implementation readiness
source is stable. This protocol freezes data/oracle semantics; it does not
authorize timing. Any timing remains on hold pending master GO.
