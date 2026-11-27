# P3 M2 independent frontier verifier — tested checkpoint

## Disposition

Independent synthetic/reference validation PASS at exact proof checkout `e1d022496f98bf50fd57d5ef3a7a0bc8194c817c`. Actual Agent #2 producer certificate replay NOT RUN: inspected core HEAD fa12fdcca0a8d7a9a697bb617ed09453cb56c3d5 still contains M1, not full producer/serializer. Integration acceptance remains pending. Operational INCOMPLETE. PR #8 draft and unmerged. No baseline/learner/ledger change. Contract: ff61b1c56138c89fc0ad9a615f0b2a587b03393a.

## Exact sources

| File | Git blob SHA |
|---|---|
| p3_frontier_verifier.py | a35281492e2677f0c57d8955227bc233d95492ea |
| test_p3_frontier_verifier.py | 9754dc3e0c21cabfbf8339b598650ddae40bcbdc |
| rgs_oracle.py | 375c36bfb2602894ce783055d1edf31f265aafa0 |
| bounded_deletion.py | e1fc61b6f03484d4428642ca157e2dac43f0572d |
| journal_v2_replay.py | 6c49013e809b5ac4d2b2a37850e6e6cece513072 |
| independent_replay.py | aa09243fa7ccc941c37609e959aefb419075df32 |
| production_replay.py | 4666c3f1aca6189331a83ff2f00de0e376e2a710 |
| ledger_replay.py | 0b615b6c17258e621d73147baa262d791985d8d0 |
| interface_artifact_replay.py | 51f928ee2311ab8995f88f0e9f195ac7c659e469 |
| test_production_replay.py (independent fixture helper only) | 630e2150d186cff9181d96ca7b8a6d713aa1a7c7 |
| .github/workflows/p3-frontier-verifier.yml | 7c5c8adcd4d99a01fa32e8361f2afda46cf889d3 |

## Executed evidence

GitHub Actions run 45591575274, job 139126846916, all steps SUCCESS: https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45591575274/job/139126846916. Actual Ubuntu 24.04 / Python 3.13.5. Selected verbatim source/test log lines are in p3-m2-ci-45591575274.log; full log remains in Actions. Initial d98c808 CI runs 45591346881 and 45591333685 failed at setup-python because ubuntu-latest was Ubuntu 26.04 and 3.13.5 unavailable. No tests executed in those runs.

Commands from repo root:

    export PYTHONPATH=tests/reference
    ulimit -v 1572864
    /usr/bin/time -f 'wall=%e RSS_KiB=%M' python -B -m unittest discover -s tests/reference -p "test_p3_frontier_verifier.py" -v
    /usr/bin/time -f 'wall=%e RSS_KiB=%M' python -B -O -m unittest discover -s tests/reference -p "test_p3_frontier_verifier.py" -v

| Metric | Normal | Optimized |
|---|---:|---:|
| Unittest methods | 10/10 | 10/10 |
| Suite seconds | 0.861 | 1.001 |
| Process wall seconds | 0.98 | 1.35 |
| Observed max RSS KiB | 26876 | 28500 |
| Literal RGS sample fixtures | 179 | 179 |
| RGS region membership checks | 7065 | 7065 |
| Direct pair_at comparisons | 43680 | 43680 |
| Main certificate mutation cases | 17 | 17 |
| Symbolic lazy alternative count | 199990000 | 199990000 |
| Symbolic fixture work units | 349428 | 349428 |

Bell counts B(0..8) = 1,1,2,5,15,52,203,877,4140; independent label enumeration n<=5. Extra tests cover 3 lazy mutations, valid one-mode vs invalid all-mode equality cutoff, tied optima, nonidentity E0 and forged journal/root, strict duplicate-key CLI, 7 explicit cap cases, false EXHAUSTED and false PARTIAL. These are synthetic reference proof fixtures, not actual core search output.

## Proof mechanism

For each flat path, reconstruct the canonical full owner by independent original-ID relabeling, with no producer DSU. Every earlier false alternative is independently checked via its parent's validated cursor log. At the residual all current class pairs are false symbolically, making it a singleton or empty. All strict coarsenings satisfy at least one pair equality and have a unique first true index. Thus checked prefix + exact suffix + residual gives disjoint full coverage. No O(k²) alternative list/hash; no per-node E/D copies. The verifier recomputes literal projection compatibility and cost from original traces/owners. FEASIBLE_MIN is valid since E is the unique lowest cost region member and every strict coarsening increases cost. EXACT_NO requires a singleton. COST requires a compatible incumbent and LB>=U (one) or LB>U (all); all+EXHAUSTED requires the full minimum-owner set from feasible minima, including the incumbent. No advanced pruning.

Root E0 comes only from exact journal/2 replay via independent P2 modules, with explicit DeletionBudget; scope canonical bytes and SHA-256 bind original traces, IDs, alphabet, journal and root. Empty journal allowed. Byte/entry/node/depth/work/time/exact-check caps fail closed. Work units include Python replay line charges and deletion debit (conservative, not producer work). Strict schema follows the frozen contract: an absent required suffix field is malformed INVALID; a correctly described nonempty suffix is unresolved INCOMPLETE under PARTIAL and contradicts EXHAUSTED. This is a deliberate distinction from informal earlier handoff language about missing suffixes; neither case can be VERIFIED.

## Limitations / integration blocker

- Actual producer replay NOT RUN; exact tiny_choice and small_choice raw/journal/scope/certificate bytes requested from core via issue #2 comment 7159148164. Do not substitute synthetic fixtures. Core HEAD verified again after CI unchanged at fa12fdc.
- Cooperative work/time caps are not hard process RSS bounds. CI enforced RLIMIT_AS 1536 MiB, not a 1536 MiB RSS cap; observed RSS above is separate. External process runner must translate timeout/OOM/killed process into INCOMPLETE without result. C-level JSON parsing and other C operations are bounded by input-byte caps and checked around the call, not interruptible inside every C operation.
- Iterative path reconstruction avoids recursive proof traversal and per-node state snapshots but may repeat work for deep/wide trees. Singleton checking can retain a capped set of projected disequalities from emitted prefixes; no quadratic alternatives pre-materialization. Large fixture establishes symbolic handling with empty prefix, not large complete search scalability.
- Python dict input convenience is not a substitute for strict serialized byte parsing; exact integration should use raw/scope/proof byte inputs. The legacy P2 trace work wrapper is conservative and not a hard external resource monitor.
- No claims about external ACCEPT or operational acceptance. No CROSS_SUPPORT/rank/AEFC/dead-cover, CDAQ, bounded or external integration.

## Coordination

Latest CLI: python -B tests/reference/p3_frontier_verifier.py --make-trusted-scope --raw RAW.json --journal JOURNAL.json --out TRUSTED.json; then python -B tests/reference/p3_frontier_verifier.py --raw RAW.json --journal JOURNAL.json --scope TRUSTED.json --proof CERT.json. Exit 0 VERIFIED, 1 INVALID, 2 INCOMPLETE for verifier. Scope builder writes output only on successful replay. Final native producer gate requires exact artifact bytes, one/all RGS agreement, both modes, and lead review.
