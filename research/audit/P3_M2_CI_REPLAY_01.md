# P3 M2 independent verifier CI evidence — checkpoint 01

Observed live proof HEAD e1d022496f98bf50fd57d5ef3a7a0bc8194c817c, fast-forward +2 from requested 4c4543775b7e2700ad0505da49023e24b2e5e9ab. PR #8 remains draft/unmerged. Frozen contract commit ff61b1c56138c89fc0ad9a615f0b2a587b03393a, blob 9dd487605f0dfdc6735f7d53a42627039fb57db8; supersedes historical nested/root_equalities addenda in P3_REGION_COVERAGE_CONTRACT.md.

## Executed CI, not a predicted result

Run 45591575274, job 139126846916, successful; fetched decoded job logs and verified actual checkout HEAD and hashes. Ubuntu 24.04 / Python 3.13.5. Previous run 45571609270 failed; optimized mode skipped there. Current run passed both.

Source Git blobs in logged order:
- tests/reference/p3_frontier_verifier.py a35281492e2677f0c57d8955227bc233d95492ea
- tests/reference/test_p3_frontier_verifier.py 9754dc3e0c21cabfbf8339b598650ddae40bcbdc
- tests/reference/rgs_oracle.py 375c36bfb2602894ce783055d1edf31f265aafa0
- tests/reference/bounded_deletion.py e1fc61b6f03484d4428642ca157e2dac43f0572d
- tests/reference/journal_v2_replay.py 6c49013e809b5ac4d2b2a37850e6e6cece513072
- workflow (fetched source) 7c5c8adcd4d99a01fa32e8361f2afda46cf889d3

Commands (PYTHONPATH=tests/reference, ulimit -v 1572864):
    /usr/bin/time -f 'wall=%e RSS_KiB=%M' python -B -m unittest discover -s tests/reference -p "test_p3_frontier_verifier.py" -v
    /usr/bin/time -f 'wall=%e RSS_KiB=%M' python -B -O -m unittest discover -s tests/reference -p "test_p3_frontier_verifier.py" -v

Normal: 10 tests, 0.861s unittest, wall=0.98 RSS_KiB=26876, OK.
Optimized: 10 tests, 1.001s unittest, wall=1.35 RSS_KiB=28500, OK.
Per mode: 179 synthetic literal fixture cases (n=0..5); 7065 region checks; Bell counts n=0..8; 43680 pair_at comparisons; 17 certificate mutations plus separate suffix/scope/cap tests; 20k-symbol identity root with 199990000 symbolic alternatives, two flat nodes, 349428 work units, INCOMPLETE. Nonidentity journal replay tested separately on 3 symbols. This is not a large nonidentity contraction stress test or a formal measured asymptotic guarantee. RSS observed, not RSS limit. No producer imports in verifier; independent P2 modules only. Source has cooperative budget checks and process address-space cap; not hard preemption inside native JSON or allocation. Path replay may repeat work.

## Remaining gates

Actual producer branch was still fa12fdcca0a8d7a9a697bb617ed09453cb56c3d5 at inspection. No actual tiny_choice or small_choice certificates delivered in issue #2; request already posted there. Actual producer replay NOT RUN. Existing RGS oracle deliberately caps at n=8, so small_choice (12 symbols) needs a separately bounded extended independent reference enumeration, not a silently reduced alphabet or planted answer. No producer acceptance or operational acceptance. No external learner, ledger or baseline edits; no external learner calls; no merge.
