# C010 independent no-K audit protocol — v1

## Scope and dependency gate

Work and artifacts are confined to C010 `audit/`. This audit removes all external component-count constraints and tests only the declared C010 model: known nonempty alphabet, independent arbitrary regular local acceptors on disjoint blocks, exact complete-word labels, no state/prime restriction. It does not modify C009, implementation, theory, shared coordination, Git, or the presentation.

The implementation directory is empty at preregistration. The independent oracle/corpus may proceed now. Provider execution is blocked until the master supplies a concrete frozen no-K API/CLI schema and source hashes. The main C010 provider comparison is itself the independent correctness gate; no circular precondition that another runtime gate already passed is imposed.

## Mathematical invariants to audit

For every valid label-consistent sample `S=(P,N)`, the one-block partition is compatible: choose the single regular language `FΣ=P`, a finite language; because `P∩N=∅`, it accepts every positive and rejects every negative. Thus every valid sample has at least one compatible partition, and any compatible partition's coarsening to one block is compatible (merge factors by inverse projections/intersection, preserving regularity). Consequences for the unrestricted version space:

* `model_inconsistent` is impossible for a valid, label-consistent input; conflicting/malformed input is `invalid_input`.
* Every symbol pair has a same-block witness (the one-block partition). `forced_different` is impossible whenever the version space is nonempty.
* A singleton compatible-partition family can only be the one-block partition. No multiblock physical ownership or true `k>1` is identifiable under this unrestricted class from a finite sample alone.
* `kmax`, the largest block count in the complete compatible family, is a certified upper bound for the true count conditional on the true model belonging to this class. It is not an estimate or unconditional physical fact.

The exact finite-sample feasibility criterion is independent of K: every negative must be rejected by at least one block, where the block's finite positive projection set is its witness regular language. Oracle counts are counts of distinct partitions, not DFA tuples and not probabilities.

## Frozen small-case corpus

Derive cases from the C009 frozen 129-case corpus with manifest SHA-256 `bd4c76b389d87887504f624248940d9bb1d65d69542bca4c01da0714f5200fa1`: remove both `allowed_k` and legacy `k` from every payload, then deduplicate by canonical payload JSON. Preserve source-case IDs, raw input hashes, and every duplicate-to-retained mapping. The pre-protocol read-only count is 125 unique derived payloads; add named controls below without replacing source records. Keep at least 100 unique valid payloads, alphabet sizes 2–7, and the original finite words. No hidden partition is planted.

Named controls must be included (deduplicating only by exact payload and recording aliases):

1. Historical graph-empty doubled-pairs: `Σ=abcdef`, `P={ε,aabb,ccdd,eeff}`, `N={bbaa,ddcc,ffee}`. Direct proof: every pair `ab,cd,ef` must stay together; all coarsenings of those three pair-atoms are feasible. Unrestricted count spectrum is `k=1:1, 2:3, 3:1`; five total. Within-pair is forced same; cross-pair is ambiguous with same count 2 and different count 3.
2. One-block-only: `Σ=ab`, `P={ab}`, `N={ba}`. The split block projections match the positive on both sides, so only the one-block partition is compatible.
3. Default positive-only sample: `Σ=abc`, `P={ab}`, `N=∅`; all Bell(3)=5 partitions are compatible.
4. No-label boundary: `Σ=abc`, `P=N=∅`; all five partitions are compatible.
5. Nonempty consistent boundary with unused symbols/epsilon from C009.
6. Forced-same and other-pairs-ambiguous sample from C009 (`Σ=abc`, `P={ab}`, `N={ba}`).
7. Former known-k forced-different counterexample after K removal (`Σ=ab`, `P={ab}`, `N=∅`): the pair becomes ambiguous, not forced-different.

Invalid controls include stale `allowed_k`, stale `k`, empty alphabet, duplicate alphabet symbols, conflicting labels, and out-of-alphabet symbols. C010 input has only `alphabet`, `positive`, and `negative`; stale count fields must not silently restrict the version space.

