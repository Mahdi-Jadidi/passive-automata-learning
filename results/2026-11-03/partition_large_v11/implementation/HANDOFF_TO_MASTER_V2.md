# C011 implementation handoff v2

The first sketch's generated-swap-only path is not recommended for long words:
substring construction may copy O(L) characters at O(L) positions. The static
alternative is RLE-indexed maximal two-symbol transition spans with
rolling-fingerprint lookup, collision buckets that retain every record, and
mandatory exact verification of boundaries, support, counts, prefix and
suffix before adding an edge.

The proof-critical question is whether a valid minimal binary-anagram
interval is always represented by aligned maximal RLE spans, including
single-symbol boundary extensions. This requires a theory proof and adversarial
review before any v2 provider implementation. The sound conditional theorem,
certificate fields, rejection tests and bounded counters are specified in
[CANDIDATE_DESIGN_V2.md](CANDIDATE_DESIGN_V2.md).

Keep C010's default API/output semantics and legacy adjacent-swap certificate
field. Put newly verified interval evidence in a separate field. Exact
projection caching and canonical witness reuse may follow as a separate small
version; no compact default output or BDD work. No provider execution or timing
has occurred in C011. Await theory proof and the master's frozen method
contract before implementation, then freeze all sources/inputs/protocol before
any captured run.
