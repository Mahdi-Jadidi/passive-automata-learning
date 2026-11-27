# Review 09 paired rank reproduction

Run on Ubuntu 24.04 with CPython 3.13.5. Use the exact producer and independent
verifier checkout commits and blob hashes in
`benchmarks/v2/p3/review09-rank.json`. The three targeted files are read from
the producer checkout's `rank-inputs` directory and matched to their RAW
SHA-256 pins. The workflow checks out only the RAW targeted inputs and
producer source from that repository. The seven original fixtures use their
existing RAW manifest hashes.

```bash
python -B benchmarks/v2/review09_rank.py --case strict --memory-mib 512 \
  --producer source-core --verifier source-proof --output strict-512
python -B benchmarks/v2/review09_rank.py --case medium_choice --memory-mib 1536 \
  --producer source-core --verifier source-proof --output medium-1536
```

Each arm receives the same identity scope from the same independently built
empty journal/2. This matches the original RAW-only ablation entry point.
The scope is independently rederived under the shared 30 s deadline on each
route before search. Both arms include the same cooperative 25 s ceiling,
producer and verifier work limits, 64 MiB frontier cap and default 64 MiB
sparse index limit. Both use sparse compatibility, with rank enabled only
for v3. The arm order alternates across matrix jobs. Restart uses a one-entry
checkpoint and independent partial replay, then the resumed search and final
independent replay with the remaining route wall allowance. The targeted RGS
oracle runs separately from the benchmark routes and supplies result checks
outside the producer invocation. Node differences are reported only for
pairs independently verified in both arms. Rank discovery overhead is the
producer's charged rank work and call count.

```bash
repo=Mahdi-Jadidi/passive-automata-learning
run=46016360030
gh run download "$run" -R "$repo" -p 'review09-rank-*' -D review09-rank-download
gh run view "$run" -R "$repo" --json databaseId,status,conclusion,headSha,url,jobs \
  --jq '{databaseId,status,conclusion,headSha,url,jobs:[.jobs[]|{databaseId,name,conclusion,url}]}' \
  > review09-rank-ci.json
python -B benchmarks/v2/review09_rank_export.py review09-rank-download \
  review09-rank-ci.json benchmarks/v2/results/review09
```
