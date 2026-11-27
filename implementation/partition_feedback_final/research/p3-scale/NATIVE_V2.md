# Review10 compact native v2 experiment

The experimental entry point is `selector_v2.scale_search`. Its traversal is
derived from frozen M4, including literal discovery and the all-pairs fallback.
`--compact` selects CompactProjections. `--targeted` independently enables
singleton-deletion discovery. With dense or sparse compatibility, targeted
discovery charges a compact recheck in the discovery phase to recover the
first failed negative. Targeted discovery uses `fact_limit=0`. The singleton
projection index is a deterministic function of the immutable sample and is
rebuilt on resume. Its build charge can land at different nodes across
invocations. The resume gate compares completed certificate bytes with adequate
finish budgets. Capped prefixes and telemetry can differ.

## Paired experiment pins

| Input | Pin |
| --- | --- |
| Review10 | `e7a5993e3593d99e7d19ac30ebf31e9b6bbde92e` |
| Producer checkout | `1e1bd145e28cbe3baed6547f9267bd587e3260a5` |
| Experimental entry blob | `5090fcd56aecee366abc9e1ac875fd3bb00f8504` |
| Frozen M4 entry blob | `fc9ea03e0bd008d528bf115a5b5b8e7eb13ce2b8` |
| Independent verifier checkout and blob | `98e913a7e15d32638319832fc69edb36edb2f505` / `5b7df580336f562e046f7b726a5e38a6e1335a51` |
| Native M3 evidence tree | `bd3184355b3685214af54597475278126d541a05` |
| Cover and raw large fixtures | `8484b8bff5b93e1be3a7924697161efc34e481d8` |
| Retained medium and huge scopes and journals | `444cea666816a4faaf875a831ec4a3949c673a4b` |
| Interface for journal construction | `122844ee5668f1c898f85b08133a562f31719718` |

For the paired comparison, use no evaluator flag for dense, `--sparse` for
sparse, `--compact` for compact and `--compact --targeted` for the discovery
ablation. Use the same raw bytes, trusted scope, objective mode and cap profile
across arms. The pairing pins were posted in [issue #11](https://github.com/Mahdi-Jadidi/passive-automata-learning/issues/11#issuecomment-7221638002).

## Reproduction

The [workflow](../../../../.github/workflows/p3-scale-native.yml) checks out
each source at its pin and runs CPython 3.13.5 on Ubuntu 24.04 in normal and
`-O` mode with 512 and 1536 MiB address-space caps. For large search the
original limits are 10 million work units, 25 seconds cooperative, 30 seconds
external, 2 million frontier admissions and 64 MiB frontier payload.
Compact and sparse each use the original 64 MiB logical scratch cap. Dense
compatibility has no logical scratch instrumentation. RSS is the high-water
mark of the fresh search process including input loading. Compatibility and
discovery cumulative time and work, total search time and work, root phases,
and index and frontier peaks are recorded separately.

The contracted test builds RAW closure and exports an authoritative journal/2,
independently derives its scope, and compares both byte-for-byte with the
retained artifacts before running search in a fresh process. Both roots have
one genuine merge. Replay runs in a separate process with the pinned verifier
on certificate bytes read from disk. The native gate also replays actual bytes.
For the native cases of up to twelve symbols, it checks against literal RGS.
Small uses the retained exhaustive result. Cover has 16 symbols and uses
frozen dense parity and independent certificate replay.

## Native results

The native jobs verified 240 complete v2 outputs and compared 440 completed
resumes byte-for-byte with their uninterrupted runs across the two memory
limits and both interpreters. Within each memory job, normal and `-O`
complete and resumed files matched. The five requested fixtures matched
the dense certificate bytes with targeted discovery disabled.

All five requested fixtures produced zero targeted hits. The separate
three-symbol control emitted a targeted witness in both objective modes
with dense and compact compatibility. It exercised checkpointing before
and after split admission and verified the literal fallback with a zero
targeted work budget. The 16-symbol cover returned cost 4 and nine optima
in all mode. Cover replay verified 641 nodes in one mode and 3,271 in all
mode on the compact targeted arm.

## Contracted results

The searches used one-optimum mode. Dense hit the work cap before deciding
either root. Sparse decided medium and hit the logical scratch cap on huge.
That scratch stop uses the existing `FRONTIER_CAP` certificate reason.
Compact decided both roots incompatible and continued searching. These
runs retain unresolved frontiers under the original limits. All 32 emitted partial certificates replayed as INCOMPLETE with an unresolved frontier. For each case and arm, the four memory/runtime combinations emitted identical partial certificate bytes.

| Root and arm | Root work | Discovery work at root | Nodes emitted | Peak logical scratch |
| --- | ---: | ---: | ---: | ---: |
| Medium dense | 9,963,699 (capped) | 0 | 1 | uninstrumented |
| Medium sparse | 69,422 | 4,078 | 265 | 850,464 B |
| Medium compact | 119,044 | 4,078 | 263 | 287,728 B |
| Medium compact + targeted | 119,044 | 25,687 | 205 | 285,768 B |
| Huge dense | 9,691,999 (capped) | 0 | 1 | uninstrumented |
| Huge sparse | 475,825 (capped) | 0 | 1 | 67,108,808 B |
| Huge compact | 1,130,014 | 4,096 | 21 | 15,242,448 B |
| Huge compact + targeted | 1,130,014 | 130,252 | 17 | 15,242,440 B |

Targeted discovery had zero hits on the contracted fixtures. It spent more
work per discovery call and left fewer admissions within the common work
budget. Medium compact and sparse had similar process RSS despite different
logical scratch charges. On huge, the compact evaluator completed the root
at substantially lower scratch and RSS than the censored sparse run.
The experiment establishes a compatibility result at huge and leaves
both large optima unresolved. The paired Agent #4 experiment is tracked
separately on issue #11.

| Root and arm | Search seconds | Peak RSS KiB |
| --- | ---: | ---: |
| Medium dense | 2.320–2.647 | 27,092–30,044 |
| Medium sparse | 0.620–0.689 | 27,052–29,848 |
| Medium compact | 0.510–0.588 | 27,164–29,464 |
| Medium compact + targeted | 1.229–1.467 | 26,892–30,148 |
| Huge dense | 2.697–4.168 | 84,796–87,124 |
| Huge sparse | 0.188–0.271 | 116,256–117,980 |
| Huge compact | 1.088–1.799 | 89,332–90,636 |
| Huge compact + targeted | 1.550–2.497 | 88,432–90,248 |

Censored runs do different amounts of search. The timing ranges describe the
measured stopping points under the caps.

## CI evidence

All six jobs passed at `565c2981a4dccf41a3d2e33ed10b1f868202c1ce`.
The artifacts contain the original emitted proofs, resume files, journal and
scope bytes, and verifier results. The [committed metrics](native-v2-ci.json)
retain the complete native certificate digests and the contracted phase rows.
The profile-only regression also passed all four jobs with the new producer
source. The first native CI attempt failed because the interface adapter was
absent from the checkout. The successful run pins that adapter and its path.

- [Final native and contracted CI](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/46022371839)
- [Existing compact and targeted regression CI](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/46021879243)
- [Initial workflow failure](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/46021526382)
