# C010 implementation handoff — v2

Use `unrestricted_solver_v2.py` through `unrestricted_cli_v2.py`. No external
`k` is accepted: `k` and `allowed_k` cause `invalid_input`. Remaining fields
are the known alphabet and exact positive/negative complete words.

## Run from workspace root (PowerShell)

```powershell
$py = 'C:/Users/Mahdi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $py -B -X utf8 'results/2026-11-02/partition_unrestricted_v10/implementation/unrestricted_cli_v2.py' 'results/2026-11-02/partition_unrestricted_v10/implementation/proofcase_no_labels_r2_v1.json' --seconds 30
& $py -B -X utf8 'results/2026-11-02/partition_unrestricted_v10/implementation/unrestricted_cli_v2.py' 'results/2026-11-02/partition_unrestricted_v10/implementation/proofcase_graph_empty_fallback_v1.json' --seconds 30
```

The captured r2 no-label case gives two partitions with spectrum `{1:1,2:1}`.
The graph-empty fallback case has six singleton atoms, no swap edges, five
partitions and spectrum `{1:1,2:3,3:1,4:0,5:0,6:0}`. All three local captured
proof cases and raw-output hashes are in [LOCAL_CAPTURE_SUMMARY_V1.json](LOCAL_CAPTURE_SUMMARY_V1.json);
full immutable attempt folders are under `../audit/attempts/`.

The default complete result returns exact total/per-k counts, pair relations
and witnesses, plus a representative projection witness. `--enumerate`
requests the full partition list and may have exponential output size.
`k_max_upper_bound` is the atom count; `k_max_compatible` is the largest k
with a nonzero completed count. Neither claims the hidden generator's true k.

## Counters and timer scope

`swap_pairs_tested`, `swap_edges`, `atoms`, and `atom_projection_checks` cover
contraction/precheck; `block_masks_computed`, `dp_states`, and `dp_branches`
cover lazy-mask DP; `enumerated_partitions` counts explicitly emitted answers.
`preprocessing_seconds` includes swap extraction, atom construction and the
atom feasibility check. `search_seconds` measures DP count evaluation only;
it is zero on the closed-form shortcut and excludes pair witness recovery and
enumeration. `provider_seconds` is assigned before building the representative
projection witness. Use capture process wall time for end-to-end timing.

Deadline/interrupt checks cover swap extraction, union-find construction and
the protected compute phases. Input validation runs before that protection;
the CLI's input read and JSON serialization are outside it. A cutoff in a
protected phase returns `unknown`, `complete:false`, without final counts or
relations. Do not report timing subphases as total cost or make speed claims.

Theory's static review cleared v2, but the independent 125-case complete-set
gate, controls and four scale correctness cells remain the acceptance gate.
See [PROVIDER_V2_STATIC_REVIEW_V1.md](../audit/PROVIDER_V2_STATIC_REVIEW_V1.md).
The frozen source hashes are in [READINESS_V3.json](READINESS_V3.json).
