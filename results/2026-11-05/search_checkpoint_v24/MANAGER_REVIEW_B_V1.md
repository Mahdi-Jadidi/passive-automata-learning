# C024-B manager source review v1

Candidate `implementation/candidate_c024b_v1/gate_v1.py`, SHA256 `4e5a8e39528efadf3d2eeaab2dfa02a0d77711d7028005737fe78a42b38cb9a3`, reviewed as a minimal delta on frozen C020, separately from A.

In the canonical RGS DFS, assigned atoms are precisely indices below pos and growing blocks are never subsequently merged. At a nonterminal node U is `full xor ((1<<pos)-1)`, the remaining atom set. Each existing final block is contained in its current mask union U. A new block can exist only if len(masks)<known_k, and any such block is contained in U. Exact reject sets are monotone under block inclusion. Therefore the computed union is an upper bound on negative coverage of every allowed completion. Missing coverage proves no completion exists. Passing coverage never certifies a completion; exact leaves remain unchanged.

Existing count bounds run first, and complete assigned nodes still use exact witness. Deadline polling and resource handlers cover added loops and reject calls. No-K DFS does not invoke the rule. Validation, shortcuts, projection/cache and graph rules are unchanged. Exhaustive returns retain the current route with explicit envelope rule/proof metadata. An ambiguous return is independently supported by its two witnesses and does not require a pruning proof to establish ambiguity.

No correctness blocker found. Additional projections, cache displacement and bound computation may regress wall time; performance requires a separate frozen comparison. Search_nodes counts DFS visits in both baseline/B; envelope_checks/prunes add work counters. Rule does not imply a smaller worst-case Stirling bound.

Authorized independent B correctness and then its separate six-cell timing only after A timing completes and theory source review B passes. B protocol/inputs must be frozen before B timing and must not overwrite A evidence. All outcomes retained. Zero semantic/certificate errors required; material target benefit (>=20% median end-to-end reduction or completion under baseline noncompletion) and A_K4 <=15% median-regression guard apply to automatic promotion. No result currently asserted.
