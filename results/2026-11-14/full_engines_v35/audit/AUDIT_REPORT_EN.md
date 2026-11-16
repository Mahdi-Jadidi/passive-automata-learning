# V35 full-engine audit

## Verdict

**PASS for the bounded checks recorded here.** Both independently authored full-output engines match the frozen C028 executable on the exercised corpus. The hypergraph optimum/infeasibility certificate producer and independently authored checker accepted valid proofs and rejected exercised tampering. This is test evidence, not a proof that either implementation is correct for every input, a count certificate, a performance result, a novelty claim, or a claim about physical ownership.

## Frozen sources

- Frozen C028 oracle: `results/2026-11-11/exact_foundations_v28/implementation/reference.py`, SHA-256 `5F60B27447B37EC07F1FD6BCE75BE6199B898573D4B32E90413E900E3A615A94`. It was used only as an audit oracle.
- Logic engine: `logic/candidate.py`, SHA-256 `2DCDC3756B688FDDE8FD0ED35C829C8308DCC7F11A1F2DA9329B890D8E1737D9`.
- Hypergraph engine: `hypergraph/candidate.py`, SHA-256 `D9594A1456C9D73E1A7DE125B48226A5B3FAA57FB6C04DB86D0DD4CA45C008C6`.
- Hypergraph certificate producer: `hypergraph/certificate.py`, SHA-256 `9E34F6E4DC3217F3756D71CA83DDB2E288B6AC17C1E5670DC6417996311037BF`.
- Independently authored hypergraph checker: `checker/hypergraph_checker.py`, SHA-256 `C97D7555CCDEB7CACC61C6A90DDB93CBCDA985A56449303C419CAB61D71EC920`.

## Full-output comparison

`output_audit.py` compares every field of each returned Python dictionary, including reasons and serialized witnesses, with both the frozen executable and an independently coded insertion-partition oracle.

- **Logic:** 2,191 completed cases passed: every ternary labeling of epsilon, `a`, and `b` over `{a,b}` (27), four empty-alphabet cases, targeted opaque-ID/duplicate/order cases, 536 budget calls and 27 invalid-input calls. An additional three-symbol tied-optimum case passed. The wider SAT corpus containing random three-symbol cases was deliberately stopped after it became disproportionately slow; this is a resource/performance limitation, not a correctness failure and is not reported as a benchmark.
- **Hypergraph:** 2,243 full cases passed, including all 2,187 ternary labelings of the seven words of length at most two over `{a,b}`, four empty-alphabet cases, two targeted cases, and 50 seeded three-symbol cases. It also passed 536 budget calls and 27 invalid-input calls.

The audit harness initially addressed the oracle using one too many parent directories. The harness path was repaired before any engine comparison; engines were not edited. Its subsequent `--quick` mode was added to bound the SAT audit to the stated small-alphabet corpus.

## Hypergraph certificate checks

For five independent instances (empty feasible, empty infeasible, one-symbol feasible, two-symbol feasible and the three-symbol tied optimum), `certificate.certify` produced OPTIMAL or INFEASIBLE and `hypergraph_checker.verify` returned ACCEPT. For every nonempty optimum witness, replacing its first block by `[]` returned REJECT. Rebinding the valid certificate to a different contradictory instance returned REJECT; malformed certificate data returned REJECT. Producer and checker requests with `max_nodes: 0` returned INCOMPLETE.

## Scope and limitations

Both full-output `solve` APIs accept the executable reference's Python input shape: `alphabet`, `positive`, `negative`. Their finite `max_candidates` behavior is observationally equivalent through a Bell-number preflight after validation and contradiction handling. They do not execute the frozen reference's literal canonical prefix and do not claim its timing, callback or interruption behavior. The engines can require exponential time and memory; caught resource exhaustion returns INCOMPLETE without exact fields. Full C/O values and canonical order are obtained by completed exhaustive search, but no separate independently checkable certificate of those counts has been implemented. The one-optimum hypergraph certificate does not prove counts.

The hypergraph implementation is a standalone mixed-cover engine but its search structurally coincides with least-symbol anchored block recursion. The user authorized its implementation; this audit does not resolve its fundamental-algorithm distinction or establish novelty.

## فارسی کوتاه

هر دو موتور در آزمون‌های کاملِ ثبت‌شده با مرجع فریز‌شده برابر بودند. گواه ابرگراف با بررسی‌کنندهٔ مستقل پذیرفته شد و تغییر عمدی گواه یا نمونهٔ ورودی رد شد. این نتیجه محدود به آزمون‌هاست؛ گواه مستقلی برای شمارش کامل C و O هنوز ساخته نشده و ابرگراف ادعای نوآوری بنیادی ندارد.
