# V46 outer-optimizer checkpoint

The frozen V45 implementation was tested without modifying its teacher or optimizer. [OUTER_PROOF.md](OUTER_PROOF.md) gives the outer proof from projection through atom contraction, cuts, the SAT maximum and certificate checking. It uses the proved teacher decision interface for completeness and separately proves that accepted certificates certify the optimum.

## Findings

- A fresh checker replay covered **2,330 completed V45 results** across the earlier 0.03-second and 0.25-second corpora, the benchmarks and fixtures, and the uncapped overlap case. All matched the saved reference and all certificates were accepted. The corpus runs overlap in their input sets. The **2,249 incomplete run records** were audited separately and carried no partition, objective or certificate.
- The **158 new end-to-end runs** covered **144 distinct wire datasets** with 0–7 events, opaque and unused IDs, repeated observations, contradictions, empty traces and samples, nonunique optima, ordering, and traces up to 302 events. The independent enumeration visited **20,938 partitions** across all inputs. All runs completed and matched the direct oracle and certificate checker, yielding **121 optima and 37 infeasibility results**. Six observed relaxation-maximizing candidates and six learned cuts were also checked against direct partition enumeration. The new cases include four attained atom-bound certificates and three general DRUP certificates. Solver caps were 10 seconds for the generated batch and 90 for the targeted cases, with a separate 30-second consumer cap. The suite is synthetic.
- The SAT master was tested separately on 36 seeded monotone-predicate instances over five to seven atoms. It passed **62,013** fixed partition-assignment checks and **1,255** threshold checks across **156** relaxation rounds. The consumer replayed all **36** refutations above the attained maximum. These are encoding tests without a teacher call or an alternate production teacher.
- The [uncapped overlap trace](../teacher_v46_uncapped/README.md) locates the bottleneck in building local tables by enumerating named DFAs. It consumed **99.4%** of that solver call. All 1,014 censored runs in the 0.25-second audit stopped in the teacher phase. Three fixed benchmark cases from that comparison still lack uncapped outcomes. Valid field trials using whole-trace AND labels remain at zero.

The checks distinguish an observed checked optimum, a certified infeasible sample, and a resource interruption. No completed result in the audited runs was found to be suboptimal.

## Reproduction

Use the [pinned Windows CPython and solver environment](../teacher_v46/evidence/environment.json). Choose fresh output paths.

```powershell
$d = 'results/2026-11-19/teacher_v46_outer_audit'
& $py -B "$d/audit.py" new-outer-evidence
& $py -B "$d/audit_master.py" new-master.jsonl
& $py -B "$d/recheck_saved.py" new-recheck.jsonl
```

Archived records are [end-to-end](evidence/cases.jsonl), [end-to-end summary](evidence/summary.json), [master checks](evidence/master.jsonl) and [certificate replay](evidence/saved_replay.jsonl).
