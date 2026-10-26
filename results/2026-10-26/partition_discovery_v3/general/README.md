# C003 general partition construction

general_solver.solve(data, *, deadline=None, max_solutions=1) uses continuing
DFS over graph components with sound learned cuts. fair_reference.solve has
the same API, quotient, traversal order and direct feasibility test, without
cuts. Both use support.py, so the fair comparator is not an independent oracle.
No external dependency or alphabet cap is imposed. No recursive DFS is used.

max_solutions=1 finds a compatible partition; 2 seeks a second by continuing the
stack; None enumerates all (exponential in the worst case). Nonpositive, Boolean
or noninteger limits are rejected. deadline is absolute time.perf_counter.
Every returned solution includes positive projection languages and negative
unseen-projection witnesses. See PROOFS.md for cut, quotient and stopping proofs.

An answer means sample compatibility for unrestricted regular factors. It is not
planted recovery. A first answer usually leaves uniqueness unknown; two prove
ambiguity. Only exhaustion permits a none/unique conclusion. On interruption,
status=incomplete preserves completed answers and any already-established
existence/ambiguity. Graph components/nodes/leaves/cuts and phase timings are in
metrics. Provider timing does not include external serialization.

Prior witness_graph is loaded read-only from
../../partition_constraints_v2/baseline/partition_solver.py, using its graph
function ONLY. Its capped validate is not reused. The parent/auditor must freeze
and supply the imported graph source as an explicit capture dependency.

Initial smoke used C003 audit/capture.py, not a private capture implementation:
audit/attempts/20261026T191237.446567Z_4d9c55ac32/ (relative to C003 root).
It preserved full results BEFORE assertions. Sixty deterministic ternary samples
were compared in full against the immutable old exact solver and the fair
reference, then first/second-answer prefix agreement was checked. A 12-symbol
case exercised removal of the old alphabet cap, graph quotient, duplicate and
input-order normalization, plus expired deadlines and invalid labels/symbols.
The outer captured run exited 0, stderr empty. This small smoke is not the
independent corpus audit or a performance comparison. No failed experiment was
discarded. No old C002 artifact was edited.
