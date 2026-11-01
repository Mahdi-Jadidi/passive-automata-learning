# C006 bounded performance proposal — v1

Status: preregistered proposal only; **no provider timing run is authorized or
included here**. Correctness has passed for the frozen `solver_v5.py` SHA
`e83c8d13e8eac248415160f6d29fb3309f19b5d447c932e00b69e24e7cb60792` and
root entry `solver.py` SHA `8fb0ecf557d9f76e2e698be4cde7ceefde5dda37ebce53a669094bdcb9f7d551`.

## Primary cells and job order

The frozen corpus has two cells, each run once in a fresh serial process for
three repetitions (six provider jobs total):

1. `large_connected_m64`: an infinite one-factor regular target
   `c (c Y)*`, with alphabet size 64, positives `c` and `ccy` for each
   non-center symbol `y`, and negative `cc`. The expected sound contextual
   must-link graph is the 63-edge star from `c` to every `y`; the provider
   should return a complete connected-graph obstruction. This measures a
   sizable replayable connected certificate without enumerating cuts.
2. `small_full_cover_m4`: the frozen manager example over `a,b,c,d`, with
   positives `acdb,cabd,bcda,dabc` and negative `abcd`. Its one-factor target
   is the infinite regular language `{acdb,cabd,bcda,dabc} union a^5 a*`.
   It has no sound old-rule edges and all seven canonical bipartitions require
   explicit collision-cover records. This measures a small complete-cover
   obstruction.

Alternate the serial order to limit order bias: repetition 1 large then
small; repetition 2 small then large; repetition 3 large then small. Each
invocation uses the root CLI with `--all --seconds 28`; immutable capture has
a 30-second hard timeout. Capture direct raw stdout/stderr, full JSON output,
provider `provider_seconds`, subprocess wall time, output byte count, and
certificate counters. Independently validate every output, every edge or
cut record, and the planted target membership after all jobs finish.

Report medians and ranges per cell only. Do not claim generic speedup or infer
hidden factor count. This is a bounded two-case characterization of distinct
proof paths, not an algorithm-versus-baseline comparison. No memory run is
planned.

## Optional cell (outside the six primary jobs)

`decomposable_m64` has the same 64-symbol alphabet, positive `c`, no negatives,
and one-factor target `c*`. If master chooses to extend the batch, run three
fresh serial decision-mode jobs (omit `--all`, retain `--seconds 28`); expect
one valid `found` witness with `complete=false` and `decision_complete=true`.
These three jobs are not part of the preregistered primary batch and are not
to be run unless the master explicitly adds them.

## Freeze and analysis

`freeze_benchmark_v1.py` creates only visible alphabet/positive/negative
provider records plus separate target grammars and expected certificate
shapes. The target grammar is independently checked before freezing. No `k`,
`q`, hidden factor count or truth grammar enters provider input. Input,
sidecar, expected-obstruction and manifest hashes are written under
`audit/benchmark_v1/`; generation itself is captured before launch. Every
provider job must use `evidence/capture.py` with the protocol, runtime sources,
CLI wrapper, helper, exact input, truth sidecar and manifest snapshotted.
Only the master can authorize timing after reviewing this proposal and the
frozen hashes.

