# C026 implementation v1

`recommend_v1.solve(data, *, deadline=None, memo_limit=100000)` consumes exactly
alphabet/positive/negative, without known K. Deadline is absolute perf_counter.
`python cli_v1.py INPUT --recommend max-blocks --seconds 5 --memo-limit 100000`
provides the opt-in CLI; public dispatch remains manager-owned.

Validation finishes before any feasible witness is published. Adjacent labelled
transpositions force same-owner atoms as in frozen C024. Projection rejection
masks compare with all original positives (C009 T1). The anchored max-plus
recurrence is C009 T2 with maximum instead of exact-count summation. Each entry
retains at most two canonical distinct optimal partitions; this both saturates
the tie count at two and supplies reconstruction choices. Sorting their RGS in
sorted symbol order selects the canonical least optimum, including interleaved
forced atoms. U-empty selects singleton atoms; uncovered negatives outside the
remaining union rejection mask are impossible by rejection monotonicity.

The memo quota counts completed and reserved in-flight DP entries. Rejection
LRU is capped at 4096. No caches cross solves. Only fully replayable constructed
witnesses replace the incumbent. An interrupted reconstruction never publishes
optimality or a tie conclusion. A nontrivial incumbent plus the one-block
witness proves unrestricted ambiguity even while computation is incomplete.
Optimality and tie claims concern the recommendation convention, not physical
device count or unrestricted uniqueness. Upper bounds begin with symbol/forced
atom count and decrease by one after the sole atom partition fails.

Developer smoke files are controlled checks only, not independent audit or
performance evidence. No real data or timing experiments were run.
