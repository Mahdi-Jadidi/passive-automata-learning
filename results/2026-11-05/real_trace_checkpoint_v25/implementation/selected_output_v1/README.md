# C025 experimental selected-output solver v1

Separate from public C024. No public files, baseline sources or Git were modified. Exactly one bounded final-block exact-cover candidate, no optimization tuning. The caller supplies a complete validated observation object with only alphabet and traces. Alphabet has1..8 distinct nonempty atomic string IDs. Each trace has exactly unique integer file_id and events; each event exactly id and outcome (bool or null). Empty traces are permitted. Every declared trace starts at a common empty local context. No labels are attached to epsilon.

Explicit API:

```python
solve(data, depth='full', model_version='selected-output-v1', known_k=None, deadline=None)
```

depth and model_version are required keyword arguments. Depth is one of0,1,2,4,8,full. Finite depth means that many PRIOR projected local IDs plus current ID, retaining true short lengths. Full means complete projected input history. Unknown outcomes impose no output constraint but their events still update memory. Outcome is current selected owner's output; inactive blocks do not vote. Outcomes never enter history. K, if present, is an externally trusted exact count, never inferred from Node/host metadata. Deadline is finite absolute perf_counter time; CLI seconds includes input read/JSON. No core frequency selection, metadata or host map access occurs.

Example command (caller-owned already selected input):

```
py -3.14 results/2026-11-05/real_trace_checkpoint_v25/implementation/selected_output_v1/cli_v1.py INPUT.json --model-version selected-output-v1 --depth full --seconds 20
```

Search anchors each FINAL block on the least remaining ID and enumerates every subset of other remaining IDs, then recurses on the complement if and only if that finalized block is exactly consistent. Every partition appears once; optional K count bounds are safe. Rejecting a finalized block is safe because it will never grow in this branch. No inadmissibility monotonicity, swap graph, bipartition shortcut or AND rejection/envelope rule is used. A lazy per-solve mask cache holds exact block results. Every trace/event loop polls deadline, including skipped events and witness construction. Full-history checks intern trie transitions (parent,event) globally across traces, resetting each trace to root. This adapts C017 evaluate_block semantics; the original copy remains byte-identical and was tested on toy controls first. New code adds strict whole-input validation, polling and certificate construction rather than changing the frozen copy.

Two actual compatible covers return ambiguous with two replayable witnesses. Exactly one only after exhaustion returns certified_unique; none after exhaustion returns incompatible. Deadline/resource interruption returns unresolved, complete=false, and no partition/witness/exhaustion claim. Malformed schema/arguments return invalid_input, distinct from valid-data model contradiction. Validation scans every event before any completed certificate, including late malformed events.

Each witness contains blocks and per-block exact observed output rules with source file/event references. At full depth, rule context is a trie node with serialized parent/event/node table; at finite depth it is [prior_ids,current_id]. Unknown transitions/outputs are explicitly arbitrary, not predictions. Trie state plus fallback gives a finite completion; finite-depth transitions use suffix updates. Exhaustion certificate includes evaluated-mask records and first-conflict references where rejected; replay derives projected contexts directly from input. This table plus algorithm reference is not a standalone independently replayed exhaustive search proof. Independent audit must enumerate the small family and replay witnesses/conflicts.

Metrics: search_nodes is cover recursion calls; complete_candidates is compatible complete covers reached (at most2), not all conceptual set partitions; block_masks_computed is distinct exact mask evaluations; block_cache_hits is cached accesses; block_scan_events and local_events are first checks only and can stop at first conflict; trie_nodes counts first-check trie allocations. Witness replay work is included in solver_seconds but not block-scan counters. No metric is a memory estimate. No predictive or physical-ownership claim follows from finite consistency.

Selection is outside core. A caller must freeze at most8 IDs by TRAIN-only event frequency with deterministic ties and report selected/excluded events, labels, types and empty projected traces. Source lineage must be split before selection. BGL's mechanical_top8_selection.json is whole-sample diagnostic only, not an approved training-selection artifact. Preserve full input streams for known-host baselines; subset projection changes causal histories and does not test omitted-state dependence.

Developer smoke uses a direct materialized-history oracle and tiny full partition enumeration on9 fixtures across6 depths and3 K settings (162 controls), plus JSON-roundtripped witness replay, conflicts, C017 per-block agreement, unknown/finite-coarsening/swap/AND semantic counterexamples, late validation and expired deadline. These controls are implementation evidence, not independent audit. No solver runs on real data, full benchmarks or public promotion occurred.
