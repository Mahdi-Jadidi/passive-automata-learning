# C026 manager review

2026-11-06. Reviewed the complete theory/PROOFS_V1.md, the original and corrected implementation/recommend_v1.py and cli_v1.py, and audit protocol/oracle sources. This is mathematical/static review, not independent execution evidence or an external novelty assessment.

## Mathematics

Prime completion: assign each negative to a block separating it from every positive; exclude those finitely many projections and one fresh nonpositive word in each block. Resulting cofinite languages are regular, nonempty and infinite. Every projection onto a proper subalphabet is universal (arbitrarily many erased letters escape finite exclusions). A proper independent factorization would therefore be universal, contradicting the excluded word. This covers empty P/N and unary blocks with the stated convention.

Characteristic sample: each invalid cut has an outside word accepted by its product of projections; two accepted lifts give a consistent three-word cut obstruction. The three-copy epsilon product realizes exactly these triples. Removing cycles from an accepting path bounds ALL transitions, hence each extracted word, by Q^3-1. This proves existence; the actual learner neither receives the DFA/Q nor knows when all certificates arrived.

Any invalid partition has an invalid bipartition coarsening: otherwise meet closure of the complete nonempty language makes it valid. Rejecting every invalid cut therefore leaves exactly coarsenings of the unique finest behavioral factorization. Its unique maximum-block member is the eventual recommendation on an exhaustive correctly labelled informant. Prime finite completions still prevent certifying a nontrivial physical count. No contradiction between these statements was found.

## Source

Anchored max DP uses original-sample rejection masks and never rejects an expandable block solely for current incompatibility. Canonical ordering compares actual symbol RGS keys, rather than numeric submask order. Retaining the first two ordered optimal children is sufficient: each fixed parent branch preserves ordering of its child partitions. Distinct branches have distinct anchored first blocks. A better value replaces prior ties; equal values preserve up to two. U-empty and remaining-union pruning are sound. The atom partition, if feasible, uniquely attains the sound atom-count upper bound.

Quota reservations include unfinished entries; no interrupted value enters the exact memo. Only completed witness constructions replace the incumbent. Once the atom partition fails, upper bound r-1 is valid. Initial oneblock exists only after complete validation and absence of contradictory labels.

Two draft defects were returned to the implementer before official runs: huge-integer deadline conversion and an incomplete-classification flag on an already proved ambiguous interrupted result. Corrected source preserves the initial draft. The CLI catches serialization errors and records process output failures by exit3; cooperative deadline remains distinct from an outer wall cap.

## Gate

Source is suitable for independent testing after developer smoke and SHA freeze. Official acceptance additionally requires full small-family maximum/tie/canonical/witness checks, theorem construction checks with an independent full-language oracle, and public CLI integration checks. Timing compares common maximum/tie/witness query; only new mode promises lex-canonical selection. No speed or memory advantage is presumed.
