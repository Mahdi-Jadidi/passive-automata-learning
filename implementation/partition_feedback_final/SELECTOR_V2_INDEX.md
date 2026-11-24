# Selector v2 — research and implementation index

Baseline: 7c90eb59561bd25ec4fdca5ac08b0e5d60d17fd6 (codex/v47-polynomial-teacher).
Integration branch: research/selector-v2. Do not modify the external automata learner or the baseline.

## Archived research
- [Master handoff](PROJECT_HANDOFF.md)
- [01 Sparse analysis / SDJ-IDA](research/2026-11-24/01_SPARSE_ANALYZE.md)
- [02 NO implication / AEFC](research/2026-11-24/02_NO_IMPLICATION.md)
- [03 Exact search / EDR-BB](research/2026-11-24/03_EXACT_SEARCH.md)
- [04 Query policy / CDAQ](research/2026-11-24/04_QUERY_POLICY.md)
- [AEFC reference validation](research/2026-11-24/no_implication_validation.py)
- [AEFC validation output](research/2026-11-24/no_implication_validation_run.txt)

## Parallel workstreams
| Issue | Branch | Dependency |
|---|---|---|
| #2 | research/v2-implementation-core | Starts immediately; P0/P1 |
| #3 | research/v2-proof-audit | Theory audit independently; verifier integration after schema freeze |
| #4 | research/v2-benchmarks | Baseline harness independently; v2 benchmarking after integration |
| #5 | research/v2-interface-audit | Paper/interface audit independently; live adapter requires confirmed protocol |

Agent instructions are in the issues. Requested model GPT-6.2 High must be selected in the execution UI; issue creation does not launch agents. Each stream commits after each testable milestone and opens a draft PR to the integration branch. No direct main writes or automatic merges.

## Integration order
Core/schema + interface contract -> typed evidence and basic exact search -> independent replay -> AEFC and rank bounds -> guarded CDAQ -> controlled ablations.
Keep structural and external acceptance distinct, preserve UNKNOWN, and report both cost bounds and independent verification. No publication novelty or external speedup is established yet.

## Status (2026-11-24)
Four research reports and the master handoff archived. Four parallel workstreams prepared; agent execution not initiated by GitHub. Raw benchmark archives and live external protocol still need availability confirmation.
