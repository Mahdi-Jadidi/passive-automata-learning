# M2 updated producer validation checkpoint
Core CI source checkout 391abf97df3b67661082c907d9ce20b4f69636c2 (solver blob 73da7bea551df73a8676b0adf0401cd7f2d307b5; M1 657c4e0e4059b32cd9e6477e61c7a3673290f36d; test 3779afe1aa2c528effbf8b081d706fbfe45e0edf; runner 9dd3c684dcae20dc5dec946878d61ac9647eb535); proof checkout e1d022496f98bf50fd57d5ef3a7a0bc8194c817c, verifier blob a35281492e2677f0c57d8955227bc233d95492ea, RGS blob 375c36bfb2602894ce783055d1edf31f265aafa0. Frozen contract ff61b1c56138c89fc0ad9a615f0b2a587b03393a.

Actual [CI run 45592454384](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45592454384): unit job 139129870490 completed SUCCESS, 7/7 tests normal (0.853s) and 7/7 optimized (0.852s). Each mode exercised 115 literal samples in both solver modes against the independent RGS oracle and verifier, duplicate/empty/unused symbols, n=0, nonidentity journal root, direct pair indexing, 100k-symbol lazy suffix, all small entry-boundary restarts, time/work caps and scope rejection. M1 regression run 45592255412 success on source fix commit 32fe278.

Actual tiny job 139129870881 (one) and 139129871221 (all) completed SUCCESS. Both normal and optimized producer/independent verifier passed; both normal/-O fresh certificate bytes and resumed bytes match the existing exact committed artifacts:
- one bce55d7db1ddbcf6140b2a841f74bb51dad8f2f0 SHA256 91996d9bc6a3d7e88b5c89fc44158bc1cd89cf778256ec67839e1d38555e7ec8, 221 nodes, 4587 work.
- all eafd651d28fc1f06f60bdbc4c0a4095a04dc390b SHA256 1be8394e233fe2c5a337766d73a1385145ab82b95d75273d5d548f60b2b781c0, 461 nodes, 11674 work.
- one.partial.json a74b5b92d7e8adf1c8b2da0b8b0acb7f5b0619ed SHA256 038c9089d72afe3d13e2f42b37366d235070ecf98c33e2940641fd094e0b3f3c.
- all.partial.json ba8bd669c6e8b24127711109fa57cf9312a46dfa SHA256 c8cfad9031f63526871ed806d3a45c36d81a068f416b3046bbf8da19705e06a2.
Both partials have exactly root split cursor=0 suffix [0,15) and explicit EXACT_NO residual. Independent replay exit 2 INCOMPLETE, reason unresolved frontier, nodes_checked 2, work_units 1044, exact_checks 6; no result. Resume from each partial yields byte-identical EXHAUSTED certificate. This validates the updated cap-unwind solver rather than transferring initial-pin evidence.

Complete native artifact ZIPs were downloaded and SHA256 verified:
- [one](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45592454384/artifacts/15011318454) ZIP 6172c5f5b5107292ce48a9b0326b3797fa97b25f88034d8e105a561acd2bda92; summary SHA256 0433fd510912d6dda26e7935e94c48b6319715527f0da369d6c01dde6bdbfc9c.
- [all](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45592454384/artifacts/15012345186) ZIP a70e1874acd43f44b77bea97356eb91ed59e8557c4c116422ab5e9ee05ae3d2f; summary SHA256 017a2d9b01f63410d2e41c5559d0ec53f37d011bffa13e93f805bddc580a99d9.
Core runner used 240s cooperative budget, 5120 MiB RLIMIT_AS, 4,000,000 generated-entry cap, separate verifier limits. This is a validation configuration, not 30s/1536 MiB benchmark acceptance. Native tiny fresh/restart outputs match independent 30s/1536 MiB run on initial pin.

## Small fixture: resource-censored independent run, not optimum
Original raw blob b361642873a73bae454d388cbfb2284559dbd69b SHA256 10b0c3534ddf42369db003bca6b323c9fdaa33cd36aa15031360c3428949931b. Agent #3 independently built scope from canonical empty journal/2 (journal blob 191247f1112e15ccc571656026e6591b42a13d3b SHA256 3d4ae1a0cff38cbc7b1bf7a2269c29a256abe205b7efc8f7ed3a31eb17334019; trusted scope blob 616e0b864a0119a333bcb8d3248bec0d871bc6f4 SHA256 89ade477b7f9029acdf8c44b4fe5d1f724038cd795c28b289cd2154e387c841b). These exact bytes are committed under small_choice/ and are suitable for further independent scope replay.

Agent #3 CI 45592409042, initial producer af0559ad7b9590c1a335ba0801f5504f00b5cdea, 64 MiB encoded-frontier cap, 30s/1536 MiB processes:
| Mode | Nodes | Work | Producer normal/-O wall s | RSS KiB normal/-O | Certificate bytes | Status |
|---|---:|---:|---|---|---:|---|
| one | 316730 | 8746102 | 17.45/17.63 | 408424/413100 | 79579990 | PARTIAL FRONTIER_CAP |
| all | 301818 | 9526424 | 16.53/17.12 | 385916/389952 | 81080550 | PARTIAL FRONTIER_CAP |

Both exact partial certificate variants normal/-O are byte-identical, verified by downloaded artifact hashes:
- [one ZIP](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45592409042/artifacts/15011612773) SHA256 2aca856f1e46485d799bca363c523538b44f7f764f7449d56d6f07e1933564fe; partial certificate SHA256 d942aadf8405101381fa4ebf8f3332e5de8a1c3b07ebb76ce351240f5dec05fc, calculated Git blob e104aae52d5535aad6f4e72cee6dc10e8df0e407 (not committed as blob).
- [all ZIP](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45592409042/artifacts/15010579503) SHA256 60cd2d1022845b609e2e635ff90a26291c89c1c41ffbbcce2a2a23d5006ad189; partial certificate SHA256 bac411b8491c1489242d67b1b013e85cb392836950598c142ddd6ce75e3ac209, calculated Git blob c9528b146649817d027684a24a3276db2d46702f (not committed as blob).
Independent verifier exit 2 INCOMPLETE at input byte cap before checking nodes; no structural replay result, no optimum. Producer best-known cost 5 is not certified. The all-optima field is empty in both partials. Larger-budget actual core small jobs remain running at this observation. Independent RGS n=12 separate enumeration required; do not truncate alphabet or claim optimum from known planted cost. No advanced rules, ledger changes, external calls or PR merge. Operational INCOMPLETE.
