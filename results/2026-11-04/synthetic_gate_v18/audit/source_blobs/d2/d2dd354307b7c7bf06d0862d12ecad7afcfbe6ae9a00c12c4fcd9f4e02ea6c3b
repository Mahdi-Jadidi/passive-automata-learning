# C018 proposed independent controls — no tests executed here

Bind a positive candidate chunk size c; test lengths c−1,c,c+1,2c−1,2c,2c+1
(deduplicate nonnegative lengths). Use the auditor's own small full-family
oracle and preserve actual inputs/source snapshots before any execution.
Descriptions below are mathematical expected outcomes, not measured results.

1. **Chunk accumulation:** a repeated across several chunks must have total
   length count, not last-chunk length. On alphabet ab, P={a^q}, N={a^q b}
   the unary route has all partitions; known_k2 is uniquely singletons.
2. **Late undeclared symbol:** append z outside alphabet ab at the final
   position, especially the first/last position of a chunk. invalid_input,
   including when an earlier negative already disproved unary feasibility.
3. **Late malformed word:** insert non-string list/int/None after valid long
   words. No shortcut may bypass it; invalid_input before final declaration.
4. **Contradiction with known_k1:** identical long positive/negative must be
   incompatible, not unique one-block. Original index references must replay.
5. **Late error after contradiction:** contradictory earlier labels followed
   by foreign-symbol word must follow the baseline's all-validation-first
   invalid outcome, if the computational budget suffices.
6. **Sparse zero:** alphabet ab, P={a}, N={epsilon}. Missing a-count0 must be
   detected. Conversely P={epsilon,a}, N={b} is distinguished by b-count1.
7. **Duplicate presence:** P={a,a}, N={epsilon}; presence must be2 vs len(P)2.
   Mixed dedup/raw counts would incorrectly admit zero for a.
8. **P empty / epsilon negative:** every partition has empty-language factor
   witnesses; m2 default ambiguous, known_k1/2 unique respective partitions.
9. **N empty / P empty / both empty:** all partitions possible. m1 unique;
   positive-only intermediate known count 1<k<m ambiguous, never data-invented
   negatives. Duplicate negatives keep every certificate index valid.
10. **Mixed positive support:** P={ab,aabb}, N={aab}. Unary predicate is false
    even though no positive has the whole negative's Parikh vector. Do not
    replace per-symbol support by full-vector matching.
11. **Unicode:** declared one-code-point é and an astral symbol remain atomic
    Python characters across chunk boundaries. Decomposed e+combining accent
    is not normalized to é; undeclared constituents are invalid. Declared
    whitespace/NUL are characters too; JSON escaping is not deletion.
12. **Empty and unhashable alphabet entries, bool/out-of-range known_k, extra
    truth/count keys:** preserve exact baseline invalid-input contract.
13. **Graph-empty but unique:** abcd, P={epsilon,aabb,ccdd}, N={bbaa,ddcc},
    known_k2 uniquely ab|cd via fallback; noK ambiguous with one-block merge.
14. **Known count insufficient:** parity-style P={epsilon,aa,bb,cc,dd},
    N={a,b,c,d}, known_k2 admits all seven bipartitions; return two witnesses.
15. **Selected partition release:** only certified_unique has top-level
    partition. ambiguous has two distinct feasible models; unresolved releases
    none. Full oracle cardinality, not one feasible witness, validates status.
16. **Deterministic injected polls:** interrupt before scan, at chunk boundary,
    after counting but before emit, and inside fallback. No unsupported
    finality; clock-expired controls are distinct from known invalid data.
17. **Actual expired wall deadline:** unresolved may precede validation and
    does not establish invalidity/incompatibility/data insufficiency. Compare
    completed semantics, not a required identical baseline timeout trajectory.
18. **Long words / few symbols:** retain same input/output contract, all
    certificates, parsing/output cost and three fresh repetitions per frozen
    protocol. Report censored/slow cases rather than selecting only wins.

Further mathematical false-prune counterexample: a partial singleton split
of P={ab}, N={ba} cannot reject the negative, but merging ab can. Do not
prune an RGS node by incomplete current-block rejection alone. The optional
envelope lemma in FASTSCAN_EQUIVALENCE_v1.md requires its exact premises.

For source-order-independent equivalent certificate choices, audit validity,
family and route/status contract; byte identity of diagnostic metrics is not
assumed. If the implementation promises exact certificate order, additionally
compare first-occurrence traversal. No C017 selected-output data/model is used.
