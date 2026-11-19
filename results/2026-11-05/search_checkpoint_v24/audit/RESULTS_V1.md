# C024 audit results V1

A automatic-promotion criteria: True. B: True. Final promotion remains the manager decision.

| Round | Cell | Baseline median s | Candidate median s | Candidate/baseline | Baseline completed | Candidate completed |
|---|---|---:|---:|---:|---:|---:|
| A | obstruction_m8_noK | 0.6646 | 0.3004 | 0.4520 | 5/5 | 5/5 |
| A | obstruction_m10_noK | 4.7829 | 0.4630 | 0.0968 | 5/5 | 5/5 |
| A | obstruction_m12_noK | censored | 0.7649 | censored | 0/5 | 5/5 |
| A | ambiguous_noK | 0.3143 | 0.3607 | 1.1478 | 5/5 | 5/5 |
| A | D_K4 | 0.6030 | 0.6578 | 1.0909 | 5/5 | 5/5 |
| A | A_K4 | 1.1403 | 1.2907 | 1.1319 | 5/5 | 5/5 |
| B | D_K4 | 0.4538 | 0.4065 | 0.8957 | 5/5 | 5/5 |
| B | obstruction_m8_K4 | 0.6767 | 0.2887 | 0.4266 | 5/5 | 5/5 |
| B | obstruction_m12_K4 | censored | 0.4419 | censored | 2/5 | 5/5 |
| B | unsafe_K2 | 0.5579 | 0.4994 | 0.8951 | 5/5 | 5/5 |
| B | ambiguous_K3 | 0.8679 | 0.5820 | 0.6706 | 5/5 | 5/5 |
| B | A_K4 | 1.9655 | 1.9202 | 0.9769 | 5/5 | 5/5 |

Zero completed semantic/certificate errors is required. Full distributions, counters, replay outcomes and capture identifiers are in each VALIDATED_SUMMARY_V1.json; all stdout/stderr and immutable source snapshots remain in attempts/ and source_blobs/.

- 21 repeated A job IDs retained; V2 addendum corrects earlier count
- Manager harness-review arrived after A launch; no discarded/restarted timing
- Raw distributions.json includes unresolved durations; validated summary exclusively controls acceptance
- Supplement preparation KeyError preserved as C024-SUPP-PREP-001; fixed in new script before any supplemental provider execution
- Integrated: 680 independently replayed calls and four CLI checks pass; integrated timing unmeasured
- No memory measurement performed; no historical cross-round ratios; no implementation or public changes
