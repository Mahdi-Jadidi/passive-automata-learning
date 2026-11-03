# C011 cross-method equality and valid differences

The semantic target is the complete sample-compatible partition family, exact total/per-k counts, exact per-pair together/apart counts and relations, with independently valid witnesses. Both methods must retain all required default fields and every pair row. Missing information is not normalized away.

`k_max_compatible` is exact and must agree. `k_max_upper_bound` is the number of sound contracted atoms; stronger contraction can lower it legitimately. Check each bound against the exact maximum; do not require the two bounds equal. Atom partitions, atom-feasibility flags, extraction certificates, metrics, and valid witness choices may differ. Verify every certificate/witness rather than requiring a particular model choice. Legacy swap evidence remains adjacent-swap-only; the additive field is `binary_interval_must_link_certificates`.

Baseline cutoff `unknown` and C011 cutoff `incomplete` both have complete=false and no final counts/relations. They are censored, not successful exact answers. Complete-result statuses, counts, relations and output completeness may not be waived by that label normalization.

Timing compares the same task with default expanded semantic output, not byte-identical JSON. Raw bytes and certificate/representation differences must be reported; no speed advantage is attributed to removing pairs, counts or witnesses. Memory is separate peak traced Python allocation, not OS RSS.
