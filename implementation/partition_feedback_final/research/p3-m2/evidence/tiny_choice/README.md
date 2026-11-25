# Native tiny_choice checkpoint — actual independent replay

Status: **VERIFIED for the exact initial producer artifacts below**, not blanket M2 acceptance.
Original producer commit `af0559ad7b9590c1a335ba0801f5504f00b5cdea`, solver blob `5b2ea2636e624ea27b2b9d113c1aee6a1739ceff`, M1 region/DSU blob `657c4e0e4059b32cd9e6477e61c7a3673290f36d`.
Independent Agent #3 proof checkout `1c292a0b2027302d4ae77cf6b81e96dfe54e5bf5`; actual CI run [45592409042](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45592409042), jobs 139129712148 (one), 139129712830 (all). Python 3.13.5, normal and optimized, producer and independent verifier separate processes. The downloaded artifact ZIPs were checked and the exact member Git blob hashes reproduced before publication. The independent trusted scope was built from an empty canonical journal/2 by Agent #3, not by the producer.

| File | Git blob | SHA-256 |
|---|---|---|
| raw.json | ef3f41b4c5e27da6ffd4882804399abf454d51a7 | 1c064aa4c7ce111ec8c403e8b6a05b64de5acdec2ef564861f06c2e2e2e42f23 |
| journal.json | 3a50ce7567b563fa87dc54395451af58b19d75fa | 290c8490b2a4ab5b4c6f49012c7580152ecc6eb7c4bad036bcf71b91925c48f5 |
| trusted.json | adf7723aa76cdf9bed09e9d42c65511c8c1e8ae8 | 9a43619ffabac9c44e65e69ccc0fc7e5c30033e021625582aa6e31668bdcd172 |
| one.cert.json | bce55d7db1ddbcf6140b2a841f74bb51dad8f2f0 | 91996d9bc6a3d7e88b5c89fc44158bc1cd89cf778256ec67839e1d38555e7ec8 |
| all.cert.json | eafd651d28fc1f06f60bdbc4c0a4095a04dc390b | 1be8394e233fe2c5a337766d73a1385145ab82b95d75273d5d548f60b2b781c0 |

Both certificates are EXHAUSTED; normal/-O certificate bytes identical in each mode. Independent RGS visited all 203 partitions; optimum 2; canonical optimum owner [0,0,2,3,3,5]. All four optima: [0,0,2,3,3,5], [0,0,2,3,4,3], [0,1,0,3,3,5], [0,1,0,3,4,3].

| Mode | Nodes | Expanded | Producer exact checks | Producer work | Verifier exact checks | Verifier work | Producer normal/-O wall (s) | Verifier normal/-O wall (s) | Producer normal/-O RSS KiB | Verifier normal/-O RSS KiB |
|---|---:|---:|---:|---:|---:|---:|---|---|---|---|
| one | 221 | 24 | 29 | 4587 | 215 | 60140 | 0.07/0.24 | 0.06/0.17 | 19304/24272 | 19648/22360 |
| all | 461 | 60 | 111 | 11674 | 677 | 131556 | 0.07/0.21 | 0.06/0.16 | 19796/24568 | 20028/22700 |

Complete original logs and artifact bytes:
- [one artifact](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45592409042/artifacts/15010952783) ZIP SHA256 213843d3e9788103a9103be23cbb9c5bac57808aecd37e12136d7061bc71f66a
- [all artifact](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45592409042/artifacts/15012046369) ZIP SHA256 071058ded3ca0d4c9c35d41cb2ed7855e0aca2cc53c69d0b0dc1cade2a7bcc26

Reproduce from initial core checkout:
```sh
export PYTHONPATH=implementation/partition_feedback_final
python -B -m selector_v2.edr_search --raw raw.json --scope trusted.json --mode one --out one.cert.json --metrics one.metrics.json
python -B -m selector_v2.edr_search --raw raw.json --scope trusted.json --mode all --out all.cert.json --metrics all.metrics.json
```
Use the separate exact proof checkout and its `tests/reference/p3_frontier_verifier.py --raw raw.json --journal journal.json --scope trusted.json --proof one.cert.json` (repeat for all and -O). The source fix at 32fe278 changes cap-unwind behavior and is not the source pin of this evidence. Latest core M2 full CI run 45592454384 still pending at publication. Small fixture results and checkpoint/resume equivalence are not established by the tiny artifacts. Operational status INCOMPLETE; no live evaluator, no ledger/learner/baseline change, no merge.
