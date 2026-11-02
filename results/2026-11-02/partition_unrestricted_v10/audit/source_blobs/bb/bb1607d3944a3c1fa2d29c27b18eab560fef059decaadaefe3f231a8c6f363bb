# C010 root-wrapper smoke — preregistration

The direct v2 CLI full-enumeration smoke has already passed. Per master handoff, exercise the root `solve.py` forwarding wrapper once with `--help`; do not rerun the direct CLI or provider gate.

Exact invocation, through the immutable capture helper:

```text
python -B -X utf8 solve.py --help
```

Use a fresh subprocess, 30-second hard capture timeout, and snapshot `solve.py`, `implementation/unrestricted_cli_v2.py`, `implementation/unrestricted_solver_v2.py`, `implementation/READINESS_V3.json`, `implementation/API_PROTOCOL_V2.md`, this protocol addendum and `audit/capture.py`. Expected: process exits 0 and captured stdout contains the v2 CLI help, including `--seconds` and `--enumerate`. Preserve stdout, stderr, attempt manifest and result; no scientific inference is made by this wrapper-only check.
