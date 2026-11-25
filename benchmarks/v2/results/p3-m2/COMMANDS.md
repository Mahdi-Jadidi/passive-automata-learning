# Reproduce P3 M2 benchmark measurements

Run on Linux with CPython 3.13.5 and Git. The measured benchmark tree was `b34cdba663af8d6b5892d1afb027a97bbc6aca7e`. The commands use detached, sparse checkouts to keep evaluation files out of the working trees. A checkout may require repository read access.

```bash
set -euo pipefail
repo=https://github.com/Mahdi-Jadidi/passive-automata-learning.git
prepare() {
  local directory=$1 commit=$2
  shift 2
  git init "$directory"
  git -C "$directory" remote add origin "$repo"
  git -C "$directory" fetch --filter=blob:none --depth=1 origin "$commit"
  git -C "$directory" sparse-checkout set --no-cone "$@"
  git -C "$directory" checkout --detach FETCH_HEAD
}
prepare bench b34cdba663af8d6b5892d1afb027a97bbc6aca7e \
  /benchmarks/v2/p3_harness.py /benchmarks/v2/test_p3_harness.py /benchmarks/v2/p3_native.py \
  /benchmarks/v2/p3/native.json /benchmarks/v2/p3/inputs/ /benchmarks/v2/review03/p3/input-manifest.json
prepare producer 391abf97df3b67661082c907d9ce20b4f69636c2 \
  '/implementation/partition_feedback_final/selector_v2/*.py'
prepare verifier d89bab4c005d17c8b27d4c1e6dd291135aca649a '/tests/reference/*.py'

(cd bench/benchmarks/v2 && python -B -m unittest -v test_p3_harness)
(cd bench/benchmarks/v2 && python -B -O -m unittest -v test_p3_harness)
for fixture in tiny_choice small_choice medium_choice hdfs_1024 \
    hdfs_holdout_1024_uncapped cover_path_8 huge_choice_active; do
  for memory in 1536 512; do
    python -B bench/benchmarks/v2/p3_native.py \
      --producer-root producer --verifier-root verifier \
      --case "$fixture" --memory-mib "$memory" --output "evidence/p3-m2-$fixture-$memory"
  done
done
```

The runner executes one/all, normal/-O, two fresh trials, and the one-entry checkpoint and resume in each case/profile. Each phase gets a fresh process. Use a fresh output path. Exact per-phase command arrays, command hashes, parent/child elapsed time, stream hashes, native metrics and certificate hashes are in `standard.json`. The independent verifier bundles no producer source. The native setup does independent scope replay in a third phase before any search.

On the report commit, download the Actions evidence and regenerate both standard files from the exact summaries. The exporter rechecks fixture hashes, scope and journal hashes, retained certificate hashes, and process stream hashes.

```bash
gh run download 45627999119 -R Mahdi-Jadidi/passive-automata-learning \
  -p 'p3-m2-*' -D evidence
python -B benchmarks/v2/p3_export.py evidence benchmarks/v2/results/p3-m2 \
  --actions-run 45627999119 --actions-head b34cdba663af8d6b5892d1afb027a97bbc6aca7e
```

Expanded small/all proof replay uses [a separate workflow](../../../../.github/workflows/p3-m2-expanded-replay.yml). It downloads the pinned producer artifact and validates the raw, journal, scope, and proof digests before independently replaying it and comparing the complete optimum set with the RGS oracle. The workflow specifies the exact commands, resource caps, and source pins. Download its per-mode verifier and oracle logs with:

```bash
gh run download 45628480530 -R Mahdi-Jadidi/passive-automata-learning \
  -p 'p3-expanded-small-all-*' -D expanded-replay
```
