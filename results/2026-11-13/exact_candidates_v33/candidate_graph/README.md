# V33 forced-pair graph candidate

Experimental only; no public entrypoint or previous results are modified. Read PROOF.md before evaluating. `candidate.py` exports `solve(data, *, max_candidates=None)`, returning the C028 dictionary contract with no extra diagnostic keys. `baseline_contract.py` is a byte-for-byte local C028 copy used for helper semantics and budgeted calls. Requires standard-library Python 3. No solver dependency.

Reproduce the developer correctness check from repository root (set the Python executable to the bundled interpreter or another Python 3):

    python results/2026-11-13/exact_candidates_v33/candidate_graph/dev_check.py

The check imports the existing C028 independent oracle and fixtures from `results/2026-11-11/exact_foundations_v28/audit/`; it compares completed full outputs, independently replays witnesses, and checks budget and invalid results against baseline. Developer run: 2,269 oracle cases and 104 budget comparisons passed on 2026-11-13. This is not the independent V33 audit or an official benchmark. Official auditor must use the frozen source and separate test corpus/protocol; arbitrary datasets might favor baseline and preprocessing is included in the cost. Run with sufficient resources; Python decimal conversion limits can affect serialization of large exact integers.

Inputs use alphabet/positive/negative arrays with opaque strings. Full output includes exact total and optimal counts, first two ordered compatible and optimal witnesses, and finite factors; incomplete/resource outcomes never assert exactness. Bounded `max_candidates` delegates to the unchanged baseline for prefix compatibility, including INVALID_INPUT precedence. The no-budget graph shortcut is used only after direct component partition compatibility; otherwise all component partitions are enumerated.
