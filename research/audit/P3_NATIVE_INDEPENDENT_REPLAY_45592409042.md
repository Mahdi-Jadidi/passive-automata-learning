# P3 independent native replay — 45592409042

Disposition: tiny_choice one/all VERIFIED in normal and optimized Python; small_choice one/all INCOMPLETE in both. No operational acceptance or general producer certification. Small partial input was rejected by verifier byte cap before node replay, so partial-region soundness was not established for those bytes.

Workflow: https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45592409042

Producer pin: af0559ad7b9590c1a335ba0801f5504f00b5cdea; producer source blob 5b2ea2636e624ea27b2b9d113c1aee6a1739ceff; edr_bb blob 657c4e0e4059b32cd9e6477e61c7a3673290f36d; core.py blob 997304c3adce9d3148d454b079639575f419ba0e.
Proof pin: 1c292a0b2027302d4ae77cf6b81e96dfe54e5bf5; verifier blob 540a7cf9e7b048684d3ea03def744175ae629b65; contract ff61b1c56138c89fc0ad9a615f0b2a587b03393a.
Workflow source commit: 4e2220f49baacc4784b3150112c1c50989a7c265 (.github/workflows/p3-native-independent-replay.yml; exact CLI invocations and environment). Ubuntu 24.04/Python 3.13.5, 30s cooperative per process, 35s external timeout, 1536 MiB address space, 200M work, 2M entries, 64 MiB producer frontier and verifier proof-byte caps. Independent scope from raw inputs and canonical empty journal. No producer imports in proof process.

Independent exhaustive oracle commit fe5c2d8939169110a12133a041ddc6d6550ff6bc: tiny n=6 203 partitions optimum 2 / four owners; small n=12 4,213,597 partitions optimum 4 / sixteen owners. Tiny native results compared against original oracle in workflow and separately against extended oracle; all matched. Small native results are not certified. Normal/-O certificate hashes match in each of four cases. No restart/resume or 512MiB claim from this workflow.

## Artifacts

[
  {
    "id": 15012046369,
    "name": "native-replay-tiny_choice-all",
    "size_in_bytes": 18936,
    "expired": false
  },
  {
    "id": 15011612773,
    "name": "native-replay-small_choice-one",
    "size_in_bytes": 9592321,
    "expired": false
  },
  {
    "id": 15010952783,
    "name": "native-replay-tiny_choice-one",
    "size_in_bytes": 11852,
    "expired": false
  },
  {
    "id": 15010579503,
    "name": "native-replay-small_choice-all",
    "size_in_bytes": 9433009,
    "expired": false
  }
]

Artifact files are stored in Actions artifacts, not committed as Git objects; Git blob IDs below were computed with git hash-object. Retention applies.

## replay (tiny_choice, one) — job 139129712148, success

