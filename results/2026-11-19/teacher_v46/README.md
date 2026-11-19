# V46 checkpoint

V46 continues the 16 November checkpoint on `codex/teacher-handoff-v46`. The implementation tested is V45. The new material is the longer-budget harness, raw runs, first-principles review and a standalone paper with complete proofs.

At 0.25 seconds per input, V45 returned 1,245 checked optima and two checked infeasibility results; 1,014 inputs were incomplete. At 60 seconds, V45 completed six of ten fixed cases and V43 completed all ten. All three fixtures passed, including the diagnostic with two learned cuts. The first censored case, `oneblock_8`, remained incomplete at 300 seconds. The prefix store was slower than the cached scanner in every workload median, with full digest agreement.

- [Standalone English paper](../../../output/pdf/Certified_Maximum_Alphabet_Partitioning_Interactive_Teacher_V46_EN.pdf)
- [Complete article source](paper/article_complete.md), [bibliography](paper/references.md), [automated page QA](paper/rendered/layout.json) and [visual inspection](paper/rendered/QA.md)
- [Corpus, fixed cases, fixtures and microbenchmark summary](evidence/summary.json), [publication tables](evidence/results.md), and [frozen integrity and environment](evidence/environment.json)
- [Proof-to-code review](audit/CODE_CORRESPONDENCE.md), [fresh kernel and oracle replay](audit/foundations.json), and [adversarial certificate replay](audit/adversarial_replay_results.json)
- [Artifact manifest](manifest.json)

## Claim ledger

| Claim | Evidence and scope |
|---|---|
| Completed producer returns a maximum | The paper proves the projection criterion, exact teacher bridge, mandatory contraction, cut validity and progress, Boolean threshold meaning and relaxation optimum. The proof assumes exact completed computations. |
| Completed result carries checkable upper bound | Direct projection and structural bounds or witnessed CNF and a checked DRUP refutation. The shared normalization, atom constructor, encoder and RUP interpreter are trusted. |
| Increased-budget evidence | Worker limits, raw traces, counters, startup and standalone consumer times are retained. Incomplete runs carry no result or certificate and are excluded from the successful groups. The 300-second escalation is diagnostic. |
| Teacher and supplied manuscript integrity | All frozen V45 manifest entries and the three handoff V43 source hashes are checked read-only before running. The evaluator calls the V45 implementation without an alternate teacher. |
| Scientific and deployment scope | Finite synthetic evaluation and AI-assisted code and proof review. Scientific priority, formally verified software, universal speed advantage and physical recovery are outside the established claims. Zero valid whole-trace AND field trials. |

## Reproduce

Use Windows x64 CPython 3.12 with the checked-in pinned vendor dependencies. Set `$py` to the absolute Python executable in [the environment record](evidence/environment.json), or the matching executable on the target machine. Keep profiling runs sequential. The example uses new result paths.

```powershell
$study = 'results/2026-11-19/teacher_v46'
& $py -B "$study/run.py" all --out new-v46-evidence
& $py -B "$study/summarize.py" new-v46-evidence
& $py -B "$study/audit/review.py" new-foundations.json
& $py -B "$study/manifest.py"
```

`run.py` keeps the versions in different interpreters. The corpus is replayed sequentially in one V45 interpreter for a correctness/resource audit. The report generator reads archived evidence and requires an exact per-row cap, the full corpus and fixtures, and valid reference or consumer results. The builder reads the shipped evidence and review outputs. ReportLab, pdfplumber, pypdfium2, Pillow and the Windows Times New Roman, Consolas and Segoe UI Symbol fonts are required for the PDF and page renders.

```powershell
& $py -B "$study/paper/build_pdf.py" --pdf rebuilt-v46.pdf --render-dir rebuilt-v46-pages
```

The Markdown, report builder and raw records permit reproduction without previous chats. The manuscript teacher's internal performance proposals appear in the final section of the paper.
