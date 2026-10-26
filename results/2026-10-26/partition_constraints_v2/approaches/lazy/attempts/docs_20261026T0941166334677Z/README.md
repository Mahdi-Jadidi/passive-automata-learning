# Lazy provider

Entry point: lazy_solver.solve(data, *, deadline=None). Imports common.engine and
common.helpers with exactly the candidate signatures in ../eager/README.md.
Only the coordinator installs shared files. No third-party dependency.

PROOFS.md gives soundness, completeness, termination and interruption semantics.
Code is initially source-only; broad validation and performance are the independent
auditor's responsibility. Experiments, if run, are recorded under attempts/ with
immutable source snapshots, input hashes, full outputs and execution status.

Incident: inherited coordinator continuation was mistakenly followed before this
scoped implementation task. It created duplicate audit thread
01a17785-8474-7a10-94e6-86c33dabace8, subsequently stood down and archived.
The coordinator's D001 record preserves the occurrence. This incident is an
orchestration error, not a scientific refutation. This provider does not depend
on that duplicate branch and performs no coordination or Git actions.

Initial archived check B001 passed in
attempts/20261026T093326541967Z_14041f71/: 2187 two-symbol ternary samples,
100 seeded three-symbol samples and all four supplied theoretical examples.
Full baseline and lazy outputs for every case, inputs, exact subprocess command,
source snapshots, environment, stdout, stderr and exit status are preserved.
Expired-deadline semantics were also checked. This uses A's candidate modules in
an isolated smoke loader; it does not certify the promoted shared runtime.
No performance comparison is inferred from this execution.
