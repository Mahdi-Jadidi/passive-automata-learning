# M2 strengthened frontier CI and actual raw-only RGS reference

## Strengthened verifier CI

Proof checkout e4ab7014933be07ff876868ef91c034d6d7659d0, run 45592083930 / job 139128588440. Git blobs from actual logs: verifier 540a7cf9e7b048684d3ea03def744175ae629b65, test 03f1a1f0bf4fe2026a5b23806d14d586e7128592, RGS 375c36bfb2602894ce783055d1edf31f265aafa0, bounded deletion e1fc61b6f03484d4428642ca157e2dac43f0572d, journal replay 6c49013e809b5ac4d2b2a37850e6e6cece513072. Ubuntu 24.04, Python 3.13.5. Commands and RLIMIT_AS identical to P3_M2_CI_REPLAY_01.md.

Normal: 12/12, 0.762s suite, 0.85s wall, 28464 KiB RSS. Optimized: 12/12, 0.981s suite, 1.23s wall, 29752 KiB RSS. Both modes:
    n 6 mode one RGS 203 nodes 17 work 5274 exact 9
    n 6 mode all RGS 203 nodes 138 work 36586 exact 91
    n 7 mode one RGS 877 nodes 23 work 6766 exact 10
    n 7 mode all RGS 877 nodes 295 work 79443 exact 147
    n 8 mode one RGS 4140 nodes 30 work 8567 exact 11
    n 8 mode all RGS 4140 nodes 558 work 154635 exact 223
    symbolic alternatives: 199990000 work: 717036
    certificate mutations: 17
    literal fixture cases: 179
    Bell counts 0..8; independent label enumeration 0..5; region membership checks: 7065
    pair_at comparisons: 43680

The new tests traverse every partition at n=6,7,8 for one two-tie fixture per n; both proof modes compared. Scope/proof byte parse work charged; duplicate raw/scope keys and padded proof work cap tested. No producer certificate claim from these tests.

## Extended RGS reference for small_choice

Existing n<=8 oracle unchanged. New tests/reference/p3_rgs12_oracle.py blob da28e66ca4ff74388be79bf9549c8e02f0c60410 was tested locally (Python 3.13.5) before upload; local Git hash-object equals created Git blob. It traverses every RGS partition of all original symbols (no partition pruning), using an independently computed table of per-block literal projection witnesses over original-ID subsets (at most 4096 entries). It never reads planted answers or producer/verifier internals. Time/work/partition/entry caps fail closed; external RLIMIT_AS 1536 MiB, observed RSS separately.

Synthetic 12-symbol two-tie check: 4213597 partitions, optimum 1, two optima, 23242754 work units; normal wall 4.90 s RSS 96392 KiB, optimized 6.42 s RSS 103788 KiB. Additional local normal-mode cross-check against independent literal projection RGS recurrence on 45 fixed-seed (9043) fixtures n=0..8, 26480 partitions, all matched. Four caps (seconds/work/partitions/entries) INCOMPLETE/no result; duplicate JSON keys INVALID. Local interpreter normal/-O actual benchmark raw results below identical byte-for-byte.

Actual raw bytes retrieved from Agent #2 core pin 32fe278daf74dde6f798acf5545e8a8e9cde7cf2, under implementation/partition_feedback_final/research/p3-m2/inputs/. Local git hash-object verified against the remote blob; no trailing newline normalization:
- tiny_choice raw Git ef3f41b4c5e27da6ffd4882804399abf454d51a7, SHA-256 1c064aa4c7ce111ec8c403e8b6a05b64de5acdec2ef564861f06c2e2e2e42f23.
- small_choice raw Git b361642873a73bae454d388cbfb2284559dbd69b, SHA-256 10b0c3534ddf42369db003bca6b323c9fdaa33cd36aa15031360c3428949931b.

Reproduce with the exact raw files and committed extended reference:
    ulimit -v 1572864
    /usr/bin/time -f 'wall=%e RSS_KiB=%M' python -B tests/reference/p3_rgs12_oracle.py --raw RAW.json
    /usr/bin/time -f 'wall=%e RSS_KiB=%M' python -B -O tests/reference/p3_rgs12_oracle.py --raw RAW.json

| Case | RGS partitions | Optimum | All optima count | Work | Normal wall/RSS KiB | -O wall/RSS KiB |
|---|---:|---:|---:|---:|---:|---:|
| tiny_choice | 203 | 2 | 4 | 2140 | 0.89 / 96140 | 2.01 / 103876 |
| small_choice | 4213597 | 4 | 16 | 28579558 | 5.59 / 96344 | 6.66 / 103980 |

Exact normal/-O identical outputs in research/audit/p3-m2-reference/:
- tiny_choice.oracle.json Git 9fa9d9556ac5db13261144c8e844b5c2c7f7398d SHA-256 da51071c414680ca70eead10ad59a1c1308a5e61a7840e7a5cd73810205aa9d1.
- small_choice.oracle.json Git 67fac862c8b4eb9f85ef0194d71b7604018958d9 SHA-256 cafb16b15a522154ef9aa80175107e5602f1fd78aafbefbebc44baa5bc280c83.

These are VERIFIED raw structural exhaustive reference answers, not producer certificate verification. Do not feed reference answers to the producer; only compare after generation. Actual producer certificates from #2 not yet delivered at observation; independent native workflow by concurrent proof session at 4e2220f49baacc4784b3150112c1c50989a7c265 is a separate execution, on earlier core pin af0559a, not the latest 32fe278. No integration acceptance yet. No external learner/baseline/ledger modifications, no external learner calls, no merges.
