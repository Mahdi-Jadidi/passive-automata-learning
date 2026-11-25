# M3 independent proof audit

The verifier implements Review 07 on the proof branch starting at
`a3b04c3d822ea445b77adc2b30d8984d3f5819b5`. It uses the frozen v1 header,
scope, exact journal replay, cutoff and result grammar. v2 adds only the
checked cross split and its atomically committed conflict residual.

For each current class, the smaller original ID from each support determines
its least internal normalized cross pair. Comparing that pair to the first
excluded alternative detects an internal prefix disequality. The verifier
uses the complete original support arrays after descendant merges. It checks
every emitted edge against the indexed family, retains the symbolic suffix,
and enforces a direct cross-parent bind for the conflict residual. No
producer code enters the proof process.

## Exact verifier gate

[Branch-push CI job](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45635333668/job/139279132881)
ran at `f24d34c6e812b23c3dbe8953a6f592653b44958e`. The verifier Git blob was
`2f66ef48353ce3c240e359b797b72bea352b2fc9`, v2 tests
`b52efbbe9aa1c87c3c405fbe0ba5c07279455a16`, and the n≤12 oracle
`da28e66ca4ff74388be79bf9549c8e02f0c60410`.

```sh
ulimit -v 1572864
PYTHONPATH=tests/reference python -B -m unittest discover -s tests/reference -p 'test_p3_frontier*.py' -v
PYTHONPATH=tests/reference python -B -O -m unittest discover -s tests/reference -p 'test_p3_frontier*.py' -v
```

| CPython 3.13.5 | Tests | Wall (s) | Peak RSS (KiB) |
| --- | ---: | ---: | ---: |
| Normal | 19/19 | 3.97 | 32,528 |
| Optimized | 19/19 | 4.21 | 33,904 |

Each mode enumerated 42,368 RGS partitions across the specified configurations
through alphabet size eight and compared membership in 1,628 reconstructed
regions with explicit original-ID constraints. Both orderings of mixed
ancestor rules occurred. The seeded sweep compared 305,186 minima-prefix
decisions with literal cross prefixes. The 20,000-symbol case verified three
nodes and two exact deletion checks for a symbolic 100,000,000-alternative
split before returning INCOMPLETE (2,014,181 charged work units). A real
nonempty RAW journal event in a test fixture proves a nonidentity root and
the v2 path lifts the deletion to the entire merged class.

Native acceptance uses the separately published producer archive, exact
byte comparisons of normal, optimized, checkpoint and resumed proofs, and
an independent original-alphabet RGS census. One-mode output is checked
against membership in the full optimum set, and all-mode output is checked
for exact set equality. Operational status remains INCOMPLETE.

## Actual native replay

[Producer run 45636477920](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45636477920)
published the exact inputs and proofs at commit
`9a361f6fa59414cc0ac262154d87c37f5aed0403`. The independent runner authenticated
archive 15032494625 with SHA-256
`ab6f173251f58f8a9678aeca1702d9f46a56bc7447f95086d8b60dfa4cceed6a`.

[Proof-only run 45637001978](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45637001978)
passed 8/8 jobs, each with normal and optimized CPython 3.13.5. The replay
commit was `316d4430538b8a9ef0c707b8c46727a830d42321` and the verifier,
artifact runner and RGS blobs were `52e83aa9fdc952aacd7955e6d4ec1783e2fa4030`,
`8b1225295c1aad263e7003397cc0edc24b309259` and
`da28e66ca4ff74388be79bf9549c8e02f0c60410`. The same commit separately
passed the [19-test regression matrix](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45637001669)
in both runtime modes.

| Fixture | RGS partitions | Cost | Full optimum set size | Nodes one / all | Proof bytes one / all |
| --- | ---: | ---: | ---: | ---: | ---: |
| tiny_choice | 203 | 2 | 4 | 10 / 10 | 2,658 / 2,737 |
| small_choice | 4,213,597 | 4 | 16 | 46 / 46 | 12,693 / 13,244 |
| journal_root | 203 | 2 | 2 | 4 / 4 | 1,102 / 1,137 |
| mixed_path | 52 | 1 | 3 | 18 / 35 | 4,043 / 7,821 |

The byte-pinned journal replay derived `[0,0,2,3,4,5]` from a nonempty RAW
journal. In each runtime and case, the one-entry checkpoint returned
INCOMPLETE with no result, false EXHAUSTED returned INVALID, and a one-byte
proof limit returned INCOMPLETE. Normal and optimized proof results matched
byte for byte. Each mode used a 60 s verifier and oracle deadline, a 64 MiB
proof byte cap and a 1,536 MiB process address-space cap. The slowest
end-to-end replay took 6.83 s, including the RGS census. Peak RSS across
the proof jobs was 21,824 KiB. The downloadable job artifacts hold exact
SHA-256 and Git blob fingerprints, all optimum owners, resource counters
and individual dispositions.

## Completed resume

The published archive retained the one-entry partial proofs and fresh
certificates. To obtain the separate resumed bytes, the audit ran the
producer's native CLI at the same source pin in a separate process, once
per case and mode under normal and optimized CPython 3.13.5. Each producer
process consumed the exact archived raw input, trusted scope and partial
checkpoint for its runtime. The proof replay process received the resumed
file as data with the producer checkout absent from its import path.

```sh
# Run in the producer checkout with its package on PYTHONPATH.
python -B -m selector_v2.edr_m3 --split-rule CROSS_SUPPORT_LEX_V1 \
  --raw "$raw" --scope "$scope" --mode "$mode" --resume "$checkpoint" \
  --out "$resumed" --seconds 30
# Run in the proof checkout with the producer removed from PYTHONPATH.
python -B tests/reference/p3_m3_artifact_replay.py \
  --case "$case" --mode "$mode" --raw "$raw" --journal "$journal" --scope "$scope" \
  --normal "$fresh_normal" --optimized "$fresh_optimized" \
  --checkpoint "$checkpoint" --resumed "$resumed" --seconds 60
```

The optimized pass adds `-O` after `-B` to both invocations. All sixteen
resumed outputs matched the corresponding published fresh certificate
byte for byte. This tests eventual completion with a renewed invocation
budget following a one-entry checkpoint. The independent replay also
matched the full RGS results and rechecked the partial, false-exhaustion
and file-cap controls. The eight paired normal and optimized replay reports
were byte-identical. [Exact checkpoint and resumed byte pins](p3-m3-resume-evidence.json)
