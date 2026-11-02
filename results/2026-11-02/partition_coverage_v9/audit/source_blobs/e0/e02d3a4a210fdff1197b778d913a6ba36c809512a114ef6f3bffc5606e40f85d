# C009 independent audit protocol — v1

**Frozen scope:** independent small-case oracle and correctness corpus only. This audit writes only under C009 `audit/`. It does not modify or infer provider code, shared coordination files, theory, public documents, or Git. No hidden generating partition is attached to cases or used to assign expected labels.

## Question and semantics

Input is a finite known alphabet `Σ`, finite disjoint positive/negative sets `P,N⊆Σ*` of complete words, and optionally a trusted list `allowed_k⊆{1,…,|Σ|}`. Omitted `allowed_k` means all nonempty block counts. A partition is compatible iff every positive projects into each local positive projection set and every negative has at least one block whose projection is absent from that block's positive projection set. Factors are arbitrary regular local acceptor languages; no state bound, noise model, RPNI behavior, or hidden target partition is assumed.

The independent oracle directly enumerates canonical restricted-growth strings (RGS) for all alphabet partitions, checks projection feasibility from the fixed labels, then filters by `allowed_k`. It does not call or reuse the provider's dynamic program. For each case it records the complete compatible partition set, exact count and block-count histogram, and for every unordered symbol pair:

- number of compatible partitions that co-own the pair;
- relation: `forced_same`, `forced_different`, `ambiguous`, or `model_inconsistent` when the feasible set is empty;
- a concrete compatible RGS witness for every relation side that exists.

An empty feasible set is model inconsistency, never vacuous universal ownership. Pair relations are derived from the complete enumerated set. Oracle witnesses are independently replayed by a second direct projection checker.

## Frozen random corpus

- Seed: `20261102`, Python standard-library `random.Random`.
- 120 unique random payloads: 20 for each alphabet size `m=2,3,4,5,6,7`.
- Words use the declared alphabet, include possible `ε`, and have length at most 5. Positive/negative labels are sampled without conflict; cases are not generated from a planted partition or hidden automaton.
- Constraint modes are interleaved where possible: omitted/default all k, singleton/exact k, contiguous allowed-k list, and noncontiguous allowed-k list. Every allowed value is within `1..m`; for `m=2`, a noncontiguous list is impossible and omitted.
- Uniqueness is defined on canonical payload JSON, not case ID or metadata. The freeze manifest records every input SHA-256 and the random-generation rule.

## Frozen named controls

1. Historical graph-empty doubled-pairs sample; default all k.
2. Same sample with `allowed_k=[3,4]`; its known mathematical proof forces `ab|cd|ef`, so the sample-compatible maximum k is 3 and the constraint leaves that one partition. This reference is the C007 proof at `partition_finest_v7/theory/DOUBLED_PAIRS_EXAMPLE_v1.md`, not a planted hidden label; the independent oracle must reproduce the full set.
3. Same sample with exact `allowed_k=[3]` (known-k control); the oracle must reproduce the same unique partition.
4. Forced `ab` with other pairs ambiguous: `Σ=abc`, `P={ab}`, `N={ba}`, default k.
5. Forced-different from trusted k only: `Σ=ab`, `P={ab}`, `N=∅`, `allowed_k=[2]`.
6. Zero answers under K: `Σ=ab`, `P={ab}`, `N={ba}`, `allowed_k=[2]`.
7. Positive-only, default all k: all partitions should remain compatible.
8. Epsilon and unused letters: `Σ=abcd`, `P={ε}`, `N={a}`, default k.
9. No-positive boundary: `Σ=abc`, `P=∅`, `N={a}`, default k.

Invalid-input fixtures separately cover empty alphabet, duplicate symbols, conflicting labels, out-of-alphabet symbols, empty `allowed_k`, and k values outside `1..m`. They are not sent to the mathematical partition oracle as valid cases.

Execution controls are protocol records, not fabricated oracle outcomes. Once provider API/readiness is supplied, test an already-expired cooperative deadline and interruption after partial work. Required result: `complete=false`, no final universal ownership/count claim, preserve partial progress and captured streams. The exact CLI/mode invocation is pending provider readiness.

## Stage gates

### Stage A — independent oracle

Freeze protocol, generator, oracle, copied capture helper, and seed before generation. Capture corpus generation and oracle enumeration. Require at least 100 unique random payloads over m2..7, all named valid controls represented, and direct witness replay for every reported pair side. Save full sets, counts, errors, capture IDs, stdout/stderr hashes, source snapshots, and input hashes. Do not claim provider agreement before its API and main gate are available.

### Stage B — provider gate (blocked on readiness)

After master supplies the frozen API/readiness and reports the main correctness gate passed, run the provider on exactly the frozen small corpus once in its small-enumeration mode. Compare exact full compatible partition sets, not only counts, status, or one representative. Independently check pair relations and witnesses. Any mismatch is saved and stops the gate; no silent rerun or source replacement.

### Stage C — bounded scale correctness only

Only after Stage B passes, freeze four correctness-only cells: one each at `m=10,12,14` and a separate long-word case with alphabet size at most 8 and target length 4096. Maximum 30 seconds per cell. Preserve incomplete outputs as censored; do not infer ownership from timeout. No official speed comparison or performance claim is in scope.

## Capture/provenance

The C007 `evidence/capture.py` is copied byte-for-byte to this audit directory. SHA-256 is checked against `68ee700f391fb6a1cf135e4b55a11a247b45f25164553c917d1664f6fc4a31cf`. Every generator/oracle/provider invocation must capture the copied helper, exact command, input, protocol, and code snapshots. No dependencies are installed. The actual provider commands and source hashes remain unset until master readiness arrives.

## Current readiness state at preregistration

The C009 workspace currently contains the contract but no implementation or provider API files. The master has been asked for readiness and main-gate status. Stage A is independent and may proceed; Stages B and C remain pending that response.
