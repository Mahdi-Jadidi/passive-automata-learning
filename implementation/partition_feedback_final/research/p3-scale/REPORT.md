# Review09 large-alphabet scale experiment

## Source pins

| Input | Commit | Blob where applicable |
| --- | --- | --- |
| Review09 assignment | `727cec6560e825974bf3dc9eb2c170c9a349b749` | `bb03cfaecfcfaa7202e00234d60b6067a7631e7d` |
| SDJ-IDA, §7.1–7.3 | `727cec6560e825974bf3dc9eb2c170c9a349b749` | `a3cb9ac47b52fa9b3b35b5c0cad19c3602b564c5` |
| Worktree base and M4 core report | `f97dba1ecfc83ff4ed3452c26e949b262c87733a` | `0c26091fc9cbe67bbec2b39e6cc0c08996ab8df6` |
| M4 evaluator used for the baselines | `140b4e51f89baf8c3e38e18d704d8c4d36c24f39` | `9aa23be274907a9c178869670abf6bef982fed23` |
| Review08 ablation CSV | `4e89007654ef0ca4ceaed255199ab046577e9bb1` | `c473736237a57c156c46b04fd0c3a521754d4582` |
| Review08 raw fixtures | `8484b8bff5b93e1be3a7924697161efc34e481d8` | Fixture SHA-256 values in [profile_scale.py](profile_scale.py) and the raw CI rows |
| Scale implementation and tests | `260a0a9322e2cd043ff00c5fe61813f18d8f6d6d` | Compact `5ffb3309ce98edf6b02feb715a74452ed0faca6e`, targeted `8ec8bf5c9513767af7356da649b8b2eeb4bf7428` |
| Successful CI checkout | `1c2a4838d6251aa511d6727f2b40833f27efc0b2` | Ubuntu 24.04 with CPython 3.13.5 |

## Results

Each CI row is a fresh process with a 64 MiB logical index cap, 10 million
charged work units and a 25 second cooperative budget. Linux profiles use
`RLIMIT_AS` at 512 or 1536 MiB. Peak RSS covers the whole process including
fixture loading. Logical index charges estimate evaluator allocations.
Ranges cover the four memory/interpreter combinations with one run each.

| 100,000-symbol raw singleton root | Outcome | Peak logical bytes | Peak RSS KiB | Root work | Root seconds |
| --- | --- | ---: | ---: | ---: | ---: |
| Frozen M4 sparse | Index cap, compatibility unresolved | 67,108,800 | 75,776–79,392 | 477,452 | 0.151–0.226 |
| Compact | Incompatible, first failed negative N0 | 12,590,688 | 56,352–60,364 | 600,014 | 0.077–0.123 |

Each huge profile used the same 10,000 positives and 10,000 negatives.
A second check with the compact index on the same owner used 200,014 work
and took 0.057–0.092 seconds. The singleton index was built once per process.
Merged owners still scan the positives and build their ordered merged-block
projections. The exhaustive three-symbol control covers their semantics.
The huge timing compares a completed check to a censored baseline.

| Raw root | First exact failed negative | Join work and seconds | Targeted work and seconds | Witnesses from either |
| --- | --- | --- | --- | --- |
| HDFS | N6 | 150,401 / 0.139–0.214 | 35,645 / 0.017–0.026 | 0 |
| HDFS holdout | N5 | 146,963 / 0.138–0.210 | 29,519 / 0.014–0.022 | 0 |

Both HDFS discovery arms receive the same root and precheck. The discovery
columns time only the optional pass, with the same 250,000-unit local limit.
Each miss went through frozen literal discovery, which used 4,096 units and
also missed in every row. The literal-only arm therefore used less discovery
work than either optional pass. Review08's roughly 6.4–6.8 million
charged HDFS join units were cumulative across incomplete searches. These
measurements cover individual root phases and provide no estimate of total
search time, search coverage, or time to an optimum.

## Exactness and Agent #2 API

A singleton ordered projection is determined by its original ID and count.
Each positive occurrence contributes to the per-token presence count even
when the same trace appears twice. A nonempty merged projection retains
literal original IDs in order. Its first ID determines its unique block
under the current owner, so a single set suffices for all merged blocks.
Epsilon has positive support exactly when the block is absent from at least
one positive occurrence. An untouched universal block therefore rejects
epsilon. The evaluator returns the first negative whose projection matches
some positive on every block. Python set membership uses literal equality
on both singleton count keys and merged projections.

For singleton deletion, the first unmatched position after a common raw
prefix requires deletion of one of the differing tokens' groups. If one
word is a prefix, the first remaining token's group is required. This
produces up to two candidates per positive. Compare the two complete
complements as streams of original tokens. Cached pair/token facts are
scoped to the immutable sample in one search. Lift the token to its current
group and perform the same exact comparison before using it. A disjoint
pair for the same failed negative emits the existing cross-support dict.
The default cache holds up to 256 pair/token facts.

Use an explicit opt-in evaluator selection at search setup. Keep one
instance of each helper for the current immutable sample and search scope.

```python
projections = CompactProjections(sample, index_bytes=index_bytes)
targeted = TargetedDiscovery(sample, work_limit=join_work)
checked = projections.check(owner, budget, counters)
if not checked.compatible:
    witness = targeted.discover(checked, budget, counters)
    # Feed the existing cross-support or all-pairs path.
```

Pass the same checked canonical owner from compatibility to discovery.
The ordinary compatibility path remains the default. A targeted miss or
local cap invokes frozen literal discovery with its size-two support
checks. A further miss passes through the caller's existing all-pairs
fallback. Global caps propagate to the caller's existing cap handling.
An index cap means the compact check is unresolved. Diagnostics and cached
facts are producer-local. Independent replay can use the existing literal
certificate checks.

Cache history can change probe order, witness choice and work at a cap.
Checkpoint continuation and certificate-byte parity across resume were
outside this isolated experiment. Keep targeted discovery opt-in and gate
any checkpoint integration on completed-resume tests. A prototype requiring
history-independent witness order can set `fact_limit=0` and measure the
change separately. The experiment adds zero pruning rules and emits no
certificates of its own.

## Reproduction and CI

```sh
export PYTHONPATH=implementation/partition_feedback_final
SCALE=$PYTHONPATH/research/p3-scale
FIXTURES=/path/to/fixture-checkout/benchmarks/v2/p3/inputs
python -B -m unittest discover -s "$SCALE" -v
python -B "$SCALE/profile_scale.py" "$FIXTURES/huge_choice_active.json" compact --memory-mib 512
python -B "$SCALE/profile_scale.py" "$FIXTURES/hdfs_1024.json" target --memory-mib 1536
```

The workflow executes the full matrix including `-O`, baseline `sparse` on
huge, and `literal`, `join`, and `target` on both HDFS fixtures.
Five tests in each job cover literal parity across all partitions on the
three-symbol control, repeated token IDs, duplicate rows, epsilon,
empty classes and alphabet, merged roots, fact reuse, sample scope,
forced baseline signature collisions, local caps and fallback, and global
work and index caps. The four jobs passed
(`140561307582`, `140561307868`, `140561307979`, `140561308033`).
All 32 phase rows are retained in [ci-profiles.json](ci-profiles.json).
[Successful CI run and artifacts](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/46015457873)

The first run stopped in Python setup because Ubuntu 26.04 did not provide
the historical CPython patch release. The retry pinned Ubuntu 24.04 and
kept the original Python and experiment source.
[Initial CI run](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/46015257806)
