# Integration review 04 — post-hardening regression checkpoint (2026-11-25)

## Disposition
Historical narrow P2.1 PASS at core c5e7e17 applies only to prior proof executable 8376243. Current post-hardening combined gate remains INCOMPLETE; P3 implementation HOLD until repinned full gate passes. Operational INCOMPLETE. No external calls, learner/baseline changes or merges.

## Independently inspected GitHub state
Read NEXT_SESSION_HANDOFF_04.md (380ea030), PROJECT_HANDOFF.md and SELECTOR_V2_INDEX.md (44ac8cd), research/INTEGRATION_REVIEW_03.md (d6daba5), and latest #10 comments including 7145645271. Compare each branch ref to recorded SHA: identical, 0 ahead/behind.
- #2 core research/v2-implementation-core c5e7e170add6f92e129099bf7444f5fd7a29eb3a, PR #7.
- #3 proof research/v2-proof-audit cf5a007571853b6cdf6259fa2a9a95f5c1e351f8, PR #8.
- #4 benchmark research/v2-benchmarks 52d21e672b0ae6420cf677ff09c01bb2a3fd6b05, PR #9.
- #5 interface research/v2-interface-audit ae04a28304507fa16830fcb470f52103d9a588c4, PR #6.
All PRs open/draft/unmerged. Changed path inventories: 32 core, 29 proof, 42 benchmark, 34 interface; confined to selector_v2, progress, research/audit, tests/reference, benchmarks/v2, research/interface. Proof compare 8376243..cf5a007: 15 commits, 2 changed executable files plus docs/log. Interface compare 0eb1050..ae04a28: one docs-only commit. Core runner blob 641aa8e9395dbc7ec8d62be731909fc16a0f3a98 still pins 8376243, 64eda7d13b3153175f09b70e41be66e1615846b2, 2f59257d0ff3396417c2cedf9845f61e2fd20928. No current repinned combined result.

## Lead's newly executed isolated regression
Fetched tests/reference/bounded_deletion.py and test_bounded_deletion.py at cf5a007, reconstructed exact files, verified git hash-object e1fc61b6f03484d4428642ca157e2dac43f0572d and 6de549b9b4d208be99a419c88fd903a1ce1a6dcc. Local git ls-remote fails DNS (Could not resolve host github.com), not clean CI. Isolated independent_replay.py contains ONLY identical extracted InvalidProof(ValueError) and require(condition,message) definitions from source blob aa09243fa7ccc941c37609e959aefb419075df32; no full verifier imported. This is standalone checker regression, NOT full journal replay. Python 3.13.5. Commands for both normal and -O:
```sh
git hash-object bounded_deletion.py test_bounded_deletion.py
timeout 30 /usr/bin/time -f 'wall=%e maxrss_kib=%M exit=%x' python -B -m unittest -v test_bounded_deletion
timeout 30 /usr/bin/time -f 'wall=%e maxrss_kib=%M exit=%x' python -B -O -m unittest -v test_bounded_deletion
```
All 6 tests passed both modes: duplicate positive dedup/entry cap, exhaustive all owners and forced collisions, long diverse trace, missing/extra/duplicate conflict rejection, random duplicate positives/negative conflicts, work/entry/length/deadline caps. Actual normal 0.349s tests, wall 1.38s, RSS 109848 KiB, exit 0; optimized 0.424s tests, wall 2.63s, RSS 112660 KiB, exit 0. Both: 4374 corpus-owner cases, 13122 filter checks, 500 random collision cases, 20000 long symbols/20001 entries/2 exact checks/200010 work. RSS is observed, not RLIMIT_AS. No recovered huge cases run here.

Additional lead probe (literal oracle from exact test file; random seed 20261125), executed normal and -O, outer timeout 30s:
```python
import random
from bounded_deletion import check_exhaustion, DeletionBudget
from independent_replay import InvalidProof
from test_bounded_deletion import literal_deletions
rng=random.Random(20261125)
checks=mutations=conflicts=0
for case in range(2000):
    n=rng.randrange(1,9)
    p=tuple(rng.randrange(n) for _ in range(n))
    X=[tuple(rng.randrange(n) for _ in range(rng.randrange(21))) for _ in range(rng.randrange(1,12))]
    Y=[tuple(rng.randrange(n) for _ in range(rng.randrange(21))) for _ in range(rng.randrange(1,12))]
    try: facts=literal_deletions(X,Y,p)
    except InvalidProof:
        for bits in (0,1,7,64):
            try: check_exhaustion(X,Y,p,set(),DeletionBudget(seconds=5),hash_bits=bits)
            except InvalidProof: conflicts+=1
            else: raise RuntimeError('duplicate accepted')
        continue
    for bits in (0,1,7,64):
        check_exhaustion(X,Y,p,facts,DeletionBudget(seconds=5),hash_bits=bits); checks+=1
    for bad in ([facts-{min(facts)}] if facts else [])+[facts|{(len(Y),0)}]:
        try: check_exhaustion(X,Y,p,bad,DeletionBudget(seconds=5),hash_bits=0)
        except InvalidProof: mutations+=1
        else: raise RuntimeError('mutation accepted')
print(f'seed=20261125 cases=2000 valid_checks={checks} duplicate_conflict_rejections={conflicts} mutation_rejections={mutations}')
```
Both modes output: seed=20261125 cases=2000 valid_checks=6800 duplicate_conflict_rejections=1200 mutation_rejections=2482. Normal wall 1.98s RSS 101356 KiB exit 0; -O wall 3.11s RSS 106212 KiB exit 0. This does not substitute for actual outer verifier or establish hard memory bound.

## Required current gate
Core #2 owns repin HEADS.proof cf5a007 and the two exact new PROOF blobs; retain unchanged source pins; fresh combined normal/-O with exact byte-verified source snapshots and logs, expected 43/31 if otherwise unchanged, four actual published artifact hashes/costs unchanged, 31 counted corruptions, five caps and partial fail-closed. Proof #3 independently verifies actual executed hashes and full replay; benchmark #4 independently reruns suites and exact hardened huge cases at 30s/1536 MiB, both modes, raw closure and full journal separate, 512 MiB if feasible. Interface #5 preserves authoritative delegation and prepares selector-side contract tests. Large-case completion not a new prerequisite for narrow structural P3; resource failures must be INCOMPLETE. No additional arbitrary gate.

## Conditional P3 authorization (not active)
After repinned combined gate VERIFIED and independent proof review, lead authorizes unrestricted structural/reference EDR-BB only; B=0. Region R(E,D), mandatory quotient root, sound necessary disjunctions, unique-first-true disjoint child coverage, residual preservation, rollback DSU and branch-local D, lazy restartable frontier. Generic all-pair fallback excludes only exact representative and covers strict coarsenings; UNKNOWN remains pending. Base n-|E|, no double-counted mandatory unions, no unproved pruning or canonical merge-parent rule. One optimum prune bound>=incumbent only with verified structural witness; all-optima strict >. Independent region/frontier replay and exhaustive literal RGS oracle; invalid or resource-incomplete never proof. Seven raw-only fixtures, evaluation references isolated. No P4-P7, live/bounded optimization or external acceptance. Commit/push validated milestones with commands, hashes, full logs, caps, statuses and limitations; keep drafts unmerged.