```text
2026-11-25T10:12:20.1796204Z normal producer_rc=0
2026-11-25T10:12:20.1807688Z {"closed":197,"elapsed_seconds":0.006935773999998673,"entries":220,"exact_checks":29,"expanded":24,"frontier_bytes":38016,"frontier_entries":220,"generated":220,"nodes":221,"operational_status":"INCOMPLETE","peak_depth":5,"peak_frontier_bytes":38016,"resumed_nodes":0,"status":"EXHAUSTED","stop_reason":null,"work":4587}
2026-11-25T10:12:20.1808842Z producer wall=0.07 RSS_KiB=19304
2026-11-25T10:12:20.2457625Z normal verifier_rc=0
2026-11-25T10:12:20.2468139Z {"exact_checks":215,"nodes_checked":221,"operational_status":"INCOMPLETE","reason":null,"result":{"optima":[],"optimum":2,"owner":[0,0,2,3,3,5]},"status":"VERIFIED","work_units":60140}
2026-11-25T10:12:20.2468937Z verifier wall=0.06 RSS_KiB=19648
2026-11-25T10:12:20.2753448Z literal RGS VERIFIED 203 2 [[0, 0, 2, 3, 3, 5], [0, 0, 2, 3, 4, 3], [0, 1, 0, 3, 3, 5], [0, 1, 0, 3, 4, 3]]
2026-11-25T10:12:20.5286135Z optimized producer_rc=0
2026-11-25T10:12:20.5296714Z {"closed":197,"elapsed_seconds":0.006283183999983066,"entries":220,"exact_checks":29,"expanded":24,"frontier_bytes":38016,"frontier_entries":220,"generated":220,"nodes":221,"operational_status":"INCOMPLETE","peak_depth":5,"peak_frontier_bytes":38016,"resumed_nodes":0,"status":"EXHAUSTED","stop_reason":null,"work":4587}
2026-11-25T10:12:20.5297950Z producer wall=0.24 RSS_KiB=24272
2026-11-25T10:12:20.7062783Z optimized verifier_rc=0
2026-11-25T10:12:20.7072569Z {"exact_checks":215,"nodes_checked":221,"operational_status":"INCOMPLETE","reason":null,"result":{"optima":[],"optimum":2,"owner":[0,0,2,3,3,5]},"status":"VERIFIED","work_units":60140}
2026-11-25T10:12:20.7073626Z verifier wall=0.17 RSS_KiB=22360
2026-11-25T10:12:20.8102556Z literal RGS VERIFIED 203 2 [[0, 0, 2, 3, 3, 5], [0, 0, 2, 3, 4, 3], [0, 1, 0, 3, 3, 5], [0, 1, 0, 3, 4, 3]]
2026-11-25T10:12:20.8163480Z Complete native certificate normal/-O bytes identical
2026-11-25T10:12:20.8204723Z GIT_BLOB 3a50ce7567b563fa87dc54395451af58b19d75fa 290c8490b2a4ab5b4c6f49012c7580152ecc6eb7c4bad036bcf71b91925c48f5  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-tiny_choice-one/journal.json
2026-11-25T10:12:20.8236965Z GIT_BLOB bce55d7db1ddbcf6140b2a841f74bb51dad8f2f0 91996d9bc6a3d7e88b5c89fc44158bc1cd89cf778256ec67839e1d38555e7ec8  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-tiny_choice-one/normal.cert.json
2026-11-25T10:12:20.8266359Z GIT_BLOB 1a20373cef6eff879f18b66a76ebfa4d24a10041 e98558bddf4cbfd1bd5b948aa0b945ca0ceb8206f1dace75dede27005d133b83  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-tiny_choice-one/normal.producer.json
2026-11-25T10:12:20.8296386Z GIT_BLOB b0f44d57f374a2a2ed385f654780e1332b9e126a 1f9b003602fea0e82fa716590945e9446ba65763c56aa75f84625e461303e17e  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-tiny_choice-one/normal.producer.stderr
2026-11-25T10:12:20.8326519Z GIT_BLOB b28363e506fae507ded2d17c8ac419f35299db0f 086a5d19b281eefeabbe69e329ae38161c66089c4bae8e43f6d872aa169a6afb  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-tiny_choice-one/normal.producer.stdout
2026-11-25T10:12:20.8356421Z GIT_BLOB aa8d45ff6646660dceff51cb19ca75ba785379e7 94b5de0fd6b5f8cd8060bdf086e37f04353d8e3c44ce861161e99ab84a2e5051  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-tiny_choice-one/normal.verifier.json
2026-11-25T10:12:20.8385196Z GIT_BLOB ebb2d68199bc07954f5ce9b29e663bfd975b51b7 13083ebd18cfb8aadf1b2e1c0f4507ba821baed22e719318ab9176c038ee05c6  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-tiny_choice-one/normal.verifier.stderr
2026-11-25T10:12:20.8416317Z GIT_BLOB bce55d7db1ddbcf6140b2a841f74bb51dad8f2f0 91996d9bc6a3d7e88b5c89fc44158bc1cd89cf778256ec67839e1d38555e7ec8  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-tiny_choice-one/optimized.cert.json
2026-11-25T10:12:20.8446307Z GIT_BLOB 0cef80cb582ecfb8ba368e6985469bfaa05addec aae841702d46a94599616145ef2730d258cf8c2f90fca1c8cd39bac86954fc9e  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-tiny_choice-one/optimized.producer.json
2026-11-25T10:12:20.8475636Z GIT_BLOB c23eb9b49858f9c6e77b07754f788253ef4e8f8a 77ec32627ebcf472e5c6c06ad3bcaf860292f5f4d9688ba03153b9d18492ab0a  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-tiny_choice-one/optimized.producer.stderr
2026-11-25T10:12:20.8504638Z GIT_BLOB 15bc7dc359f74388745a7256f74ec67cf2367d38 1e60f2b5b5b9b7ba4b5ed352a3befbb1cbd4ccfa1c3d3967c66bcc63e14a109b  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-tiny_choice-one/optimized.producer.stdout
2026-11-25T10:12:20.8534095Z GIT_BLOB aa8d45ff6646660dceff51cb19ca75ba785379e7 94b5de0fd6b5f8cd8060bdf086e37f04353d8e3c44ce861161e99ab84a2e5051  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-tiny_choice-one/optimized.verifier.json
2026-11-25T10:12:20.8563131Z GIT_BLOB acdae60b8bca1dc6cfdacb5205b7686b6ba312b8 46c0cc36f5ebb936748950aa3143a7152a3445562407e1159e55253fcdb686e7  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-tiny_choice-one/optimized.verifier.stderr
2026-11-25T10:12:20.8592234Z GIT_BLOB ef3f41b4c5e27da6ffd4882804399abf454d51a7 1c064aa4c7ce111ec8c403e8b6a05b64de5acdec2ef564861f06c2e2e2e42f23  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-tiny_choice-one/raw.json
2026-11-25T10:12:20.8621475Z GIT_BLOB adf7723aa76cdf9bed09e9d42c65511c8c1e8ae8 9a43619ffabac9c44e65e69ccc0fc7e5c30033e021625582aa6e31668bdcd172  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-tiny_choice-one/scope.json
```

