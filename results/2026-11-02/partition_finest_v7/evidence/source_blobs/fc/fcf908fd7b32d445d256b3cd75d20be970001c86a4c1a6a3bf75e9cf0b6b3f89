# C007 v4 timing proposal V2 — frozen, not run

Status: **READY FOR MASTER GO; NO PROVIDER TIMING HAS RUN.** V1 remains preserved and unrun. V2 replaces only the planned m=6 singleton fast-path case with a correctness-accepted case that has no forced-edge graph and requires adaptive separator search.

## Question and interpretation

Compare `adaptive` and `reference` on the same three frozen inputs to measure **time to the same certified finest-partition decision**. Both methods must return the same all-k decision for each input, while their certificates and serialized output sizes can differ. `reference` enumerates compatible bipartitions; `adaptive` searches separators and can stop once it proves its decision. These results are not identical-enumeration measurements and must not be presented as a pure search-speed ratio.

Frozen input manifest: `input_manifest_v2.json`, SHA-256 `e07b0a15559becc5b13a44a5baee978b7ccefb86f06a0a4034aaa668b4625737`. It binds the individual input hashes, all-k RGS/poset oracle sources, and the already accepted v4 targeted-control gate. V1's unused input and proposal remain intact.

| Case | Purpose | Alphabet | Max word | Positives / negatives | Compatible binary cuts | Expected decision |
|---|---|---:|---:|---:|---:|---|
| `c007_gen_m04_013` | fallback path; multiple maximal refinements | 4 | 8 | 5 / 14 | 7 | `multiple_maximal_exist` |
| `ctrl_empty_must_link_unique_3` | empty forced graph; unique nontrivial three-block result; separator cover | 6 | 4 | 4 / 3 | 3 | `finest_unique`, `ab|cd|ef` |
| `c007_gen_m08_000` | singleton swap-only path; largest registered cut count | 8 | 12 | 1 / 18 | 127 | `finest_unique` |

Selection uses no timing observations. The m=4 fallback and m=8 swap-only rows are retained from V1. The m=6 row is the previously frozen empty-must-link control; its adaptive and reference outputs were independently accepted against 5 all-k compatible partitions and the direct-poset oracle. This adds a case where v4 finds no forced edges and must establish the nontrivial unique finest partition through separators.

## Frozen execution protocol

- **Provider:** `implementation/finest_solver_v4.py`, SHA-256 `c6c803da1088450d352d56bc1a208d6fa7c0d19416bd702255d866052e454fff`.
- **CLI:** `implementation/finest_cli_v2.py`, SHA-256 `46642a86c315b95de7b784eb614af4000b52fa96ce55c965f1bbb3de1d15e879`.
- **Public wrapper:** `solver.py`, SHA-256 `d4d1644fa3144c68c626fc8daff818e9500a89453a21871df45ffb3e7b7232de`.
- **Protocol:** `implementation/PROTOCOL_V5.md`, SHA-256 `74ee1895c49e40abc5cc1c328bc1fad006e06dde397963dc1779c7266a2a06bd`.
- **Capture:** `evidence/capture.py`, SHA-256 `68ee700f391fb6a1cf135e4b55a11a247b45f25164553c917d1664f6fc4a31cf`.
- Each invocation uses a fresh process through the public wrapper: `solver.py INPUT --mode MODE --seconds 28`; `capture.py` enforces a 30-second hard deadline. Preserve full JSON stdout, stderr, source snapshots, hashes, environment, exit status, and child cleanup for every invocation.
- Three repetitions per case and mode: **18 maximum provider processes**. Counterbalanced order by cell: m4 `A,R / R,A / A,R`; m6 `R,A / A,R / R,A`; m8 `A,R / R,A / A,R` (`A=adaptive`, `R=reference`). Serial execution only.
- Maximum captured subprocess budget: 300 seconds per method. There are nine jobs per method, so nine hard-deadline runs can consume at most 270 seconds. Preserve every timeout or unrun cell; do not rerun a failed cell without new preregistration.
- Independently replay each complete result against the matching frozen all-k oracle and direct-poset oracle before including its timing. A mismatch, bad witness, source drift, unreaped child, or malformed/truncated result pauses the comparison. Keep that capture and its failure reason.

## Metrics and limits

Primary measure: capture `subprocess_seconds` for the public CLI process, including Python startup, wrapper/CLI setup, input read/parse, preprocessing, search, and complete JSON serialization. Report per-case/per-mode medians and ranges only for three complete, independently accepted repetitions. Also report output bytes, certificate kind and size, timeouts/censoring, and method counters. Do not compute a ratio unless both sides have three validated repetitions for that case. No memory measurement is planned.

V4 internal timing fields are secondary diagnostics. On fallback, `swap_stage_seconds` includes fallback runtime and `provider_seconds` omits preliminary swap work; they do not partition total elapsed time and must not be summed or described as pure preprocessing/search time. Earlier 218-row correctness-batch wall times are not timing evidence.

**This proposal is frozen for review. Timing remains on hold until the master explicitly replies GO to V2.**
