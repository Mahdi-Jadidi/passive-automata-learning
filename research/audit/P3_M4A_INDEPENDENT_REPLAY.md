# M4-A independent verification audit

The sparse evaluator is opt-in through `verify_frontier(..., sparse_exact=True)` or `--sparse-exact`. It indexes each positive's ordered, nonempty original-token projections and counts positive trace positions per touched atom. An untouched group separates a negative exactly when every positive touches that group. It uses the difference between universal-group counts to test this without iterating the declared alphabet per negative. Equal hash values select a bucket for budgeted exact tuple comparisons. Work, entry, projection and deadline caps are cooperative. Entry accounting bounds logical index and scratch entries; physical process memory depends on Python and the outer replay process limit.

The existing v1/v2 grammar, default literal evaluator, and expected format/mode binding stay in place. The offline rank prototype validates deletion equalities on whole quotient classes, derives restricted floors, and checks fractional capacities with exact arithmetic. Tests verify mandatory base cost, quotient support collisions, overlap and tie cutoffs against literal RGS. The triangle example obtains two from three half-weight rank-one rows. The [rank proposal](P3_M4A_RANK_COST_PROPOSAL.md) describes a future contract.

## Source and execution pins

| Item | Pin |
| --- | --- |
| Review and starting branch | `05eeab8cf2b17b770c1a96476b7598201e27ecc3` and `cea576889c5d9bd2fb846f2f883403be85b2033b` |
| Proof implementation commit | `5a10e649a91f8c5b159b818de7e71d4028b8170d` |
| Sparse verifier and rank prototype blobs | `d5a2047b9e8e0fbb461e597d979a0c72b4ad4651` and `3342aabdf98bac28d1e6e8034c83e14661038394` |
| Test source blob | `7eef63849f822a713320920646c3fe599d5457f0` |
| M3 retained raw/journal/scope and artifact source | `096fd14b684624d00c68071db7450f4c0b9c717f` |
| M4 producer source | `140b4e51f89baf8c3e38e18d704d8c4d36c24f39` |
| M4 engine and sparse evaluator blobs | `fc9ea03e0bd008d528bf115a5b5b8e7eb13ce2b8` and `9aa23be274907a9c178869670abf6bef982fed23` |

Local Windows tests passed 47/47 on Python 3.13.5 in both modes. The sparse census covers 57,826 owner/sample combinations over alphabets up to three, words of length at most two, and multisamples of size at most two. The large controls use 250,000 declared symbols with few active groups and a 40,000-token diverse trace. They also cover forced hash collisions and exact/work/index/deadline caps. Ubuntu CI passed 27/27 in each mode under a 1,536 MiB address-space cap, with 65,888 KiB normal and 67,756 KiB optimized peak RSS. [Exact CI job and logs](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45831290801/job/139948424470).

```powershell
py -3.13 -m unittest discover -s tests/reference -v
py -3.13 -O -m unittest discover -s tests/reference -v
```

## Retained M3 replay

The independent `p3_m3_artifact_replay.py --sparse-exact --seconds 120` gate replayed eight complete retained certificates in each interpreter. It checked the exact retained resume files, matched normal and resumed bytes against the optimized manifest, rejected modified partial proofs claiming exhaustion, and returned incomplete without a result for genuine partial proofs and one-byte caps. Each complete result matched a fresh literal RGS census. The 30-second trial reached 2,870,770 of 4,213,597 partitions on small/one and returned incomplete at the independent census. The 120-second run finished in both modes.

| Case | RGS partitions | Cost | All optima | One/all nodes |
| --- | ---: | ---: | ---: | ---: |
| tiny_choice | 203 | 2 | 4 | 10 / 10 |
| small_choice | 4,213,597 | 4 | 16 | 46 / 46 |
| mixed_path | 52 | 1 | 3 | 18 / 35 |
| journal_root | 203 | 2 | 2 | 4 / 4 |

## Native M4 replay

The core worktree's normal and optimized output directories supplied 32 case/mode/arm combinations each. The proof-only driver read original raw and journal bytes from the retained inputs, independently reconstructed the trusted scope, compared actual complete, partial and resumed bytes across the producer interpreters, and replayed each artifact type with strict v2/mode binding. Each proof process verified 32 complete and 32 resumed combinations, returned incomplete without a result on 32 genuine partial combinations, and checked all complete/resumed results against a fresh RGS census. The driver ran under both Python 3.13.5 interpreter modes and emitted identical rows. All four producer arms in each fixture/mode yielded identical complete certificate bytes in this experiment. The complete byte sizes and SHA-256 values also matched the actual producer logs. This is parity evidence for these inputs.

The [native replay pins](P3_M4A_NATIVE_PINS.jsonl) contain exact input and certificate hashes, checked results, and census counts. Reproduce the inputs from the normal retained evidence directory at the M3 pin. For producer output generation and artifact layout, use the core M4 workflow at the pinned producer commit. The proof process requires only the output byte directories.

```powershell
py -3.13 tests/reference/p3_m4_artifact_replay.py --inputs $inputs --normal $normal --optimized $optimized
py -3.13 -O tests/reference/p3_m4_artifact_replay.py --inputs $inputs --normal $normal --optimized $optimized
```

The separate large `medium_choice` one-mode sparse producer diagnostic reached its work cap and emitted a partial proof (SHA-256 `0829ead1cf7588cff50d67caf4d3dc92d028c3167bef18f7e42d9d2710ea399f`). Using the producer's raw fixture, empty journal and scope, the independent sparse verifier also returned incomplete without a result at its 15-second deadline, after 161 nodes normal and 198 optimized. Those counts are time-capped observations. The genuine nonempty journal fixture above is a small native control. The benchmark team's large RAW-to-journal pipeline and broader integration acceptance are separate gates.
