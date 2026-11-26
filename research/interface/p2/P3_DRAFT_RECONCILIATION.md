# Non-destructive reconciliation plan for PRs #6–9

The four PRs target `research/selector-v2`. This review uses the integration branch at `05eeab8cf2b17b770c1a96476b7598201e27ecc3` and the Review 08 draft snapshots below. Each change set is the branch-side file list from `git diff --no-renames --name-only $(git merge-base BASE HEAD) HEAD`. This retains both endpoints of a rename for the overlap check.

| Draft | Review 08 head | Merge base with integration | Behind / ahead | Changed paths |
| --- | --- | --- | ---: | ---: |
| #6 interface | `122844ee5668f1c898f85b08133a562f31719718` | `c0aae9fb222aef9dfea4c13cb44e5a37f0d86f8a` | 28 / 46 | 42 |
| #7 core | `096fd14b684624d00c68071db7450f4c0b9c717f` | `c0aae9fb222aef9dfea4c13cb44e5a37f0d86f8a` | 28 / 31 | 152 |
| #8 proof | `cea576889c5d9bd2fb846f2f883403be85b2033b` | `4a2f3d6ce0b4b974430f02d79b1a98f2c8fc9e4b` | 26 / 75 | 61 |
| #9 benchmark | `8484b8bff5b93e1be3a7924697161efc34e481d8` | `c0aae9fb222aef9dfea4c13cb44e5a37f0d86f8a` | 28 / 58 | 86 |

All six pairwise intersections of changed file paths are empty at these snapshots. The additions for this M3 interface milestone also use #6-owned paths. The shared `.github/workflows/` directory has separate workflow files. Recompute the intersections at the actual review heads, including file/directory collisions and rename endpoints, before any future branch reconciliation.

| Path or contract | Ownership and dependency |
| --- | --- |
| `implementation/partition_feedback_final/selector_v2/{registered_ledger,component_closure,edr_m3,edr_cross}.py` | #7 owns the implementation. #6 calls the authoritative ledger, RAW closure and native producer at exact pins. #8 verifies producer artifacts as data. #9 runs the producer in its paired harness. |
| `tests/reference/{p3_frontier_verifier,journal_v2_replay,p3_rgs12_oracle,p3_m3_artifact_replay}.py` | #8 owns independent code. #6 uses the guarded `316d443` checkout. The frozen #7 core and #9 benchmark runs used `f24d34c`. Keep those historical pins with their results and use the guarded checkout for new interface replay. |
| `implementation/partition_feedback_final/research/p3-m3/evidence/` | #7 owns retained producer bytes. #6 consumes `096fd14` directly. #8's prior proof-only workflow consumed the immutable core archive and performed separate resumes. #9 has its own paired outputs and resume evidence. |
| `research/interface/p2/` and `.github/workflows/p3-*-interface*.yml` | #6 owns gateway delegation and interface evidence. The core's registered ledger accepts the existing interface adapter and strict parser as explicit, pure dependencies. |
| `benchmarks/v2/p3/inputs/{tiny_choice,small_choice}.json`, #7's retained `raw.json` files and #6's `fixtures/p3/*.raw.json` | Separate fixture paths represent the same tiny and small input identities. Compare exact bytes and declared scope for equivalent cases when reconciling coverage. Retain the original input files referenced by historical manifests. |
| `implementation/partition_feedback_final/research/P3_SERIALIZATION_V1.md`, `INTEGRATION_REVIEW_07.md`, `INTEGRATION_REVIEW_08.md` and `implementation/partition_feedback_final/SELECTOR_V2_INDEX.md` | The integration branch records the frozen v1 contract and approved v2 extension. These are common dependencies across the four drafts. |

1. Capture the four current heads, PR bases, immutable dependency commits, workflow run IDs and artifact digests. Verify frozen blobs and track any expired external artifacts before reviewing a combined tree. Keep branch refs, published history and draft status intact.
2. Ask the lead to review a proposed staging order when reconciliation is authorized. Review #7 and #8 together as the producer and independent reader, including journal/2 compatibility and proof independence. Then use #6 to check the complete certificate-to-ledger path and #9 to check comparable benchmark and checkpoint-accounting results. Keep #9's benchmark and #6's registration gate as separate acceptance evidence.
3. Until merge authorization, inspect candidate changes with read-only diffs and local scratch Git objects, using `git merge-tree` for conflict diagnostics. Record any conflicts by path and assign the owner shown above. Where the core and proof depend on each other's evidence, keep those dependency commits pinned throughout replay.
4. Before a later integration decision, rerun the frozen normal and optimized v1 and v2 gates on the reviewed source provenance, checking exact raw/journal/scope/certificate/resume bytes, structural optima, registration and UNKNOWN behavior. Review artifacts and job logs separately from the workflow conclusions. Keep the offline opt-in gate and `operational_status=INCOMPLETE`.
