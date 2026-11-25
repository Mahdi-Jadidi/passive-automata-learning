# P3 M1 — rollback region algebra and first-true coverage

Date: 2026-11-25. Stream: Agent #2, branch research/v2-implementation-core.

## Scope and disposition

This is the first independently testable P3 producer milestone. It implements the in-memory region algebra and its literal coverage tests only. It is not an end-to-end EDR-BB solver, serialized proof format, restartable frontier, independent certificate verifier, or operational result.

The implementation follows the P3 authorization in issue #11 and the semantics in research/audit/P3_REGION_COVERAGE_CONTRACT.md at proof commit 7ac2314d0b8f49cbe4a315ce2d3d6ba4349b1044 (contract blob 8a5cbeaf6cd3018ea6c077d71d6ab90376841934). The contract is still marked DRAFT / not a frozen wire schema. Core requested schema coordination from Agent #3 in issue #3 comment 7155418880: https://github.com/Mahdi-Jadidi/passive-automata-learning/issues/3#issuecomment-7155418880. No serializer or certificate semantics are being relied on before that review.

## Implemented

- RollbackDSU: deterministic union-by-size, minimum-original-ID tie-break, no path compression, nested rollback markers, canonical owner snapshots.
- RegionState: R(E,D) over the complete original alphabet. E is a canonical owner array; D retains sorted/deduplicated original-ID endpoint pairs, not ephemeral DSU roots. Unused IDs remain present. An E/D contradiction is represented as an explicit empty region.
- first_true_split: preserves alternative order; child j adds equality e_j and all earlier disequalities; returns one child per alternative and an explicit all-false residual. Empty children/residuals are retained, not silently omitted.
- Generic fallback: every unordered pair of distinct current E-classes in stable original-ID order.
- Base lower bound: LB = n - number_of_E_classes; one-optimum cutoff is LB >= U; all-optima cutoff is LB > U.
- SearchCaps / SearchBudget: cooperative seconds and work limits, cumulative generated-entry cap, and a live retained-frontier-payload byte cap. Frontier admission returns a ticket; release returns its accounted bytes. Frontier byte accounting is not a claim of total process-RSS enforcement; rejected entry admission is atomic.

A non-singleton root owner must be supplied by a caller that reconstructed it from independently verified journal/2 evidence. RegionState.root(n) creates only the no-contraction identity root. This milestone does not itself read or re-interpret journal/2.

## Tests and exact observations

Python 3.13.5, Linux. From the implementation/partition_feedback_final module root (the test snapshot was isolated because direct Git clone is DNS-blocked in this runtime):

    /usr/bin/time -f 'elapsed=%e maxrss_kib=%M' env PYTHONPATH=. python -m unittest discover -s selector_v2/tests -p 'test_edr_bb.py' -v
    /usr/bin/time -f 'elapsed=%e maxrss_kib=%M' env PYTHONPATH=. python -O -m unittest discover -s selector_v2/tests -p 'test_edr_bb.py' -v
    python -m compileall -q selector_v2
    python -O -m compileall -q selector_v2

Both test modes passed 9/9. Exact run records are committed in selector_v2/integration/p3-m1/normal.log, optimized.log, normal.time, and optimized.time.

| Metric | Normal | Optimized (-O) |
|---|---:|---:|
| unittest tests | 9/9 | 9/9 |
| unittest internal elapsed | 0.166 s | 0.180 s |
| process elapsed | 0.95 s | 1.03 s |
| process max RSS | 97,808 KiB | 97,804 KiB |

Literal first-true coverage test: 21,195 membership checks across all 15 RGS partitions on four symbols, 157 ordered alternative lists (length 0–3), three parent E states, and three D contexts. It generated/checked 3,834 child records and 1,413 explicit residual records. For every parent member, exactly one first-true child contains it if any alternative is true; otherwise the residual contains it. No parent member is lost and no two children/residual overlap.

Additional checks cover deterministic DSU tie-breaking, no path compression, nested rollback, original-ID owner arrays with unused positions retained, D endpoint provenance through E changes, explicit empty regions, all-pairs fallback coverage of strict coarsenings, base-LB soundness on all four-symbol partitions, one/all-optima cutoff boundary, and cap behavior. The cap fixture records 3 work units, 2 cumulative entries, and 10 live frontier bytes before the next operation is rejected; zero-second, work, entry and memory caps are separately exercised. Rejected admissions leave counters unchanged. A separate ticket test releases a 4-byte entry, admits another 4-byte entry under the same 10-byte live cap, verifies cumulative entries do not decrease, and rejects double release.

Source/test Git blob IDs are recorded below; log hashes are exact Git blob hashes:

- selector_v2/edr_bb.py: a98fd2bb22574e6f80d5ac5267ee1d12a8ee54b7
- selector_v2/tests/test_edr_bb.py: 77c2403c5ebba93ca3742a1a66ad73e479b9d137
- selector_v2/integration/p3-m1/normal.log: 4753ba15d4c48f3c2f4833d94c10cea2affd0a35
- selector_v2/integration/p3-m1/optimized.log: c7c4537bb0cf1f99af4c77eb279307eedc62da38
- selector_v2/integration/p3-m1/normal.time: e4ce4a4dfcd3102ad7f4bfc73311ad4fd9ff243e
- selector_v2/integration/p3-m1/optimized.time: 8b240334ef97f70f59eddc43bfac79faeaf77ec0

## Explicitly not implemented / limitations

- No deterministic serialized region/node/frontier schema yet; awaiting Agent #3's exact field/encoding agreement. No restart/resume or lazy suffix cursor yet.
- No trace-evidence conflict extraction, cross-support proof generation, root E0 reconstruction, or journal/2 integration.
- No complete search loop, incumbent handling, pending UNKNOWN queue, or search-level VERIFIED / INVALID / INCOMPLETE result mapping. No optimality/completeness claim.
- No pruning beyond the authorized mandatory-equality lower bound. No canonical merge-parent restriction, symmetry pruning, rank bounds, AEFC, advanced dead-cover pruning, CDAQ, or bounded mode.
- memory_bytes caps accounted serialized frontier payload only; it does not enforce DSU/scratch/process RSS. Reported RSS is observational, not a cap. Time is cooperative between calls.
- The full existing selector suite was not run in this isolated snapshot; only this new standard-library-only P3 module/test pair and compile checks were executed. No external endpoint, learner, baseline, or authoritative ledger was called or modified.

Milestone disposition: unit tests PASS for region algebra / first-true coverage only. Search status: NOT RUN. Operational status remains INCOMPLETE.
