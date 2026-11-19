# Uncapped V45 follow-up

Ran the previously censored fixed V33 case `overlap_8` with no solver or consumer time limit. The observer delegated to the frozen functions and recorded local-table and teacher-call entries, exits and progress. The V45 teacher hash is recorded in the trace. The prior V46 evidence and paper are unaffected.

The solver returned `OPTIMAL` with six blocks: `{s0,s1}, {s2,s3}, {s4}, {s5}, {s6}, {s7}`. The V45 consumer accepted the 44-line threshold-7 DRUP proof, and direct enumeration of partitions of the eight declared events independently confirmed the same optimum. There were four learned cuts, five teacher calls and six recorded master SAT queries.

| Observed phase | Seconds |
|---|---:|
| Entire solver call, as reported by V45 | 59.156 |
| Fixed-partition teacher calls | 58.829 |
| Local-table service, including cache hits | 58.809 |
| Solver time outside the fixed-partition teacher | 0.327 |

Local-table service accounted for 99.41% of the solver call. Four uncached two-symbol tables with sufficient trie bound four took about 14–16 seconds each. Each visited 1,054,474 named DFAs. The total, including singleton tables, was 4,219,768 representations with 22 cache hits. The elapsed envelope in `result.json` includes observer startup and logging. Solver-only time is `profile.metrics.total_seconds`. The uncapped trace is a diagnostic, not a paired timing comparison with the earlier capped trial.

The other three previously censored cases were outside this uncapped run. Their observed local enumeration scales and their capped outcomes remain in the [V46 summary](../teacher_v46/evidence/summary.json). In particular, the active eight-symbol table in `oneblock_8` has a sufficient bound of ten and about 10^83 named representations. Its 300-second run reached 4,401,840 representations without completing that table. Finite theoretical termination and practical completion are different claims.

Raw files are [event trace](overlap_8/events.jsonl), [output and checked certificate](overlap_8/result.json) and [derived metrics and hashes](overlap_8/summary.json). To rerun from the repository root with the matching Windows x64 CPython 3.12 runtime, choose a fresh output path.

```powershell
python -B results/2026-11-19/teacher_v46_uncapped/trace_run.py overlap_8 new-uncapped
```
