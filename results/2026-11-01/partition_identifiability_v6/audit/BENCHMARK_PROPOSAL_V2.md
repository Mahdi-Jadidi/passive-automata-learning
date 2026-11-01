# C006 bounded performance proposal — frozen inputs

This is a proposal for six captured provider jobs. **No performance job has
been run.** The provider passed the independent correctness gate, and the two
primary inputs below have been frozen and independently checked for target
membership and obstruction shape.

## Frozen corpus

- Protocol: `audit/PROTOCOL_BENCHMARK_V2.md`, SHA256
  `d3448cc48c182f56165d9c1696c6e82463cdf0c519983681c9ebee1945926c7a`.
- Manifest: `audit/benchmark_v1/manifest.json`, SHA256
  `a2457aa91343f148dfe46f9de602af8249316eb6f468d91e4c27d5a2c6e3fd8f`.
- Visible inputs SHA256: `f8577319ecaf9ca03f1337c1e63104362c74ab6386f2935964fedf4a7dd88096`.
- Infinite-regular target sidecars SHA256:
  `d7b7b01c6cadc9d5ee03ea48ce49452cd90aca88ec36f99380d0066b5323fa5e`.
- Expected obstruction shapes SHA256:
  `533a0e252b52dc9676bb295de405b0504ddba389fffa7a71f1519ccd47391383`.
- Deterministic corpus generation was captured at
  `20261101T155847.026359Z_5e1feb4a4c`; independent target and obstruction
  validation passed at `20261101T155934.245778Z_f637716014`.
- Independent freeze validation report:
  `audit/benchmark_v1/freeze_validation.json`, SHA256
  `c2aa7a769777f189fdb5d562bb4666c72227756fb7887089c4c8ec940f49e506`.

The provider sees only alphabet, positives and negatives; there is no `k`,
`q` or hidden grammar in the input. The separate sidecars establish that both
samples come from infinite one-factor regular targets.

## Six primary jobs

| Cell | Frozen sample | Expected certificate | Repetitions |
|---|---|---|---:|
| `large_connected_m64` | 64 symbols, 64 positives, 1 negative; context length 128, max word length 130; target `c^128 (cY)*` | 63 independently justified star edges; connected non-decomposition certificate | 3 |
| `small_full_cover_m4` | manager example, 4 symbols, 4 positives, 1 negative; target `{acdb, bcda, cabd, dabc} ∪ a^5a*` | no contextual edges; complete collision cover of all 7 canonical cuts | 3 |

Run fresh serial processes in order: large/small, small/large, large/small.
Each job invokes root `solver.py --all --seconds 28` through the frozen CLI,
with immutable capture's hard timeout set to 30 seconds. Preserve full JSON
and raw streams. Report per-cell median and range for provider time and total
subprocess time, output bytes, edge/cut counters and certificate size.
Independently validate each result and certificate after capture. This is a
two-cell characterization, not a comparison against an old method; make no
general speedup claim.

The optional 64-symbol decomposable decision cell is frozen in the manifest
but outside the primary batch. It is not authorized or counted among the six
jobs.

## Related audit report

`audit/AUDIT_GATE_V1.json` contains the provider/CLI runtime anchors, exact
135-row gate counts, duplicate payload aliases, all preserved harness
failures, proof references and this frozen proposal. No source changes or
timing data are required before the master decides whether to run the six-job
batch.

