# Review 03 — core gate checkpoint 8 (regression, not closure)

Reviewed integration d6daba598ba382f6c213deb12a598d60d3817b00 and issue #10 comment 7144845512. Pinned actual sources: core 4e21dbf0d06c030681e774cb15f1a5cf0c802f0d, interface b27850a667a55927fd3ad127dccce3956d8ead22, proof ed20d9b12ea9730e07e7d2d1e0581744a266eb02; benchmark head a784d2d6ecb75bc0469c0aa60e210946a2566947 noted, not executed. Direct Git network DNS resolution fails; byte-verified snapshots used. All 22 reviewed blobs (including both gz exports) matched. Latest proof head observed after run 0f7140f81707c0ba713522d508277e25b90fcaab adds only bounded_deletion.py; no independent journal/2 entrypoint yet at that head. Interface communicated intended open_gateway delegation, not yet published as of run.

## Reproduction

From implementation/partition_feedback_final, materialize exact core and sibling source directories at the above pins. In a byte-verified snapshot where pinned/interface and pinned/proof contain actual stream modules and artifact-dir contains the committed gzip exports, execute:

    /usr/bin/time -f 'elapsed=%e maxrss_kib=%M' env PYTHONPATH=. python -m selector_v2.integration.run_review03 --interface-dir pinned/interface --proof-dir pinned/proof --artifact-dir . --output-dir review03-run

Python 3.13.5. Runner checks blob identities before executing; normal full regression, optimized integration regression, boundary tests in both modes, normal/-O/committed gzip equality; logs and gate.json emitted in new output dir. Existing output dir refused. Reproduction using actual checked-out repo: point artifact-dir to selector_v2/integration and point interface/proof dirs at the pinned research/interface/p2 and tests/reference directories in respective worktrees.

## Actual output summary

- normal full regression: 21 tests, 10.015s, OK.
- normal boundary: 5 tests, 0.051s, OK.
- optimized regression: 9 tests, 0.159s, OK.
- optimized boundary: 5 tests, 0.054s, OK.
- full runner elapsed 15.80s, max RSS 217804 KiB. Expected exit 2 (INCOMPLETE), not test failure.
- actual roundtrip: 3 epochs, 12 records, 9 events, structural optimum 2 under existing independent v1 projection replay.
- 20 outer provenance corruptions rejected by core-authored outer audit, 12 events/13 records/3 quarantines on adversarial fixture; 18 byte-identical v1 gateway parity records.
- original short/context 100k/20k traced peaks 29232675 / 42752483 bytes.
- roundtrip decompressed 34313 bytes SHA256 14f0dc4cb606ca7f1b20a5cd575a937dd6471da594d983d86254e210573e5ab8.
- adversarial decompressed 32962 bytes SHA256 1b78c4aefe974db58409cb186528af75b1981752ba0a3778634fe3bcb406e97c.
- Both match prior committed gzip exactly and match normal/-O byte-for-byte.

## Gate semantics

New replay_boundary.py classifies typed malformed proof INVALID; missing verifier, resource/cancellation, wrapped resource exception, unexpected failure or nonclosed replay INCOMPLETE, with no proof exposed. Core-authored outer audit is diagnostic only, never VERiFIED authority. Positive VERIFIED branch tested with explicitly labeled stub solely for result contract, not evidence. Actual false EXHAUSTED rejected by existing proof v1 checker; actual partial closure not certified. Operational status always INCOMPLETE. The runner does not accept arbitrary verifier path or self-authorize; pin actual proof-stream verifier and interface delegation once published. The journal/2 and evidence/1 formats are unchanged.

Formal P2.1 remains OPEN: #5 actual core delegation and /2 export, #3 independent outer /2 replay, then pinned combined rerun. Coordination comments #6 7144996482 and #8 7144997325, issue #10 7144997981. Clean checkout CI unavailable; byte-verified regressions are not CI. The separate full proof/interface test suites and benchmark sweep were not rerun here; their actual pinned modules were exercised in core cross-stream tests. Full-history replay cost, durable recovery, real external protocol/authentication, bounded policy and long-diverse exact replay remain limitations. No P3, external calls, learner changes, schema revision or merge.
