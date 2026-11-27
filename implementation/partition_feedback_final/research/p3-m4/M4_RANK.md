# Review09 M4-B experimental rank producer

Run the producer with `--sparse --rank` to emit `p3-region-frontier/v3`.
With rank disabled, M4 retains v2 output. Join requires `--join`. On resume,
repeat the original mode, sparse, rank, join, split rule, and local discovery
settings. The frozen header binds scope, mode, and v2/v3 format. The invocation
supplies the other settings.

Discovery greedily minimizes literal deletion supports against positives in raw
order, then selects disjoint supports for each negative. It tries both a
unit-weight disjoint family and a fractional family whose row denominator is
the maximum incidence of its atoms. The producer charges trace scans and
bounded exact rational operations to the shared search budget. It recomputes
atom loads and rounds the weighted rank up before adding the mandatory cost
once. It emits a closure only after the exact mode cutoff. Discovery is
bounded and a miss leaves the existing split logic in control. If a witness
would exceed the cumulative wire limits, the producer skips that witness.
Configured work, time, or frontier-payload exhaustion leaves an open frontier.
Retained rank payload bytes count toward the frontier cap on resume.

`rank-inputs/` contains the three raw-only fixtures. `evidence/rank-targeted/`
contains exact raw, journal, scope and certificate bytes, with SHA-256 and sizes
for all certificate variants in its manifest. The fixture journals are empty
journal/2 envelopes tied to the raw samples. Python 3.13.5 and the independent
verifier at `98e913a7e15d32638319832fc69edb36edb2f505` replay complete,
partial and resumed artifacts. The independent literal RGS oracle checks
optimum cost and all-mode membership on those six-symbol fixtures.

| Witness | Mode | Rank leaves | Complete SHA-256 |
| --- | --- | ---: | --- |
| equality | one | 1 | 9e2134d3468246b4719b2cdbad9d5f5649a65cffc4c76f37177432b0cd0cc392 |
| strict | all | 14 | ab6b1e423ef12a55efed314cd0257ad2ea861421f963a7b3bae6e7557bf7f212 |
| fractional | one | 1 | dd1a255a8b41d5ded01497bcf6a48c6336051197f5e393de9523852df126b6dc |

`run_rank.py` generates the artifacts. The native CI gate selects 512 MiB and
1536 MiB address-space limits and compares normal and optimized output bytes.
The 16-symbol cover case is checked by independent certificate replay and
rank-off/on parity. RGS is used through 12 symbols.
