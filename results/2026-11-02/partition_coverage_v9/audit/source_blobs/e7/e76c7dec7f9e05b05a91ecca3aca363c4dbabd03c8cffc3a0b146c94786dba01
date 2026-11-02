# C009 validation controls — v1

This protocol follows the accepted primary gate (129/129 exact full-set agreement, zero mismatches). It is frozen before any control invocations. Controls are separate from the finite-sample correctness denominator and from scale observations.

## Invalid inputs

Run all seven frozen `corpus_v1/invalid/` fixtures once through the frozen provider CLI. Expected result: JSON `status=invalid_input`, `complete=true`, with no partition count, pair relations, or representative. The CLI's intentional exit code is 2; the capture helper will record this as `program_error` and it is accepted only when the JSON contract is valid.

## Expired cooperative deadline

Run `addenda/feasible_count_not_unique_ownership_v1.json` through the frozen CLI once with `--seconds 0 --enumerate`. Expected result: `status=unknown`, `complete=false`, null/absent exact count and ownership fields, exit code 3, and a reaped child. This is a deadline control, not a provider batch rerun.

## Interruption after confirmed partial work

Run `controls/interruption_input_v1.json` through the frozen API interruption wrapper once. The wrapper hooks `_project` in memory and raises SIGINT after the third completed projection call. This deliberately injects interruption after observable partial computation (the first block mask has completed); it does not modify provider files. Expected API result: `unknown`, `complete=false`, exact count/relations/representative/enumeration null, and `metrics.block_masks_precomputed >= 1`. The outer capture must finish successfully and reap its wrapper child. This tests API interruption semantics; it is not claimed as a natural scheduler-timing or CLI-process-kill test.

## Frozen anchors and limits

Provider solver SHA-256 `79255b0a306f8a30dffdd813c018bc4fd9368dad880c07489a86abd50968a5e7`; CLI SHA-256 `356ac0db3ca272403d95bc275e4babc48c5d7fc29caf00cb9685f8e49aed8507`; API protocol SHA-256 `111226b52eef31fd67dc599082e10ca53ae941f4527e8db48063809a85fd761b`; readiness SHA-256 `e0c362047b3c63a1a0e25be52396357a900add60e37dde91c025a3c8fa2d0087`; interruption input SHA-256 `68e9e9cb3e62f583a6ea58bcc76035742df5dc297c4b72fbbd9e164b0874b6d8`; contract SHA-256 `c3f5fddc4e8356e57c01870648234cfbb02a0a6e893bd78484661df7426b1521`.

Every subprocess is captured with the audit's copied helper and a 25-second hard cap. Any invalid result or timeout is retained as a failed/incomplete control; do not rerun an individual control in this version.
