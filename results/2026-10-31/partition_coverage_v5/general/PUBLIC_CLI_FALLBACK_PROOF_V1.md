# Combined CLI and hybrid fallback proof

`public_cli_v1.py` is an additive entry point; it does not edit either provider or the repository root. The repository root `solver.py` can dispatch to it using `runpy.run_path` on this file. Its own `ROOT` resolves to `results/2026-10-31/partition_coverage_v5`, and provider imports are relative to that cycle root.

## Modes and defaults

- `exact` is the default. Omitted `--q` selects unrestricted regular-factor compatibility; finite `--q` selects the at-most-q finite projection-language class. It defaults to returning at most two solutions; `--max-solutions all` requests complete enumeration.
- `certificate` requires finite `--q`. It reports a unique certificate or finite-q infeasibility when proved, `insufficient_coverage` when the sparse certificate abstains, and `incomplete` when interrupted. The selected structural runtime is `structural/sparse_certificate_v2.py`.
- `hybrid` requires finite `--q`. It returns a completed certificate result directly; on `insufficient_coverage` only, it calls the exact provider with the same input, q, and original absolute deadline. A timeout or interruption is not converted into infeasibility and does not trigger a second deadline.

`--no-q-opposition` is restricted to exact mode to support matched baselines. `--timeout-seconds` must be finite and nonnegative. Input is read as UTF-8 with optional BOM. Exit codes are 0 for found/infeasible completed results, 2 for invalid input, 3 for incomplete, and 4 for certificate insufficiency.

## Why the fallback preserves the declared semantics

The sparse provider v2's `insufficient_coverage` result means only that its bounded anchor-and-forcing search did not produce the required graph certificate. It is not an infeasibility claim. Hybrid mode then invokes the exact provider, which enumerates every unordered known-k partition permitted by the same `q` class, with the same direct full-block positive cap and negative rejection checks. Therefore the fallback can find partitions the certificate abstained on without changing the model class. A certificate's sound `found` or `infeasible` decision needs no fallback. `incomplete` remains incomplete because the exact provider receives the same absolute deadline and may have no remaining time.

## Root wrapper contract

This file's root and imports are cycle-relative. A thin root `solver.py` wrapper can use `runpy.run_path(str(Path(__file__).parent / "results/2026-10-31/partition_coverage_v5/general/public_cli_v1.py"), run_name="__main__")`; this preserves one implementation of CLI parsing and status/exit behavior. No root-file edit is part of this worker artifact.
