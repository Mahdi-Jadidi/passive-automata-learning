# C007 v4 candidate — corrected local smoke protocol

The provider under test remains the immutable `finest_solver_v4.py` candidate.
This protocol supersedes only the erroneous edge-case list in v4 smoke
protocol; it does not alter the solver or earlier evidence.

`smoke_v5.py` checks exact swap recognition using four cases: an adjacent
reversal (`ab` / `ba`) must create an edge; a nonadjacent transposition
(`abcd` / `cbad`), two simultaneous adjacent swaps (`abcd` / `badc`), and a
three-position reversal (`abc` / `cba`) must not create a single-swap edge.
The v4 smoke incorrectly marked `abc` / `bac` as a negative case even though
it is exactly a valid adjacent reversal. Its failed capture is preserved as a
test-authoring error, not evidence against the solver.

All RGS oracle, proof replay, adaptive/reference comparison, fallback, and
interruption checks remain as described in `PROTOCOL_V4.md`. The later
independent corpus gate is still required. No timing claim is made by this
correctness smoke.
