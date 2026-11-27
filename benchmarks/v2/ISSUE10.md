# Issue #10 execution — source verification, archive recovery and paired runs

This checkpoint uses reviewed core commit `822a45084dcad4f21f09c445802d12c1312e331a` and pinned legacy commit `7c90eb59561bd25ec4fdca5ac08b0e5d60d17fd6`. It does not implement P2, P3 or any external evaluator. The reviewed Python tests passed byte-for-byte (see results/issue10-python-rerun.md). The updated harness tests also passed: 4 tests, 0.058 s. Exact code Git blobs: harness.py 1e405a2aa5f0e8c6569bbf4b8f33c0a0b7bec71a; sparse_bench.py a7a71f7e51dba973c265a9e84ea8553590928318; recover_inputs.py 070389b54fa559300baa08e420d4e390e101f985; issue10_checks.py 8ccac19ead4886c217a57b4157151317e92f21de.

## Recovered datasets

The original full planted archive, enhanced package and earlier handoff package were recovered from the user's Library, not guessed or recreated from expected labels. The split archive aliases and several uploaded copies were located but raw-byte materialization was denied; the full generated archive was authorized. Local Git DNS remains unavailable; the handoff contains all six required legacy modules. Four already match the pinned blob bytes; sample.py and search.py match exactly after CRLF-to-LF normalization. The three bundled inputs also match their pinned Git blob IDs after optional line-ending normalization; the 1000-symbol raw fixture matches as-is. No source under test was modified except byte normalization to recover the exact Git blobs.

| Archive | Raw bytes | SHA-256 |
|---|---:|---|
| partition-planted-benchmark.zip | 75205429 | 5d2dae2ca718cc65d48e5fbcb62480baeae0da35d37edb9184ba2b61d91e1dc4 |
| partition-scale-handoff-a3a4afba.zip | 110357 | 79791dea6e84370ef852709edd6680bb8d371299f2a84bea58e0d4ad4efc6541 |
| partition-scale-improved.zip | 706981 | 595f928ef085f8decc9533404eeb3a8b458ff4e82e527e80d889c20fa55946ca |

The extraction script generated 41 archive input/reference-member records and 33 unique raw input hashes. All repeated names have identical input and reference bytes. The generated planted-manifest.csv SHA-256 is `49d09e6632ea0af6e6db6e392459a52fb2dfc6f8d3f647d2be92c0d81b1a6381` (CSV CRLF). Independent second extraction produced the same manifest. The archive bytes are kept outside Git; no large dataset is reuploaded or fabricated. The enhanced package is recovered and hashed but its differing code has not been executed in this checkpoint.

## Reproduce

Obtain the three original archives with the exact checksums above. From the benchmark branch root:

```sh
python -B benchmarks/v2/recover_inputs.py /path/to/archives /tmp/v2-recovered
python -B -m unittest discover -s benchmarks/v2 -p test_harness.py -v
git worktree add --detach /tmp/v2-core 822a45084dcad4f21f09c445802d12c1312e331a
(cd /tmp/v2-core/implementation/partition_feedback_final && \
  PYTHONHASHSEED=0 /usr/bin/time -v python -B -m unittest discover -s selector_v2/tests -v)
CORE=/tmp/v2-core/implementation/partition_feedback_final
for f in hdfs_1024 hdfs_holdout_1024_uncapped cover_path_8 scale-1000-original; do
  python -B benchmarks/v2/harness.py /tmp/v2-recovered/pinned-inputs/$f.json /tmp/v2-legacy-$f \
    --engine legacy --repo /tmp/v2-recovered/legacy --verified-snapshot --seconds 5 --memory 512
  python -B benchmarks/v2/sparse_bench.py "$CORE" /tmp/v2-recovered/pinned-inputs/$f.json /tmp/v2-p1-$f \
    --seconds 5 --memory 512
done
for f in huge_long_active huge_reverse_unused large_reverse_dense small_count tiny_choice; do
  python -B benchmarks/v2/harness.py /tmp/v2-recovered/planted-inputs/$f.json /tmp/v2-legacy-$f \
    --engine legacy --repo /tmp/v2-recovered/legacy --verified-snapshot --seconds 5 --memory 512
  python -B benchmarks/v2/sparse_bench.py "$CORE" /tmp/v2-recovered/planted-inputs/$f.json /tmp/v2-p1-$f \
    --seconds 5 --memory 512
done
python -B benchmarks/v2/harness.py /tmp/v2-recovered/planted-inputs/tiny_choice.json /tmp/v2-targeted \
  --engine legacy --legacy-mode targeted --repo /tmp/v2-recovered/legacy --verified-snapshot --seconds 5 --memory 512
python -B benchmarks/v2/issue10_checks.py /tmp/v2-recovered/legacy /tmp/v2-p1-scale-1000-original
```