## Independent exact oracle

For every valid input, enumerate every canonical RGS partition directly for all `m≤7` (Bell(7)=877 maximum), apply the direct projection-feasibility criterion, and save the complete compatible set, exact total and per-k spectrum, kmax, all pair same/different counts, relations, and concrete witnesses for every relation that occurs. Independently replay witnesses using finite positive projection languages. Do not use provider code or block-mask DP in the oracle.

For valid nonempty unrestricted data, require `Z≥1`, `C_1=1`, all pairs `q_ij≥1`, and no `forced_different`. For positive-only and no-label data, require `C_k=S(m,k)` and `Z=Bell(m)`; `q_ij=Bell(m−1)` for each pair. For the doubled-pairs control, verify the five coarsenings above; a graph-empty result is not evidence of no semantic must-links.

## Provider gate after API readiness

Once the master supplies concrete API/CLI/schema and frozen source hashes, preregister the exact invocation before running it. Capture provider/runtime, exact input, C010 contract, frozen protocol, and helper snapshots. On small cases use full enumeration mode if available, and compare complete partition sets exactly. Compare per-k counts, total, kmax, all pair counts/relations, and witnesses. If the API provides only counts by default, do not expect or claim a default full listing; request `--enumerate` for this gate. Independently reject any `forced_different`, impossible empty valid model, or multiblock singleton answer. Preserve every failure and stop acceptance on the first mismatch.

Expired-deadline and interruption controls remain pending the actual API. Require `unknown`/`complete=false`, no final exact count/ownership claim, preserve raw streams, and confirm child cleanup. No outcomes or command schemas are fabricated before readiness.

## Later scale gate (only after small gate passes)

Exactly four correctness-only cells are preregistered for a later, separately frozen protocol; each has a 30-second hard cap and is run once, with incomplete output censored and never rerun:

* m=14 paired atoms with unrestricted K: oracle by quotienting to r=7 atoms, enumerating Bell(7)=877 partitions; total Bell(7)=877, within-atom coownership 877, cross-atom coownership Bell(6)=203.
* m=64, eight proved connected must-link groups (eight atoms): oracle counts from Bell(8)=4,140 and Bell(7)=877; no Bell(64) enumeration. Default output is count/witness mode without full listing.
* Graph-empty doubled-pairs at m=10 (five atoms): exact coarsening oracle Bell(5)=52; per-k `S(5,k)`, within-atom same count 52, cross-atom same count Bell(4)=15.
* Separate long-word case: `Σ=abcd`, `P={a^2048 b^2048}`, `N={b^2048 a^2048}`, no K. The split of a,b is incompatible; the exact family is the coarsenings of atoms `{ab},{c},{d}`, hence Bell(3)=5 answers. Within `ab` coownership is 5; every cross-atom pair coownership is Bell(2)=2. The independent oracle still enumerates all Bell(4)=15 symbol RGS partitions before filtering.

The atom-family oracle is exact only after independently replayable proof that every compatible partition coarsens the atoms and the atom partition itself is feasible. No Bell(64) enumeration, official timing benchmark, or general speed claim is authorized. Record exact preprocessing/mask/DP state/branch counters and one-run cost only, with all preprocessing included.

## Provenance anchors and current state

* C010 contract SHA-256: `4e4b5f1c29d604774b4e19ac62b75554221dd821ab1c2b435029c3c48df884fe`.
* C009 source corpus manifest SHA-256: `bd4c76b389d87887504f624248940d9bb1d65d69542bca4c01da0714f5200fa1`.
* C009 theory proof reference SHA-256: `11aa7b5e0c9caaa024e1aaf9765929b8b9f1d64146afce532daa20413c9438d4`.
* Copied capture helper SHA-256: `68ee700f391fb6a1cf135e4b55a11a247b45f25164553c917d1664f6fc4a31cf`.

Current state at freeze: no provider/API exists in C010 implementation; no C010 provider call has been made. Stage A independent corpus and oracle proceed; provider gate is pending readiness.
