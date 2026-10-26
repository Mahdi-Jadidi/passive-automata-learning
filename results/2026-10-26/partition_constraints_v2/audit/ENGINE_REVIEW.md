# C002 shared engine review

Decision: **accepted for coordinator promotion at the exact source hashes recorded in `engine-review.json`.** This decision covers `engine_candidate.py` and `common_helpers_candidate.py` only. It does not approve either solver provider or claim a performance improvement.

The review used a separately written reference checker and a captured run (`20261026T093916.601359Z_bbdb4b94fc`). The exact commands, raw output, Python environment, candidate snapshots and SHA-256 hashes are in that attempt directory. The reviewed candidate hashes agree with A's candidate manifest.

The independent checks covered 11,934 three-valued expression evaluations, 608 constraint-set enumeration comparisons, all completions of every tested partial-false expression, and first-model ordering. For the helper routines, 1,600 word pairs over `abc` through length three were checked against all seven nonempty blocks (11,200 equivalence checks). Six graph equalities, 13 validation/graph examples, and 13 complete feasible-set comparisons against the unpruned frozen baseline also passed. Each returned negative witness was checked directly against all positive projections for that block. The baseline loader worked after changing the current directory.

The engine follows the fixed lexicographic variable order, excludes the all-zero ownership, and emits each canonical nonempty bipartition once. Three-valued evaluation treats unknown as non-pruning and implements empty AND/OR correctly. Helper outputs match the frozen baseline on reviewed cases, while direct projection feasibility agrees with its unpruned enumeration.

The bounded review is not a substitute for the full eager/lazy comparison. Provider equality over every frozen sample, witness validation across that corpus, interruption behavior under an external timeout, and repeated timing/memory runs remain open audit gates. The shared engine is cooperative about deadlines; the external runner must enforce hard process limits.
