# C025 recorded-artifact ingestion checkpoint

Status: prepared observations and provenance only. No AND input, solver run, context analysis on real data, training, or host-recovery result. This resumes ingestion under the new authorization; C017 paused drafts remain unchanged and are not counted as executed evidence.

## Sources and scope

Verified cached Zenodo artifact: `.cache/lancer/cas-artifact-cav2026_20261103T211638Z.zip`, 244813827 bytes, SHA256 `06039a2cb4c8a5e2230aa7681f2b7e09914ce7ce44a7721b272a437ce2daef76`. Read ZIP in place; selected members are CRC-checked by zipfile and individually SHA256 hashed. Original artifact scripts were read as text, never imported/executed. PyYAML 6.0.3 safe_load successfully parsed all six selected CAGE2 members; no custom-tag workaround was needed. Baby records use bounded ast.literal_eval with an AST allowlist, never eval/unpickle.

CAGE2 raw and BabyCyborg random/heuristic single-host scenarios are archived recorded simulator-generated cybersecurity observations. They are real files from the published benchmark, not newly synthesized controls and not production telemetry. Six files per pool are the first six lexicographically sorted full archive paths: suffixes 1,10,100,1000,1001,1002, not numeric 1..6. Each pool has 5000 files. The exclusion ledger names all 14982 unselected files in those pools. Other archive entries are outside declared scope and remain represented by the authenticated C016 full inventory; no claim of full-archive CRC validation is made.

## Boundaries, observations and labels

Preserve source file and explicit Baby episode boundaries as separate trace containers. Every prepared sequence starts independently; this is a declared prospective modeling reset convention, not evidence that simulator hidden state physically resets. Never join files, scenarios, or episodes. CAGE2 has file boundary only; no inferred episode field. Within a recorded step retain Blue then Red order, matching static learner code. This is a serialization convention, not an assertion of physical causal ordering. Every faithful record retains source locator, step/episode values, actor, raw action and raw aligned outcome.

CAGE2 action[i] gets status from the same actor's obs[i+1]. Integer1→true,3→false,2→null, missing/unsupported→null. Final action has null outcome rather than being dropped. Unknown events remain in history. No UNKNOWN codes occurred in the selected CAGE2 aligned sample; policy is separately unit checked. Baby TRUE/FALSE are retained as published event outputs; any original UNKNOWN coercion upstream cannot be undone from processed files. No attempt is made to improve or invent published labels. All twelve final unlabelled events are retained. No events are excluded.

The outcome describes the current event's success, not AND acceptance of the complete accumulated word. A previous failure does not force later events negative. C024/C020 full-word DFA-AND assumptions are therefore not automatically applicable. No faithful conversion is claimed. C017's selected-output model and proofs are candidates for separate theory review. Its contexts_v1.py is copied byte-for-byte to contexts_c017_copy_v1.py; only toy helper tests were run. The adapter reuses the documented C016 literal/boundary inspection and C017 strict next-status alignment policies in new code. No C017 100-file experiment is reconstructed.

## Two explicit abstractions

Action-only atomic IDs describe action plus present non-null exploit_class/exploit_port. Host/IP/subnet/actor and all other fields are withheld and stored in faithful_records_and_metadata.json. IDs are SHA256 of canonical descriptions with collision checks; token strings are atomic IDs, never character alphabets. Labels, file IDs, step, episode and TrueState never enter token descriptions. There are19 action-only types.

The alternate target-qualified view adds literal observed hostname/ip_address/subnet/subnetname fields to the atomic event description. This NEW abstraction intentionally uses observed target metadata; opaque hashing does not make it blind host recovery. No IP-to-host lookup or simulator TrueState is used. Missing, empty, host and IP representations are retained literally, without invented normalization. It is not the original learner's action/value-token stream and may fragment semantically equivalent targets across files. There are122 qualified types. Fourteen action-only types alias multiple observed target descriptions; that is not proof of multiple owners. Actor is excluded from both abstractions and remains metadata.

Combined observations.json files are storage bundles only. Per-scenario observation files avoid silently fitting a common model across different simulator systems or policies. All events are retained for a possible known-host baseline; projecting a selected type subset cannot diagnose omitted-state dependence or establish physical ownership. Host mapping, global actions and shared dependencies require explicit later review. No train/test split or predictive claim is made from these development selections.

## Evidence and next stage

Prepared totals:18 source files/18 trace containers,1560 events,1257 true,291 false,12 unlabelled. CAGE2:1200 events,976 true,212 false,12 unlabelled. Baby random:180 events,131 true,49 false. Baby heuristic:180 events,150 true,30 false.

Checks include selected-byte replay against ZIP hashes, exact selected-path rule, artifact/output hashes, event alignment and token/metadata separation, strict unknown handling, unsupported executable AST rejection, and C017 toy controls for finite/full history and per-file reset. These are implementation checks, not independent ingestion audit or scientific results. The archive's size/mtime was unchanged during reading; its entire SHA was verified before parsing. No whole archive extraction, installation, external artifact execution or public solver modification occurred.

READINESS_v1.json records exact commands, source hashes, output hashes and remaining model decisions. Ready for independent adapter replay and alternate-model review. The public solver remains unchanged.
