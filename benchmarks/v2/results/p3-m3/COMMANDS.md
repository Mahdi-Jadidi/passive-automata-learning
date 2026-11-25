# P3 M3 benchmark reproduction

Use Linux, CPython 3.13.5, Git, and repository read access. The [M2 commands](../p3-m2/COMMANDS.md) show how to prepare detached sparse worktrees. Check out this benchmark branch and prepare M2 producer `391abf97df3b67661082c907d9ce20b4f69636c2` and M2 verifier `d89bab4c005d17c8b27d4c1e6dd291135aca649a` as `m2-producer` and `m2-verifier`. The runner checks the source HEAD and exact Git blobs before staging source separately for each role.

## M2 restart audit

```bash
python -B benchmarks/v2/p3_m3_export.py benchmarks/v2/results/p3-m3
for fixture in small_choice hdfs_1024 hdfs_holdout_1024_uncapped cover_path_8 nonempty_root; do
  python -B benchmarks/v2/p3_m3.py --audit --case "$fixture" --memory-mib 1536 \
    --producer-root m2-producer --verifier-root m2-verifier \
    --output "evidence/p3-m3-evaluation-$fixture-1536"
done
```

The first command regenerates the 24 rows from the frozen M2 CSV. The runner independently replays each usable proof. The adjusted arms deduct the checkpoint's admission bytes and entries from the corresponding resume caps. The cumulative-work arm additionally deducts checkpoint work from the resume work cap. The separate journal case uses unadjusted standard limits.

To reproduce the CI export, use the actual run ID below. The exporter checks the manifest, artifact lengths and hashes, and the preserved checkpoint node and split prefixes in retained resume artifacts.

```bash
run=45634969027
repo=Mahdi-Jadidi/passive-automata-learning
gh run download "$run" -R "$repo" -p 'p3-m3-evaluation-*' -D evidence
gh run view "$run" -R "$repo" \
  --json databaseId,headSha,status,conclusion,jobs > audit-ci.json
python -B benchmarks/v2/p3_m3_export.py benchmarks/v2/results/p3-m3 \
  --kind audit --download evidence --ci audit-ci.json
```

## Controlled M2/M3 pairs

Build `benchmarks/v2/p3/m3-native.json` from the frozen `p3/native.json` after #2 and #3 publish their immutable source pins. Set both exact commit and blob maps and append the published producer opt-in flag(s). Check out the pinned M3 producer and verifier under `m3-producer` and `m3-verifier`, with only their source directories. The paired workflow uses the committed config to select the complete matrix and stages only the original fixture bytes and source files.

```bash
for fixture in tiny_choice small_choice medium_choice huge_choice_active hdfs_1024 \
    hdfs_holdout_1024_uncapped cover_path_8 nonempty_root; do
  for memory in 1536 512; do
    python -B benchmarks/v2/p3_m3.py --case "$fixture" --memory-mib "$memory" \
      --producer-root m2-producer --verifier-root m2-verifier \
      --m3-config benchmarks/v2/p3/m3-native.json \
      --m3-producer-root m3-producer --m3-verifier-root m3-verifier \
      --output "evidence/p3-m3-evaluation-$fixture-$memory"
  done
done
```

Use the paired run ID in the CI download and run-view commands and pass `--kind paired` to the exporter. Use a fresh evidence directory per run. The exporter writes standard and nonempty-journal data to separate files. Phase CSV provides coverage, counters, timings, peak RSS and proof sizes. JSON retains all native telemetry and exact command arrays, including any discovery metrics exposed by the producer. Missing telemetry stays empty. A cross-split count measures admitted splits. It cannot measure discovery attempts or rejected witnesses.

The arms share one CI runner per case/profile, with alternating order across fixture/profile pairs. Each arm gets independent fresh processes and independently rebuilt journal and scope, whose byte digests must match the other arm. Both run the full one/all, normal/-O matrix. Runtime includes CLI startup, parsing and serialization. Use the separate proof replay measurements for verifier cost. Work counters are native to each revision. Proof size reflects emitted search coverage as well as representation. Interpret byte or node ratios at equal verified coverage separately from ratios between partial frontiers. The v2 header and cross witness records carry wire overhead. No compressed or streaming proof format is involved.