The verified-snapshot option checks exactly six source files by Git blob hash and does not pretend to be a Git worktree. The normal clean-worktree check remains the default. The core runner checks both producer modules by exact blob. The reference and producer only receive an input-only snapshot. Planted reference bytes stay in separate directories; the proof replay consumes only the original input and produced artifact. The benchmark replay is a scoped P1 singleton-edge check, not a production P2 proof kernel. It checks sample identity, literal deletion equalities, reconstructs a forest with graph traversal, and validates per-negative separating witnesses; an incompatible root receives only a lower bound, not a completed optimum. No claim of a hardened arbitrary-untrusted proof grammar (e.g. strict bool-as-int and unknown-key rejection) is made. The test script rejects four selected mutations.

For synthetic core-test constructions (NOT recovered planted cases), create raw JSON with the following independent input generator:
```python
import json
from pathlib import Path
for ctx,name in [((),'reverse100k'),((99997,99998,99997,99999),'context100k')]:
    a=list(map(str,range(100000)))
    d={'alphabet':a,
       'positive':[[a[i] for i in ctx+(2*j,2*j+1)+ctx] for j in range(10000)],
       'negative':[[a[i] for i in ctx+(2*j+1,2*j)+ctx] for j in range(10000)]}
    Path(name+'.json').write_text(json.dumps(d,separators=(',',':'))+'\n')
```
Run sparse_bench.py on each with the same limits. The SHA-256 values in results/issue10-sparse.csv distinguish those synthetic cases from the recovered archives.

## Actual findings

See results/issue10-paired.csv for 9 paired original inputs and one additional targeted legacy run. All were on Linux-6.18.57-x86_64-with-glibc2.41, CPython 3.13.5 GCC 14.2.0, PYTHONHASHSEED=0, 512 MiB RLIMIT_AS, 5 s per stage plus 1 s subprocess allowance. One measured run per mode/fixture, not a statistical speedup. Legacy compute time excludes raw JSON parsing and output serialization; P1 compute includes JSON load and artifact writing, so stage wall time is the closest common metric. Producer/replay RSS are separate processes. Missing RSS on MemoryError is censored, not zero. All external attempts and bytes are zero; operational status INCOMPLETE.

- Legacy: four verified optima (HDFS and holdout cost 2; cover_path_8 cost 4; tiny_choice cost 2); three incomplete (scale, large_reverse_dense, small_count); two actual Python MemoryError events at staged.py line 23 allocating the dense singleton mask tuple. No proof from those failures.
- P1: five structurally verified optima (scale cost 986; both huge planted cases cost 10000; large_reverse_dense cost 9990; small_count cost 40); four lower-bound-only results (HDFS, holdout, cover_path_8, tiny_choice). This is not a full exact-search comparison. The two 100k-symbol original planted inputs produced 90k blocks, matching archived labels when compared **after** replay. Also post-run checked archived costs for large_reverse_dense, small_count and tiny_choice, consistent with verified results.
- Targeted legacy tiny_choice: 1 local query, 1 response, 237 compact JSON bytes; exact event/transcript match and legacy replay VERIFIED. Direct actual simulator test: NO 128 bytes, ACCEPT 93 bytes, then an interrupted attempt without response, exactly five event records. Forced tick raises real DeadlineExpired; this is a test injection, not a live external timeout. No mutation to committed legacy source. JSON proxy is not wire bytes. The existing decimal integer conversion limit can obstruct serialization of very large masks; not encountered in completed queried cases.
- Core tests (with tracemalloc) and reference smoke results are separate from the paired runs. Historical 30 s failure and enhanced historical timings remain historical. No comparison of external speed, no universal guarantee, no proof of completeness of P1.
- Remaining: run remaining 28 distinct planted inputs, controlled repetitions and 30 s budgets; enhanced archive measurements; full clean Git worktree CI; P2 shared schema integration and external transport. No merging.

This checkpoint partially satisfies issue #10; all original planted inputs are now recovered and hashable, and the exact reviewed Python core and exact legacy modules have executed. Do not treat the benchmark replay as the proof agent's production verifier.
