# Master reporting clarifications; original audit records are preserved

- Stage-1 old-source metadata paths in the first gate have one extra `../`; exact corrected paths and verified unchanged hashes are recorded in AUDIT_PATH_ERRATA_01.json. No provider result is affected.
- Stage-1 timings serialize a normalized first-answer summary, as the frozen protocol declares. They are not full-API-result serialization times. Full correctness evidence is separate. STAGE1_SCOPE_ERRATUM_01.md under audit/ records this scope; Stage-2 measurements are separately specified to serialize the full API result.
- The auditor's HTTP404 note lacked request details in its local context. The master did retain tool-visible endpoint, request ID and cf-ray metadata in RESUME_2026-10-28.json. Neither record contains a full server-response log. This is available metadata, not a reconstruction of missing raw logs.
- Stage 2 has 106 case records plus one addendum; canonical normalization gives 104 payloads and three duplicate groups. These are not 107 independent random observations. Root CLI inputs and command counts also differ: the original freeze has five CLI inputs and the gate checks twelve CLI command records.
- Four larger q=2 exact-search checks include two complete `found` runs and two `incomplete` runs with valid first answers. The latter do not prove uniqueness. QOP's separate structural certificates prove uniqueness within the declared cap-q class.
- Long contextual targets are prefix languages L_i=u_i E_i*, not bare tile-star languages. Raw repeated center negatives deduplicate to k distinct negatives; total distinct labels are n+1. MASTER_CONTEXT_REVIEW_02.md and the independent target-language proof preserve the rationale.
- Python allocation peaks from incomplete runs are retained but cannot be ranked as completed-work memory against another method. Tracemalloc peaks are not process RSS.

These clarifications change no captured output, accepted runtime source or historical failure. Current acceptance is determined by the master decisions and exact referenced report hashes.
