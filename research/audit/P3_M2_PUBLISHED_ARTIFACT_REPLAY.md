# M2 exact published producer artifact replay — tiny PASS, small pending

## Exact executed boundary

- Agent #2 core workflow run 45592454384, checkout 391abf97df3b67661082c907d9ce20b4f69636c2; producer edr_search.py Git blob 73da7bea551df73a8676b0adf0401cd7f2d307b5; M1 edr_bb.py blob 657c4e0e4059b32cd9e6477e61c7a3673290f36d.
- Proof-only workflow run 45592784988, actual checkout 8e6689e8cf3fa0aef7ce2e54032b8b68c611138a. Independent verifier blob 540a7cf9e7b048684d3ea03def744175ae629b65 (green reference run 45592083930); independent RGS12 blob da28e66ca4ff74388be79bf9549c8e02f0c60410. Python 3.13.5 / Ubuntu 24.04.
- No producer checkout in this replay. Downloaded exact Agent #2 artifacts from pinned run; independently checked size, Git SHA-1 and SHA-256 against its published manifest and original raw pin. Rebuilt trusted scope from exact journal bytes and compared byte-for-byte. Replayed each exact certificate in normal and -O; re-enumerated all RGS partitions in each mode, compared optimum/incumbent and complete all-optima list.
- Core retained one certificate where normal/optimized producer bytes were identical (both exact pins recorded); proof replay ran the same immutable bytes under both verifier modes. Core logged normal/optimized and checkpoint/resume byte equality and partial verifier exit 2 for tiny.
- Acceptance replay caps: 240s verifier cooperative, 250s outer process timeout, RLIMIT_AS 5120 MiB, max proof bytes 2147483648, max work 4000000000, max exact checks 200000000, nodes/entries 4000001. RGS oracle 30s/35s outer timeout, 4213597 partitions, 150000000 work, 100000 entries. These are larger acceptance-replay caps, not the benchmark 30s/1536 MiB profile.

Commands in .github/workflows/p3-published-artifact-replay.yml at the exact proof checkout. In particular:
    python -B tests/reference/p3_frontier_verifier.py --make-trusted-scope --raw raw.json --journal journal.json --out independent-trusted.json --seconds 30
    cmp trusted.json independent-trusted.json
    python -B tests/reference/p3_frontier_verifier.py --raw raw.json --journal journal.json --scope trusted.json --proof normal.json --seconds 240 --max-work 4000000000 --max-exact-checks 200000000 --max-nodes 4000001 --max-entries 4000001 --max-proof-bytes 2147483648
    python -B tests/reference/p3_rgs12_oracle.py --raw raw.json
Repeat verifier and oracle with -O. No producer module in PYTHONPATH.

## Tiny actual published artifacts, verified

Agent #2 artifact IDs 15011318454 (one), 15012345186 (all), source run https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45592454384. Proof-only result artifacts 15011353515 (one), 15011367819 (all), run https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45592784988. Both jobs SUCCESS. Exact source pins independently rehashed in proof logs:

| file | bytes | Git blob | SHA-256 |
|---|---:|---|---|
| raw.json | 228 | ef3f41b4c5e27da6ffd4882804399abf454d51a7 | 1c064aa4c7ce111ec8c403e8b6a05b64de5acdec2ef564861f06c2e2e2e42f23 |
| journal.json | 130 | 3a50ce7567b563fa87dc54395451af58b19d75fa | 290c8490b2a4ab5b4c6f49012c7580152ecc6eb7c4bad036bcf71b91925c48f5 |
| trusted.json | 560 | adf7723aa76cdf9bed09e9d42c65511c8c1e8ae8 | 9a43619ffabac9c44e65e69ccc0fc7e5c30033e021625582aa6e31668bdcd172 |
| one certificate | 46588 | bce55d7db1ddbcf6140b2a841f74bb51dad8f2f0 | 91996d9bc6a3d7e88b5c89fc44158bc1cd89cf778256ec67839e1d38555e7ec8 |
| all certificate | 99931 | eafd651d28fc1f06f60bdbc4c0a4095a04dc390b | 1be8394e233fe2c5a337766d73a1385145ab82b95d75273d5d548f60b2b781c0 |

Both normal and optimized verifier exit 0 and RGS exit 0; all result data and counters match. One job 139131014769; all job 139131014713. Result:

| mode | optimum | returned optima | nodes | work | exact checks | normal wall/RSS KiB | -O wall/RSS KiB |
|---|---:|---:|---:|---:|---:|---|---|
| one | 2 | 0 (required by wire mode) | 221 | 60140 | 215 | 0.04 / 20964 | 0.12 / 23964 |
| all | 2 | 4 | 461 | 131556 | 677 | 0.06 / 21136 | 0.16 / 23796 |

Incumbent [0,0,2,3,3,5]. RGS enumerated 203 partitions per execution, optimum 2 and all four owners exactly equal to the all certificate: [[0,0,2,3,3,5],[0,0,2,3,4,3],[0,1,0,3,3,5],[0,1,0,3,4,3]]. Operational status always INCOMPLETE. Actual tiny published producer certificate replay VERIFIED, not merely a synthetic certificate.

## Small distinct outcomes and blocker

- Independent raw-only reference already VERIFIED optimum 4, 16 optima, 4213597 partitions (see P3_M2_RGS12_AND_CI.md).
- Earlier actual native workflow 45592409042 used core pin af0559ad7b9590c1a335ba0801f5504f00b5cdea, verifier 540a7cf and 30s/1536MiB, explicit frontier bytes 67108864. Both small modes produced PARTIAL/FRONTIER_CAP; verifier returned INCOMPLETE/input byte cap, no result, nodes/work/exact checks all zero. No mathematical INVALID established.
  - one: 316730 nodes, producer work 8746102, exact checks 13421; normal producer 17.45s / 408424 KiB, optimized 17.63s / 413100 KiB; certificate Git e104aae52d5535aad6f4e72cee6dc10e8df0e407 SHA-256 d942aadf8405101381fa4ebf8f3332e5de8a1c3b07ebb76ce351240f5dec05fc in both modes.
  - all: 301818 nodes, producer work 9526424, exact checks 23985; normal producer 16.53s / 385916 KiB, optimized 17.12s / 389952 KiB; certificate Git c9528b146649817d027684a24a3276db2d46702f SHA-256 bac411b8491c1489242d67b1b013e85cb392836950598c142ddd6ce75e3ac209 in both modes.
  - Earlier tiny actual native run independently verified the identical tiny hashes under the smaller 30s/1536MiB profile; not an excuse to transfer small results.
- Latest core run 45592454384 small one/all jobs in progress at inspection; exact published artifacts absent. Proof-only run 45592784988 small jobs failed at artifact download (not verifier failures; NOT RUN). Rerun only after exact artifacts exist. No result or complete certificate claim for small.

M2 integration gate overall INCOMPLETE, tiny structural gate VERIFIED. P2.1 unchanged. No external learner/baseline/ledger edits, calls, advanced pruning or PR #8 merge. Concurrent proof commits retained; exact source pins rather than moving HEAD are authoritative.
