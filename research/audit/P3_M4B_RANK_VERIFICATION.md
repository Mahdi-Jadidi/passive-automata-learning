# M4-B independent frontier verification

Integration contract pinned to 727cec6560e825974bf3dc9eb2c170c9a349b749.
Proof baseline a563e1b54f5e3c57edcb7d74cde96259fc7d3fc1.

The v3 verifier binds an explicitly supplied format and mode. It reconstructs
each leaf's quotient from the checked path, validates the header incumbent
against the same scope, checks every ordered literal deletion, and applies
the exact capacity-weighted absolute rank floor. Structural entry and byte
counters span the entire proof. Configured replay caps and unresolved frontiers
return INCOMPLETE without a result.

## Independent synthetic evidence

The raw positive traces are [0] and [1] and the negative trace is [0,1].
All other alphabet symbols are unused. Literal RGS exhausts 5,292 partitions
over six alphabet sizes. Every case has optimum cost 1, with unique owner
[0,0,2,...,n-1]. One mode uses an equality cutoff at the root. All mode uses
two strict cutoffs below the root with base cost 1 and rank floor 2. The
all-mode output contains the unique owner in its optima list. The one-mode
output has an empty optima list as required by the wire.

The table compares synthetic COST-only and rank-substituted certificates in
the sparse verifier. Counts and work are verifier measurements.

| Alphabet | RGS | One nodes | One work | All nodes | All work |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | 5 | 5 -> 1 | 2440 -> 1932 | 5 -> 5 | 2538 -> 3278 |
| 4 | 15 | 8 -> 1 | 3106 -> 1958 | 20 -> 12 | 6224 -> 5013 |
| 5 | 52 | 12 -> 1 | 4016 -> 1984 | 61 -> 47 | 16323 -> 13660 |
| 6 | 203 | 17 -> 1 | 5213 -> 2010 | 149 -> 127 | 38841 -> 34164 |
| 7 | 877 | 23 -> 1 | 6695 -> 2036 | 311 -> 279 | 82667 -> 75319 |
| 8 | 4140 | 30 -> 1 | 8486 -> 2062 | 580 -> 536 | 158998 -> 148317 |

There are six synthetic equality closures and twelve synthetic strict
closures before counting repeated dense/sparse and interpreter replay.
Tests also cover whole-class deletion with multiple used symbols, original
residue order, stale representatives, bad trace IDs, overlap, exact ceiling,
repeated-row capacity, invalid rationals, oversized integer text, false
incumbent, false exhaustion, and cumulative limits. Cumulative structural
tests use lowered constants to exercise both crossing paths.

## Reproduce

Run both commands from the proof checkout.

    python -m unittest discover -s tests/reference
    python -O -m unittest discover -s tests/reference

## Native v3 gate

The proof-only replay is closed for the targeted matrix at producer pin
`579a6b3b860854b158a8d71f61855228f0c70873`, evidence tree
`e1e38bd8c0f876ba071f584c9030a094ff80275d`. Fresh producer processes ran
under Python 3.13.5 normal and optimized. Each reproduced the retained
manifest, nine input files and 40 certificates byte for byte. Separate
proof-only processes used strict expected format and mode and independently
replayed all 40 certificates in both interpreters. Complete and resumed
results matched literal RGS over 203 partitions per six-symbol fixture.
Fourteen checkpoints returned INCOMPLETE without a result. The equality/all
and strict/all v3 checkpoints each included one verified RANK_COST leaf,
and their resumes reproduced the respective retained complete bytes.

| Rank-bearing checkpoint | Bytes | SHA-256 |
| --- | ---: | --- |
| equality/all | 2631 | b779bb0bb886e08a977e2c508404e09e93873989d5906a5ca32f69d74c2d34d7 |
| strict/all | 2039 | 49ef39c46aa5f73eb51fd2779c54b7dab61ee7f338fead9e5a81b012f11535a8 |

[P3_M4B_NATIVE_REPLAY.jsonl](P3_M4B_NATIVE_REPLAY.jsonl) contains identical
normal/optimized replay records, including input and certificate SHA-256s,
Git blob hashes, closure counts and results. Its SHA-256 is
`562d4ffa2dd719d8008b939fac3dd9cbc61fe9c1fa61852acafaa38a660825ac`.

Set PYTHONPATH to the proof tests and producer implementation directories for
the producer commands only. Use a separate process from the proof checkout
for the two replay commands. RETAINED is the pinned producer checkout's
`implementation/partition_feedback_final/research/p3-m4/evidence/rank-targeted`.

    python PRODUCER/implementation/partition_feedback_final/research/p3-m4/run_rank.py --output NORMAL --case equality --case strict --case fractional
    python -O PRODUCER/implementation/partition_feedback_final/research/p3-m4/run_rank.py --output OPTIMIZED --case equality --case strict --case fractional
    python tests/reference/p3_rank_pin_replay.py RETAINED NORMAL OPTIMIZED
    python -O tests/reference/p3_rank_pin_replay.py RETAINED NORMAL OPTIMIZED

This replay covers the published targeted cases. Producer CI
[46016164222](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/46016164222)
covers the broader producer matrix and Linux process memory profiles.
See the [M5-A report](P3_M5A_AEFC_VERIFICATION.md) for the final full
reference regression and proof-only CI.