## replay (small_choice, one) — job 139129712685, failure

```text
2026-11-25T10:12:09.0716396Z normal producer_rc=0
2026-11-25T10:12:09.0729577Z {"closed":305159,"elapsed_seconds":11.29263335600001,"entries":316729,"exact_checks":13421,"expanded":11571,"frontier_bytes":67108731,"frontier_entries":316729,"generated":316729,"nodes":316730,"operational_status":"INCOMPLETE","peak_depth":11,"peak_frontier_bytes":67108731,"resumed_nodes":0,"status":"PARTIAL","stop_reason":"FRONTIER_CAP","work":8746102}
2026-11-25T10:12:09.0731523Z producer wall=17.45 RSS_KiB=408424
2026-11-25T10:12:09.1751692Z normal verifier_rc=2
2026-11-25T10:12:09.1763669Z {"exact_checks":0,"nodes_checked":0,"operational_status":"INCOMPLETE","reason":"input byte cap","status":"INCOMPLETE","work_units":0}
2026-11-25T10:12:09.1765252Z verifier wall=0.10 RSS_KiB=84776
2026-11-25T10:12:26.8142896Z optimized producer_rc=0
2026-11-25T10:12:26.8156242Z {"closed":305159,"elapsed_seconds":11.402825443000012,"entries":316729,"exact_checks":13421,"expanded":11571,"frontier_bytes":67108731,"frontier_entries":316729,"generated":316729,"nodes":316730,"operational_status":"INCOMPLETE","peak_depth":11,"peak_frontier_bytes":67108731,"resumed_nodes":0,"status":"PARTIAL","stop_reason":"FRONTIER_CAP","work":8746102}
2026-11-25T10:12:26.8157637Z producer wall=17.63 RSS_KiB=413100
2026-11-25T10:12:27.0430327Z optimized verifier_rc=2
2026-11-25T10:12:27.0443054Z {"exact_checks":0,"nodes_checked":0,"operational_status":"INCOMPLETE","reason":"input byte cap","status":"INCOMPLETE","work_units":0}
2026-11-25T10:12:27.0444262Z verifier wall=0.22 RSS_KiB=87784
2026-11-25T10:12:27.0494174Z GIT_BLOB 191247f1112e15ccc571656026e6591b42a13d3b 3d4ae1a0cff38cbc7b1bf7a2269c29a256abe205b7efc8f7ed3a31eb17334019  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-small_choice-one/journal.json
2026-11-25T10:12:27.3188323Z GIT_BLOB e104aae52d5535aad6f4e72cee6dc10e8df0e407 d942aadf8405101381fa4ebf8f3332e5de8a1c3b07ebb76ce351240f5dec05fc  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-small_choice-one/normal.cert.json
2026-11-25T10:12:27.3232308Z GIT_BLOB 900242d52bf69b5e127e97ed8d217de250cb35c2 0610aa9fc5b7fb216c578fce13183a1faf7706a5a342327403c3ca9883a55de1  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-small_choice-one/normal.producer.json
2026-11-25T10:12:27.3268918Z GIT_BLOB b5d62c058f39e666b78d3f28c7040b73dd86db1f 23ccdd44490090aa86677f2067b2128c106d3f0dd1c0426a2eae61710349d96c  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-small_choice-one/normal.producer.stderr
2026-11-25T10:12:27.3306146Z GIT_BLOB 15974e13a3dcd70dcaaddfdbc39aa400dbcfde9d 6fcdbe2d6a959e65c4d361c523cee449c243b4f6fa0ec74a4c679ead45f7d2e9  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-small_choice-one/normal.producer.stdout
2026-11-25T10:12:27.3342756Z GIT_BLOB b267f8a30ef4b6ebd378ae23eac22c48b2274109 05f9ba8f8b9d8e0e5d32824c5c0f7670b9c142fa32f9c87bc92713321a7e34f7  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-small_choice-one/normal.verifier.json
2026-11-25T10:12:27.3378973Z GIT_BLOB dbc08bacc2ef27c46eecfb5d76882be7fb143c2f f91b1653ce00ee1a5f9349ca9a8380af2f650ffbd3b7903e5386fd3f33d7fec8  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-small_choice-one/normal.verifier.stderr
2026-11-25T10:12:27.6063012Z GIT_BLOB e104aae52d5535aad6f4e72cee6dc10e8df0e407 d942aadf8405101381fa4ebf8f3332e5de8a1c3b07ebb76ce351240f5dec05fc  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-small_choice-one/optimized.cert.json
2026-11-25T10:12:27.6104235Z GIT_BLOB f65076a2344dd2116566ba6dd692047701001404 8fa41180813ece6688e90e03854ae8241433a6e7af737cfb92798fec26be457c  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-small_choice-one/optimized.producer.json
2026-11-25T10:12:27.6140990Z GIT_BLOB 494bc2b77074d59b1af78be9d7ba877bc4c09e7d ae95446fcab41f4ae9f5805719089ab9bf5242fb9610f8f100f406d9d78e6faa  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-small_choice-one/optimized.producer.stderr
2026-11-25T10:12:27.6176901Z GIT_BLOB 67aae1158f4121cbe10caeaa991c4ac9e2a71292 2583abadecda72e4a3456bcfc2c3372cfe098187e67c5774f0025d3325ece953  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-small_choice-one/optimized.producer.stdout
2026-11-25T10:12:27.6212265Z GIT_BLOB b267f8a30ef4b6ebd378ae23eac22c48b2274109 05f9ba8f8b9d8e0e5d32824c5c0f7670b9c142fa32f9c87bc92713321a7e34f7  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-small_choice-one/optimized.verifier.json
2026-11-25T10:12:27.6248741Z GIT_BLOB cc92dd6ed44768e4ccc595743c7bc3a43827afb4 8e9a4c1a240675943fef447c3ea7f9aeaa93d83a5456f87997fd416c84cfc616  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-small_choice-one/optimized.verifier.stderr
2026-11-25T10:12:27.6284524Z GIT_BLOB b361642873a73bae454d388cbfb2284559dbd69b 10b0c3534ddf42369db003bca6b323c9fdaa33cd36aa15031360c3428949931b  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-small_choice-one/raw.json
2026-11-25T10:12:27.6320222Z GIT_BLOB 616e0b864a0119a333bcb8d3248bec0d871bc6f4 89ade477b7f9029acdf8c44b4fe5d1f724038cd795c28b289cd2154e387c841b  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-small_choice-one/scope.json
```

