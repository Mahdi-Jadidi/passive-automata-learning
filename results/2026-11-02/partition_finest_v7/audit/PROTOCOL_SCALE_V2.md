# C007 adaptive-only scale correctness protocol addendum v2

Date: 2026-11-02 (Asia/Tehran). This addendum retains all five frozen input
rows and all resource limits from `PROTOCOL_SCALE_V1.md`. No solver input,
truth sidecar, seed, or target is changed.

At the time of the scale launch, the master-owned workspace root `solver.py`
wrapper is not yet present. To avoid silently changing the preregistered CLI
surface or delaying the bounded correctness batch, these five scale runs use
the hash-frozen versioned entry point `implementation/finest_cli_v1.py` with
the implementation directory as working directory. Each is still a fresh
process with adaptive mode, `--seconds 28`, and a 30-second hard capture cap.
The actual root wrapper is a separate pending integration check; it does not
retroactively alter these captured CLI results.

This is a protocol-version change made before any scale provider process has
run. It remains correctness-only and authorizes no timing comparison.
