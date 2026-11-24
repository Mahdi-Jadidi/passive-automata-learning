# Benchmark execution — integration review 02 / issue #10

## Scope and provenance
Read integration review at b2c20d7c3f73144b6bc27aa5be4e02d6d57a9bb9 and issue #10 latest comment (7144366533 at review start). Reviewed pins: legacy 7c90eb59561bd25ec4fdca5ac08b0e5d60d17fd6; P1 822a45084dcad4f21f09c445802d12c1312e331a; P2 core 539af04bb0b097de5704c28f2b82f23cea5ef783; proof db8fb33a5726c779e385544219e39db662a6cb5b; interface c6487af8f234cf183ed6febce1e1263de0a57e15. Source files retrieved and verified by exact Git blob SHA, not clean worktrees (GitHub DNS blocked). Enhanced source was extracted unmodified from verified archive SHA-256 595f928ef085f8decc9533404eeb3a8b458ff4e82e527e80d889c20fa55946ca. Original planted archive SHA-256 5d2dae2ca718cc65d48e5fbcb62480baeae0da35d37edb9184ba2b61d91e1dc4; original handoff SHA-256 79791dea6e84370ef852709edd6680bb8d371299f2a84bea58e0d4ad4efc6541. All 33 distinct recovered inputs; archive reference costs read strictly after runs, not passed to producers. All certified finite optima match archive reference cost, all verified lower bounds are <= reference. References are comparison data, not proof.

Linux x86-64 CPython 3.13.5, PYTHONHASHSEED=0, worker RLIMIT_AS 512 MiB except explicitly marked high-cap P2. Each stage has cooperative time budget and hard subprocess timeout budget+1s. Three concurrent case lanes for full 5s sweep (four-CPU quota, 4 GiB cgroup); core tests overlapped late sweep. Serial repeat and selected long trials; no statistical or end-to-end speedup claim. VM address-space limit differs from RSS. Missing resource measurements on censored processes remain blank. Legacy and enhanced measured through same local simulator instrumenting wrapper, including transcript serialization; response bytes are compact JSON proxy, not network bytes. Producer timing boundaries differ for P1, and P1 is a partial structural optimizer.

## New measurements, not historical results

120 actual baseline/P1 run records: 99 full-cohort, 12 serial repeat, 9 selected 30s (including committed 1,000-symbol input outside planted cohort). 13 P2 runs, 11 unique inputs (9 successful 5s raw roundtrips and 2 failures; 2 high-cap retries). 39 reviewed test methods independently passed.

| 5s/512 MiB, 33 original inputs each | Legacy | Enhanced | P1 |
|---|---:|---:|---:|
| Independently verified structural optimum | 11 | 15 | 29 |
| Independently verified lower bound only | 0 | 0 | 4 |
| Producer cooperative INCOMPLETE | 2 | 3 | 0 |
| Producer TIMEOUT | 13 | 5 | 0 |
| Producer MEMORY_ERROR | 6 | 9 | 0 |
| Producer optimum, replay censored | 1 | 1 | 0 |

P1 lower-bound-only: huge_choice_active, medium_choice, small_choice, tiny_choice. Legacy medium_singleton producer OPTIMAL but verifier timeout; enhanced medium_reverse_pairs producer OPTIMAL but verifier MemoryError. Neither counted as certified optimum. Full sweep has 99/99 planned summaries. Repeat tiny_choice and tiny_reverse two serial repetitions each engine, all statuses/costs reproduced. Enhanced tiny_reverse: 1 local attempt/response, 283 serialized bytes both repeats. Only small serial cohort, not full timing replication.

30s/512 MiB: small_count legacy and enhanced newly verified cost 40 (12.453247140s and 14.056706866s compute; P1 0.027928477s). large_reverse_dense legacy hard timeout (31.016221547s); enhanced MemoryError during JSON serialization after 1 query/902395 local response bytes; P1 verified cost 9990. scale-1000-original legacy timeout (31.010360741s); enhanced verified cost 986, compute 0.138159544s and replay 0.603928411s, 1 local attempt/response, 112684 bytes; P1 verified cost 986, compute 0.151456261s and replay 0.063239438s. No claim all inputs were tried at 30s.

## Latest P2 actual serialized record roundtrip

Three separate capped workers: core component_closure + structural_record and canonical export; fresh EvidenceLedger append + canonical export; independent proof replay_ledger_json against raw input and exported bytes. Exact export equality checked; proof worker imports no producer implementation. Timed closure, structural check, serialization, ledger ingestion, export, replay and stage wall/RSS separately. Operational status INCOMPLETE and external attempts/bytes 0 in every run. This tests real core records, not full adapter-to-ledger transaction unification; that remains a separate integration gate.

5s/512 MiB: nine successful replays: five structural optima (scale-1000-original, huge_reverse_unused, large_reverse_dense, extra_interleaved, small_count) and four bounds only (HDFS, holdout, cover_path_8, tiny_choice). huge_long_active closure MemoryError in inverse deletion index append; huge_choice_active ledger accepted exact export but replay MemoryError at structural projection set insertion. 30s/1536 MiB: huge_long_active successfully verifies cost 10000 (closure 1.905487334s; ingestion 0.702924074s; independent replay 2.017802936s; 5141877 ledger bytes); huge_choice_active closure and ledger complete, replay MemoryError at materialization of remainder tuple in expected_deletions (10.159854642s wall). Do not count unverified producer claims or infer bound from failed replay. Need bounded-memory independent replay for high-diversity long words and producer index memory budgeting.