## replay (small_choice, all) — job 139129712721, failure

```text
2026-11-25T10:12:12.2603097Z normal producer_rc=0
2026-11-25T10:12:12.2615945Z {"closed":284713,"elapsed_seconds":10.882927304000006,"entries":301817,"exact_checks":23985,"expanded":17105,"frontier_bytes":67108862,"frontier_entries":301817,"generated":301817,"nodes":301818,"operational_status":"INCOMPLETE","peak_depth":11,"peak_frontier_bytes":67108862,"resumed_nodes":0,"status":"PARTIAL","stop_reason":"FRONTIER_CAP","work":9526424}
2026-11-25T10:12:12.2618260Z producer wall=16.53 RSS_KiB=385916
2026-11-25T10:12:12.3617312Z normal verifier_rc=2
2026-11-25T10:12:12.3628595Z {"exact_checks":0,"nodes_checked":0,"operational_status":"INCOMPLETE","reason":"input byte cap","status":"INCOMPLETE","work_units":0}
2026-11-25T10:12:12.3630164Z verifier wall=0.09 RSS_KiB=84804
2026-11-25T10:12:29.4931886Z optimized producer_rc=0
2026-11-25T10:12:29.4944723Z {"closed":284713,"elapsed_seconds":11.188189011000006,"entries":301817,"exact_checks":23985,"expanded":17105,"frontier_bytes":67108862,"frontier_entries":301817,"generated":301817,"nodes":301818,"operational_status":"INCOMPLETE","peak_depth":11,"peak_frontier_bytes":67108862,"resumed_nodes":0,"status":"PARTIAL","stop_reason":"FRONTIER_CAP","work":9526424}
2026-11-25T10:12:29.4946882Z producer wall=17.12 RSS_KiB=389952
2026-11-25T10:12:29.7126725Z optimized verifier_rc=2
2026-11-25T10:12:29.7137809Z {"exact_checks":0,"nodes_checked":0,"operational_status":"INCOMPLETE","reason":"input byte cap","status":"INCOMPLETE","work_units":0}
2026-11-25T10:12:29.7139314Z verifier wall=0.21 RSS_KiB=87776
2026-11-25T10:12:29.7183365Z GIT_BLOB 191247f1112e15ccc571656026e6591b42a13d3b 3d4ae1a0cff38cbc7b1bf7a2269c29a256abe205b7efc8f7ed3a31eb17334019  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-small_choice-all/journal.json
2026-11-25T10:12:29.9904311Z GIT_BLOB c9528b146649817d027684a24a3276db2d46702f bac411b8491c1489242d67b1b013e85cb392836950598c142ddd6ce75e3ac209  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-small_choice-all/normal.cert.json
2026-11-25T10:12:29.9940908Z GIT_BLOB 4fd8f639ca6abb219c3342038a243df1d4b2072c e8436d5599da03148d6a1ec138aaf84a65fc9c8d1303d332686d041cd64009fb  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-small_choice-all/normal.producer.json
2026-11-25T10:12:29.9975856Z GIT_BLOB 0dfc9dd86ceb10ef70df6fd8c16c42d7e5b1a37a 1d50593bfaaa14bbc72faa3b7003dfa0ca2c1528b2c40a1f05194801a9aa389e  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-small_choice-all/normal.producer.stderr
2026-11-25T10:12:30.0010204Z GIT_BLOB b9efdc77a23818698f0ff587175f3503b67c3e63 10fa4b450b96b7a5d14cc1d1e7dfb0b0ce07b3d8d34b55fe43dcede64c3a7104  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-small_choice-all/normal.producer.stdout
2026-11-25T10:12:30.0044741Z GIT_BLOB b267f8a30ef4b6ebd378ae23eac22c48b2274109 05f9ba8f8b9d8e0e5d32824c5c0f7670b9c142fa32f9c87bc92713321a7e34f7  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-small_choice-all/normal.verifier.json
2026-11-25T10:12:30.0079523Z GIT_BLOB be46bdb153ae00afe40878202dbb6357f805ea61 99c106f56821babed4bf167e3b2a0bacbb39913e22cef43fa3a747d25997fa1f  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-small_choice-all/normal.verifier.stderr
2026-11-25T10:12:30.2886518Z GIT_BLOB c9528b146649817d027684a24a3276db2d46702f bac411b8491c1489242d67b1b013e85cb392836950598c142ddd6ce75e3ac209  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-small_choice-all/optimized.cert.json
2026-11-25T10:12:30.2925527Z GIT_BLOB b222af8fec37e4a7cb45771d9a338597ef8bd085 c1dc4548b4d84a1896542e9bac222418b25af806cb1b84562a08dd09ffdad04e  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-small_choice-all/optimized.producer.json
2026-11-25T10:12:30.2961949Z GIT_BLOB f2149f52fbc27057513139082ed845baa488a694 a7fc7bfa5e14f639d4ccad4b40dfa171c8f69f85707bbf8f9de37f8a207f0fcb  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-small_choice-all/optimized.producer.stderr
2026-11-25T10:12:30.2997594Z GIT_BLOB a53094f71438f150d530293984014f94b3986642 1a1fa0619cca9269180ea6f4f486686412ec549d26ad722fd1ffd04313b016cf  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-small_choice-all/optimized.producer.stdout
2026-11-25T10:12:30.3032573Z GIT_BLOB b267f8a30ef4b6ebd378ae23eac22c48b2274109 05f9ba8f8b9d8e0e5d32824c5c0f7670b9c142fa32f9c87bc92713321a7e34f7  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-small_choice-all/optimized.verifier.json
2026-11-25T10:12:30.3067910Z GIT_BLOB 05180c9f72611d988675398c68e7426e002546a9 4ce2872d3899df4ce97d522112991b7647a07789459bf313f7c207292e4dbd9b  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-small_choice-all/optimized.verifier.stderr
2026-11-25T10:12:30.3102642Z GIT_BLOB b361642873a73bae454d388cbfb2284559dbd69b 10b0c3534ddf42369db003bca6b323c9fdaa33cd36aa15031360c3428949931b  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-small_choice-all/raw.json
2026-11-25T10:12:30.3137819Z GIT_BLOB 616e0b864a0119a333bcb8d3248bec0d871bc6f4 89ade477b7f9029acdf8c44b4fe5d1f724038cd795c28b289cd2154e387c841b  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-small_choice-all/scope.json
```

