# B static review of eager: C002-R1

Date: 2026-10-26. Reviewer: research fork B. Scope: A's eager_solver.py and
PROOFS.md, with the promoted common/engine.py and common/helpers.py read for
implementation correspondence. No experiment or external source lookup was
performed for this review. Source hashes are recorded in REVIEW_A_MANIFEST.json.
This review does not replace the independent empirical audit or verify the
bibliographic attribution afresh.

## Decision

No substantive correctness defect found in the stated model. The code preserves
the shared rejecting side for each negative and, on complete termination,
enumerates the whole feasible partition set. Acceptance of empirical correctness,
performance and reproducibility remains with the independent auditor and master.

## Shared rejecting side

For one negative n, code initializes side_terms = [[], []]. For every positive p
it appends T_s(n,p) to the list for that same s. After all positives, it constructs
OR_s AND_p T_s(n,p). Thus the side is selected outside the conjunction over
positives, exactly as PROOFS.md Section 3 requires. A different side is allowed
for a different negative. The code does not use the unsound AND_p OR_s weakening
documented in REJECTED_IDEAS.md.

The reconstruction proof in Section 2 is valid: singleton projections fix letter
counts. For unequal words with these counts, neither can be a proper prefix of
the other. After their longest common prefix, the distinct next letters a,b make
the {a,b} projections differ immediately after the common projected prefix. For
any proposed block B this argument applies to the B-projected words. Therefore
different B-projections have a distinguishing singleton/pair contained in B.
Pairs containing a distinguishing singleton are redundant because that singleton
already suffices whenever the pair is contained in B. The helper follows this
rule. side_distinguishes encodes precisely the existence of such a subset.

## Complete F2 and witnesses

The feasibility criterion is both necessary and sufficient with unrestricted
regular factors: accept exactly the finite sets of observed positive projections.
Every negative must then have an unseen projection on some block. Thus the eager
formula is exact, rather than only a necessary filter. Additional graph equalities
rely on the frozen baseline soundness argument; this review does not re-prove
that graph theorem.

The shared engine fixes the first symbol's owner to zero and excludes all-zero
ownership, so each unordered nonempty bipartition has exactly one representation.
It traverses all assignments not pruned by a false three-valued constraint;
structural induction on the expression gives sound partial pruning. Unknown
constraints do not prune. There are no auxiliary witness variables. Consequently
each satisfying complete ownership assignment is yielded once, and every feasible
partition is reached. The provider invokes partition_record on every yielded
assignment and raises an assertion on an unexpected infeasible one; it never
silently drops such a model. Witness records contain the positive projection
languages and an actually unseen negative projection. result_from_records sorts
records without replacing full enumeration by one representative answer.

Empty positive and negative classes give the correct vacuous conjunctions.
Baseline validation sorts/deduplicates samples and rejects contradictory labels.
Symbols absent from observations remain ownership variables. No state bound or
target-generator information enters this encoding.

## Interruption and reporting limits

The provider catches cooperative SearchInterrupted/KeyboardInterrupt within its
enumeration block and returns only stored feasible records with complete=false,
status=incomplete and a null exact count. It cannot claim uniqueness/infeasibility
from that partial set. Validation occurs before that catch and result construction
after it; a hard process kill or interruption outside the caught region need not
produce a JSON result. The external runner must preserve that execution outcome.

preprocessing_seconds for eager includes graph and complete formula construction.
Lazy's equally named field covers a different phase. Compare methods using the
external end-to-end measurement including parsing, all phases and output; provider
timing alone does not include CLI serialization. Output can itself contain
2^(m-1)-1 partitions, so sound pruning provides no general speedup guarantee.
