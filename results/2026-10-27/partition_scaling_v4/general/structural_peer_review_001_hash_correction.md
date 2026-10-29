# Hash correction for structural peer review 001

This correction preserves the review text and findings in
`structural_peer_review_001.md`. The hashes in that review were manually
mistyped. Direct `Get-FileHash -Algorithm SHA256` output gives:

| File | Correct SHA-256 |
|---|---|
| `structural/singleton_solver_v1.py` | `16065fdfabf52d4280e3c0f5a7f427faff8990583579bd97b4ea64f70c5a023e` |
| `structural/PROOFS_S001.md` | `437167d2c294ef3c4ef13f2be8c3dafc4cd0c7dfd1ff0156ac738270ae9f1d84` |
| `structural/PROOFS_S002_PREPARED.md` | `ed5f40f67815420cb0ea4bd1ca633513dae77bd5ceacd4ee13eb91a0ef0f1273` |

The previously recorded hashes are superseded. No reviewed source or proof was
modified.
