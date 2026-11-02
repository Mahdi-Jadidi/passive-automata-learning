# Archive integrity v3 erratum

The v2 final audit report is preserved at
`coordination/FINAL_INTEGRITY_C007.json` with three findings: attempt records
had no source snapshots. Inspection of each original manifest and result shows
all three were capture setup failures before a child process could start:
the manifest and result contain the same `FileNotFoundError`, `subprocess_seconds`
is zero, there is no child PID or reap status, no exit code, and stdout is
empty. The three attempt IDs are recorded in
`ARCHIVE_INTEGRITY_PROVENANCE_V3.json`.

The new checker version counts such provable prelaunch failures separately as
`prelaunch_capture_failures`. It still reports an integrity error for any
missing-source capture without all of those conditions, especially any record
with a child PID or nonzero subprocess time. It does not relabel these failed
attempts as successful scientific runs. No provider, data, or output was
changed, and archive_integrity_v3.py has not been executed.
