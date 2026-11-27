# V2 benchmark checkpoint

This is a benchmark-only workstream for issue #4. Nothing here implements or changes the external learner/evaluator. The default reference engine is the pinned audit.py literal compatibility predicate and partition-enumeration algorithm, with a small reporting wrapper. Its independent replay uses restricted growth strings and per-block projected positive sets. The reference is deliberately capped at nine symbols; it is not the production selector. The legacy engine is an adapter for the unchanged pinned staged.py / verify.py.

## Run on Linux (Python 3.10+)

From repository root on the benchmark branch:

```sh
python -B -m unittest discover -s benchmarks/v2 -p 'test_harness.py' -v
python -B benchmarks/v2/smoke.py /tmp/v2-smoke-new
git worktree add --detach /tmp/partition-legacy 7c90eb59561bd25ec4fdca5ac08b0e5d60d17fd6
python -B benchmarks/v2/harness.py /tmp/v2-smoke-new/inputs/order.json /tmp/v2-legacy-order \
  --engine legacy --repo /tmp/partition-legacy --seconds 5 --memory 512
```

Output directories must not exist. The pinned checkout must have the exact HEAD and clean module directory; benchmark outputs go elsewhere. Use separate producer/replay subprocesses. Do not run legacy on the integration worktree. `--seconds` is the legacy internal deadline and hard subprocess deadline minus one second of startup allowance. For reference, only the outer hard deadline is enforced. The timeout smoke uses a microscopic budget and may require a larger adversarial input on a very fast host. No claim of a hard RSS limit: `--memory` uses RLIMIT_AS (virtual address space, MiB), while measured Linux ru_maxrss is KiB. Worker runtime excludes JSON input parsing and output serialization; wall time includes subprocess startup and transfer. Parent input parsing and output capture are outside the worker cap. Run multiple repetitions on the same host with explicit budgets before comparing speed. The one-second allowance is a harness choice, not a paper requirement.

For raw inputs already in the pinned checkout:

```sh
python -B benchmarks/v2/harness.py /tmp/partition-legacy/implementation/partition_feedback_final/evidence/synthetic_10000_traces_1000_symbols.json /tmp/v2-legacy-scale30 \
  --engine legacy --repo /tmp/partition-legacy --seconds 30 --memory 1536
```

For a bundled legacy fixture, extract input and reference into distinct directories **before** running a solver, e.g.:

```sh
mkdir -p /tmp/v2-input-only /tmp/v2-reference-only
python - <<'PY'
import hashlib, json, pathlib
source = pathlib.Path('/tmp/partition-legacy/implementation/partition_feedback_final/evidence/hdfs_1024.json')
raw = source.read_bytes()
bundle = json.loads(raw)
print('source SHA-256', hashlib.sha256(raw).hexdigest())
data = bundle.pop('input')
assert set(data) == {'alphabet', 'positive', 'negative'}
path = pathlib.Path('/tmp/v2-input-only/hdfs_1024.json')
path.write_text(json.dumps(data, separators=(',', ':'))+'\n')
pathlib.Path('/tmp/v2-reference-only/hdfs_1024.json').write_text(json.dumps(bundle)+'\n')
print('input SHA-256', hashlib.sha256(path.read_bytes()).hexdigest())
PY
python -B benchmarks/v2/harness.py /tmp/v2-input-only/hdfs_1024.json /tmp/v2-legacy-hdfs5 \
  --engine legacy --repo /tmp/partition-legacy --seconds 5 --memory 1536
```

Repeat for holdout and cover path, then 30 seconds with a fresh output directory. For hdfs_cases.json extract one named input at a time, not the whole mapping. Never pass a bundle or reference directory as selector input. See INVENTORY.md for the pinned blob IDs and missing archive caveats.

## Output semantics