## Reproduction

In a scratch copy of benchmarks/v2, use the original archives (checksums above) and the exact pinned source files. Preserve producer and independent proof snapshots separately; no source modifications. The following layout is required by runner scripts:
- verified-legacy/ = six legacy files recovered by recover_inputs.py (legacy/ output).
- recovered/partition-scale-improved.zip = original enhanced archive; review02/enhanced-src/ = six files named by harness.LEGACY_BLOBS extracted from ZIP, byte-exact.
- pinned-core/selector_v2/ = P1 at pin above.
- review02/p2/selector_v2/ = P2 core at pin above (five modules and committed tests).
- review02/proof/ = proof audit files at pin above (three modules and three tests).
- review02/interface/ = interface audit files (four modules/tests and golden.json).
- recovered/planted-inputs, recovered/planted-refs, recovered/pinned-inputs = recover_inputs.py output. Copy only scale-1000-original.json from pinned-inputs into review02/scale-input.

The exact archive recovery script is already committed. For example, if the original ZIPs are in /path/archives:
```bash
python -B recover_inputs.py /path/archives recovered-new
cp -r recovered-new/legacy verified-legacy
mkdir -p recovered review02/enhanced-src review02/scale-input
cp /path/archives/partition-scale-improved.zip recovered/
cp -r recovered-new/{planted-inputs,planted-refs,pinned-inputs} recovered/
cp recovered/pinned-inputs/scale-1000-original.json review02/scale-input/
PYTHONPATH=. python - <<'PY'
from zipfile import ZipFile
from pathlib import Path
from harness import LEGACY_BLOBS
with ZipFile('recovered/partition-scale-improved.zip') as z:
    for name in LEGACY_BLOBS:
        (Path('review02/enhanced-src')/name).write_bytes(z.read(name))
PY
# Restore source snapshots from exact pins, then:
python -B review02/run_batch.py review02/all5 --inputs recovered/planted-inputs --jobs 3 --seconds 5 --memory 512
python -B review02/run_batch.py review02/repeat5 --inputs recovered/planted-inputs --jobs 1 --seconds 5 --memory 512 --cases tiny_choice tiny_reverse --repetitions 2
python -B review02/run_batch.py review02/long30 --inputs recovered/planted-inputs --jobs 1 --seconds 30 --memory 512 --cases small_count large_reverse_dense
python -B review02/run_batch.py review02/scale30 --inputs review02/scale-input --jobs 1 --seconds 30 --memory 512
python -B review02/export_results.py review02/all5 recovered/planted-refs review02/all5.csv
python -B review02/export_results.py review02/repeat5 recovered/planted-refs review02/repeat5.csv
python -B review02/export_results.py review02/long30 recovered/planted-refs review02/long30.csv
for c in hdfs_1024 hdfs_holdout_1024_uncapped cover_path_8 scale-1000-original; do
 python -B review02/p2_bench.py recovered/pinned-inputs/$c.json review02/p2-$c --seconds 5 --memory 512
done
for c in tiny_choice small_count large_reverse_dense huge_reverse_unused huge_long_active huge_choice_active extra_interleaved; do
 python -B review02/p2_bench.py recovered/planted-inputs/$c.json review02/p2-$c --seconds 5 --memory 512
done
for c in huge_long_active huge_choice_active; do
 python -B review02/p2_bench.py recovered/planted-inputs/$c.json review02/p2-high-$c --seconds 30 --memory 1536
done
(cd review02/p2 && PYTHONHASHSEED=0 /usr/bin/time -v python -B -m unittest discover -s selector_v2/tests -v)
(cd review02/proof && PYTHONHASHSEED=0 /usr/bin/time -v python -B -m unittest discover -s . -v)
(cd review02/interface && PYTHONHASHSEED=0 /usr/bin/time -v python -B -m unittest -v test_adapter test_strict_ledger)
```
Existing output directories must not be reused. Test file blob hashes in results/review02-core-tests.md and results/review02-proof-interface-tests.md. Benchmark runner blobs independently matched executed copies: enhanced_runner e58848a1574b979f69b769d907de339f593c78a2, run_batch 7ead00d83c9e551deb260cede887fbf6b59198cc, export_results 2fcc9fb25d5dfab9618f0a6f4a92499d9671dba4, p2_bench 195787dc6f154dffd6e192d5c3c794ac19fd9da8. Committed compact all5 CSV matches local projection blob 6a1cc2330a768c783380b8f980a720d1487a2432; join to review02-input-index.csv for hash and archived reference.

## Blockers / limits
Clean Git worktree CI and live black box unavailable; authoritative adapter/ledger/replay transaction integration not completed by benchmark stream. Huge choice independent replay needs resource-safe exact expected-deletions validation. Remaining controlled broad repeat and full 30s matrix not executed; no extrapolation. All numerical results above newly executed (archive labels are historical reference only). No external learner or baseline source changes; no merge.
