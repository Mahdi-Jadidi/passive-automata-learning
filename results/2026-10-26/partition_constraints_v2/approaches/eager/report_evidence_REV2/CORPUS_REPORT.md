# Frozen C002 audit corpus

The sample-only corpus `corpus/frozen_v1/` was generated before solver runs and
then independently validated. Its manifest SHA-256 is
`a4ef5c7124b9852cb30c5eb8e86f6e8bd1fa53bf3d4e9ab5d89d70f9b48efd13`.
The corpus validator attempt is `20261026T094108.315995Z_eb0687d525` (exit 0);
the complete raw result, exact command, source snapshots, and environment are in
that attempt directory.

| Dataset | Cases | SHA-256 |
|---|---:|---|
| Previous exhaustive binary samples | 2,187 | `3fefe218a668d65309dbd71dc95ade9a2dd7d7ecb12cc48ed24860d25628a883` |
| Previous exhaustive `abc`, length at most 1 | 81 | `d2773eedcad2f534594810b7c843ff8693e20034608d37819c7d61b40d4af227` |
| Previous theory examples | 4 | `788798e24bc5f7a3b3797098c93456a3db98cea8a7f714ed450c7cc10cba87bc` |
| Targeted swap, rescue, infeasible, and empty-class controls | 9 | `6fc157213d22e966466abe61f5c601733b22df47f846bb3561fa96d463eaf881` |
| Random ternary `abc`, words of length at most 2 | 5,000 | `599f89ad50b512a9588c714f790916df30da2fb29fd89b8427151cb91779222e` |
| Finite product generators, 20 for each alphabet size 4–10 | 140 | `fda7ac29653c2e4903437983a3cd249fcabf364b063976b4ea83ed4c973a04cb` |
| Performance inputs, 25 each at alphabet sizes 4, 6, 8, and 10 | 100 | `509928210c1075d502d7244f0c5a8f5f75d0b65b33298ddbe288995e0ef5ce20` |

The 5,000 ternary cases are unique and sampled with seed `20261026`; each of
the 13 words independently receives absent, positive, or negative status with
equal probability. The sample was not balanced after generation: 4,962 cases
have both classes, 25 have positives only, 13 have negatives only, and none are
unlabeled. The per-word status counts and class-size histograms are in the
manifest.

The finite generator and performance inputs use seeds `20261027` and
`20261028`. Each local factor is a nonempty random finite language over words
of length at most 2. Samples contain up to 32 positives and 32 negatives,
drawn from global words of length at most 4 that touch both true blocks. Hidden
partitions and local languages are stored in separate hash-listed truth
sidecars; only the `input` object in each solver-input record is passed to a
solver. Independent validation confirmed every sampled label against its
generator, class caps, word bounds, group counts, unique input hashes, and all
file and per-case hashes.

An initial corpus-validator attempt,
`20261026T094021.088946Z_433e28e28a`, failed because the validator expected
ordinary lexicographic ordering for local factor words while the documented
generator ordering is length then lexicographic. The corpus is unchanged; the
corrected verifier passed and its distinct source snapshot is recorded in the
successful validation attempt.
