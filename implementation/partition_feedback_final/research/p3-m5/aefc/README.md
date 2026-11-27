# M5-A named AEFC producer and native fixtures

The producer lives in `selector_v2.feedback_aefc`. On the existing gateway
ledger, call `export()` once to capture the locked journal/2 bytes. Call
`prepare(raw, journal_bytes, limits=Limits(...))` once per snapshot. On
`READY`, call `snapshot.prove(owner, containment_only=False, limits=...)`
with canonical original-symbol class minima. Both calls return a status and
a payload. A successful query returns `PROVEN_NO` and canonical sidecar
bytes for independent verification. A capped or unproved query returns
`UNKNOWN` and no sidecar.

Preparation uses the proof stream's `journal_v2_replay.verify_journal`.
The fixture uses `gateway.open_gateway` and the registered adapter in the
interface stream. Reproduction used interface head
`edc6425b4560652b66d3342a6d9ec53b9c307efc` and proof head
`98e913a7e15d32638319832fc69edb36edb2f505`.

From the repository root in PowerShell, with the sibling interface and
proof worktrees at those pins:

```powershell
$env:PYTHONPATH='implementation/partition_feedback_final;../p3-interface/research/interface/p2;../m3-proof/tests/reference'
$env:AEFC_ARTIFACT_DIR='implementation/partition_feedback_final/research/p3-m5/aefc'
py -3.13 -m unittest selector_v2.integration.test_feedback_aefc
py -3.13 -O -m unittest selector_v2.integration.test_feedback_aefc
```

Each fixture directory contains canonical raw, exact journal, target owner and
sidecar bytes. All eight artifacts were byte-identical across interpreters.
The target loop exhaustively enumerated restricted-growth partitions and
compared every emitted NO against literal ordered projections.

| Fixture | Targets | Literal NO | Containment | Named AEFC | Sidecar bytes |
| --- | ---: | ---: | ---: | ---: | ---: |
| named | 15 | 10 | 4 | 5 | 784 |
| cross-id | 52 | 37 | 9 | 10 | 895 |

The cross-ID fixture uses distinct positional IDs for duplicate negative
words. The binary atom [0,1] links N0 to N1 via a checked free group on
abe and N1 to P0 via a named zero on ab. All queries are offline projection
simulations with zero external calls.

The snapshot reuses the checked source index; atom forests live for a
single target query. Query limits are cooperative. Journal replay uses its
existing byte and deletion budgets. A caller processing untrusted inputs
must enforce a hard deadline and address-space limit around preparation
and proof generation. Sidecars are proposed proofs and await the separate
M5-A sidecar verifier.
