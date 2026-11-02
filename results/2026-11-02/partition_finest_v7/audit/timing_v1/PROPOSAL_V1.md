# C007 v4 timing proposal — frozen, not run

Status: **READY FOR MASTER REVIEW; NO TIMING RUN AUTHORIZED OR STARTED.**

## Question and comparison

Measure the cost of the v4 staged swap path in `adaptive` mode against the exhaustive-binary `reference` mode on three deterministic, already validated rows from the frozen 218-case corpus. The exact same JSON input is used for both modes. This is a narrow diagnostic sample, not a claim about general speedup.

Frozen input manifest: `input_manifest_v1.json`, SHA-256 `0ff7527b1762105971e6883062ab430f2e29203af50f8cf03d4b1eb2579fff17`. Parent corpus SHA-256 `906152be7d6830fac80b722da24873195687ca257650b30a02ec8ace2025c39b`; all-k oracle SHA-256 `a4216c69d0328419086096ff7b28f7efc39f98fb85ff904d798c5a6f54421281`.

| Case | Purpose | Alphabet | Max word | Positives / negatives | Compatible binary cuts | Expected result |
|---|---|---:|---:|---:|---:|---|
| `c007_gen_m04_013` | fallback path and multiple maximal refinements | 4 | 8 | 5 / 14 | 7 | `multiple_maximal_exist` |
| `c007_gen_m06_000` | swap-only path, moderate cut count | 6 | 10 | 1 / 22 | 31 | `finest_unique` |
| `c007_gen_m08_000` | swap-only path, largest registered cut count | 8 | 12 | 1 / 18 | 127 | `finest_unique` |

Selection was fixed without using timing observations: for m=4, choose a fallback/multiple-maximal case; for m=6 and m=8, choose swap-only/unique-finest cases. Within each class, maximize the independently computed compatible-bipartition count, then maximum word length, then case ID. Input and output hashes are in the manifest.

## Frozen execution protocol

- **Provider:** `implementation/finest_solver_v4.py`, SHA-256 `c6c803da1088450d352d56bc1a208d6fa7c0d19416bd702255d866052e454fff`.
- **CLI:** `implementation/finest_cli_v2.py`, SHA-256 `46642a86c315b95de7b784eb614af4000b52fa96ce55c965f1bbb3de1d15e879`.
- **Public wrapper:** `solver.py`, SHA-256 `d4d1644fa3144c68c626fc8daff818e9500a89453a21871df45ffb3e7b7232de`.
- **Protocol:** `implementation/PROTOCOL_V5.md`, SHA-256 `74ee1895c49e40abc5cc1c328bc1fad006e06dde397963dc1779c7266a2a06bd`.
- **Capture:** `evidence/capture.py`, SHA-256 `68ee700f391fb6a1cf135e4b55a11a247b45f25164553c917d1664f6fc4a31cf`.
- Each provider invocation is a fresh process through the public wrapper: `solver.py INPUT --mode MODE --seconds 28`, captured with a hard 30-second deadline. The full JSON stdout, stderr, hashes, environment, exit, child cleanup, and all sources are retained for every invocation.
- Three repetitions per case and mode: **18 maximum provider processes**. Orders are counterbalanced: m4 `A,R / R,A / A,R`; m6 `R,A / A,R / R,A`; m8 `A,R / R,A / A,R` (`A=adaptive`, `R=reference`).
- Serial only. Stop a method at 300 seconds cumulative captured subprocess time; every unrun cell is reported as budget-censored. Nine jobs per method at the hard cap can consume at most 270 seconds.
- Before reporting timings, independently replay every complete JSON result against the frozen all-k oracle and direct-poset oracle. A mismatch, malformed certificate, source drift, unreaped child, or truncated output invalidates that run and pauses comparison; preserve the capture and report the reason. Do not rerun a failed cell without a new preregistration.

## Metrics and limits

Primary measure: `subprocess_seconds` from the capture result for the public CLI process. It includes Python startup, wrapper/CLI setup, input reading and parsing, preprocessing, search, and complete JSON serialization. Report all 18 planned rows, per-case/mode median and range only when all three repetitions completed, plus output bytes and timeout/censor counts. Do not report a ratio if the paired cells do not both have three validated repetitions.

Internal counters and provider timings are secondary descriptions only. In v4 fallback cases, `swap_stage_seconds` includes fallback runtime, while `provider_seconds` omits preliminary swap work; therefore they do not partition elapsed time and must not be summed or described as pure preprocessing/search attribution. No memory measurement is proposed. The earlier 218-row correctness-batch wall times are not timing evidence.

**No timing starts until the master gives explicit GO against this proposal and hash manifest.**
