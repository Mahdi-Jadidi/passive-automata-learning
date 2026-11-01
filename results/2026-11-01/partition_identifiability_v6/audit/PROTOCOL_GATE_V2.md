# C006 solver v5 independent gate — protocol clarification v2

This is a prospective clarification for driver v4. The original frozen
criteria remain in `PROTOCOL_GATE_V1.md`; this amendment only clarifies the
completion field and records the v3 harness result. No provider source or
frozen corpus bytes changed.

## Clarification

For a completed exhaustive result, require `complete == true` and
`decision_complete == true`, along with exact full-set equality and independent
certificate replay. Do not require the optional `enumeration_complete` key:
the stable provider's early singleton/connected-graph proof paths return a
complete decision without that field. A positive exhaustive result still has
to match every reference bipartition. This matches `implementation/PROTOCOL_V4.md`
and the documented result contract.

## Preserved v3 harness outcome

Attempt `20261101T154934.519006Z_c03b5db53a` exited with program error at
`c006_m02_17`. The returned provider result was `not_decomposable`,
`complete=true`, `decision_complete=true`, with one adjacent-swap edge and a
connected-graph certificate that independently replayed. The audit harness
incorrectly required `enumeration_complete=true` and aborted before comparing
the remaining cases. This is a harness schema overconstraint, not a provider
correctness failure. The attempt and streams remain preserved.

Driver v4 has SHA256
`98753d50cbb36d2c56a29f5dc67ef64b17e163fe2906c4aba5a88f280cdff26c`; it is snapshotted alongside this amendment,
`PROTOCOL_GATE_V1.md`, the frozen data, all-k oracle output, provider, CLI,
root wrapper, and C005 helper before launch. The only acceptance criteria are
those above and in v1. Performance remains unauthorized pending the complete
correctness gate and master GO.

