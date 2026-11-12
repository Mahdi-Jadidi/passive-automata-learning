# V33 exact candidates: integration skeleton

**PENDING:** independent audit and official timings. This skeleton does not assert correctness beyond the scoped proofs and source reviews, does not report speedup, and is not a recommendation to change any default.

## Objective and invariant contract

Compare the unchanged C028 full-output baseline and the two frozen candidates on identical input and output contracts: normalized opaque IDs and complete positive/negative words, epsilon and empty alphabets, C (all compatible partitions), k* (maximum block count), O (optimal ties), first two ordered witnesses per family, factor and first-rejector serialization, statuses and replay. Explicit `max_candidates` calls delegate to C028 in both candidates; they are not DP-state or contracted-partition budgets. Incomplete execution is not an exact result. These are sample-consistency claims rather than physical identification.

## Frozen candidates and proof scope

- **Subset DP:** [source](../candidate_dp/candidate.py), SHA-256 `8EC5B68A08D9EC430C0BF5F10D86024408C3BB9408A4045F7EFB41EED6E5F86F`; [proof](../candidate_dp/PROOF.md), SHA-256 `37E99838EE8B869ACDE908191819DD31B3B173E5024A0017B0EB1CB7E0A80623`. Coverage-state counts and exact RGS-prefix feasibility reconstruction; reference helper dependency is hash-checked. Exponential states and repeated prefix-query costs remain.
- **Forced-pair graph:** [source](../candidate_graph/candidate.py), SHA-256 `71204F44840353AD5BD1F1BBFBB6365F6AABDA5FFF788F335AE788928F7CC242`; [proof](../candidate_graph/PROOF.md), SHA-256 `C40BF6F290003D1B92703387823286952F0AC0AFA54D7435523EA2298A76B62D`; [source/proof review](../candidate_dp/REVIEW_GRAPH.md). Sound must-link contraction; a successful component compatibility test certifies all coarsenings and Bell count, otherwise all component partitions are checked. Component numbering and expansion preserve full-alphabet lexicographic order. Exponential fallback and extra graph preprocessing remain.
- **Baseline:** C028 reference SHA-256 `5F60B27447B37EC07F1FD6BCE75BE6199B898573D4B32E90413E900E3A615A94`. C030 optional optimizer may be included as an additional named comparator only if it is in the official audit protocol; no public default is changed.

## Independent review and correctness audit

**PENDING:** insert reviewer verdicts and exact source/proof hashes, independently generated test corpus, full-output equality and independent witness-replay results, invalid/budget edge checks, retained failures and repairs. Separate developer smoke checks from independent evidence. Do not label an interrupted run compatible, incompatible, optimal, or counted.

## Performance comparison

**PENDING:** insert the auditor's approved protocol, fixed corpus and hashes, exact commands, runtime versions, fresh-process repetitions, output equality checks, raw measurements and summary statistics. Report preprocessing and witness construction in end-to-end time; distinguish each candidate, baseline and any optional C030 comparator. Note timeouts, resource failures, hardware/environment, memory if measured, variance and the small-sample limits. Neither asymptotic argument nor one favorable case proves universal superiority.

| Dataset / condition | Baseline | Subset DP | Forced-pair graph | Scope and verified output |
|---|---|---|---|---|
| Pending audit | Pending | Pending | Pending | Pending |

## Conclusion and decision

**PENDING:** state only findings supported by the final audit. Distinguish mathematical equivalence, completed empirical correctness, observed speed on named cases and a general runtime guarantee. If no candidate is faster under the requested fair conditions, state that directly. Identify unresolved risks and retain the existing default unless separately authorized.

## Review and artifact manifest

**PENDING:** bind final integration, candidate, proof, review, corpus, raw data and audit report SHA-256 values after audit. The largest overlooked issue is that fast maximum-only results or partial output are not comparable to C028's full count, canonical witness and serialization contract.
