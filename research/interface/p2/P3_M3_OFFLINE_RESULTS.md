# M3 opt-in offline interface results

Review 08 assignment #4 passed at tested interface commit `58185fe493b921a27ca5b9936213906009ed4ec4`. Both Python 3.13.5 jobs independently produced, replayed and registered all eight case/mode combinations. Each job registered 29 candidates. All 21 tests passed in each job, including the existing interface suite and a native default-v1 replay and format-guard check. Operational status is `INCOMPLETE`. [Actions run 45831750484](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45831750484)

| Python | Job | Logs | Wall time | Peak RSS (KiB) |
| --- | --- | --- | ---: | ---: |
| Normal | [139950013806](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45831750484/job/139950013806) | [Committed transcript](evidence/m3-offline/normal.log) · [Artifact 15122114125](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45831750484/artifacts/15122114125) | 16.72 s | 30,156 |
| `-O` | [139950014294](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45831750484/job/139950014294) | [Committed transcript](evidence/m3-offline/optimized.log) · [Artifact 15121789310](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45831750484/artifacts/15121789310) | 15.82 s | 31,608 |

The downloaded transcript SHA-256s were `69e9fb4f90d81be86d747c8670470faf0ea74575434dc91bcbb8e2b55dc523a7` (normal) and `8bac6794a586a240dc73ecf4516248641d628ee424674a71316d8c6d665056d5` (`-O`). Parsed per-case records from the two logs matched in full, including proof and checkpoint hashes and sizes, independent replay counters, complete RGS optima and registration counts.

A second push at `61706a87c9c5b5194ae74bc8f2d9cdce837e017a` also logged 21 passing tests, eight native case/mode combinations and 29 registrations for each interpreter. [Confirmation run 45832271962](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45832271962)

| Case | Mode | Verified nodes | Work units | Exact checks | RGS partitions | Optimum cost | RGS optima | Registrations per interpreter |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| tiny_choice | one | 10 | 4,768 | 22 | 203 | 2 | 4 | 1 |
| tiny_choice | all | 10 | 5,075 | 46 | 203 | 2 | 4 | 4 |
| small_choice | one | 46 | 19,631 | 98 | 4,213,597 | 4 | 16 | 1 |
| small_choice | all | 46 | 24,244 | 608 | 4,213,597 | 4 | 16 | 16 |
| mixed_path | one | 18 | 5,917 | 18 | 52 | 1 | 3 | 1 |
| mixed_path | all | 35 | 10,665 | 68 | 52 | 1 | 3 | 3 |
| journal_root | one | 4 | 6,282 | 25 | 203 | 2 | 2 | 1 |
| journal_root | all | 4 | 6,401 | 37 | 203 | 2 | 2 | 2 |

The isolated proof subprocess used the expected v2 format and requested search mode. It rebuilt the trusted scope from the journal bytes, verified the complete proof, checked the mixed-rule ancestor path for `mixed_path`, and compared one-mode winner membership and all-mode winner sets with a fresh full RGS census. The census confirms `mixed_path` cost **1**, consistent with the pinned raw/RGS/certificate bytes. The frozen `M3_CORE.md` summary table lists cost 2 for that fixture.

For each `journal_root` mode, the pinned `component_closure` generated two existing-format epochs from the raw sample. The sole `RegisteredLedger` returned by `open_gateway` appended them in one RAW transaction. Its 961-byte pre-registration export matched the immutable archive byte for byte with SHA-256 `ed26e7bd99bf672d53a1a9c4f3449522ccfc84c72bcc574872ba91dfc7aa2cce`. Independent journal replay derived `[0,0,2,3,4,5]`. After proof and RGS verification, the test checked that the same ledger preserved that RAW prefix and appended one or two ordinary REGISTER/REQUEST entries. In all eight cases an offline UNKNOWN observation preserved every pending candidate and appended one QUARANTINE/OBSERVATION entry with null feedback. Proof content and digests stayed outside journal/2.

