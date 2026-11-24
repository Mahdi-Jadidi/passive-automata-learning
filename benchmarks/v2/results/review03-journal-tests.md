# Review 03: independent journal/2 execution

Review 03 at d6daba598ba382f6c213deb12a598d60d3817b00; issue #10 comment 7144845512. Reviewed core 4e21dbf0d06c030681e774cb15f1a5cf0c802f0d, interface b27850a667a55927fd3ad127dccce3956d8ead22, proof ed20d9b12ea9730e07e7d2d1e0581744a266eb02. GitHub DNS unavailable (git ls-remote failed), so exact byte-verified snapshots, not clean worktree CI. Existing predecessor files matched all 14 hashes checked by run_p21.py. Additional source blob hashes independently verified:

| File under selector_v2 (core) | Blob |
|---|---|
| registered_ledger.py | 092507fc156e604be242e3100117fedc27b96d04 |
| integration/run_p21.py | 6c7dec2aa2e3c0a98d2640e9b6e3bc77b2dd23e6 |
| integration/audit_journal.py | 2485d498069564a23cd36940f7c791a678c6d8e9 |
| integration/test_roundtrip.py | fb15567da4265aaa7f147b76bcad5921ff8f2ec2 |
| integration/test_journal_audit.py | 3b5c12b92161c83afefaa552c1252d3aadee8d7e |
| integration/test_gateway_parity.py | c58c25a70f6b5b94f2ff37b04b19ddc8429aa294 |

From scratch snapshot parent with core/selector_v2, interface/, proof/:

```sh
PYTHONHASHSEED=0 /usr/bin/time -v python -B core/selector_v2/integration/run_p21.py --interface-dir interface --proof-dir proof --artifact roundtrip-v2.json --adversarial-artifact adversarial-v2.json --full
PYTHONHASHSEED=0 /usr/bin/time -v python -B -O core/selector_v2/integration/run_p21.py --interface-dir interface --proof-dir proof --artifact roundtrip-v2-opt.json --adversarial-artifact adversarial-v2-opt.json
cmp roundtrip-v2.json roundtrip-v2-opt.json
cmp adversarial-v2.json adversarial-v2-opt.json
sha256sum roundtrip-v2*.json adversarial-v2*.json
```

Actual normal run (abbreviated unittest names, no failures):
```
test_epochs_atomic_and_replay ... ok
test_observations_and_binding ... ok
test_exhaustive_small ... ok
test_golden ... ok
test_multi_epoch ... ok
test_100k_sparse ... ok
test_budget_and_mutation ... ok
test_component_replay_and_scope ... ok
test_degenerate_and_duplicates ... ok
test_exhaustive_ordered_pairs_and_collisions ... ok
test_ids_and_validation ... ok
test_random_corpora_and_root_soundness ... ok
test_actual_producer_adapter_proof ... ok
test_concurrent_attempt_uniqueness_and_mutation ... ok
test_partial_conflict_and_false_exhaustion ... ok
test_transaction_rejections_and_retry ... ok
test_corruptions ... ok
test_full_outer_roundtrip ... ok
test_raw_atomic_rollback ... ok
test_untrusted_and_reentrant_authentication ... ok
test_latest_gateway_projection_and_auth_binding ... ok
Ran 21 tests in 9.640s
OK
100k/20k context length 0 peak traced bytes: 29226235
100k/20k context length 4 peak traced bytes: 42752483
actual roundtrip: 3 epochs, 12 records, 9 events, structural optimum 2
outer provenance corruptions rejected: 20
outer replay: 12 events, 13 records, 3 quarantines
latest gateway parity: 18 byte-identical v1 records; exact-byte and registration auth binding PASS
artifact roundtrip-v2.json bytes 34313 sha256 14f0dc4cb606ca7f1b20a5cd575a937dd6471da594d983d86254e210573e5ab8
artifact adversarial-v2.json bytes 32962 sha256 1b78c4aefe974db58409cb186528af75b1981752ba0a3778634fe3bcb406e97c
Elapsed wall 10.77s; maximum RSS 218032 KiB; exit 0
```

Optimized run: same last nine test names passed; 9 tests in 0.146s, elapsed wall 3.12s, RSS 103820 KiB, exit 0. Same corruption and parity output, same exact artifact bytes, both cmp passed. Both SHA-256 digests match core checkpoint 7 published decompressed digests; generated outputs are fresh. This is independent execution of the reviewed core-authored integration suite, NOT independently authored full outer /2 proof-stream sign-off. Interface at review03 still uses SharedGateway reference, not final delegated production path. No live calls, no operational ACCEPT, no P3 implementation, no merge.
