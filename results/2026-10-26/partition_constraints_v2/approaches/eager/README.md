# Fork A candidate interface

The coordinator may promote `engine_candidate.py` to `common/engine.py` and
`common_helpers_candidate.py` to `common/helpers.py` after independent review.
These candidates are ready for that review. Do not modify promoted copies here.

## Engine signatures

- `SearchInterrupted(Exception)` and `check_deadline(deadline)`.
- `eval_expr(expr, assignment) -> True | False | None`.
- `iter_models(num_vars, constraints, *, deadline=None, stats=None)` yields immutable
  ownership tuples, smallest symbol on side zero and both blocks nonempty.
- `find_model(num_vars, constraints, *, deadline=None, stats=None)` returns the
  first such model, or `None`. Lazy callers restart after adding a constraint.

Expressions and fixed symbol order are exactly those in CONTRACT.md. Constraints
are snapshotted on each iterator call. Stats dictionaries accumulate across lazy
restarts. `complete_assignments` counts every full, nonempty ownership assignment
visited, including constraint-rejected assignments; it excludes the all-zero
ownership. `nodes_visited` also counts partial and all-zero search nodes.

## Helper signatures (fixed for B integration)

- `cycle_root() -> pathlib.Path`; `load_baseline() -> module`.
- `validate(data) -> (sorted_alphabet, sorted_unique_positive, sorted_unique_negative)`.
- `project(word, block) -> str`.
- `witness_graph(alphabet, positive, negative) -> (components, edges)`.
- `distinguishers(alphabet, n, p) -> tuple[tuple[int,...],...]` returns all
  distinguishing singleton indices, then distinguishing pairs not containing a
  distinguishing singleton, in deterministic order. No global mutable cache.
- `graph_constraints(alphabet, edges) -> list[expression]`.
- `partition_record(alphabet, positive, negative, assignment) -> dict | None`:
  direct finite projection feasibility check and per-negative possible rejection
  witnesses, independent of expression evaluation.
- `result_from_records(alphabet, positive, negative, records, *, method,
  components, edges, stats=None, complete=True, metrics=None) -> dict`.

The helper result builder deterministically sorts complete partition records.
An incomplete result always has `complete=false`, `status=incomplete`, and
`feasible_partition_count=null`; `found_partition_count` is merely a lower bound.
Providers must catch `SearchInterrupted` and call that builder with partial records.

## Provider and driver

`eager_solver.py` exposes `solve(data, *, deadline=None)` and imports the reviewed
`common.engine` and `common.helpers`. It builds the exact eager formula before
ownership enumeration. `driver_candidate.py` is supplied for promotion to root
`solver.py`; it selects baseline/eager/lazy, defaults to baseline, validates input,
and exits 3 on an incomplete result. The immutable baseline call has cooperative
deadline checks before/after its call; the external runner enforces the hard
per-process limit for all methods. It is not timed through a separate extra
baseline subprocess, which would skew the timing comparison.

## Evidence and preservation

The first archived run A001_initial_candidate_smoke passed. Its source hashes,
source-byte blobs, exact command, stdout/stderr and exit code are retained under
`attempts/20261026T092510693896Z_4f28b836/`; the index is `attempts/journal.jsonl`.
It checks four supplied examples, 100 deterministic sampled labelings, 169 word
pairs against all eight blocks, empty-class cases, a multi-positive shared-side
regression, partial-expression soundness and timeout semantics. These are
initial branch checks; independent broad audit and performance claims remain
the auditor's responsibility. No wrong version has been overwritten by a retry.

`record_attempt.py` is a temporary local capture for runs made before the audit
runner exists. Subsequent experimental executions use the auditor's capture
runner once available. PROOFS.md and SOURCES.md document the formal and citation
boundaries. No changes to shared or baseline files are made by this branch.
