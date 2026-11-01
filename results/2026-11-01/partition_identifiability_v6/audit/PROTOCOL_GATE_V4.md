# C006 solver v5 independent gate — protocol clarification v4

Prospective amendment for driver v6. V1–V3 and prior attempts remain
immutable. The stable provider, frozen corpus and all-k reference are unchanged.

Attempt `20261101T155142.867016Z_8128c9ad46` used 30.273 seconds of captured
subprocess time and was terminated by the capture deadline with empty child
stdout/stderr. Static inspection identifies the auditor's cause: its
independent verifier materialized a canonical mask list of size
`2^(40-1)-1` for the intentionally empty 40-symbol certificate before
checking the submitted record count. The candidate verifier itself performs
the expected-count check first. This attempt is a harness timeout, not a
provider timeout or mismatch; it is not an accepted gate.

Driver v6 corrects the audit verifier to compare the submitted-record count
with the expected exponential count before building any mask list. It also
reports record count separately from the number of unique normalized visible
payloads and duplicate records. Driver SHA256:
`98c72c09daa4a8c58ea074bcf0d8f30264ff4f8d52b24f3a3f12dd5b47e38131`.
This driver and the V1–V3 protocols are snapshotted with all frozen data,
provider, CLI, root wrapper and helper before execution.

All prior acceptance criteria stay in force; no provider source changes are
in scope. Timing and memory comparisons remain held pending a complete gate
and master authorization.

