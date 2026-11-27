# Review 08 reproduction

Use Ubuntu 24.04, CPython 3.13.5 and GitHub read access. The pipeline and ablation configuration files list the exact checkout commits and staged Git blobs. Create fresh detached checkouts under the local names below. The Actions workflows record their checkout paths and commands in job logs. All runs use the seven frozen original raw bytes or the specified four-fixture subset.

```bash
python -B benchmarks/v2/review08_pipeline.py --case medium_choice --memory-mib 512 \
  --producer pipeline-core --verifier pipeline-proof --interface pipeline-interface \
  --output pipeline-evidence
python -B benchmarks/v2/review08_ablation.py --case medium_choice --memory-mib 512 \
  --producer ablation-core --verifier ablation-proof --output ablation-evidence
```

The pipeline executes the closure, ledger and scope for every variant. Fresh and checkpoint/resume routes have separate 30 s end-to-end deadlines. A phase receives the remaining wall allowance and cooperative phases receive at most 25 seconds. The wrapper may finish slightly beyond its deadline while killing a child or collecting telemetry. Such a run cannot count as verified. The address-space limit applies per child. End-to-end RSS is the maximum measured child RSS across sequential phases. Closure and ledger run in the same child, so their internal wall times are separate and their RSS is joint. Resume renews the producer's per-invocation work cap and stays within the route's shared deadline. A capped checkpoint can be replayed and resumed only if the independent verifier reports an unresolved proof.

The ablation uses three arms on the same producer revision. Compare dense and sparse to isolate compatibility, then sparse and sparse-join to isolate deletion discovery. Both independent replay implementations are run on each available proof. All arms use the frozen M3 raw cap profile and independently derived identity scope. Each stage receives the original 30 s wall cap and the configured cooperative and native caps. The CLI commands pass the raw input, independently derived scope and caps to the producer. They pass the original raw input and journal to the independent verifier. Neither stage receives reference answers.

```bash
repo=Mahdi-Jadidi/passive-automata-learning
for kind in pipeline ablation; do
  run=45832542233
  [[ "$kind" == ablation ]] && run=45831832220
  gh run download "$run" -R "$repo" -p "review08-$kind-*" -D "$kind-download"
  gh run view "$run" -R "$repo" --json databaseId,status,conclusion,headSha,url,jobs \
    --jq '{databaseId,status,conclusion,headSha,url,jobs:[.jobs[]|{databaseId,name,conclusion,url}]}' \
    > "$kind-ci.json"
  args=()
  [[ "$kind" == ablation ]] && args+=(--ablation)
  python -B benchmarks/v2/review08_export.py "$kind-download" "$kind-ci.json" \
    benchmarks/v2/results/review08 "${args[@]}"
done
```

The exporter checks each artifact's hash and length. The retained nonidentity scopes and their corresponding journals are compressed byte-for-byte. Decompress them and use the matching frozen raw input for standalone verification. Use the SHA-256 in each archive name to check the decompressed bytes.
