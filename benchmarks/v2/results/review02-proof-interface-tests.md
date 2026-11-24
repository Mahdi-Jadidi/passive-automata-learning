# Independent reviewed P2 proof and interface suites

Proof pin db8fb33a5726c779e385544219e39db662a6cb5b; interface pin c6487af8f234cf183ed6febce1e1263de0a57e15. Exact byte-verified snapshots (not clean Git worktrees; network/DNS unavailable).

| File | Git blob |
|---|---|
| independent_replay.py | aa09243fa7ccc941c37609e959aefb419075df32 |
| production_replay.py | f0bfa1785b49aab010f2af69e0e14c0af46d577c |
| ledger_replay.py | c2ae28e42a71aab91f329cf728ab7a95538cbf4e |
| test_independent_replay.py | cbb924c5ffc13ccda66910313703c4b8723e7ae8 |
| test_production_replay.py | 630e2150d186cff9181d96ca7b8a6d713aa1a7c7 |
| test_ledger_replay.py | e42dcec06d7d2e52d2fe7ede112498c74cd6f07a |
| adapter.py | c38e441c7327a44adad8a0fe1125d45c93e8ef69 |
| strict_ledger.py | a66975de137e3ec556b8c7aacd108cf975c46344 |
| test_adapter.py | bfa7dee3373da7d267c373e238b95d271a8a2669 |
| test_strict_ledger.py | 268a4d118e383f1f4c559d972d1d607a0514fd81 |
| golden.json | 602d16bd2cc54f299521789383cf1753ba66b3eb |

## Proof, actual output

Command in proof snapshot: PYTHONHASHSEED=0 /usr/bin/time -v python -B -m unittest discover -s . -v

```
test_component_chain_and_scope ... ok
test_exhaustive_tiny_replay ... ok
test_frozen_epoch_reuse_and_arbitrary_deletion ... ok
test_golden_vectors ... ok
test_label_conflict_and_empty ... ok
test_mutations ... ok
test_ledger_mutations ... ok
test_observations_never_accept ... ok
test_raw_ledger_prefix ... ok
test_duplicates_empty_and_scope ... ok
test_epoch_mutations ... ok
test_exhaustive_closure ... ok
test_golden_core_request ... ok
test_multi_epoch_and_partial ... ok
Ran 14 tests in 0.638s
OK
exhaustive_corpora=2187 structural_checks=4374 forced_edges=925
golden_vectors=["b3e6b42446211a76362e92236de37cf631bee2bcaf04c4fff3463d061904fc1c", "d4d34208a22f662dea22de0c3fa9d983e74c08a9c77984d5be7dafc774806128", "55860bacb2ab0d7ee214c489b206145a14d1276e4a8fbbb17d547c3f1fdf89c9"]
mutation_rejections=44
ledger_mutations=30
epoch_structural_mutations=39
production_corpora=2187 epochs=3112 deletion_facts=7087 structural_checks=4374
core_golden_vectors=2 request_mutations=13
Elapsed wall: 1.72s
Maximum RSS: 98064 KiB
Exit status: 0
```

## Interface, actual output

Command in interface snapshot: PYTHONHASHSEED=0 /usr/bin/time -v python -B -m unittest -v test_adapter test_strict_ledger

```
test_accept_and_auth ... ok
test_atomic_and_immutable ... ok
test_bounded ... ok
test_golden ... ok
test_id_mapping ... ok
test_projection_corruption ... ok
test_request_mutations ... ok
test_symbol_policy ... ok
test_atomic_concurrent_delivery ... ok
test_duplicate_keys_and_origin ... ok
test_no_operational_accept ... ok
test_registered_map_and_snapshot ... ok
test_unsolicited_replay_and_retry ... ok
Ran 13 tests in 0.019s
OK
Elapsed wall: 1.05s
Maximum RSS: 97672 KiB
Exit status: 0
```

Combined with the separate core suite, 39/39 test methods passed. Counts of rejected mutations are reported by committed test code; 44+30+39+13=126. This is unit-test evidence, not a unified adapter-to-ledger transaction test, and never an authenticated external acceptance.