Every case checked an actual one-entry checkpoint and a one-byte proof cap as `INCOMPLETE` and false exhaustion as `INVALID`, with no result envelope payload. Separate admission probes used the genuine RAW ledger and recorded zero registration calls and an identical ledger export for partial, malformed, unapproved-format and wrong-mode proofs. A real v2 proof was also rejected by the v1 format guard, while the producer with its default split rule produced a verified v1 proof.

## Reproduction and pins

The workflow runs `python -B -u -m unittest -v test_p3_contract test_gateway_v2 test_p3_m3_integration` from `research/interface/p2`. The optimized job adds `-O`. Set `PYTHONPATH` to the pinned producer's `implementation/partition_feedback_final`, `P3_M3_PROOF` to the independent checkout's `tests/reference`, and `P3_M3_EVIDENCE` to the retained `p3-m3/evidence` directory with exact checkout bytes.

The producer subprocess runs `python -B [-O] -m selector_v2.edr_m3 --split-rule CROSS_SUPPORT_LEX_V1 --raw raw.json --scope scope.json --mode {one,all} --out FILE --seconds 30`. Generate the checkpoint with `--entries 1` and complete it with `--resume PARTIAL`. Each runtime compares generated fresh, checkpoint and resume bytes with the retained artifacts and both manifest pins. The independent proof and RGS subprocess removes the producer path and runs `p3_m3_artifact_replay.py` with the case and mode, raw/exact ledger journal/trusted scope paths, the fresh proof for its corresponding runtime, the retained parity reference for the other runtime, and the generated checkpoint and completed resume.

- Producer `9a361f6fa59414cc0ac262154d87c37f5aed0403`. Workflow checks blobs `edr_m3.py 6dd0bdbc2d9436c2eeb15cc0812cf8a6fcf18655`, `edr_cross.py c82e137d277644e6d880fb4295b674d897ef70d1`, `component_closure.py 97844bc266556cc04cd54a75c0d57dc00d6709ea` and `registered_ledger.py 092507fc156e604be242e3100117fedc27b96d04`. The ledger blob matches the M2 authority pinned at `4e21dbf0d06c030681e774cb15f1a5cf0c802f0d`.
- Independent proof `316d4430538b8a9ef0c707b8c46727a830d42321`. Workflow checks blobs `p3_frontier_verifier.py 52e83aa9fdc952aacd7955e6d4ec1783e2fa4030`, `p3_rgs12_oracle.py da28e66ca4ff74388be79bf9549c8e02f0c60410`, `journal_v2_replay.py 6c49013e809b5ac4d2b2a37850e6e6cece513072` and `p3_m3_artifact_replay.py 8b1225295c1aad263e7003397cc0edc24b309259`.
- Retained `096fd14b684624d00c68071db7450f4c0b9c717f`. The test checks manifest blobs `normal/manifest.json 8179a80dcd4d93844a86d2cfb19b0e87dcc2a79d` and `optimized-manifest.json d91c253634dd988b990be1f073705e0e8989ffe6`. Both transcripts list exact raw, journal, scope, fresh, partial and resumed size/SHA-256/Git blob pins for each case.
- Interface test blob `f6947cb145eb4d73976a2642445647bfd95b3e93` and workflow blob `749c4bd7da264aa7120bcd2534af2f3140357a29`. Workflow checks `gateway.py 8b314e11c0d935122779365b08666c482697621f`, `adapter.py c38e441c7327a44adad8a0fe1125d45c93e8ef69` and `strict_ledger.py a66975de137e3ec556b8c7aacd108cf975c46344`.

Each Linux job used a 1,572,864 KiB address-space limit. Producer processes had a 30-second search cap and a 45-second timeout. Independent replay and RGS used a 120-second cap per invocation in the proof harness and a 135-second subprocess timeout. Proof limits were 65,536 bytes, 4 billion work units, 200 million exact checks and 6,000,001 nodes and entries. RGS limits were 4,213,597 partitions, 150 million work units and 100,000 entries.

This gate covers pinned offline structural cases. The four PRs remain separate drafts. [Non-destructive reconciliation plan](P3_DRAFT_RECONCILIATION.md)
