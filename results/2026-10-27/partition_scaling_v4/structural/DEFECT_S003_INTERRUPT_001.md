# Preserved S003 v3 interruption failure and v4 correction

Date 2026-10-27. Defect class: real interruption/control-flow defect; no partition-set mismatch observed. Original singleton_solver_v3.py remains unchanged with frozen hash 146898b89ac3df0878e8e156e60f4826b6b83b879473d6ebf19c9bad954c8ab0.

Minimal reproducer input: alphabet abcd; positives abcd,cdab; negatives bacd,abdc; infer_k=True and no k in data. Inject one KeyboardInterrupt at the first singleton_solver_v1.check during base preprocessing. The base provider catches it and returns status incomplete with a partial graph. V3 reset the status to insufficient_coverage and continued, then attempted to project a nonempty positive through an empty graph owner mapping, raising KeyError('a'). A single interruption could also be misreported as unresolved depending on its precise location. This violates the interruption contract even though ordinary and expired-deadline smoke cases passed.

Initial/minimal regression: interruption_regression_v1.py. Captured failure: audit/attempts/20261027T094232.668971Z_70a83ef430. Program exit 1, stdout raw 257 bytes, stderr raw 394 bytes. The observed exception and input were printed before the assertion. Every imported research source and inline input-containing harness were snapshotted. This attempt is preserved and not replaced.

New source singleton_solver_v4.py (SHA256 5cc301477d10aad356b857e05df73ec326c2f94b2475a554348fb7eaf53b8958) stores whether base preprocessing returned incomplete before resetting wrapper metadata. It then propagates incomplete with no graph processing, exhaustion or uniqueness claim. Default known-k behavior still delegates to v2. V1/v2/v3 and QOP001 were not edited.

New regression interruption_regression_v2.py passes in captured attempt audit/attempts/20261027T094323.372761Z_6cf11853a5, exit 0, no stderr. New smoke_stage2_v2.py reruns the same 562 independent-oracle comparison records using v4 for unknown-k inference and passes in audit/attempts/20261027T094334.435675Z_8c3386f4c8, exit 0, no stderr. These are own prototype results, not independent audit acceptance. Raw stdout is saved before assertions.

The old frozen root solver.py still selected v3 at the time of this rerun. Therefore its four ordinary root-CLI calls demonstrate ordinary example behavior, not a corrected CLI interruption path. Both v3 and v4 were included in that capture's source manifest. Master was notified to introduce a preserved new CLI version selecting v4 and to request independent interruption verification before promotion.
