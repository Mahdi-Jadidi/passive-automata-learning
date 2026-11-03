# C013 grid analysis v1

`analyze_grid_v1.py` is a standard-library-only, read-only analysis tool.
It does not launch a solver/generator, import audit scripts, install plotting
libraries, or change audit files. No analysis execution occurred during authoring.
Run it only after the master's GO and final audit-ledger freeze.

Pass only the final grid ledger (or nonoverlapping final shards), not historical
retry/revision ledgers together. Duplicate or unplanned slots fail explicitly.
Every ledger requires its exact final SHA-256. All other consumed files are
hashed and checked again before outputs are written; changes abort the run.
This stability check does not itself grant master approval or replace freeze.

Example recipe, with the final hash substituted after GO:

```powershell
python -B results/2026-11-03/partition_random_dfa_v13/implementation/analyze_grid_v1.py --audit 'results/2026-11-03/partition_random_dfa_v13/audit' --ledger grid_inference_ledger_v4.jsonl --ledger-sha256 FINAL_64_HEX_SHA256 --validation GRID_VALIDATION_V3.json --preparation-ledger grid_preparation_ledger_v3.jsonl --input-map GRID_INPUT_MAP_V4.json --out 'results/2026-11-03/partition_random_dfa_v13/implementation/analyses'
```

`--ledger`, `--validation`, `--preparation-ledger` and `--input-map` paths are
absolute or relative to `--audit`; audit/out are relative to the calling working
directory. Include every final preparation ledger, including resume attempts,
to preserve all generation costs. `--input-map` is optional when recorded
input paths and the original grid directory convention suffice; pass the map
when unstarted slots use resumed data. The tool fails on missing required
ledger/validation/map files, and records per-slot errors for missing captures.

Each invocation creates `analysis_UUID/` under out, which must be outside the
audit tree. It saves analysis.json, slots.csv, cells.csv, generation.csv, and
SUMMARY_FA.md. Analysis provenance includes all input hashes and script hash.
No previous analysis is overwritten.

The fixed contract is 20 K values, six caps, two sample counts and three broad
replicates (720 slots), plus two separately reported 20-second confirmations
(K1/K20, cap1m, n8). Missing rows become unstarted; ledger budget-unstarted
reasons remain visible. Each slot records complete_ambiguous, unique_recovery,
cooperative_unknown, hard_timeout, error or unstarted. Complete categories
require matching independent validation and capture success, not only a raw
complete flag. No complete result is independently revalidated by this tool.
Validation failure/unassessed complete outputs become errors, not recovery.

actual_T is the sum of lengths from saved generation sample records with
index<n for both labels. Raw requested cap never substitutes for actual_T.
Missing metadata remains null with visible errors where applicable. True K,
world hash, event profile and actual sample count are retained separately.
Times include both capture duration_seconds and subprocess_seconds; they have
different boundaries. Median capture/subprocess times exist only for broad
cells with all three independently validated complete replicates and identical
world hash/T. Censored/error/missing replicates never produce a winning median.

Generation costs have one row per shared K/cap parent, not one copy per solver
replicate or n. It preserves all supplied preparation attempts' external
capture/subprocess times, internal world/sample-generation times, preparation
wall time, and independent replay time as separate fields. It does not sum
these overlapping measures. Missing generation records remain explicit.

Optional descriptive log-log slopes are automatically emitted only within a
fixed K/world-hash/n/profile group, using broad-cell medians at at least three
completed distinct caps and distinct actual_T values. The report lists included
and excluded caps. Confirmations are excluded. These selected complete-length
fits omit censored observations and are descriptive only; no global regression,
worst-case bound, or asymptotic inference is claimed. No plot is needed and no
plotting dependency is imported.
