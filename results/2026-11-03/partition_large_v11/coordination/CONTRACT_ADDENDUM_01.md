# C011 contract clarification 01: cutoff labels and prelaunch corrections

Client date 2026-11-03. No timing/provider execution authorized yet.

The old user research plan explicitly requested status=incomplete on cutoff, while the accepted C010 parent used unknown. After discovering conflicting draft labels, master accepts C011 status=incomplete with complete=false and no final counts/relations; C010 stays unchanged. This is a documented label difference, not a mathematical change or a performance optimization. Source, CLI, API protocol and NEW readiness must agree before any execution. Preserve stale READINESS_V1 instead of editing it. The cross-method comparison may normalize only these censored-status labels; it may never erase differences in complete results, counts, relations or witness validity.

PROTOCOL_V1's written Bell16/Bell15 decimal constants were found truncated during master review. Correct values from Stirling/Bell recurrence are 10,480,142,147 and 1,382,958,545. Auditor must preserve the original protocol and bind a correction before launch; independently computed oracle values must be checked, not assumed. This is a static finding, not a claimed provider runtime failure.

No extra timing cells or implementation features are added. I002 sparse fingerprints and I003 global pair-commutation normal forms remain future/theory-only. Final execution gate still requires frozen corpus/oracle acceptance, actual candidate hashes matching readiness and protocol, independent static review, then explicit master GO.
