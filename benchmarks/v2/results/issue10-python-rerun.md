# Issue #10 — independently executed Python suites

Reviewed core ref: 822a45084dcad4f21f09c445802d12c1312e331a; benchmark ref: 26330252c663db1506c9753920b8d90fd583d2bd. Integration review: 26d1dc39d04188737677f35d82d91ae0f8af99c6. Read issue #10, review and schema proposal comment. No P2 schema claim.

Local git ls-remote still fails: Could not resolve host: github.com. Fetched exact core source through GitHub connector, reconstructed files in isolated directory, then verified git hash-object equals committed blob IDs before running. This is a byte-verified source snapshot, not a clean Git worktree. No modifications to source under test.

| File | Verified Git blob |
|---|---|
| selector_v2/core.py | 997304c3adce9d3148d454b079639575f419ba0e |
| selector_v2/sparse_analysis.py | f773cc1c6b1a852193ba2afb75aa2fce4941a5c2 |
| selector_v2/tests/test_sparse_analysis.py | 965abe7e10fecf35b441fefa844aebf75e549646 |
| harness.py | 2fe8790651e357ebb124f5abfd53d2c1c2ab230e |
| test_harness.py | 99ad6c03ec3b25f9d1798306b26761325138d70e |
| smoke.py | edc0aeb57412fb0e2123af0ab1799df77aa7a983 |

Commands from respective isolated source directories: 

```sh
PYTHONHASHSEED=0 /usr/bin/time -v python -B -m unittest discover -s selector_v2/tests -v
PYTHONHASHSEED=0 /usr/bin/time -v python -B -m unittest discover -s . -p test_harness.py -v
python -B smoke.py issue10-smoke
```

Core output:
```
test_100k_sparse ... ok
test_budget_and_mutation ... ok
test_component_replay_and_scope ... ok
test_degenerate_and_duplicates ... ok
test_exhaustive_ordered_pairs_and_collisions ... ok
test_ids_and_validation ... ok
test_random_corpora_and_root_soundness ... ok
Ran 7 tests in 11.612s
OK
100k/20k context length 0 peak traced bytes: 29333203
100k/20k context length 4 peak traced bytes: 42753347
Elapsed wall: 13.05 s
Maximum resident set size: 216560 KiB
Exit status: 0
```

Harness output:
```
test_corruption ... ok
test_counts ... ok
test_isolation ... ok
test_reference ... ok
Ran 4 tests in 0.056s
OK
Elapsed wall: 1.04 s
Maximum resident set size: 97420 KiB
Exit status: 0
```

Both 100k/20k cases are synthetic constructions from committed core tests, not recovered planted archives. Tracemalloc measures traced Python allocations, not RSS; full-process RSS includes test runner. No external calls. Smoke command completed; separate measurement record follows. Library/project title search for partition-scale-improved, partition-benchmark, planted returned no original archive, only partition-scale-result.json. Full archive access remains blocked. Legacy instrumentation has not yet been validated against exact legacy source in this checkpoint.
