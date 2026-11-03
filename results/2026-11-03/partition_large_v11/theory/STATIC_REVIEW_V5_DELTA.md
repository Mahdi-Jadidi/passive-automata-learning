# C011 readiness V5 — final None-guard delta

Disposition: **STATIC CLEARED FOR INDEPENDENT EXECUTION GATE**.
No runtime correctness or performance acceptance is implied. Theory executed
no provider and changed no provider source. Prior failed source/review remain.

Verified authoritative hashes before comparison:

* solver v3: 42726e740198787645783acefd1fa06f6490ec16d609ef07d22cbfafd34a00fa
* CLI v3: 169d7d468a5e3d8a0ba93b686ccb2b058ba231fa1b8e85150d5840df4fec563c
* protocol V3: 73a89169040d0d2bfe678f9d4f54dbd214de700c1e791364449dbc289eb792f7

The solver was compared to the immutable previously reviewed snapshot with
hash 699f88004cc12201642eccb801fde5a0f6a720b063815a99032cac078fa29ba0.
The only solver delta is guarding both optional pair-witness results:

    candidate = find_partition(k, ai, aj, wanted_relation)
    if candidate is not None:
        relation_witness = intern_partition(candidate)

When a relation has no witness at this k, the variable stays None and the
loop correctly continues to later k. When a valid partition exists, it is
interned exactly as before. Counts, relation classification, search constraints
and default expanded fields do not change. Thus the None iteration TypeError
identified in STATIC_REVIEW_V3.md is removed without weakening completeness.

On the preserved mathematical input Σ=abc, P={ε,abc}, N={a}, the different
witness query at k=1 now returns None without interning; at k=2 it can recover
ac|b for pair a,b. This is direct source reasoning, not a claimed run.

The CLI imports unrestricted_solver_v3, binding the frozen corrected module.
No additional RLE/hash/cache/DP feature delta was found. The previous bounded
review of those paths remains applicable. Accepted incomplete status contract,
shared read-only Python witness lists, entry-count-only LRU bound and scoped
metrics remain known nonblocking limitations; no extra churn is requested.

Action: proceed with the frozen-source independent full-set/count/pair/witness
gate and preserved regression input. Runtime, collision-injection, interruption
and performance acceptance are separate evidence owned by the auditor.
Snapshots and hashes: static_review_v5_delta/MANIFEST.json.
