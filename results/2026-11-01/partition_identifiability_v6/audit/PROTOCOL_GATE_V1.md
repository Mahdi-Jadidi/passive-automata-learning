# C006 solver v5 independent gate — protocol freeze

Freeze time: 2026-11-01 UTC, before the v3 gate driver is executed.

## Candidate and reference

- Provider: `implementation/solver_v5.py`, SHA256
  `e83c8d13e8eac248415160f6d29fb3309f19b5d447c932e00b69e24e7cb60792`.
- CLI: `implementation/cli_v4.py`, SHA256
  `b824ca3751abfaaf424e31357d804f038f7eb79dad3c7a97048caacc240d7c8f`.
- User entry point: root `solver.py`; it dispatches to the frozen CLI.
- Parent helper: frozen C005 `known_k_qexact_v2.py`, SHA256
  `9f08dd645e7fcccbe8ea8022c758b7cf3277a5f01b6533fb9c1ad0cf08b6c84d`.
- Independent all-k reference: `audit/oracle_v4/expected.jsonl`, SHA256
  `ca4b932d12d094a34b46a73580aab551e7a00f3fbd1ddd58f08f9fc75a4d632c`.
- Gate driver v3: `audit/gate_solver_v5_v3.py`, SHA256
  `f40de8cf1f20430e2e540b09bf99f3b062fa85093e749a155d7f5281bcace305`.

## Frozen visible data

The provider receives only the visible positive/negative data, one case at a
time. The oracle's all-k rows are used by the auditor only. The 135 cases are
assembled from these UTF-8 JSONL files:

| File | SHA256 |
|---|---|
| `audit/corpus_v1/inputs.jsonl` | `81d52773ed725d8cc25d20874c585001432d399b2ba643cc85182037472f3139` |
| `audit/corpus_v1/controls.jsonl` | `494326a70999317d590b39f950bfdf45d2f890a09ae210111b5be5406f5b313d` |
| `audit/targeted_nondec_v1/input.jsonl` | `365b45e2eeef8aa00bd9491dbd6b4cc43e40eae17ce658260af18e1c8993b836` |
| `audit/theory_examples_v1/inputs.jsonl` | `4930d9d27abebf58dfd46d90160327d749c2cdc6760cc2d53f5e827fa56ca1fb` |

The implementation owner's `FINAL_TARGET_V1.json` is an additional targeted
case. Hidden grammar/truth sidecars are never given to the provider.

## Pass criteria

1. Enumerate every compatible unordered two-block partition (`max_solutions=None`)
   and require exact set equality with the oracle's complete `k=2` partition
   set for each of the 135 cases. Require the two-block existence result to
   agree with the oracle's nontrivial all-k frontier; do not compare only a
   single answer or a Boolean status.
2. Independently check every positive and negative projection witness.
   Independently replay every returned no-decomposition certificate: each
   must-link edge, reconstructed components, every canonical cut exactly
   once, and a negative/positive collision on both sides for each rejected
   cut. Also call the candidate's public verifier as a secondary check.
3. Run certificate tampering controls (missing/duplicate cut, invalid
   collision, unknown edge symbol, malformed edge rule, and a 40-symbol
   empty-cover certificate), positive-witness tampering, forbidden/invalid
   inputs, singleton alphabet, expired deadline, one-solution truncation, and
   a deterministic interruption after retaining one valid solution. Invalid
   or incomplete outcomes must not be promoted to a complete conclusion.
4. In a separate captured execution, invoke the root `solver.py` CLI with
   `--all` on `implementation/example_manager_candidate_v1.json`. Parse its
   complete JSON and independently replay the returned no-decomposition
   certificate.

Any mismatch, invalid witness, incomplete certificate, unexpected complete
status, or source hash drift fails the gate and is preserved before changes.
Each execution uses immutable `evidence/capture.py` with the source, protocol,
driver, frozen inputs, reference, runtime dependency and CLI wrapper snapshotted.
This is a correctness gate only: no timing or memory comparison is authorized
by this protocol.

## Harness history

Two preliminary gate-driver attempts were preserved before correction:

- `20261101T154742.496460Z_4ebd58b99c` (`gate_solver_v5_v1.py`): the independent
  checker used the wrong polarity for a collision-covered cut.
- `20261101T154817.524320Z_bf7481a386` (`gate_solver_v5_v2.py`): same checker
  logic defect remained. These were auditor harness errors, not provider
  failures; neither is counted as a successful gate.

