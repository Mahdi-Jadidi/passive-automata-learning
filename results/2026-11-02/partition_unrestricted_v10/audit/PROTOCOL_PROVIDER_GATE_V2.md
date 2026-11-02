# C010 v2 independent provider gate — preregistration

## Frozen anchors

Run this protocol once against the immutable v2 source below. A source/input hash drift invalidates launch and requires a new protocol version.

| Artifact | SHA-256 |
|---|---|
| `implementation/READINESS_V3.json` | `13733c49a331a05dd1b6e59dbb73cd2323d869b17d50bed88f9997ae855b420e` |
| Solver v2 | `4c7959e96c02023d85943c8c52fae3f198c0de67ea172a72ad0669485f60c502` |
| CLI v2 | `3140df25bab5d60c6c2705098029db9061e3c9d76743bf1dfd48d46aaf2d5eaa` |
| API protocol v2 | `0120261cec26de42a812a18760d0dea598b9085fb14a9e72f63da073bc3a9562` |
| Independent corpus manifest | `82fbc29c1b960cd4b7ca3b177bba586cfdfb8b7cedad55fbade06334d3e13e4c` |
| Independent direct-RGS oracle | `f14d31d8c1dc2b69e742478b80407bf6ba1efc51e70a10ceb395b6f221206cb9` |
| Corpus/oracle cross-validation | `oracle_validation_v1.json`, accepted, 125/125 cases |
| Capture helper | `68ee700f391fb6a1cf135e4b55a11a247b45f25164553c917d1664f6fc4a31cf` |

The source hashes and byte counts were checked against READINESS_V3 before this file was frozen. Three captured implementation preflight cases already exist, but are not treated as the independent gate; this audit will recompute their full answer sets and witnesses.

## Provider run A: full sets and witnesses

Run `audit/provider_runner_v2.py` through `audit/capture.py`, in one fresh Python process, with a 180-second hard capture deadline. The runner invokes `unrestricted_solver_v2.solve(data, deadline=None, enumerate_partitions=True)` exactly once for each of the 125 unique frozen valid corpus payloads, followed by the three frozen analytic preflight inputs in `implementation/PREFLIGHT_CASES_V1.json`. It emits one JSONL record per provider call to captured stdout; it must not write or overwrite any other result file.

The capture source snapshot includes, at minimum: runner, v2 readiness/solver/CLI/API protocol, C010 contract, frozen C010 audit protocol, this provider-gate protocol, corpus manifest/oracle/validation, every referenced valid input, preflight manifest and all three preflight inputs, capture helper, and local preflight capture summary. The exact argument vector and source hashes are retained in the capture attempt manifest. No v1 provider source is imported or run.

The provider capture output and metadata are immutable. Validate them once with `audit/validate_provider_v2.py` in a separate captured process. That validator uses an independent set-insertion partition generator for any extra preflight payloads; for the 125 corpus cases it compares against the separately RGS-enumerated oracle already cross-validated by a second implementation. It checks exact full-set equality, exact total and every per-k count, `k_max_compatible`, all pair counts/relations and both witnesses where they exist, direct projection evidence for every enumerated/representative witness, every adjacent-swap certificate, atom components, and atom feasibility. Acceptance requires 128/128 exact sets, every witness replayed, no missing output, no source/hash drift, and no valid empty model or `forced_different` claim. Preserve any failure and stop acceptance at its first recorded mismatch; do not rerun v2 or shrink away a failure.

## Provider run B: input and interruption controls

Only after run A passes, capture one fresh call of `audit/provider_controls_runner_v2.py` with a 30-second hard cap and source snapshots of its script, v2 readiness/solver, corpus invalid manifest and all six invalid files, v2 API protocol, C010 contract and capture helper. Expected results are `invalid_input` for stale `allowed_k`, stale legacy `k`, empty alphabet, duplicate alphabet symbol, conflicting labels and out-of-alphabet word; `unknown`/`complete:false` with no final counts or relations for an already-expired absolute deadline; and the same incomplete/no-finality response when a synthetic `KeyboardInterrupt` is injected exactly at the protected atom-extraction call. The interrupt control is explicitly a deterministic handler-path injection, not an OS-level timing claim.

Then capture one CLI smoke on `proofcase_no_labels_r3_v1.json` with `--enumerate --seconds 30`, recording the exact input and v2 CLI sources. Independently check the five canonical partitions and spectrum `1,3,1`; preserve all raw output. This smoke is separate from the API gate.

## Gate conditions and exclusions

Any provider error, incomplete result, incorrect count/set/witness, invalid control accepted, final claim in an incomplete result, interruption escaping the API handler, capture cleanup failure, or byte/hash mismatch rejects the v2 candidate. The preregistered comparisons are correctness checks, not a performance benchmark. No provider timing claim is made. Do not begin the four scale cells unless run A, run B, and CLI smoke are accepted. Their exact inputs and separate one-run scale protocol must be frozen before those runs.
