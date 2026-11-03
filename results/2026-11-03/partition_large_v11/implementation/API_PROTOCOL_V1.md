# C011 exact no-K solver API, static candidate v1

## Scope and status

This is the bounded implementation contract for the C011 RLE binary-interval
candidate. It preserves the C010 no-K exact partition search and output fields,
while adding `binary_interval_must_link_certificates` and instrumentation. The
source is under static review. No provider execution, correctness run, or
performance measurement has been made; this document does not certify the
candidate as accepted.

## Input and invocation

Input JSON has a nonempty list of unique one-character symbols in `alphabet`,
plus lists of complete strings in `positive` and `negative`. The empty string
denotes epsilon. Labels must not conflict and words may contain only declared
symbols. Keys `k` and `allowed_k` are rejected: the model considers all
component counts from 1 through the alphabet size.

Python API: `unrestricted_solver_v1.solve(data, deadline=None,
enumerate_partitions=False)`. `deadline` is an absolute
`time.perf_counter()` time. The CLI accepts an input path, optional
`--seconds N`, and optional `--enumerate`. Only Python's standard library is
used.

## Result semantics

Complete statuses and C010 meanings are retained: `identified_unique_partition`,
`partial_ownership_identification`, `model_inconsistent`, and `invalid_input`.
An interrupted/deadline-limited call returns `status: incomplete`,
`complete: false`, and null exact counts/relations. Consumers must not infer
uniqueness or inconsistency from an incomplete result. `--enumerate` exports
the complete family without truncation.

The result retains the C010 fields: `method`, `status`, `complete`, `alphabet`,
`atom_partition`, `swap_edge_witnesses`, `atom_projection_feasible`,
`partition_count`, `partition_count_by_k`, `k_max_upper_bound`,
`k_max_compatible`, `pair_relations`, `representative`,
`enumerated_partitions`, and `metrics`. `swap_edge_witnesses` remains limited
to verified adjacent swaps. The new
`binary_interval_must_link_certificates` field contains verified contextual
two-symbol interval witnesses with positive/negative words, half-open interval,
exact left/right contexts, symbol pair, and exact per-symbol interval counts.
It can be empty even when other sound must-links exist; absence of an edge is
never treated as a proof that two symbols can be separated.

The exact search remains authoritative: interval edges only contract symbols
that every compatible factorization must co-own, then the solver checks the
atom partition and exactly searches all atom coarsenings if needed. Every
complete partition family and pair count is intended to equal C010. This
equivalence is not yet runtime-validated.

## Index and collision contract

RLE transition grouping enumerates maximal contiguous intervals containing
exactly two symbols. A deterministic 64-bit polynomial fingerprint indexes
outside contexts. A bucket retains every positive interval record; a hit is
only a candidate. Before union, the solver verifies exact prefix and suffix
characters, interval shape/support, and both exact counts. Fingerprints may
collide without changing correctness. `_fingerprint_range` is an explicit
monkeypatch point for a future constant-fingerprint adversarial audit; that
audit has not been run.

The interval certificate is a direct T1 proof: if its two symbols belonged to
separate independent factors, each factor's projection would be unchanged
between its positive and negative words. This contradicts their labels.
`swap_edge_witnesses` and interval certificates are separate evidence types.

The projection LRU is bounded to 4096 exact `(word, canonical block)` entries;
this is an entry-count bound, not a byte/memory bound. Empty-block projections
bypass the LRU and its hit/miss counters. Memory must be measured separately.
Witnesses are memoized by canonical partition in the current solve call.
Counters for fingerprints, RLE windows, exact candidates/context checks,
verified intervals, unions, projections and witness caches are diagnostic;
they are not timing claims. Worst-case collisions, context verification,
partition search, expanded witnesses and serialization can still be expensive.
`metrics.provider_seconds` retains the C010 timer boundary and is assigned
before constructing the final representative projection witness; it is not a
whole-call measure. Compare external fresh-process wall time including input
reading and JSON output. Nested pair-witness partition lists may be shared by
reference inside the returned Python object; callers should treat results as
read-only. JSON serialization expands the complete fields as usual.

## Known evidence limits and deferred gate

The C010 source baseline is recorded in
`../coordination/parent_manifest.json` and remains unchanged. Earlier C011
generated-swap-only and unbounded candidate sketches are preserved in the
versioned design/handoff notes; they are not silently substituted for this
candidate. No result may be cited as correctness evidence until the frozen
corpus independently compares the complete partition sets and replays every
witness. No speed claim may be made until preregistered whole-process fresh-run
comparisons include preprocessing, output construction and serialization.
