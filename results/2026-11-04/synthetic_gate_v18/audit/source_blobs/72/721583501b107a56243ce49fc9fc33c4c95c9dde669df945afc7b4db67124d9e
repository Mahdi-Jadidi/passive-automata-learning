# C018 first frozen run — incomplete, preserved

Run: `runs/20261104T063310.541595Z`, launched once by master from frozen run_v3.py after GO. Closure reports71.5307361 active seconds, incomplete_or_rejected. No candidate or timing capture was launched; no speed comparison exists from this run. No independent full-suite validation acceptance was obtained.

Preparation capture20261104T063310.562715Z_5735e00a63 succeeded (12.4386613 subprocess seconds), produced1695 jobs =1638 held +57 additions, plus8held performance cells. Baseline capture20261104T063324.152853Z_a5bae58d90 succeeded as process (3.7981103 subprocess seconds); stdout2813497 bytes,1695JSON rows, no stderr. Raw statuses759certified_unique,694ambiguous,204incompatible,35invalid_input,3unresolved. These are provider-emitted counts, not independently accepted semantic counts.

Unresolved rows:

- c018_unicode_atomic:0.2515081 seconds under frozen per-call0.25s, reason Halt. This is unexpected censoring of a correctness control, not a provider exception or a proved mismatch. Its input/oracle remain unchanged.
- c018_expired_before_validation and c018_expired_valid: intentional deadline0 controls, expected unresolved.

The runner checks process/row completeness and unresolved status before timing. It stopped before candidate and all48performance jobs due to the Unicode row. Full semantic oracle replay was scheduled only at the final validation phase: this sequencing limitation is explicit; pre-timing process checks must not be called an already-passed independent correctness gate.

Final validator capture20261104T063331.510352Z_59a1f3e852 hit hard50s (50.1133399 subprocess seconds), with empty stdout/stderr. It was reaped and raw capture retained. The source unconditionally replays all8held worlds even when no timing job ran; this is a static efficiency concern. Without progress output, the exact timeout location is unknown. No missing validation report is reconstructed.

No repeated provider run, source edit or new experiment was performed by auditor after master launch. C017/LANCER remains paused. Continuation requires a separately frozen/authorized harness that preserves this run and its marker; its execution must be recorded as a new attempt, never overwrite this result. Suggested review direction is a small-only independent gate over preserved baseline outputs, explicit handling of the censored Unicode control, then any further candidate/timing work within remaining active budget. No continuation authorization is implied by this note.
