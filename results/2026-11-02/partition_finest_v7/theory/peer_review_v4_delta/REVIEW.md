# C007-T005: stable staged-swap V4 delta review

Static only; no provider import, solver call, experiment, benchmark or runtime
edit. Source and CLI match master's hashes, with exact snapshots in MANIFEST.json.
The prior V3 review remains unchanged. V3's 436 accepted outputs do NOT constitute
V4 acceptance; the fresh independent gate and scale results remain pending here.

## Decision

No blocking mathematical defect identified in the staged shortcut or fallback
delta. It instantiates STAGED_SWAP_SHORTCUT_PROOF_v1.md without new assumptions.
One instrumentation finding must be reflected in reporting (below). Existing V3
partial-result preservation/async-interrupt caveats are not fixed by this delta.

## Swap detector is exact

_swap_only_edges (480–505) compares positives only to negatives of equal length.
It records the first mismatching positions and rejects immediately on a third.
A recorded edge requires exactly two adjacent mismatch positions, unequal
positive letters, and reversed matching negative letters. When exactly two
mismatches remain, the loop has inspected the whole word; every other position
was equal. Hence the stated negative is EXACTLY that adjacent swap. A third
mismatch cannot belong to an adjacent-swap witness, so the early exit is sound.
Same pair repeated across observations can retain one genuine context witness.
No approximate hashes or inferred independence relation are used here.

_components_from_edges retains all declared symbols, including isolated ones.
_direct checks the whole candidate component partition. If successful, all its
blocks are forced by supplied sound edges and the partition itself is feasible;
the existing T4 theorem proves unique finest. It does not matter whether rescue
would supply additional edges. A missing edge is not a correctness gap for a
SUFFICIENT shortcut. One component means one_block_only, not absence of a model.

## Gating, proof replay and unchanged fallback/reference

The staged path runs only for mode=adaptive. Every other mode delegates to the
old function, which retains its mode validation. Reference still executes the
same full graph and full binary reference path. The diff renames old solve to
_solve_full_v3 but changes no search/verifier code in that body; METHOD metadata
is the only global change affecting its result tag.

The new early result uses the SAME must_link_components_compatible certificate:
exact supplied edges, reconstructed components and complete direct witness.
Existing verify_result replays labels/swap roles and checks component/witness
identity, so graph extraction need not be exhaustive. Metadata records
preprocessing_path=swap_only_stage and fallback_used=false. This certifies the
sample-finest target, not real hidden factor count or true local languages.

If _direct fails, no ambiguity/finality decision is made from the sparse graph.
_solve_full_v3 runs with the ORIGINAL absolute deadline and original data.
It re-extracts the full graph and, if necessary, initializes adaptive meet at
one-block; the sparse component partition never becomes a forced upper meet.
Reference and early ambiguity/complete-cover semantics thus carry over. C006
enhanced A/B remain inactive. The wrapper does not silently grant a new time
budget on fallback, though the additional stage can consume time before it.

Stage KeyboardInterrupt/_Stop returns incomplete without a finest assertion.
The validation region, some built-ins and final serialization retain cooperative
deadline limitations; no strict wall-preemption guarantee is added. Full result
finality must not be inferred from partial outcomes or a preprocessing counter.

CLI V2 imports V4 and keeps adaptive/reference selection and finite nonnegative
duration validation. It restricts --max-solutions to reference in the CLI, labels
truncation incomplete, and uses the existing complete-result/invalid/runtime
exit codes. Real-system membership/equivalence queries are not introduced.

## P3 — instrumentation boundary on fallback (not a mathematical defect)

At line 573 the wrapper runs the FULL fallback, and only AFTER it returns sets
swap_stage_seconds=perf_counter()-start (578). That field therefore includes
initial validation, swap stage AND the fallback, not isolated swap-stage time.
Meanwhile fallback metrics.provider_seconds was measured from the fallback's
own later start, so it excludes successful completion of the initial failed
shortcut stage. The two fields are neither disjoint additive phases nor the
same full provider-clock boundary as a shortcut-success result.

If this version remains frozen, do not publish swap_stage_seconds as preprocessing
time or fallback provider_seconds as total V4 runtime. External fresh-process
wall time includes the complete pipeline and can remain authoritative. A future
metric correction would require a new source/version/gate as directed by master;
this review changes no code. Missing fast-path counters are absent, not measured
zeros. Timing alone cannot establish which phase caused an observed difference.

## Preserved negative result and limitations

The reported V3 m16/length65536 case hit its 28-second cooperative deadline in
inherited full graph preprocessing. That measured negative remains a V3 result;
V4's mathematical early-return justification does not solve the long case by
itself. Its swap comparison worst case still examines many positive/negative
word pairs, direct checks/output can be large, and fallback adds work. No V4
long-case success, speed ratio, scale ceiling or independent acceptance is
claimed here. Wait for captured/regated results, and preserve censored outcomes.
