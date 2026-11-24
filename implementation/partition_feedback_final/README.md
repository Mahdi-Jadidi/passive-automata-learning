# Exact alphabet partition selection

Start with [the current research handoff](RESEARCH_STATUS.md). This package finds one compatible partition with the maximum number of blocks and emits a replayable optimality certificate. The input is ordered positive and negative traces over a declared alphabet. See [project notation](../../docs/ALGORITHM_NOTATION.md).

| Resource | Purpose |
|---|---|
| [Current algorithm, Persian](ALGORITHM_UNCAPPED_FA.md) | Uncapped execution and line-by-line pseudocode |
| [English mentor handoff](HANDOFF.md) · [Persian mentor handoff](MENTOR_HANDOFF_FA.md) | Research background, proofs and original delivery results |
| [Solver](staged.py) · [Independent verifier](verify.py) | Produce and replay a certificate |
| [Decision rules PDF](../../output/pdf/Partition_Decision_Rules_Final_EN.pdf) · [Rule index](evidence/rule_index.json) | Frozen published rules, their targets and replay evidence |
| [Scaling fixture and runner](stress_10000.py) · [Recorded result](evidence/synthetic_10000_traces_1000_symbols_run.json) | Reproduce the 10,000-trace bottleneck |

The mentor handoffs and PDF describe the earlier measured delivery. The current handoff records the uncapped defaults, triple-block proof and new stress result.

The two supplied research reports are preserved as background. [Independent analysis](research_sources/independent_partition_selection_report.md) · [Alphabet partition research](research_sources/alphabet_partition_research_report.md)
