# C022 sole candidate: validated coarsening witness transfer

Parent gate SHA256: `5331a1787a9ff74afe1afcbea1668dbe9ee69ef1f7121fec14c7281caa2d8680` (C020 C2).

Entry point and schema are unchanged. From repository root:

```text
py results/2026-11-04/partition_transfer_v22/implementation/candidate_transfer_v1/partition_gate_v1.py INPUT.json --seconds 20
```

Add `--known-k K` only for an externally trusted exact count. The CLI accepts exactly the original options and retains exit codes: completed scientific status 0, invalid input 2, unresolved 3. The copied CLI is byte-identical to the parent.

The only algorithm change replaces projection replay for the two ambiguity witnesses constructed from compatible forced atoms. It transfers the validated atom rejection index to the containing coarsened output block. Other branches and search remain unchanged. Full validation and the original exact atom-feasibility witness precede transfer. The candidate does not accept new assumptions or external witness input.

Completed alternatives have the same partitions and local-language rule. A different valid rejection block may be chosen. Projection/cache metrics and interruption progress need not equal baseline. The method identifier distinguishes this candidate. No runtime gain has yet been measured. Do not promote it before independent static review, correctness tests and audit of witness validity.

Proof and negative-premise checks are in `../../theory/TRANSFER_PROOF_V1.md` and `../../theory/COUNTEREXAMPLE_ATTEMPTS_V1.md`. There is one candidate only; no new generator or heuristic was added.
