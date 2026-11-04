# C020 C2 v1 — final bounded static delta review

Decision: **STATIC CLEARANCE FOR INDEPENDENT CAPTURED CORRECTNESS GATE**.
No blocking defect found in the actual C1→C2 delta. No provider executions,
imports, source edits or timing by theory. This is not runtime acceptance or
measured speedup. Paper work remains paused; this is candidate slot2, not
authorization for another optimization.

Verified final implementation/READINESS_C2_V1.json bindings:

* candidate_c2_v1/gate_v1.py:
  `5331a1787a9ff74afe1afcbea1668dbe9ee69ef1f7121fec14c7281caa2d8680`
* candidate_c2_v1/partition_gate_v1.py:
  `60a5865a1846ed060b0954eef9cc7937d8709cb2a1aec4a4dbfc0925fac27758`
* candidate_c2_v1/PROTOCOL_V1.md:
  `25031f126782245dbd37b67c18527900064fd8fb41fbbf5da886c8aa4f19b2a5`

Compared actual source to the previously reviewed C1 hash
`334772356836e5dcc5376af756518125c94cf8df3119b9a0492bff86f7b7d8f0`.
Only method/diagnostics and reject's exact projection implementation change.
The final readiness became available during this review and matches the same
source hash observed before and after inspection. CLI remains byte-identical.

## Exact Unicode projection

reject(mask) computes allowed using the unchanged block_symbols(mask), then
builds deletion_table[ord(symbol)]=None for every alphabet symbol outside
allowed. Each allowed symbol is absent from the table and retained unchanged.
Because all input words were fully validated before graph/feasibility work,
every input character is in the alphabet. Thus native translate deletes
exactly the outside-block characters and leaves the inside characters in
order: it is the original projection, for arbitrary declared one-code-point
Unicode symbols. It introduces no encoding, normalization, regex expansion,
case folding or approximate comparison.

The table is constructed afresh on each uncached mask computation, then reused
for all P/N words for that mask. There is no cross-mask table confusion.
An empty allowed set deletes all validated characters; the full alphabet
creates an empty table and retains the whole word. Epsilon yields epsilon.
Non-BMP, combining, whitespace and NUL symbols follow the same ordinal rule.
Foreign symbols cannot be silently excused by projection because unchanged
all-input validation rejects them first.

Consecutive chunks of at most16384 code points cover each word exactly once.
Projection is concatenation-preserving; joining chunk.translate results in
input order equals the original character loop. The result uses exact strings
in the unchanged positive-language set and negative equality checks. Therefore
every reject bit, atom-feasibility test, witness rejection index and complete
partition decision is unchanged. C1 graph-order guarantees and RGS traversal
also remain unchanged. No pruning or extra model assumption was added.

## Deadlines and metrics

Each projection chunk polls before and after native translate. Table-building
polls per alphabet symbol, and join is followed by a poll. Native translate,
join and allocation are not instruction-preemptible; an external hard timeout
is still necessary. Larger chunk granularity can change timeout trajectories,
which is allowed; unfinished proofs retain unresolved and no selected answer.

Completed projection_characters adds the input length, including characters
deleted by the table, so its logical meaning matches the original full scan.
Interrupted progress need not match the per-character baseline. projection_chunks
counts completed chunk calls; deletion_tables_built counts finished tables,
including ones followed by interruption before a completed mask. These are
diagnostics, not exact family counts or proof of less total work.

Table/chunk/join creation has real overhead and memory costs. Native projection
may regress on short words or leave counting/graph/search/output bottlenecks.
The profile-motivation document distinguishes diagnostic profiling from timing;
this source review does not independently validate those profile artifacts or
convert them into speed evidence. No metric-only churn is requested.

## Gate and disposition

Proceed on these frozen hashes with the existing independent full-small-family,
status and witness gate, Unicode/empty/full projection/chunk-boundary controls,
late-invalid/contradictory input, graph-empty known-K cases and cutoffs.
Compare the same input/default compact contract; method/diagnostic/time fields
are scoped differences. Only after correctness acceptance may master authorize
the existing fresh-process six-cell timing/memory comparison. Preserve all
censored/regressing/error cases and obey the two-slot plateau stop.

Snapshots and hashes: source_review_c2_v1/MANIFEST.json. Prior C1 review and
all unimplemented theoretical alternatives remain unchanged.
