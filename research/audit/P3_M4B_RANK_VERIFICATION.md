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

For native replay, provide producer inputs under INPUTS/CASE as raw.json,
journal.json and trusted.json. Each producer runtime directory must contain
CASE/MODE/ARM/{complete,partial,resumed}.json with arms sparse and rank.
Use --case repeatedly for additional fixtures or a different case list.

    python tests/reference/p3_m4_artifact_replay.py --rank --inputs INPUTS --normal NORMAL --optimized OPTIMIZED
    python -O tests/reference/p3_m4_artifact_replay.py --rank --inputs INPUTS --normal NORMAL --optimized OPTIMIZED

The runner compares producer interpreter bytes and completed resume
fingerprints, checks each replay against literal RGS, requires complete
rank closures in both modes, and reports closure counts, proof fingerprints,
exact results and replay work. Agent #2's published branch was still at
f97dba1ecfc83ff4ed3452c26e949b262c87733a when checked for this milestone.
Native v3 certificates, producer pruning measurements and producer checkpoint
evidence remain pending.
