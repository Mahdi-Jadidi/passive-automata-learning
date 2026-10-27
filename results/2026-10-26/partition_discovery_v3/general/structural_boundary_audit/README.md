# Independent fixed-word boundary audit

Result: nine small cases accepted against the independent exhaustive
fixed_word_product partition oracle in check.py. Only nine provider calls were
made; no benchmarks, general/fair reruns, or runtime edits occurred.

run_001/report.json is the standalone accepted report. Each case's full raw
input/result was written, flushed and fsynced as *.raw.json BEFORE its oracle
comparison and certificate/witness checks. No failure occurred; no missing
failure record or experimental counterexample is invented. The script would
preserve a separate *.failure.json before raising on any observed discrepancy.

| Case | Returned status | Independent class model count |
|---|---|---:|
| odd opposition cycle | assumption_violation | 0 |
| positive count variation | assumption_violation | 0 |
| forced candidate accepts a negative | assumption_violation | 0 |
| absent symbol | insufficient_coverage | 2 |
| single positive, unique but disconnected | insufficient_coverage | 1 |
| no positives | insufficient_coverage | 3 |
| epsilon positive | insufficient_coverage | 1 |
| permuted alphabet and duplicate words | found, unique | 1 |
| expired deadline | incomplete, unknown | 1 |

The oracle enumerates canonical nonempty bipartitions, forces each side's word
to its common positive projection, and checks every negative against those
singleton languages. With no positives, any partition is feasible by selecting
local words longer than every observed negative; it does not confuse a missing
positive sample with empty local languages, which are not singleton languages.
No candidate projection/graph helper is imported by the oracle.

The odd-cycle path is independently checked as a simple closed odd cycle whose
edges all follow from actual positive pair-projection variation; graph edge
indices and count-conflict certificates are checked too. Accepted-negative
conflicts are independently projected. The successful case's partition, singleton
positive languages, local words, full negative witness coverage and all-unseen
side sets are checked. Deadline state is checked against false exhaustion,
uniqueness and decision claims. This suite does not exercise mid-run nonempty
partial results; it exercises the requested already-expired deadline only.

insufficient_coverage is treated as unresolved, never as evidence of no/one/many
models. These nine cases directly exercise one and multiple compatible models
under that status; the checker also permits zero, without claiming a separate
zero-model insufficient-coverage fixture was run. All assumptions/refutations
here are class-specific, not unrestricted regular-factor conclusions.

Captured attempt, relative to this directory:
../../audit/attempts/20261026T200614.006683Z_8f46830c80/

Its manifest records the exact command and all imported code/input snapshots
(checker, inputs.json, structural provider and capture itself). Outer exit was
0, stderr empty, with the direct child reaped. Capture's generic scientific_status
not_assessed is intentionally separate from this checker report's accepted=true.
Original general/fair boundary evidence remains unchanged and valid in its scope.