## replay (tiny_choice, all) — job 139129712830, success

```text
2026-11-25T10:12:06.6347170Z normal producer_rc=0
2026-11-25T10:12:06.6358964Z {"closed":401,"elapsed_seconds":0.010491934000000924,"entries":460,"exact_checks":111,"expanded":60,"frontier_bytes":80376,"frontier_entries":460,"generated":460,"nodes":461,"operational_status":"INCOMPLETE","peak_depth":5,"peak_frontier_bytes":80376,"resumed_nodes":0,"status":"EXHAUSTED","stop_reason":null,"work":11674}
2026-11-25T10:12:06.6360452Z producer wall=0.07 RSS_KiB=19796
2026-11-25T10:12:06.7019432Z normal verifier_rc=0
2026-11-25T10:12:06.7029653Z {"exact_checks":677,"nodes_checked":461,"operational_status":"INCOMPLETE","reason":null,"result":{"optima":[[0,0,2,3,3,5],[0,0,2,3,4,3],[0,1,0,3,3,5],[0,1,0,3,4,3]],"optimum":2,"owner":[0,0,2,3,3,5]},"status":"VERIFIED","work_units":131556}
2026-11-25T10:12:06.7030688Z verifier wall=0.06 RSS_KiB=20028
2026-11-25T10:12:06.7283833Z literal RGS VERIFIED 203 2 [[0, 0, 2, 3, 3, 5], [0, 0, 2, 3, 4, 3], [0, 1, 0, 3, 3, 5], [0, 1, 0, 3, 4, 3]]
2026-11-25T10:12:06.9497606Z optimized producer_rc=0
2026-11-25T10:12:06.9507808Z {"closed":401,"elapsed_seconds":0.011080746999994062,"entries":460,"exact_checks":111,"expanded":60,"frontier_bytes":80376,"frontier_entries":460,"generated":460,"nodes":461,"operational_status":"INCOMPLETE","peak_depth":5,"peak_frontier_bytes":80376,"resumed_nodes":0,"status":"EXHAUSTED","stop_reason":null,"work":11674}
2026-11-25T10:12:06.9509477Z producer wall=0.21 RSS_KiB=24568
2026-11-25T10:12:07.1134591Z optimized verifier_rc=0
2026-11-25T10:12:07.1144691Z {"exact_checks":677,"nodes_checked":461,"operational_status":"INCOMPLETE","reason":null,"result":{"optima":[[0,0,2,3,3,5],[0,0,2,3,4,3],[0,1,0,3,3,5],[0,1,0,3,4,3]],"optimum":2,"owner":[0,0,2,3,3,5]},"status":"VERIFIED","work_units":131556}
2026-11-25T10:12:07.1145578Z verifier wall=0.16 RSS_KiB=22700
2026-11-25T10:12:07.2049176Z literal RGS VERIFIED 203 2 [[0, 0, 2, 3, 3, 5], [0, 0, 2, 3, 4, 3], [0, 1, 0, 3, 3, 5], [0, 1, 0, 3, 4, 3]]
2026-11-25T10:12:07.2104203Z Complete native certificate normal/-O bytes identical
2026-11-25T10:12:07.2140589Z GIT_BLOB 3a50ce7567b563fa87dc54395451af58b19d75fa 290c8490b2a4ab5b4c6f49012c7580152ecc6eb7c4bad036bcf71b91925c48f5  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-tiny_choice-all/journal.json
2026-11-25T10:12:07.2173641Z GIT_BLOB eafd651d28fc1f06f60bdbc4c0a4095a04dc390b 1be8394e233fe2c5a337766d73a1385145ab82b95d75273d5d548f60b2b781c0  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-tiny_choice-all/normal.cert.json
2026-11-25T10:12:07.2202668Z GIT_BLOB 9922d4eaab114bf102e2b5a78d4ba24bb28c6da6 9a8d3dc05e25cc5c9d966766807601833bd95a5bd08acc92e0dc04f220501241  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-tiny_choice-all/normal.producer.json
2026-11-25T10:12:07.2231545Z GIT_BLOB eab54c96c21281a7d7a6ba6ec99bac299644aa8c 5fb9eac3dbe10aeaea0b97dd37ce41609dc903c0e6436ea1c3fcdccb2e2af04f  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-tiny_choice-all/normal.producer.stderr
2026-11-25T10:12:07.2260527Z GIT_BLOB 94fd2a20e95696166fa7fc4968c30d8260afccf3 e7b12f9d1b6d074cf9e119f407e34d5335b3be6f2ec6b78f57cea85fdaab0294  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-tiny_choice-all/normal.producer.stdout
2026-11-25T10:12:07.2289329Z GIT_BLOB 86153d5beb4f36daa543bd1dd1fc538c14c3078b 6601e02ec56b4d7b8d3cbc91712e3250a43c7b2a404e009d155d2e30261a3d70  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-tiny_choice-all/normal.verifier.json
2026-11-25T10:12:07.2319598Z GIT_BLOB 4a7c6b74616c728a1580aababc2c1acd4eae5163 1ebbcc3b7b1fa0375dcca1231ddc9b2569910c0f386cb9fe5ef4cf0a8898811a  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-tiny_choice-all/normal.verifier.stderr
2026-11-25T10:12:07.2353621Z GIT_BLOB eafd651d28fc1f06f60bdbc4c0a4095a04dc390b 1be8394e233fe2c5a337766d73a1385145ab82b95d75273d5d548f60b2b781c0  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-tiny_choice-all/optimized.cert.json
2026-11-25T10:12:07.2384315Z GIT_BLOB 8670b0a849fce958a462ebf908bc9b21f173f7a1 fe0a2ee127c00e30fd59390a32185058a67c96a740e631954ec62b8ca35d0104  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-tiny_choice-all/optimized.producer.json
2026-11-25T10:12:07.2415305Z GIT_BLOB 1f026be983da098eb89b37cad8379f6d48596b9a 4925f5543912215e8ac5328b4dd3bcb73c707f576bea0931a2be403c2af52829  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-tiny_choice-all/optimized.producer.stderr
2026-11-25T10:12:07.2446032Z GIT_BLOB bef29169d864521b124ee9d6502f3a333602aa4d 552c233d1ff45091079b5d0c9f7bbf56e54967c01c136019cb7510e712e17537  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-tiny_choice-all/optimized.producer.stdout
2026-11-25T10:12:07.2477577Z GIT_BLOB 86153d5beb4f36daa543bd1dd1fc538c14c3078b 6601e02ec56b4d7b8d3cbc91712e3250a43c7b2a404e009d155d2e30261a3d70  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-tiny_choice-all/optimized.verifier.json
2026-11-25T10:12:07.2509523Z GIT_BLOB eff518d7d2f2ad8d635b3fb0f8fc4be1ff0bd218 d795dddb0cb931ed12406803d449ef4da149ff2d4505b1cc649c9f0fbac00a08  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-tiny_choice-all/optimized.verifier.stderr
2026-11-25T10:12:07.2541455Z GIT_BLOB ef3f41b4c5e27da6ffd4882804399abf454d51a7 1c064aa4c7ce111ec8c403e8b6a05b64de5acdec2ef564861f06c2e2e2e42f23  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-tiny_choice-all/raw.json
2026-11-25T10:12:07.2572873Z GIT_BLOB adf7723aa76cdf9bed09e9d42c65511c8c1e8ae8 9a43619ffabac9c44e65e69ccc0fc7e5c30033e021625582aa6e31668bdcd172  /home/runner/work/passive-automata-learning/passive-automata-learning/replay-tiny_choice-all/scope.json
```
