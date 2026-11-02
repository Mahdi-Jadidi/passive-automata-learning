# Independent C009 provider gate — v1

## Scope and gate order

This is the auditor's first local execution of the frozen provider. It is a correctness gate, not a timing benchmark. The candidate readiness file reports `core_candidate_ready_for_auditor_feedback`, says the independent 100-case gate is pending, and records no prior local execution. Accordingly, this gate is the independent main correctness gate; the scale cells remain blocked until this gate is accepted.

The frozen Stage-A inputs and exact independent oracle are the sole ground truth. Run all 129 valid rows in the manifest order, once each, using full enumeration. Each process has a 20-second cooperative deadline and a 25-second capture deadline. The first invocation failure, incomplete response, malformed JSON, or correctness mismatch stops the gate. Preserve every attempted process and do not rerun a provider case in this version.

## Frozen artifacts

* Contract: `coordination/CONTRACT.md`.
* Stage-A protocol: `audit/PROTOCOL_AUDIT_V1.md`.
* Corpus manifest SHA-256: `bd4c76b389d87887504f624248940d9bb1d65d69542bca4c01da0714f5200fa1`.
* Independent oracle SHA-256: `01f7973358400f6e17d0b60ed6646e75f2244bfcba92d262d6149b5e0e9d35d2`.
* Provider `ownership_solver_v1.py`: `79255b0a306f8a30dffdd813c018bc4fd9368dad880c07489a86abd50968a5e7`.
* Provider `ownership_cli_v1.py`: `356ac0db3ca272403d95bc275e4babc48c5d7fc29caf00cb9685f8e49aed8507`.
* Provider API protocol: `111226b52eef31fd67dc599082e10ca53ae941f4527e8db48063809a85fd761b`.
* Readiness snapshot: `e0c362047b3c63a1a0e25be52396357a900add60e37dde91c025a3c8fa2d0087`.
* Capture helper: copied C007 helper, SHA-256 `68ee700f391fb6a1cf135e4b55a11a247b45f25164553c917d1664f6fc4a31cf`.

The provider must remain byte-identical to these anchors. Every CLI run snapshots the provider, CLI, API/readiness, exact case input, corpus, oracle, both protocols, and capture helper into content-addressed blobs under this audit directory.

## Exact invocation and comparison

For each case, run from the workspace root:

```text
python -B -X utf8 <implementation/ownership_cli_v1.py> <frozen-input.json> --seconds 20 --enumerate
```

Require exit code zero, a reaped child, valid JSON, and `complete=true`. Compare the **entire** provider enumeration after canonical block normalization with the independent full compatible partition set. Independently recompute the partition feasibility criterion and all pair counts/relations. Replay the provider's representative, each pair-side witness, every emitted positive/negative projection witness, and each enumerated partition against the fixed labels. Compare exact per-k counts. A single discrepancy rejects the gate and is preserved with both original and minimized input if minimization is useful.

`invalid_input` controls, deadline, and interrupt controls are separate contracts and are not mixed into the valid-case partition comparison. Deadline/interruption must report `unknown`, `complete=false`, and no exact ownership/count claims. The CLI's cooperative expired-deadline control is run only after the valid full-set batch passes; interruption is a separately captured wrapper/API control. No provider source edits are permitted in this audit scope.

## Stopping and interpretation

Accepted means exact agreement on these 129 finite samples under the C009 model and the listed API semantics. It does not establish asymptotic speed or correctness outside the tested model. Only an accepted main gate permits the four bounded correctness-only scale cells in the Stage-A protocol; no speed comparison is in scope.
