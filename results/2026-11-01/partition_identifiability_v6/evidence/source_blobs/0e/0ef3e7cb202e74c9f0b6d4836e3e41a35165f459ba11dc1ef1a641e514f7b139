# C006 protocol v2 addendum

This file supplements, and does not replace, `PROTOCOL_V1.md`. It adds one
manager-supplied candidate obstruction as an explicit single-case extension.
The candidate is preserved literally in `targeted_nondec_v1/input.jsonl`:

- alphabet `{a,b,c,d}`;
- positives `acdb, cabd, bcda, dabc`;
- negative `abcd`.

The audit-only witness grammar is the one-factor infinite regular language
`{acdb,cabd,bcda,dabc} union a^5 a*`, which verifies label consistency without
introducing k or q into the solver input. The independent RGS oracle evaluates
all partitions, with direct all-k projection feasibility and the complete
bipartition frontier. The swap/insertion-rescue graph is reimplemented
independently from its definition. No provider or timing run is authorized by
this addendum.

If the candidate does not have the proposed property, preserve that result as
a rejected hypothesis; do not change its input. Any minimized or corrected
candidate is a distinct new case/version.
