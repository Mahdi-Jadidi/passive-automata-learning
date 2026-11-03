# C011 audit protocol v1 — frozen correctness inputs and bounded performance plan

Status at creation: **preregistered data and measurement protocol; no provider, baseline timing, or memory job has launched.** This file is the auditor-owned freeze candidate. Runs remain gated on (1) the captured direct-RGS/family oracle receipt, (2) candidate source readiness and independent static review, and (3) a separate master GO receipt. The three gates do not authorize one another implicitly.

## 1. Fixed model and scope

Use the C010 unrestricted model unchanged: known nonempty finite alphabet, disjoint symbol ownership, independent arbitrary regular local factors, exact complete-word positive/negative labels, no noise, no state bound, no prime promise, and no externally supplied K. The complete answer family, counts by k, every pair relation/count, and valid witnesses must remain exact. Partial/censored output cannot claim finality.

This round evaluates an exact binary-anagram interval must-link extractor and its effect on bounded performance. It does not infer physical device IDs or nontrivial true ownership from finite labels. It does not enumerate full answers in CLI default mode.

## 2. Immutable source and corpus anchors

C010 parent commit frozen by C011: `0e0c52cc33825b9e820e083b8a90db2a9ab120d0`. C011 `coordination/parent_manifest.json` SHA-256: `1d71f4983d83cf8dc2998d3c220607485886a0bb118d9decd554a7cd7778a7c4`.

| Artifact | SHA-256 |
|---|---|
| C011 contract | `16198e1cea3cd61f603ac4ddfa808b5f3773f1aa5bbf9a33ebd10119893b15ce` |
| copied C010 durable capture helper | `68ee700f391fb6a1cf135e4b55a11a247b45f25164553c917d1664f6fc4a31cf` |
| C010 v2 solver baseline | `4c7959e96c02023d85943c8c52fae3f198c0de67ea172a72ad0669485f60c502` |
| C010 v2 CLI baseline | `3140df25bab5d60c6c2705098029db9061e3c9d76743bf1dfd48d46aaf2d5eaa` |
| C010 v2 readiness | `13733c49a331a05dd1b6e59dbb73cd2323d869b17d50bed88f9997ae855b420e` |
| C010 125-case corpus manifest | `82fbc29c1b960cd4b7ca3b177bba586cfdfb8b7cedad55fbade06334d3e13e4c` |
| C010 direct-RGS oracle JSONL | `f14d31d8c1dc2b69e742478b80407bf6ba1efc51e70a10ceb395b6f221206cb9` |
| C010 independent oracle validation | `62390af5472527d9e4504027b140b52fbf214362612e74e5bb0a67feacc68912` |
| C011 correctness manifest v2 (138 cases) | `33d4054fbea394084e32fae3aa8f3a6cdfce62789b7856a7ae8fda21c81fd6b9` |
| C011 revised performance manifest v2 (8 cells) | `546251ced53020b64333015870ca9167385774e331aae5b0d8861570d202a927` |
| C011 collision controls v2 | `c0815ad42936761f198cc2e922c6508f668546d79e668e958d8886c54f52f3c5` |
| C011 direct-RGS/family oracle source v2 | `d1af8af1d8a5a89457eecaa52e4da685b49210f939f6af6607299306a862fcb0` |
| C011 memory probe source v1 | `20959b3fa6fec381fb13cac7c997f2a4d36a87e9a739b581a0e9a17f2c43a4e8` |
| C011 interval-theorem static note | `02422b6f56b2261821766cde372bb49cfa2d7740dcba449195da469f94d4d8ff` |

The C011 corpus contains **138** exact small/full-set cases: 125 reused C010 valid unique cases, 10 targeted regressions (the duplicate-label case is one of these ten), one m=8 graph-empty performance control, and two appended fingerprint-collision controls. Every full-set input has m≤8. The C010 125 expected families are reused byte-for-byte with their accepted direct-RGS oracle; the 13 added cases are computed by C011's provider-independent canonical-RGS oracle and direct projection feasibility. The copied direct oracle has no provider imports. Acceptance also replays every pair witness and checks exact full families, all k counts, and all pair counts/relations.

