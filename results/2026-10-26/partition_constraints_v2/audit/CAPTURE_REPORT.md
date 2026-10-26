# Capture runner verification

`capture.py` stores every run in a fresh directory under `attempts/`, saves raw
stdout/stderr bytes, records execution and scientific status separately, hashes
and snapshots the command's declared sources, and records Python/platform and a
safe allowlist of environment values. Its self-test checks success, a nonzero
exit, timeout, partial timeout output, raw output preservation, and source blob
hashes. There are no external dependencies.

The first outer self-test invocation is preserved at
`attempts/20261026T093136.091516Z_13bfd16f4c/`. The command used a path relative
to the workspace while the child working directory was already `audit/`, so the
child exited 2 with a file-not-found error. This was a harness invocation error;
the capture record and source snapshot are intact.

The corrected outer invocation succeeded at
`attempts/20261026T093216.792626Z_23d24d43e3/` with exit code 0. It created and
verified three immutable nested attempts:

| Attempt | Execution status | Exit code | Check |
|---|---|---:|---|
| `20261026T093217.069473Z_c95b7c8643` | success | 0 | stdout and stderr retained |
| `20261026T093217.262856Z_5851f2d42d` | program_error | 7 | nonzero status and both streams retained |
| `20261026T093217.327585Z_83aecc5d44` | timed_out | — | timeout status and partial stdout retained |

The successful self-test verified every referenced source blob against its
SHA-256. The corresponding capture runner source hash is recorded in each
attempt manifest. Future smoke, correctness, timing, memory, and failed runs use
this capture runner; no terminal-only experimental result is accepted.
