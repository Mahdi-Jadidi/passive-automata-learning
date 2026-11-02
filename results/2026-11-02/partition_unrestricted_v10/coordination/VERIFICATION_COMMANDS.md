# Verification invocations

Actual interpreter for master checks:

`C:/Users/Mahdi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`

From the workspace root, run with that executable:

```powershell
& 'C:/Users/Mahdi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B -X utf8 'results/2026-11-02/partition_unrestricted_v10/coordination/verify_delivery_v1.py'
& 'C:/Users/Mahdi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B -X utf8 'results/2026-11-02/partition_unrestricted_v10/implementation/verify_bundle_v1.py'
```

Receipts: `presentation_integrity_result.json` and `bundle_integrity_result.json`. The `command` field printed by the first checker is shorthand reproduction syntax from the cycle directory; the actual invocation used the absolute executable and script paths above. Snapshot manifests exclude themselves and subsequently produced verification/publication receipts to avoid recursive self-hashing. All such receipts remain in Git.

Presentation snapshot is closed with 215 files plus its manifest. The C010 manifest separately records its hash and the final deck hash. The independent auditor's own capture integrity receipt and final closure index cover scientific capture provenance; the master checks cover frozen parent bytes and file delivery integrity. None of these hash checks replace mathematical correctness proofs or the independent behavioral oracle.
