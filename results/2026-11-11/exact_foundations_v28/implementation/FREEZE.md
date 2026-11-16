# C028 implementation freeze v1

Biggest overlooked point: finite mathematical termination is not a promise that available memory or a deadline is sufficient, and an optimum is not a physical truth claim.

`reference.py` SHA-256: 5F60B27447B37EC07F1FD6BCE75BE6199B898573D4B32E90413E900E3A615A94. Frozen for independent audit; do not alter in place without a versioned repair and fresh hash.

Interface: `solve(data, *, max_candidates=None)` with schema from SPEC plus AMENDMENT_1. `max_candidates` is an optional nonnegative candidate budget; exhausting it produces INCOMPLETE and null mathematical fields. Python integers provide arbitrary-precision counters. Generation is iterative, lexicographic RGS. No DP, atom contraction, greedy decision, pruning, or external libraries.

Developer smoke run used local Python 3 and exercised empty alphabet with and without a negative, quantifier-order example, optimal-versus-compatible uniqueness, multi-character symbols, and a one-candidate interruption. Outcomes matched expectations. These are preliminary smoke checks, not the independent audit or an official provider experiment. The independent auditor must inspect the source, replay witnesses and verify counts before any official run.
