# Archive integrity checker v2

`archive_integrity_v2.py` is a new version; v1 remains unchanged. Its only
behavioral change is owner-scope dependency resolution: a readiness document
may declare an owner folder inside C007 while naming a file in an immutable
parent cycle, such as `scope: implementation/` plus `../../../.../solver.py`.
The checker still rejects a declared owner scope outside C007 and still rejects
resolved dependencies outside the workspace. It performs no basename or hash
search. All raw-stream, source-blob, completion, runtime-manifest, parent
manifest, and scope checks from v1 remain present.

The final archive checker has not been run. The master should run v2 once after
`coordination/runtime_final.json` and final evidence are ready. Provenance and
the artifact hash are recorded in `ARCHIVE_INTEGRITY_PROVENANCE_V2.json` and
`ARCHIVE_INTEGRITY_READINESS_V2.json`.
