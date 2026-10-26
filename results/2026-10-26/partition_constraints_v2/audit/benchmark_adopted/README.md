# Adopted serial benchmark harness

This directory contains the independently adapted BMARK-A001 runner and worker. The original candidate remains unchanged at `approaches/eager/benchmark_support/`; its recorded hashes are in `integration_record.json` after the smoke checks. This version uses the reviewed durable capture backend `B-CAPTURE-R1` from `audit/capture.py` and has not changed any frozen solver source.

## Scope and execution

The suite uses only the 100 frozen `performance_100` solver inputs. It checks the dataset and input hashes and all six C002-R1 runtime source hashes before, between, and after jobs. It never reads generator truth. The schedule contains 900 timing runs (100 cases × 3 methods × 3 fresh-process repetitions) and 300 separate memory runs (100 cases × 3 methods). No jobs run concurrently. Timing methods rotate through each ordinal position; every job and every skipped job gets a ledger row.

Each method has a shared 900-second budget across timing and memory. The ledger charges `capture.subprocess_seconds`, measured from the Popen launch attempt through direct-child completion or cleanup. Source snapshots, environment/manifest preparation, output hashing and final capture metadata are excluded. The runner rejects a missing, non-finite or negative clock instead of treating it as zero. It records capture backend and clock source with each executed job.

The capture timeout limits the post-launch `wait`; process creation is not preemptible, and timeout cleanup can add a terminate grace period before kill/reap. Consequently, 30 seconds is the requested wait cap, not a strict launch-to-reap wall ceiling. `subprocess_seconds` preserves the actual interval and any overrun; budgets are never rounded down. The capture controls only its direct child. If cleanup reports an unreaped child, or the capture clock is invalid, the runner stops and leaves the attempt and suite evidence for reconciliation. A raw interrupted status is authoritative and aborts the suite after preserving captured output.

After a cleanup failure, the suite lock is deliberately retained; verify the recorded child is no longer running before removing it. A zero runner exit means the planned schedule ended, not that all jobs were complete or scientifically accepted. Inspect `summary.json`, job status counts, and the independent output-validation verdict.

The worker invokes the unchanged `solver.py` through `runpy.run_path`, with the actual CLI arguments. `pipeline_seconds` starts after the tiny worker bootstrap and covers driver imports, input reading, preprocessing, search, JSON serialization, and flushing stdout/stderr to the capture files. It does not include Python interpreter startup or metrics-sidecar writing. It is a repeatable end-to-end pipeline measure, not pure search time. A timeout can leave no worker sidecar.

Memory mode starts `tracemalloc` before importing the driver and parsing input. It reports Python-tracked allocations, not process RSS or native allocations. The runner checks that the traced peak is a nonnegative integer. Memory-mode elapsed time is diagnostic and is never compared as speed.

## Results and limitations

The raw capture classifies nonzero exits generically. This runner keeps that evidence and separately interprets exit 3 as `incomplete` only when stdout, sidecar, method, mode, exit status and incomplete-result fields agree. It preserves the full raw JSON in the capture attempt. The harness does not certify F2 equality or witnesses; the independent saved-output validator must check every complete set and every partial set before performance comparisons are reported.

Paired timing summaries require all three complete timing repetitions for both methods on a case. Censored, incomplete, failed, and skipped jobs are never imputed as 30 seconds. Per-case medians are taken before distributions and ratios, and the completed-case denominator is retained. Missing counters remain missing. Eager preprocessing and lazy initial preprocessing/online separation phases have different scopes; those counters are reported separately. Results describe only this frozen corpus and do not establish general speedup or significance.

The capture backend's broad `duration_seconds` includes stream reading and result assembly before hashes and final result writing. It is retained only as capture overhead context; benchmark process time comes exclusively from `subprocess_seconds`.
