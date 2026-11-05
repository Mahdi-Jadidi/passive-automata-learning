# C022 timing and replay handoff — frozen five-cell round

The 30 fresh timing captures and independent-helper replay are accepted. There are no validator errors, no solver errors, no timeouts, and no unstarted calls. All 15 paired completed statuses agree. This does **not** establish overall wall-time superiority. Retain C020 C2 as the public default; archive C022 as an exact candidate with fewer projection operations on its targeted branch. No additional experiments were run to obtain more favorable timings.

## Fresh wall-time medians

Each value is the median of three fresh subprocesses under the frozen order. Subprocess wall time includes launch, input reading, validation, solving, and output. Capture bookkeeping is outside this metric. Changes below compare candidate wall time to baseline wall time; positive means slower. This table must not be substituted into older C020 timing tables or used for cross-round ratios.

| Cell | C2 seconds | Transfer seconds | Change | Completed status for both |
|---|---:|---:|---:|---|
| A_unknown | 1.915708 | 1.959142 | +2.27% | ambiguous |
| A_K2 | 2.360644 | 2.272160 | -3.75% | ambiguous |
| B_K4 | 3.826016 | 5.478952 | +43.20% | ambiguous |
| C_K10 | 7.394133 | 7.053525 | -4.61% | ambiguous |
| D_K4 | 0.389520 | 0.388420 | -0.28% | certified_unique |

B_K4 has a recorded regression of about 43.20% in the median. Its baseline repetitions were 6.735821, 3.826016, 3.069864 seconds and candidate repetitions were 5.478952, 6.461924, 2.981984 seconds. The variation is substantial; three repetitions do not explain the cause. A_unknown also regressed slightly. D's nearly unchanged wall time does not mean its internal pipeline got faster: median input-and-solver time changed from 0.064974 to 0.080530 seconds. No blanket speed or memory superiority is claimed.

## Deterministic projection work

These counts were identical across all three repetitions of each provider/cell. They are the solver's instrumented input characters processed by projection and projection chunks, not unique input characters or bytes. Independent replay validates scientific decisions and witnesses; it does not independently instrument these counters.

| Cell | C2 projection characters | Transfer characters | C2 chunks | Transfer chunks |
|---|---:|---:|---:|---:|
| A_unknown | 20,334,305 | 16,267,444 | 5,145 | 4,116 |
| A_K2 | 24,401,166 | 16,267,444 | 6,174 | 4,116 |
| B_K4 | 165,374,920 | 132,299,936 | 10,330 | 8,264 |
| C_K10 | 711,436,088 | 646,760,080 | 43,868 | 39,880 |
| D_K4 | 446,464 | 446,464 | 1,744 | 1,744 |

Computed block-mask counts are C2→transfer: A_unknown 5→4; A_K2 6→4; B_K4 10→8; C_K10 22→20; D_K4 218→218. The branch-specific reduction matches omission of replay for merged blocks. The Bell/Stirling search space is unchanged.

## Interpretation and independence disclosure

A, B and C were generated with 4, 8 and 20 physical factors respectively. Declared counts 2, 4 and 10 intentionally permit merged explanations and do not assert the actual device count. Their ambiguity is mathematical assumption sensitivity, not an error rate or a physical-ownership recovery test. A_unknown also permits coarsenings. D_K4 is a unique completed control and does not exercise the new transfer ambiguity branch. Planted swap anchors and repaired traces remain part of the original fixture design; no natural-data accuracy claim follows.

The original auditor reached its usage limit before this timing matrix. The **candidate implementation author** then ran the frozen matrix and replay. Replay uses the previously independently authored `certificate_replay_c015_v2.py` and `oracle_data_v1.py`, which construct projections without importing either solver. This provides algorithmic independence, **not independent personnel execution**. The master independently reviewed the source delta, proof and v4 extraction fix. Master retains responsibility for final review and promotion decisions.

The v3 validator incorrectly passed alternative witness dictionaries to partition canonicalization. It was preserved. v4 extracts `w['blocks']`, and runner v4 plus freeze V5 were written, hashed, and all frozen hashes checked **before the first timing child**. No candidate source or timing plan changed. Older runner/validator/freezes and earlier setup failures remain present. This run required no post-capture scientific source edits or reruns.

## Durable evidence

- Freeze: `SOURCE_INPUT_FREEZE_V5.json`, SHA256 `e51ed774b94ea0f8c083365dbcbf8d27e30acb96562e034bb6f29d74ac3df163`.
- Runner: `run_timing_v4.py`, SHA256 `3e9e365bed006ed92b67609cba3906060f425b1788d998ef74dcef2e9edbefaa`.
- Validator: `validate_timing_v4.py`, SHA256 `604f7eb4ccc6d05b1d29326731f6d764d3db512d66f5a7102af86e9cb54e9149`.
- Timing directory: `timing_runs/C022-IND-20261104-01/`, with `ledger.jsonl`, `closure.json`, `validation_report.json`, and `validator_capture_v4.json`.
- Validator capture: `attempts/20261105T175058.664118Z_e45ed72e68/`, exit 0, no stderr, raw stdout and source manifest preserved. Replay subprocess took 104.203013 seconds; this is audit cost, not solver timing.
- All 30 solver captures are separately addressed by ledger attempt IDs and retain stdout/stderr, source snapshots, hashes, exit status, and child cleanup metadata.
- Handover and pre-execution correction: `HANDOVER_AND_VALIDATOR_FIX_V1.json`. Earlier setup failures: `PRE_RUN_FAILURES_V1.json` and prior versioned files.

No public root file, Git state, or generator was changed in this handover. No memory experiment was added. The round ends with these results.
