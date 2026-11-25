# Supplementary independent P3 M2 path-reconstruction audit

## Exact pins and scope

Reviewed verifier source at e1d022496f98bf50fd57d5ef3a7a0bc8194c817c (blob a35281492e2677f0c57d8955227bc233d95492ea), frozen contract ff61b1c56138c89fc0ad9a615f0b2a587b03393a (blob 9dd487605f0dfdc6735f7d53a42627039fb57db8), existing RGS oracle blob 375c36bfb2602894ce783055d1edf31f265aafa0. Concurrent proof-session commits are preserved; this supplementary audit adds only independent test code and its report, not a second verifier or production changes.

Audit script: tests/reference/p3_path_exhaustive_audit.py, Git blob bee88b911d4f52d42dd9a0ec8aeb05b485f4ad05. It independently reconstructs equality connectivity using graph traversal and enumerates literal RGS region membership. For every original alphabet size 0..6 and every canonical root partition (including nonidentity roots), it enumerates every child and residual of every nonempty nonsingleton region. It checks exact E owner, representative list, emptiness, singleton classification on nonempty regions, unique minimum cost member, pair_at against combinations, and coverage/disjointness as a literal membership multiset.

## Executed local evidence (Python 3.13.5)

Direct Git access from the execution container was blocked by DNS. I recovered the exact RGS oracle bytes (verified Git blob above) and three target functions pair_at, representatives, path_state from the pinned verifier. The extracted bytes were Git blob ccc099c6ae34c8c7b9880390b2986a7336c573da, independently checked locally. The local harness loaded these exact functions with a lightweight work-counting Budget stub; this is a function-level mathematical audit, not an end-to-end verifier execution and not a resource-budget test. Both normal and optimized modes exited 0; stdout byte-identical. Runtime measurements: normal 1.28 s / 97420 KiB RSS; optimized 2.70 s / 103780 KiB RSS (observed, not a hard limit).

From the full repository, reproduce with the actual Budget implementation:
    
    PYTHONPATH=tests/reference python -B tests/reference/p3_path_exhaustive_audit.py
    PYTHONPATH=tests/reference python -B -O tests/reference/p3_path_exhaustive_audit.py

For exact offline excerpt reproduction, extract the following from the pinned verifier, preserving newlines:

    fragment = text[text.index("def pair_at("):text.index("def compatible(")] + text[text.index("def path_state("):text.index("def verify_frontier(")]

Check the Git blob hash above, then load the fragment into a module named p3_frontier_verifier with need (raise ValueError on false), Incomplete=RuntimeError and Budget (max_depth=10000; debit accumulates work, entries no-op). Inject the module in sys.modules and run the committed audit script with runpy.run_path(..., run_name="__main__"). This harness deliberately does not test budget enforcement.

Verbatim stdout, identical in both modes:

    Bell counts 0..8; independent label enumeration 0..5; region membership checks: 7065
    Structural examples, duplicate/empty/unused symbols, malformed token and caps: PASS
    n= 0 {'empty': 0, 'membership_checks': 1, 'nodes': 1, 'roots': 1, 'singleton_nonempty': 1}
    n= 1 {'empty': 0, 'membership_checks': 1, 'nodes': 1, 'roots': 1, 'singleton_nonempty': 1}
    n= 2 {'empty': 0, 'membership_checks': 8, 'nodes': 4, 'pair_checks': 1, 'residuals': 1, 'roots': 2, 'singleton_nonempty': 3, 'splits': 1}
    n= 3 {'empty': 0, 'membership_checks': 85, 'nodes': 17, 'pair_checks': 7, 'residuals': 5, 'roots': 5, 'singleton_nonempty': 12, 'splits': 5}
    n= 4 {'empty': 5, 'membership_checks': 1350, 'nodes': 90, 'pair_checks': 50, 'residuals': 25, 'roots': 15, 'singleton_nonempty': 60, 'splits': 25}
    n= 5 {'empty': 91, 'membership_checks': 30940, 'nodes': 595, 'pair_checks': 397, 'residuals': 146, 'roots': 52, 'singleton_nonempty': 358, 'splits': 146}
    n= 6 {'empty': 1208, 'membership_checks': 949431, 'nodes': 4677, 'pair_checks': 3476, 'residuals': 998, 'roots': 203, 'singleton_nonempty': 2471, 'splits': 998}
    TOTAL {'empty': 1304, 'membership_checks': 981816, 'nodes': 5385, 'pair_checks': 3931, 'residuals': 1175, 'roots': 279, 'singleton_nonempty': 2906, 'splits': 1175}

## Independent inspection of actual CI

GitHub Actions push run 45591592249, job 139126899455, passed on the pinned implementation, Ubuntu 24.04 / Python 3.13.5. Source pins in the actual log: verifier a35281492e2677f0c57d8955227bc233d95492ea, test 9754dc3e0c21cabfbf8339b598650ddae40bcbdc, oracle 375c36bfb2602894ce783055d1edf31f265aafa0, bounded_deletion e1fc61b6f03484d4428642ca157e2dac43f0572d, journal replay 6c49013e809b5ac4d2b2a37850e6e6cece513072. Normal 10/10 (0.595 s unittest, 0.68 s wall, 26532 KiB RSS), optimized 10/10 (0.811 s unittest, 1.06 s wall, 28224 KiB RSS). Both report 179 literal fixtures, 17 principal certificate mutations plus boundary tests, 43680 direct pair comparisons, 7065 RGS membership checks, and symbolic 199990000 alternatives with 349428 work units. RLIMIT_AS 1536 MiB, RSS observed separately. Separate run 45591575274 also passed and is recorded by concurrent proof session in 72144bb.

## Proof review and limitations

Induction: root E is independently replayed mandatory owner; each child merges exactly its checked pair and carries all earlier checked pairs as false. Projecting every ancestor false pair through the current owner detects precisely the E/D contradiction; for a nonempty region, exact singleton recognition is equivalent to all distinct current classes being separated by such constraints, or being the explicit all-false residual. Every strict coarsening of E has a unique first true pair; E itself lies in the residual. The equality-class cost bound and FEASIBLE_MIN uniqueness follow because strict coarsening decreases class count. All-optima cannot prune at equality.

Current implementation treats a missing mandatory suffix field as malformed INVALID (even PARTIAL), whereas a well-formed nonempty suffix yields INCOMPLETE. The task wording calls a missing suffix INCOMPLETE; integration lead should distinguish missing/truncated evidence from a malformed present certificate before changing the frozen schema. Both cases expose no optimum. Direct dict API can canonicalize tuple-valued scope data as JSON arrays; serialized CLI inputs remain strict about duplicate keys and field values. Recommend JSON-native validation for object callers and explicit work debit for scope/proof parse and metadata; byte limits and cooperative time/work checks are present, but C-level JSON operations cannot be interrupted on every token. No production acceptance or claim of hard RSS/time from the function-level audit.

No producer, producer DSU, cache, ranking or pruning imports in this audit; no learner, baseline, authoritative ledger changes, external calls, or merges. Actual producer tiny_choice/small_choice one/all certificates are NOT RUN (core head fa12fdcca0a8d7a9a697bb617ed09453cb56c3d5 at inspection); request posted to issue #2. P3 integration and operational status remain INCOMPLETE.
