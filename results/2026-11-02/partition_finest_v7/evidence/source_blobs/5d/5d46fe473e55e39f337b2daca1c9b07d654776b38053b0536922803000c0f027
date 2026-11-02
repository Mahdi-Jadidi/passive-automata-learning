# C007 adaptive-only scale correctness protocol v1

Date: 2026-11-02 (Asia/Tehran). These are five separate, deterministic
structured correctness cells. They are not a benchmark and do not authorize
timing comparisons. Every provider run is a fresh root-CLI process, adaptive
mode only, `--seconds 28`, capture hard deadline 30 seconds. Reference mode is
deliberately excluded at 16 blocks: enumerating 32,767 compatible cuts with
full witnesses can produce enormous output. Matched timing remains restricted
to moderate alphabets/block counts and requires master GO.

The solver-visible rows contain only a known alphabet and exact positive and
negative complete words. Hidden sidecars state the intended sample partition,
base positive word, and adjacent-swap negative positions. There is no `k`, DFA,
state count, generator architecture, or target partition in provider input.
These cases are structured finite-sample witnesses, not planted infinite-DFA
trials. No hidden-factor recovery score is computed.

For each cell, the positive set is the singleton `{w}`. Every negative is
formed by swapping one adjacent pair `xy` in `w`, where `x,y` are neighbors
inside one intended block. The intended partition is compatible: its local
projection of the swapped block differs from the only positive projection.
Every such pair is forced to co-own in any compatible partition: if a
partition separates `x` and `y`, each block projection of the negative equals
the corresponding projection of `w`, so no block rejects it. The path edges
connect each intended block, making it the unique finest sample partition.
The gate independently checks the exact edge derivation, component partition,
direct factor projections, final witness, and certificate. Incomplete cells
remain censored and make no finality claim.

Frozen cells:

| ID | Alphabet | Intended blocks | Context length | Shape |
|---|---:|---:|---:|---|
| scale_m64_equal8 | 64 | 8 × 8 | 64 | balanced |
| scale_m64_unequal8 | 64 | 2,3,4,5,6,7,8,29 | 64 | unequal |
| scale_m128_equal16 | 128 | 16 × 8 | 128 | balanced |
| scale_m256_unequal16 | 256 | 1..15,136 | 256 | strongly unequal |
| scale_m16_len65536 | 16 | 4 × 4 | 65,536 | long-context separate cell |

No censored cell is rerun without a new explicit source version and a reason.
