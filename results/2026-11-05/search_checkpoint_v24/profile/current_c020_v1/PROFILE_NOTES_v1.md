# Current C020 diagnostic profile

The baseline snapshot gate hash is 5331a1787a9ff74afe1afcbea1668dbe9ee69ef1f7121fec14c7281caa2d8680. Each case was invoked once, with a 19-second cooperative solve deadline; both completed normally (process exit 0). No ordinary benchmark or speedup estimate is provided. Python is 3.14.6, Windows 11, as recorded per case.

Commands from repository root:

```
py -3.14 results/2026-11-05/search_checkpoint_v24/profile/current_c020_v1/profile_stage.py obstruction_m8
py -3.14 results/2026-11-05/search_checkpoint_v24/profile/current_c020_v1/profile_stage.py D
```

Solver stdout is preserved in CASE.stdout.json; stderr is CASE.stderr.txt (empty). The wrapper printed respectively `{"case": "obstruction_m8", "status": "certified_unique", "seconds": 0.6393567000050098}` and `{"case": "D", "status": "certified_unique", "seconds": 0.4438459000084549}`. Metadata includes input/code hashes, read/JSON, profiled solve, output serialization/write, output size, certificate and native metrics. Binary profiles and complete pstats tables are retained.

For obstruction m8, DFS cumulative time is 0.634s; witness 0.578s; block_symbols 0.417s; reject misses 0.040s; project 0.024s. For D_K4 these are 0.441s, 0.384s, 0.279s, 0.036s, 0.021s. Obstruction has 5296 search nodes and 4141 complete candidates including atom precheck; D has 4005 and 1702. Cache misses are block_masks_computed (255 and 218); hits are the native reject_cache_hits metric. Forced atoms are in the certificate. Projection work and mask/cache counters are in metadata.

These cumulative costs overlap: DFS contains witness calls, witness includes reject and block_symbols, and reject includes project and block_symbols. They must never be summed. Poll costs also overlap all stages. Validation/counting and graph construction are inline within solve, so cProfile does not independently isolate their wall time; solve self time includes these and other inline overhead. Initial atom checking shares witness/reject functions with DFS and is not separately timed. This is an explicit instrumentation limitation, not zero cost. Input/read/JSON and serialization/write are separate wrapper intervals. A deeper stage attribution would require another versioned instrumentation run. The evidence supports investigating search/witness work for these fixtures only, without extrapolating to long traces.

The wrapper calls only the frozen solver on alphabet/positive/negative and explicit K. It neither loads hidden generator data nor changes the solver. Optional A_K4 was not run.
