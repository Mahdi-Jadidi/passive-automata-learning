# C020 candidate C1 contract

One exact gate, same C018 observational schema and compact result contract.
No generator, hidden K/state count or truth file is read. Optional --known-k
remains externally trusted. Original sources/public partition.py are untouched.

After independent source/fixture review and master GO:

```powershell
python -B -X utf8 results/2026-11-04/scaling_v20/implementation/candidate_c1_v1/partition_gate_v1.py INPUT.json --seconds 20
```

The CLI source is byte-identical to C018 and imports the colocated candidate.
Only method and diagnostic metrics change. A selected partition is released
only in certified_unique; ambiguity has two verified compatible alternatives;
incompatible has a completed proof; unresolved has no finality. The same model
assumptions, data validation, proof routes and full compact witnesses remain.

C1 stores exact length/Parikh signatures from existing validated counters and
tests swap pairs only within equal-signature negative buckets. It never unions
on count agreement alone. Full proof/limits are in ../C1_ARGUMENT_V1.md.

Metric word_signatures counts completed signature records. graph_pair_universe
is P*N only when graph work is entered, otherwise0. swap_pairs still means
actual pairs passed to the unchanged graph comparison loop, now after the
necessary-count filter. graph_pairs_filtered counts pairs excluded for positive
rows reached so far; on complete graph traversal it is universe minus tested
pairs. On interruption it is partial progress. No altered field is an exact
output-family count. Existing character/projection/search counters retain their
definitions. Extra signature work is included in solver and process timings.

Worst-case graph work and exact search remain potentially expensive. Native
signature sorting/hash operations have before/after cooperative polls, not
hard real-time preemption. Auditor soft20/hard25 and <=600seconds/provider
limits apply. No C011, rolling-hash index, translation projection or new search
pruning is included in C1. A second slot remains conditional on profiling.

Timing only follows correctness. Compare identical input/default compact output
in fresh processes; method/work diagnostics/times may differ, complete decision
and independently verified witnesses must agree. Include all slow/censored
and unstarted-budget cells and memory costs as preregistered.
