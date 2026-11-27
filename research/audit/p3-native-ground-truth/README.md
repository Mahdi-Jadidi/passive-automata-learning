# Independent exhaustive ground truth for native tiny/small inputs
Core candidate pin af0559ad7b9590c1a335ba0801f5504f00b5cdea. This is oracle evidence, not a producer certificate or operational result. Raw bytes recovered verbatim from core research/p3-m2/inputs and verified by Git blob before running. No producer code or reference labels/costs used.
- tiny_choice raw Git ef3f41b4c5e27da6ffd4882804399abf454d51a7; SHA256 1c064aa4c7ce111ec8c403e8b6a05b64de5acdec2ef564861f06c2e2e2e42f23
- small_choice raw Git b361642873a73bae454d388cbfb2284559dbd69b; SHA256 10b0c3534ddf42369db003bca6b323c9fdaa33cd36aa15031360c3428949931b
- extended oracle Git 1b972edfb233cafd1a2473298f07d760787d7b36; SHA256 0ca70b3f24a60d7cfb2c11c8c50df7ccae1cfc5b04573bcf0c9ba1c461051ba6
- original RGS oracle unchanged, Git 375c36bfb2602894ce783055d1edf31f265aafa0.

For every nonempty subset B of original alphabet, precompute exactly the bit mask of negative trace IDs separated by B, using literal ordered original-ID projections and exact tuple equality. A partition is structurally compatible iff bitwise OR of its block masks covers all original negative IDs. Enumerate every RGS partition once, using mutable block masks; no pruning, no restriction of original alphabet. Retain all canonical owners at minimum n-|P|. Time/work/partition caps discard results. Work counter is projection-token debit plus per-leaf 1+number of blocks, not CPU instruction count; deadline checked at precomputation and every 1024 leaves plus final. Local process RLIMIT_AS 1536 MiB; observed RSS separate. The extension is oracle-only and does not authorize any additional producer pruning rule.

Commands (Python 3.13.5, with exact raw files copied into working directory):
    ulimit -v 1572864
    PYTHONPATH=tests/reference python -B tests/reference/p3_subset_rgs_oracle.py --self-test
    PYTHONPATH=tests/reference python -B -O tests/reference/p3_subset_rgs_oracle.py --self-test
    python -B tests/reference/p3_subset_rgs_oracle.py --raw tiny_choice.json
    python -B -O tests/reference/p3_subset_rgs_oracle.py --raw tiny_choice.json
    python -B tests/reference/p3_subset_rgs_oracle.py --raw small_choice.json
    python -B -O tests/reference/p3_subset_rgs_oracle.py --raw small_choice.json
Defaults: seconds 30, work 100000000, partitions 4213597; original alphabet cap 12. Both self-tests passed 227 literal-oracle parity cases and 3 cap cases. Normal/-O JSON byte-identical for each fixture.

| fixture | visited | optimum | optima | work | normal wall/RSS KiB | -O wall/RSS KiB |
|---|---:|---:|---:|---:|---|---|
| tiny_choice | 203 | 2 | 4 | 1834 | 0.78s / 96396 | 2.33s / 103932 |
| small_choice | 4213597 | 4 | 16 | 27763216 | 2.45s / 96392 | 4.26s / 103896 |

Result bytes (including trailing newline) are committed alongside this report:
- tiny-oracle.json Git 6650704d1f266b8cc297c7018404c9cf25db25c8; SHA256 44c34b1cfac966608dcb5cc4d50c8b755504957e627363e365695e51ab435207
- small-oracle.json Git d8cd79767b076d3a82c1f35362af19cb37a349c7; SHA256 171b62c61ecafe452de8051e5a6c5adf7a7e041fb021c97ced91f78920d6fb14

Both oracle results VERIFIED (literal structural optimization only). The separate native producer cross-replay workflow is pinned and launched; producer certificate acceptance requires actual independent replay. Operational INCOMPLETE. No learner, baseline, authoritative ledger changes or merge.
