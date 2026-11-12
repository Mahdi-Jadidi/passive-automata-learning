# V33 graph candidate freeze manifest

Frozen 2026-11-13 for independent audit; hashes are SHA-256 of raw bytes. This is not a claim of audit approval or measured performance. Do not change a frozen file without a new manifest and renewed review.

| File | SHA-256 |
|---|---|
| candidate.py | 71204F44840353AD5BD1F1BBFBB6365F6AABDA5FFF788F335AE788928F7CC242 |
| baseline_contract.py | 5F60B27447B37EC07F1FD6BCE75BE6199B898573D4B32E90413E900E3A615A94 |
| dev_check.py | 699101DC08791456C40D6B4A77C948B8AA13C0A61DBAAB95EEAA0FB7A26005F7 |
| PROOF.md | C40BF6F290003D1B92703387823286952F0AC0AFA54D7435523EA2298A76B62D |
| README.md | B2DB57A620B62315899C14ED3035DA2CF01B08307088D4EC50AF86DF8DDB18B8 |

The local baseline copy matches the C028 reference SHA-256. `dev_check.py` additionally imports the independent C028 oracle/fixture files in the existing results tree; it does not freeze those dependencies or replace independent review. The algorithm is specified in PROOF.md, including order, costs, constraints and budget delegation. Full output only; no optimum-only comparison. Interrupted computation is not reported as exact.
