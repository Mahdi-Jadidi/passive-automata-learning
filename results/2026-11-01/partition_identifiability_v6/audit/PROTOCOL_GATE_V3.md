# C006 solver v5 independent gate — protocol clarification v3

Prospective amendment for `gate_solver_v5_v5.py`. V1 and V2 remain immutable.
The provider and all 135 frozen corpus records/reference bytes are unchanged.

`implementation/FINAL_TARGET_V1.json` is a readiness manifest, not a labeled
sample. The gate checks its recorded provider/CLI hashes against the actual
frozen source bytes. The additional sample-level check uses
`implementation/example_manager_candidate_v1.json`, which contains the
implementation owner's concrete alphabet/positive/negative example. The same
example is the direct CLI input under v1's CLI criterion.

Preserved attempt `20261101T155028.770089Z_88e1928241` reached the post-loop
extra-target line after all 135 case-level equality, witness, certificate,
existence, and verifier assertions completed without failure. It then raised
`KeyError: 'alphabet'` because v4 treated the readiness manifest as a sample.
Thus this attempt observed 135 passing per-case checks, but the execution
terminated with an auditor error and is not recorded as a completed/accepted
gate. No provider mismatch occurred in those cases.

The corrected driver v5 SHA256 is
`4b1e8991223148b3c56ca815ac755b72dc5fd47e20c73cc1da83ba4f6aa651b5`.
It is snapshotted with this protocol, v1/v2, candidate/reference sources, all
frozen inputs, root CLI wrapper, and helper before launch. The v1 and v2
acceptance criteria otherwise remain in force; performance is still held.

