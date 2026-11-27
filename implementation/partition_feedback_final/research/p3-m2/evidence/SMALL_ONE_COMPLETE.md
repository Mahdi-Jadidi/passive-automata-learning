# M2 small_choice one-optimum: complete exact certificate

Core CI source checkout 391abf97df3b67661082c907d9ce20b4f69636c2, solver blob 73da7bea551df73a8676b0adf0401cd7f2d307b5, M1 region primitives unchanged (657c4e0e4059b32cd9e6477e61c7a3673290f36d). Independent verifier checkout e1d022496f98bf50fd57d5ef3a7a0bc8194c817c, verifier blob a35281492e2677f0c57d8955227bc233d95492ea.

Actual completed CI: https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45592454384/job/139129870863
Exact bytes: https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45592454384/artifacts/15011812225

ZIP SHA256: 4f3642287acd18b12e183a4f8e2cf023ecfe2e1cc22c01a19627243025dd3387
ZIP downloaded and SHA256 independently recomputed. Streamed normal.json and recomputed both SHA256 and Git blob identity. The certificate exceeds GitHub's 100 MB file limit; calculated Git identity below is not a claim that the blob was committed. Workflow archive preserves exact certificate, source logs, metrics, partial certificate and summary. Normal, optimized and resumed certificates byte-identical; archive retains one copy.

| Exact member | bytes | SHA256 | Git blob identity |
|---|---:|---|---|
| raw.json | 416 | 10b0c3534ddf42369db003bca6b323c9fdaa33cd36aa15031360c3428949931b | b361642873a73bae454d388cbfb2284559dbd69b |
| journal.json | 130 | 3d4ae1a0cff38cbc7b1bf7a2269c29a256abe205b7efc8f7ed3a31eb17334019 | 191247f1112e15ccc571656026e6591b42a13d3b |
| trusted.json | 754 | 89ade477b7f9029acdf8c44b4fe5d1f724038cd795c28b289cd2154e387c841b | 616e0b864a0119a333bcb8d3248bec0d871bc6f4 |
| normal.json | 264463193 | dafa72f9e8ec4cc63330d4a7cd420cd478237dd7431c7e488267345ed810471e | d1539a0a9ed03d208a88c515c51f6e6473126c3c |
| partial.json | 588 | 8c0293e8f9cdc56db18d64f23a98e3d0208bcda5541a98f8d5fe9d8b5571a395 | cd0a7fb4a3c11450661238ddf88eabecdc32e397 |

Producer EXHAUSTED, 1,091,642 nodes, 32,181 expanded, 1,059,461 closed, 37,238 exact checks, 29,399,963 work, peak depth 11. Producer elapsed search 26.689 s normal, end-to-end 42.456 s normal, 42.363 s optimized, 42.714 s resumed. Independent verifier VERIFIED normal and optimized, optimum 4, owner [0,0,2,3,3,5,6,6,8,9,9,11], 193,106,624 work, 659,914 exact checks, 1,091,642 nodes checked; wall 56.39/56.50 s, RSS 2,026,448/2,028,484 KiB. One-entry checkpoint independently INCOMPLETE with unresolved suffix [0,66), no result; resumed full certificate equals fresh bytes.

Independent raw-only RGS n12 ground truth Agent #3: fe5c2d8939169110a12133a041ddc6d6550ff6bc and 7ee071e0bfdfabeb4d54a02f97b1b838f5c1d123, all 4,213,597 partitions enumerated, cost 4 and 16 optima. Current one-optimum agrees on cost; full producer all-optima agreement not established here. Agent #3 notified in issue #3 and separate proof-only replay job 139131014351 rerun requested.

Commands (from implementation/partition_feedback_final, use actual raw/scope files):
```sh
python -B -m selector_v2.edr_search --raw raw.json --scope trusted.json --mode one --out normal.json --metrics normal.metrics.json --seconds 240 --entries 4000000
python -B -O -m selector_v2.edr_search --raw raw.json --scope trusted.json --mode one --out optimized.json --metrics optimized.metrics.json --seconds 240 --entries 4000000
python -B -m selector_v2.edr_search --raw raw.json --scope trusted.json --mode one --out partial.json --metrics partial.metrics.json --seconds 240 --entries 1
python -B -m selector_v2.edr_search --raw raw.json --scope trusted.json --mode one --out resumed.json --metrics resumed.metrics.json --seconds 240 --entries 4000000 --resume partial.json
```
Replay via pinned independent p3_frontier_verifier.py with --raw raw.json --journal journal.json --scope trusted.json --proof normal.json --seconds 240 --max-nodes 4000001 --max-entries 4000001 --max-proof-bytes 2147483648 --max-work 4000000000 --max-exact-checks 200000000, normal and -O. CI RLIMIT_AS 5120 MiB. This is larger-budget structural validation, not 30s/1536 MiB benchmark acceptance. Operational INCOMPLETE; no merge; no external learner, baseline, ledger or endpoint changes.
