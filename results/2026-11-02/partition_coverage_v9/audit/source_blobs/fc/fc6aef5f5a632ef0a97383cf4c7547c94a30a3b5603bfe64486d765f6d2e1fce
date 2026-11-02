# Targeted count-vs-ownership addendum — v1

This is supplemental to the immutable 129-case Stage-A corpus and does not change its manifest or provider-batch order. It was suggested by the theory handoff to make the distinction between a known/identified block count and identified ownership explicit.

Frozen input `feasible_count_not_unique_ownership_v1.json`: `Σ={a,b,c}`, `P={ε,abc}`, `N={a}`, `allowed_k=[2]`. The direct oracle must return exactly `{ab|c, ac|b}`. Thus exactly two compatible components is known, but no pair is forced same; `b,c` are forced different, while `a,b` and `a,c` are ambiguous. This tests the claim on sample-compatible partitions only and uses no planted hidden partition.

After the primary 129-case gate is accepted, invoke the **public root wrapper** exactly once on this same input, with a 20-second cooperative and 25-second capture limit. Independently compare its full enumeration, exact pair counts/relations, and witnesses with the frozen addendum oracle. Snapshot wrapper and provider source bytes. This is a one-case CLI integration control, not a scale cell or timing experiment. Do not run it if the primary gate fails.
