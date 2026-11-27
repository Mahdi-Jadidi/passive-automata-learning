# Review 02 — independently executed reviewed P2 core suite

Read INTEGRATION_REVIEW_02.md at b2c20d7c3f73144b6bc27aa5be4e02d6d57a9bb9 and latest review comment on issue #10. Core reviewed head 539af04bb0b097de5704c28f2b82f23cea5ef783. Local GitHub DNS still fails. Byte-verified source snapshot, not clean worktree CI. All eight exact Python files matched Git blob IDs before execution:

| Path under selector_v2/ | Blob |
|---|---|
| core.py | 997304c3adce9d3148d454b079639575f419ba0e |
| sparse_analysis.py | f773cc1c6b1a852193ba2afb75aa2fce4941a5c2 |
| component_closure.py | 97844bc266556cc04cd54a75c0d57dc00d6709ea |
| schema.py | 65a7522a8442a184c14f7a0fa74fc307ce60229f |
| evidence_store.py | 42e38c8ee590267b292ebc0d678e9d4f3a56849b |
| tests/test_sparse_analysis.py | 965abe7e10fecf35b441fefa844aebf75e549646 |
| tests/test_schema_closure.py | ad959bcd10615d951f4207a7b0e0cf8098c753db |
| tests/test_evidence_store.py | 56ffa92c8bb75606a0ffc70e20e57cda8f905bbe |

Command from the source snapshot parent of selector_v2:
```sh
PYTHONHASHSEED=0 /usr/bin/time -v python -B -m unittest discover -s selector_v2/tests -v
```

Actual output:
```
test_epochs_atomic_and_replay (test_evidence_store.LedgerTests.test_epochs_atomic_and_replay) ... ok
test_observations_and_binding (test_evidence_store.LedgerTests.test_observations_and_binding) ... ok
test_exhaustive_small (test_schema_closure.SchemaClosureTests.test_exhaustive_small) ... ok
test_golden (test_schema_closure.SchemaClosureTests.test_golden) ... ok
test_multi_epoch (test_schema_closure.SchemaClosureTests.test_multi_epoch) ... ok
test_100k_sparse (test_sparse_analysis.SparseTests.test_100k_sparse) ... ok
test_budget_and_mutation (test_sparse_analysis.SparseTests.test_budget_and_mutation) ... ok
test_component_replay_and_scope (test_sparse_analysis.SparseTests.test_component_replay_and_scope) ... ok
test_degenerate_and_duplicates (test_sparse_analysis.SparseTests.test_degenerate_and_duplicates) ... ok
test_exhaustive_ordered_pairs_and_collisions (test_sparse_analysis.SparseTests.test_exhaustive_ordered_pairs_and_collisions) ... ok
test_ids_and_validation (test_sparse_analysis.SparseTests.test_ids_and_validation) ... ok
test_random_corpora_and_root_soundness (test_sparse_analysis.SparseTests.test_random_corpora_and_root_soundness) ... ok

----------------------------------------------------------------------
Ran 12 tests in 14.119s

OK
100k/20k context length 0 peak traced bytes: 29224163
100k/20k context length 4 peak traced bytes: 42752483
User time (seconds): 14.52
System time (seconds): 0.30
Percent of CPU this job got: 95%
Elapsed (wall clock) time (h:mm:ss or m:ss): 0:15.58
Maximum resident set size (kbytes): 216444
Exit status: 0
```
Suite ran during the 3-lane benchmark sweep on a four-CPU-quota Linux host; test timing is not a controlled isolated comparison. Tracemalloc synthetic tests are not the archived planted datasets. No operational ACCEPT or external calls. Full proof/interface suite execution distinct from this core suite.
