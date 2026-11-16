# C025 theory input ledger v1

Local source reads only; some lengthy report output was truncated, and converter/raw YAML inspection was bounded to selected source lines/header. No external search or execution; external simulator provenance confirmation supplied by manager. No C025 implementation inventory existed at bounded check. C017 code is an unrun draft, not independently validated here.

| ID | Path | SHA256 |
|---|---|---|
| R1 | results/2026-11-04/lancer_case_study_v16/theory/LAST_EVENT_OUTPUT_OBSTRUCTION_v1.md | 9ce30912c03f5d8ab442fda481007ba5b49e5016b3ba55b95cdeb3ff13cdb7eb |
| R2 | results/2026-11-04/lancer_case_study_v16/theory/PAPER_ALIGNMENT_FA_v1.md | c5aa96e37b08263bbfaa5e0fdf856491b2d0343732cca34466889f047f24ee86 |
| R3 | results/2026-11-04/lancer_case_study_v16/theory/STAGED_EXPERIMENT_FA_v1.md | 8738be08ce5cd7220c14f4d0d8127d6544637e712852229c80714a216f6ec94f |
| R4 | results/2026-11-04/lancer_host_partition_v17/theory/SELECTED_OUTPUT_PROOFS_v1.md | c00119c492bbd3df08167596a8df07efe9d9bdc8971c974647b1221d454c3082 |
| R5 | results/2026-11-04/lancer_host_partition_v17/implementation/contexts_v1.py | 9f4613f24763cc3c309f96de38b2ae2d56729860421d991738749ab1f40ae565 |
| R6 | results/2026-11-04/lancer_case_study_v16/implementation/PAPER_SCHEMA_REVIEW_V1.md | 1f093f16d881c70538bf3830c09d6e94ddfc01e0331f3cb9025765efcac8122a |
| R7 | results/2026-11-04/lancer_case_study_v16/implementation/M1_M2_REPORT_FA_V1.md | a7ababfefce9d59784924d1b375222132df081bf477f8a85f64da822c14aba89 |
| R8 | results/2026-11-04/lancer_host_partition_v17/coordination/CONTRACT.md | 3041a7ad9bde68797f71f01660c1b9cce99670404ec479f79fc890ee1ca8b4ed |
| R9 | results/2026-11-04/lancer_host_partition_v17/implementation/PAUSED_STATUS_V1.md | 05c2fa7973b23288b95eeedef37190c9316bf1fe5d923a8049ebbaea0da46b05 |
| R10 | results/2026-11-04/lancer_case_study_v16/data_audit/selected_v1/artifact/data/cage2/convert_traces.py | 73d537b7afde020db99ee9a363102e6e1dca9f5eaf0ab3510e8cb09b7d0d0549 |
| R11 | results/2026-11-04/lancer_case_study_v16/data_audit/selected_v1/artifact/data/cage2/cage2_raw_traces/raw_1.yaml | 65bd39d037016314dffb8051f5e61453e8b2b9b33a2d7c418608248cbcef5e7b |

Primary web sources read for operational complement: https://github.com/logpai/loghub/blob/master/BGL/README.md (BGL provenance/label semantics) and https://zenodo.org/records/19828945 (official LANCER artifact description). No broad literature search. Correction: the initial check used the wrong repository-root relative path. Acquisition is present under results/2026-11-05/real_trace_checkpoint_v25/external/loghub_bgl_v1; all five manifest-listed local SHA256 values were subsequently recomputed and match. Sample outcomes remain untested here. URLs are mutable descriptive sources; experimental pinning remains in manager acquisition ledger.

| BGL-ACQUISITION_V1.json | results/2026-11-05/real_trace_checkpoint_v25/external/loghub_bgl_v1/ACQUISITION_V1.json | 38b9229e6fcd27a4c5b31300463adbd4ead287bac5065ea1761e62e59b925e22 |
| BGL-BGL_2k.log_structured.csv | results/2026-11-05/real_trace_checkpoint_v25/external/loghub_bgl_v1/BGL_2k.log_structured.csv | 3fe74103c0b02a28514534e2a47257a3f770135ca61afd425bbd3b9d6a31fe26 |
| BGL-BGL_2k.log | results/2026-11-05/real_trace_checkpoint_v25/external/loghub_bgl_v1/BGL_2k.log | 2a819ea540909db682005c9cf948387a40729b5c2e9f19d430e29ce704825496 |
| BGL-BGL_README.md | results/2026-11-05/real_trace_checkpoint_v25/external/loghub_bgl_v1/BGL_README.md | 4ec19cee4f8b4086ab511cae2fe901a9e298475f4d678f8c9e84e484691031ef |
| BGL-LOGHUB_README.md | results/2026-11-05/real_trace_checkpoint_v25/external/loghub_bgl_v1/LOGHUB_README.md | b9819b1e12d959a0c046a9a4213b4e4d7bd0647fe474dba0137af5770bc004fd |
| BGL-LICENSE | results/2026-11-05/real_trace_checkpoint_v25/external/loghub_bgl_v1/LICENSE | 9ffa6ae259833cdc6e7ed8a0219fec72ef6455fb457b3c44096cb1ac1f0696d4 |
| BGL-commit.json | results/2026-11-05/real_trace_checkpoint_v25/external/loghub_bgl_v1/commit.json | 82339a0d3bb8f72e728689f8502a534a30fe8351aca4d18ba28b742821793178 |
BGL ledger scope: manifest and BGL README/LICENSE read; commit metadata inspected; raw/CSV and repository README hashed without sample-content analysis. Pin dd61d0952749ee7963bde24220d1be5ede023033. No experiment or acquisition mutation.

C025 actual-source review: implementation/selected_output_v1/solver_v1.py SHA256 73ff8ecae70a55525ec6a2d3f1216e721ad2f1298d973d334e6f743080358e4e; cli_v1.py SHA256 89f58a396593921ba8accc664de8d7e3ff94e7de9a7d7e8ca01211042ca6f2ef. Both complete sources read and locally hashed; no execution. Findings in SOURCE_REVIEW_V1.md. One shell inspection failed from unsupported PowerShell brace syntax before execution; corrected hash-only command succeeded; no source mutation.

Smoke evidence follow-up (read only, no execution): smoke_v1.py SHA256 f3fefd32c44f08ec4f1b291ad39fe55ccd57fc3dd21822eab9e1443d78d510d6; smoke_results_v1.json SHA256 c1380885c7d4af4266f88d8af23fed04e446e2881cc715f1b8f07b3f21983055. Parsed report: passed=true,162 rows, real_data_solver_runs=0, matching reviewed solver hash. implementation/contexts_c017_copy_v1.py and historical C017 contexts_v1.py both SHA256 9f4613f24763cc3c309f96de38b2ae2d56729860421d991738749ab1f40ae565. Script read completely; lengthy report display truncated, then summary fields parsed. Initial copy lookup used wrong child path, corrected parent lookup succeeded. Two writing commands failed PowerShell parsing before writes; corrected commands succeeded. No implementation edits or experiments.
