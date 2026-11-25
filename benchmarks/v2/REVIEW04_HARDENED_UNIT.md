# Review 04 — hardened bounded-deletion isolated validation

**Date:** 2026-11-25  
**Branch:** `research/v2-benchmarks`  
**Parent branch head:** `52d21e672b0ae6420cf677ff09c01bb2a3fd6b05`  
**Proof source head:** `cf5a007571853b6cdf6259fa2a9a95f5c1e351f8`

## Disposition

- Exact hardened bounded-deletion unit suite: **PASS**, 6/6 normal and 6/6 optimized.
- Actual `huge_choice_active` / `huge_long_active` raw closure: **NOT RUN — ORIGINAL INPUT BYTES UNAVAILABLE**.
- Actual journal/2 outer replay: **NOT RUN — ORIGINAL JOURNAL BYTES UNAVAILABLE**.
- 512 MiB large-case trials: **NOT RUN**. No new 512 MiB failure or result is inferred.
- No VERIFIED/INVALID/INCOMPLETE status is assigned to either large case under the new checker pin. The correct status for these unexecuted trials is NOT RUN / BLOCKED, not INCOMPLETE.
- No prototype result is mixed with the hardened verifier. No external learner calls, learner edits, merges, or operational-acceptance claims.

## Exact source identity

The following Git blob identities were fetched from the proof branch and independently recomputed locally using Git blob framing:

| File | Git blob | Bytes |
|---|---|---:|
| `bounded_deletion.py` | `e1fc61b6f03484d4428642ca157e2dac43f0572d` | 6,817 |
| `test_bounded_deletion.py` | `6de549b9b4d208be99a419c88fd903a1ce1a6dcc` | 5,274 |
| `independent_replay.py` dependency | `aa09243fa7ccc941c37609e959aefb419075df32` | 7,508 |

All three recomputed Git blob IDs matched exactly. The dependency is the independent raw proof kernel; the bounded module imports only its `require` helper.

## Environment and commands

Python: `Python 3.13.5 (main, Jul 15 2026, 20:25:40) [GCC 14.2.0]`

Commands, executed from a directory containing the three exact-blob files:

```sh
timeout 30s /usr/bin/time -f 'process_wall_s=%e maxrss_kib=%M exit=%x' \
  python -B -m unittest -v test_bounded_deletion

timeout 30s /usr/bin/time -f 'process_wall_s=%e maxrss_kib=%M exit=%x' \
  python -B -O -m unittest -v test_bounded_deletion
```

### Normal output

```text
exhaustive_corpus_owner_cases= 4374 filter_checks= 13122
long_diverse_symbols= 20000 index_entries= 20001 exact_checks= 2 work= 200010
random_collision_cases=500
test_duplicate_positive_index_is_deduplicated_and_bounded ... ok
test_exhaustive_all_owners_and_forced_collisions ... ok
test_long_diverse_trace ... ok
test_missing_extra_and_duplicate_conflict_rejected ... ok
test_random_duplicate_positives_and_negative_conflicts ... ok
test_work_entry_length_and_deadline_caps ... ok

Ran 6 tests in 0.366s
OK
process_wall_s=1.11 maxrss_kib=110092 exit=0
```

### Optimized output

```text
exhaustive_corpus_owner_cases= 4374 filter_checks= 13122
long_diverse_symbols= 20000 index_entries= 20001 exact_checks= 2 work= 200010
random_collision_cases=500
test_duplicate_positive_index_is_deduplicated_and_bounded ... ok
test_exhaustive_all_owners_and_forced_collisions ... ok
test_long_diverse_trace ... ok
test_missing_extra_and_duplicate_conflict_rejected ... ok
test_random_duplicate_positives_and_negative_conflicts ... ok
test_work_entry_length_and_deadline_caps ... ok

Ran 6 tests in 0.396s
OK
process_wall_s=2.41 maxrss_kib=112632 exit=0
```

### Additional counters

- 4,374 exhaustive corpus/owner cases.
- 13,122 forced 0/2/64-bit filter checks.
- 500 seeded randomized collision cases.
- 1,000 duplicate positive traces checked under `entries=2`.
- Long diverse trace: 20,000 symbols; peak index entries 20,001; exact comparisons 2; work 200,010.
- All four resource-cap paths exercised by the unit suite.

The stdout SHA-256 was `bbcb7db643bea36e83d70067f05eacb1ec9adf5a70853f05ce1fe43f1defb57f` in both modes. Normal stderr SHA-256: `ad93c7fd5c283cfda5aa22a16e0ceca43088d3850b8fe701ae9f7ac3ce4ef4ed`. Optimized stderr SHA-256: `102206db3caaf612c2c2398ef016df2dafeeab3ac1984e4e46961a585842e919`.

RSS is observed process RSS, not a virtual-address-space cap. The unit suite's synthetic long-trace case is not a substitute for the recovered huge cases.

## Why the actual huge-case replay is blocked

The Project Library lists `review03-benchmark-evidence.zip` and `p3-exact-search-inputs.zip`, but the Files materialization operation returned `This Project file does not have an authorized raw-byte materialization path` for both archives. Reading the ZIP through the text reader also failed. The current GitHub benchmark branch contains the REVIEW03 scripts, manifests, and results, but not the original raw planted inputs or actual exported journal/2 bytes. A local `git ls-remote` attempt also failed because this runtime cannot resolve `github.com`; GitHub's repository connector remains available for source inspection and commits.

I therefore did not:
- regenerate or approximate either original input;
- infer input or journal SHA-256 values from old reports;
- treat REVIEW03's previous checker results as results for the hardened blobs;
- run the old `bounded_join.py` prototype as if it were the official verifier;
- report a timeout or memory failure when the new large-case process was never started.

## Required continuation

Make the original recovered input JSONs and exact journal/2 artifacts available as raw files in the active execution environment. Then run the exact proof blobs above in normal and optimized modes with 30 s / 1536 MiB, and 512 MiB separately. Report raw closure and complete outer journal replay as separate phases, preserving input/journal SHA-256, work, peak entries, exact checks, wall time, RSS, and VERIFIED/INVALID/INCOMPLETE semantics. Resource censoring must remain INCOMPLETE with no inferred proof.
