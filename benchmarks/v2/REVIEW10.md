# Review 10 benchmark checkpoint

Review09 remains frozen at `90c861f71f2ba3e170fd2a7bfe0cce8fe04f7327`. The Review10 CSV and JSON describe history generation and independent replay.

```sh
python -B benchmarks/v2/review10_histories.py --source /path/to/pinned-staging --output /tmp/review10-normal
python -B -O benchmarks/v2/review10_histories.py --source /path/to/pinned-staging --output /tmp/review10-optimized
```

Use staging commit `be52e6aa51dcbc6a7cc37d84608df97cfffd1f43`. The summary records the three source trees and exact raw, journal, replayed scope and target hashes. Each case exports one immutable journal through the existing gateway and authoritative RegisteredLedger. The simulator calculates complete tables from original ordered words and registered owners. It executes 11 offline queries across three cases with zero external calls. Each target list enumerates all 15 canonical partitions of the original alphabet, independently of verdicts.

- Named uses the Review10 ab|c|d, ac|b|d and bc|a|d history for abcd versus abdc. The held-out target is abc|d.
- Cross-ID uses two positional negative IDs with the same word. The deterministic reply policy varies the failing ID and the equal positive witness on three registered ab|c|d requests, licensing the ab path N0–P0–N1–P1. The ac and bc requests supply N0–P1. N2 and N3 also share a genuine free group on ab. A negative in a checked free group has no matching positive on that source block. The report's abstract same-block free-group-to-named chain is a theorem-only example under different information semantics.
- Repeated order uses a duplicate positive and a repeated symbol to preserve positional IDs and ordered projection semantics.

Snapshot exports and independently replayed scope timings are measured here. Producer index reuse, verified sidecars, literal parity, resource ablations and hostile sidecar controls remain pending exact named producer and checker pins. No evaluation labels are included in these inputs.

## Compact native v2

The Linux pairing driver uses the frozen Review09 sparse route and a candidate configuration populated from Agent #6's published native v2 pin. Use the same verifier and interface pins, structural caps, memory profile, interpreter modes and restart policy. The retained and fresh origins reuse the existing hash-checked archive and authoritative RAW generation respectively. Independently reconstructed medium/huge choice roots must have a mandatory merge. The paired CSV gives trusted scope construction and end-to-end search separate rows. Native compact root-check work and projection metrics depend on the producer's published interface. An end-to-end VERIFIED result requires independent complete v2 replay within the standard deadline.

```sh
python -B benchmarks/v2/review10_compact.py --compact-config /path/to/pinned-config.json \
  --baseline-producer /path/to/frozen-sparse --compact-producer /path/to/pinned-compact \
  --verifier /path/to/frozen-verifier --interface /path/to/frozen-interface \
  --case huge_choice_active --memory-mib 512 --journal-origin retained --output /tmp/review10-pair
```

The driver above expects a CLI adapter. The published native API gate below supplied the executed comparison.

## Executed compact pair

Agent #6's native entry point and workflow were pinned at `23883be28cbde727443d8d3c5d2a723d924e3aec`. The same six jobs ran both interpreter modes and both memory profiles. Search used 25 cooperative seconds, 10 million work units, 2 million entries and a 64 MiB frontier cap. The large searches and replay had separate 30-second process deadlines. The large gate regenerated the journal through the authoritative adapter and checked byte parity with the retained journal and independently reconstructed scope before search. The large gate ran mode one. Native fixtures ran modes one and all, with independent v2 proof replay and deterministic resume checks.

The 200 native routes independently verified. All 32 contracted medium and huge routes remained incomplete. At the huge contracted root, compact completed the compatibility check in all four memory and interpreter combinations with 1,130,014 work units per check. Dense and sparse hit their root check caps. Root compatibility and whole-search completion are reported separately. Timing and process RSS belong to the measured stage. The native gate reports search counters but does not isolate per-route process RSS. These observations do not estimate time to optimum on the large fixtures.

```sh
gh run download 46021645996 -R Mahdi-Jadidi/passive-automata-learning -D /tmp/review10-scale-ci
python -B benchmarks/v2/review10_scale_export.py /tmp/review10-scale-ci benchmarks/v2/results/review10-scale
```

[Native compact CI and exact command log](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/46021645996)
[History provenance CI](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/46021650707)

The frozen CLI pairing driver above covers a separate Review09-style end-to-end budget, including HDFS. The executed native gate used the published Agent #6 API and separate stage deadlines as documented here.