Targeted regressions cover non-adjacent binary anagram intervals (`aab/baa`, `aabb/bbaa`), an exact shared-context interval (`caabd/cbaad`), the unsafe three-symbol window (`acb/bca`), duplicate-label idempotence, unary input, no negatives, no labels, graph-empty fallback, repeated-symbol adjacent swap, and the two forced-collision contexts. The latter require a test-only constant-fingerprint seam or an audit monkeypatch of the candidate's private fingerprint function. Case `hash_collision_keep_all_contexts` checks that the second exact-context representative is not lost; `hash_collision_exact_context_guard` checks that unequal outside contexts cannot create an edge.

The C010 invalid input controls and expired-deadline/synthetic-interrupt controls are copied under `audit/controls/`; they are run only against a ready, statically reviewed candidate and are compared to their frozen C010 contracts. The injected interrupt is not an OS signal race.

## 3. Interval theorem and certificate checks

For `p=u s v` positive and `n=u t v` negative, if the outside strings u,v are exactly equal and s,t use only distinct symbols x,y with equal x- and y-counts, then any ownership partition separating x,y yields identical p/n projections on every block: the x-owner sees the same x-run count, the y-owner sees the same y-run count, and all other blocks erase the interval. The factor model would then accept n whenever it accepts p. Hence every compatible partition must co-own x,y.

Fingerprints are candidate keys only. Before union or certification, verify exact boundaries, full outside prefix/suffix equality, interval alphabet `{x,y}`, exact x/y counts, and label polarity. The candidate must retain all colliding representatives. Its new `mustlink_interval_certificates` field is additive; the existing adjacent-swap certificate field remains separate. Independently replay all interval certificates. Separately test promised extractor coverage: omission of a sound edge may leave a complete exact fallback answer set correct, but does not substantiate exhaustive interval extraction.

The phrase “RLE groups of consecutive transitions with the same unordered pair” must be defined in the source/reviewer proof. If it denotes literal repeated transition labels only, it may miss non-alternating windows such as `aabb/bbaa`; no completeness claim passes without the frozen RGS and coverage controls. Hash collision coverage is explicitly tested. The `acb/bca` window includes a third symbol, violates the binary premise, and must not force any pair.

The exact family comparator compares every semantic field: complete/status, full compatible partition set where enumerated, total and all per-k counts, k bounds, every pair relation/count and both witnesses, atom semantics, and representative witness. Only method identifier, implementation-specific metrics, and the one documented additive interval-certificate field may differ. No other omission/addition is silently normalized.

## 4. Larger family oracle, not Bell(m) enumeration

For structured cells, the independent checker will compare every positive/negative word pair for exact adjacent-swap edges, prove the edge union components equal the advertised groups, and directly check the atom partition rejects every negative by projection. The already reviewed coarsening theorem then makes the exact compatible family all coarsenings of r atoms; Bell(r), Stirling S(r,k), and pair counts Bell(r−1) follow by recurrence. The checker must not enumerate Bell(m) for m=64 or 128, and must report both m (symbols) and r (atoms): m=64,r=8 gives Bell(8)=4,140; m=128,r=16 gives Bell(16)=10,480,142. For m=128 it may compute S(16,k) and Bell(15)=1,382,958 by recurrence only.

The graph-empty m=8 negative control has zero adjacent-swap edges and an infeasible singleton atom partition; its full family, spectrum, and pair witnesses are obtained from direct RGS enumeration over at most Bell(8)=4,140. No graph absence is treated as proof of independence.

Expected structured families after the v2 pair-local context fix:

| Cell type | m | r | Expected family size | Same count within atom | Same count across atoms |
|---|---:|---:|---:|---:|---:|
| three pair-context volume cases | 8 | 4 | Bell(4)=15 | 15 | Bell(3)=5 |
| two long-word pair-context cases | 8 | 4 | Bell(4)=15 | 15 | Bell(3)=5 |
| structured alphabet | 64 | 8 | Bell(8)=4,140 | 4,140 | Bell(7)=877 |
| structured alphabet | 128 | 16 | Bell(16)=10,480,142 | 10,480,142 | Bell(15)=1,382,958 |

