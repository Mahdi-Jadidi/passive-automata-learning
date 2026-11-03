# Frozen v4 delta review

Bound to candidate files recorded in `READINESS_V5.json`. No code was
executed and neither reviewer edited files.

## Implementation review: approved for next correctness gate

All v4 delta artifact hashes and byte counts match. In the solver, same and
different witness recovery each checks that the candidate partition is not
`None` before interning it. The loop continues across later k values when the
requested relation has no witness at the current k. No other delta control-flow
or API issue was found by static inspection.

## Independent theory review: approved

The five partitions of a three-symbol set give the compatible family
`{abc}`, `{ab}|{c}`, and `{ac}|{b}`, with counts `(1, 2, 0)` by k. The
different relation can be globally present while absent for k=1. The guard
does not alter the search or R1–R4 proof assumptions; certificate sufficiency
is unchanged.

## Review clarification

The counterexample’s `(b,c)` discussion is a row-local demonstration. Under
alphabetical output order the old code would fail earlier on `(a,b)` for the
same reason. This is clarified in `STATIC_COUNTEREXAMPLE_ADDENDUM_V1.md`.

Approval is static only. The corrected provider, exact full partition family,
constant-fingerprint collisions, witness replay and performance remain
unexecuted and unmeasured.