Each run writes input snapshot SHA-256, producer artifact, stdout/stderr, event stream and summary.json. It records producer/verifier outcomes separately, stage wall/compute time and peak RSS (if the worker returned telemetry), input cardinalities, budgets, host, proof/result artifact bytes, observed local query attempts/distinct candidates/response counts, compact JSON response byte proxy (not wire), and external attempt/response counters (zero: no external service connected). Runtime instrumentation wraps only the local simulator in the worker and does not modify committed baseline code. Event append and serialization add overhead. A raw shortcut can issue zero local queries. If a stage is killed, report censored telemetry, not guessed measurements. MEMORY_ERROR means a Python MemoryError was observed; other nonzero exits remain PROCESS_ERROR, not inferred OOM.

Only verified finite optimum receives equal structural bounds and gap zero. Infeasibility has no finite gap; incomplete/no proof receives null bounds, since the legacy timeout output discards them. This intentionally conservative schema does not yet recover partial bounds or checkpoint frontier. Reference replay is exhaustive, not a production proof schema. No external operational ACCEPT or deployment is claimed. External status is INCOMPLETE throughout these runs.

## Actual checkpoint measurements

See results/reference-smoke.csv: 8 completed reference cases (6 finite OPTIMAL, 2 INFEASIBLE), all independently VERIFIED; one censored TIMEOUT; no external or local simulator queries. Input hashes are measured, not derived from expected answers. The order and triple inputs match pinned rank_order/rank_triple. The path4 is a smaller path construction, not the pinned path8. Four unit tests passed: 250 seeded random corpora plus 8 targeted, Bell counts n=0..8, isolation rejection, corrupted partition rejection. No legacy full-solver run or full planted experiment has been executed in this runtime: GitHub connector read/write works, but network DNS prevents a local checkout. Thus no timings or replay outcomes are claimed for those runs. Historical observations remain in INVENTORY.md. No v2 core implementation comparison yet.

Host: Linux-6.18.57-x86_64-with-glibc2.41, CPython 3.13.5 (GCC 14.2.0), PYTHONHASHSEED=0; 512 MiB RLIMIT_AS, 5 s per stage (6 s hard wall) except timeout (0.000001 s plus startup allowance). One run per fixture. The unusually high ~96,650 KiB RSS and ~0.8–1.1 s worker wall times reflect this runtime; do not extrapolate or claim scale performance. Reference compute times are sub-millisecond except path4, which enumerated 4,140 partitions. For all completed cases the verifier process returned VERIFIED; timeout verifier NOT_RUN, RSS unknown and artifact '{}' (2 bytes, not a proof). All external response bytes/attempts and local simulator response bytes/attempts are 0.

## Review05 continuation (2026-11-25)

See [REVIEW05_HARDENED_RECOVERY.md](REVIEW05_HARDENED_RECOVERY.md), [P3_BENCHMARK_PROTOCOL.md](P3_BENCHMARK_PROTOCOL.md), [p3/README.md](p3/README.md), and [review05/p2-raw-closure-results.json](review05/p2-raw-closure-results.json). The seven P3 input-only fixtures are recovered; evaluation references remain in a separate Library archive. The benchmark harness has 9/9 mock-adapter tests passing in normal and optimized modes. These tests validate the harness only, not EDR-BB.

P2 raw closure has been measured with the pinned core source. Ledger ingestion and complete independent replay of the original journal/2 artifacts remain NOT RUN until the two original journal files are supplied. The 512 MiB huge_long_active MEMORY_ERROR applies only to the raw-closure phase, not the hardened verifier.

## Next gate

Obtain the original review03-benchmark-evidence.zip bytes (or the two exact journal/2 JSON artifacts), then run the hardened bounded-deletion verifier and independent journal replay separately in normal/optimized modes. In parallel, wait for Agent #2 and Agent #3 to freeze the same P3 producer/frontier and independent verifier contracts; only then configure and run integrated P3 benchmarks. Preserve evaluation references outside solver input. Do not merge this checkpoint until review.