The v1 auditor's initial cross-group contexts did not satisfy the advertised atom-feasibility precondition. That harness failure and its partial outputs are preserved; the v2 generator restricts volume contexts to their own pair and is separately captured. No provider or timing job was run on v1.

## 5. Frozen performance design

Exactly eight cells, with three small profiles followed by five scale profiles:

1. m=8, 128 positive / 128 negative, short pair-local contexts.
2. m=8, 512 / 512, short pair-local contexts.
3. m=8, four 10,000-symbol positives and four negatives.
4. m=8, 1,000 / 1,000, short pair-local contexts.
5. m=8, four 100,000-symbol positives and four negatives.
6. m=64, 8 verified groups of 8 symbols, 224 positives / 224 negatives.
7. m=128, 16 verified groups of 8 symbols, 448 positives / 448 negatives.
8. m=8, graph-empty unstructured fallback control, 1 positive / 1 negative.

Each method/cell gets exactly three fresh CLI processes with the same input, default expanded output and partition enumeration disabled. CLI arguments use cooperative `--seconds 28`; the durable C010 capture helper applies a 30-second hard child cap. Timeout/incomplete output is preserved as censored and is never rerun or counted as exact. Every capture stores raw stdout/stderr, child status/reap, source snapshots, output size and both `subprocess_seconds` and `duration_seconds`. `subprocess_seconds` measures the whole child CLI from spawn through reap, including Python startup, input read, preprocessing, witness construction and output serialization. `duration_seconds` additionally includes source snapshot and capture overhead.

With candidate source ready, run cell/repetition pairs in the frozen manifest order; within repetition 1 use baseline then candidate, repetition 2 candidate then baseline, repetition 3 baseline then candidate. Do not launch the baseline early as a separate block while candidate source is absent; paired interleaving avoids order bias. The source-binding amendment and independent static review must precede both methods.

The all-in per-method limit is 900 seconds, including eight separate tracemalloc probes. There are at most 24 CLI runs (720 seconds of hard child caps) and eight memory probes (12-second cap each; 96 seconds), leaving 84 seconds for capture overhead. Enforce the budget before each launch; if it cannot fit, mark unstarted cells/repetitions budget-censored and retain all completed records. Do not replace timeout or slow cases.

Memory is measured separately once per cell/method in a fresh process using only standard-library `tracemalloc`, starting before input load/import and ending after the exact default solver call plus default JSON serialization. The result is peak traced Python allocation, not OS/native RSS or a general memory claim; each probe has a 12-second hard cap. The total method budget includes these probes.

Record raw stdout bytes and JSON bytes for every method. The candidate may add the interval certificate and its implementation-specific metrics, so raw byte equality is not expected. No output-size reduction claim is valid unless all baseline semantic fields and witnesses are present and exact. Do not suppress pairs, counts, or witnesses for speed.

## 6. Candidate binding, launch gates, and preserved failures

The candidate source is not ready and has no hash in this preregistration. Before any baseline or candidate run, add an immutable source/readiness binding and an independent static review that clears the exact RLE/interval definition, hash collision behavior, certificates, and deadline/incomplete semantics. Then require a separate master GO receipt in `audit/MASTER_GO_V1.json`; the capture drivers refuse to launch without it. The baseline remains the frozen C010 v2 solver/CLI above. No dependency is installed.

All oracle validation, controls, baseline/candidate CLI, and memory measurements use the byte-identical copied C010 capture helper at `audit/capture.py` in C011, never the Windows `python` alias. Builder and oracle failures remain versioned and are never overwritten. Uncaptured pre-capture construction errors are explicitly marked as having no raw logs; they are not reconstructed as if captured. The current preserved records are `MANUAL_ATTEMPTS_V1.json` through `MANUAL_ATTEMPTS_V4.json`, plus the failed v1 oracle's partial JSONL outputs.

No baseline, candidate, invalid-control, deadline-control, or memory run has launched under this protocol. No speedup is assumed. A correct but slower candidate, timeout/censoring, or missed accelerator coverage is an admissible negative result.