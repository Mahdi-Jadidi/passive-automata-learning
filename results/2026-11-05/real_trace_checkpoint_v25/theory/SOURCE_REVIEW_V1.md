# C025 selected-output actual-source review v1

Verdict: no blocking algorithmic correctness bug found by static mathematical/source inspection. Independent execution/replay is still required. No experiments or solver edits were performed by this reviewer.

## Source identity
Read complete files under implementation/selected_output_v1:
- solver_v1.py SHA256 73ff8ecae70a55525ec6a2d3f1216e721ad2f1298d973d334e6f743080358e4e (matches requested source).
- cli_v1.py SHA256 89f58a396593921ba8accc664de8d7e3ff94e7de9a7d7e8ca01211042ca6f2ef.
Hashes were locally recomputed. MODEL_CONTRACT_V1.md and C017 SELECTED_OUTPUT_PROOFS_v1.md supply the proof contract; source inspection is not new experimental evidence.

## Exact final-block cover
At cover(remaining,masks), selected masks are disjoint FINAL blocks and partition the complement of remaining. The least remaining bit anchors the next block. Descending submask enumeration visits every subset of the other remaining bits exactly once, so every possible next block occurs once. Any complete unordered partition has exactly one such recursive path: its block containing the least remaining symbol is forced first. No partial-block incompatibility prune is used.

block(candidate) rejects exactly an inconsistent finalized block; a completion containing it cannot satisfy the model. Thus rejecting it is safe even though a different larger block could be consistent. K bounds are sound: selected count cannot decrease and at most one block per remaining symbol can be added; when already at K with remaining symbols, no completion is possible. Terminal count checks enforce exact K.

Two successful terminal paths yield distinct partitions and replayable witnesses, so stop2 proves ambiguity. If fewer than two are found, normal recursion return has exhausted every admissible path, giving unique for one solution and incompatible for zero. Interruptions escape through unresolved before proof construction/emit. search_exhausted is internal completion metadata, not a separate replayable enumeration certificate.

## Context and witness semantics
Finite depth uses (tuple(prior local IDs),current), then appends current. deque(maxlen=0) gives depth0 current-type constancy. Other-block events do not advance local history. Unknown-labelled local events do advance it. Each trace starts empty, with the same output table across traces.

Full depth interns (parent ID,current) across all traces for this block, resetting prefix to root per trace. Inductively a node identifies exactly one local word and equal local words receive the same node. Known outputs indexed by that node therefore implement complete projected history through current. The shared trie includes unknown-labelled events; it does not reset at unknowns or use outcome as input. Conflict references identify two events with unequal outputs and equal context under the chosen block/depth.

witness repeats the same context construction, retains one known output per context, and emits trie transitions for full depth. Unspecified outputs/extensions are marked arbitrary. Together these define a finite realization under the prior proof; they are not a uniquely determined predictor. Full-depth trie output rules refer to destination nodes, equivalent to the unique incoming transition. Finite-depth fallback can use suffix states; no AND acceptance semantics enter the source.

## Validation, API and resources
All traces/events are validated before block search, including late records. Nonempty distinct atomic strings, 1..8 alphabet, bool-or-None labels, unique integer file IDs, exact field sets, supported depth/model and optional externally supplied K are checked. bool is excluded from integer depth/K/deadline by exact type checks. Deadline and resource failures return unresolved; malformed data returns invalid_input. Expired deadline can preempt schema validation, so unresolved does not imply a fully validated input. Empty traces impose no output constraints. Opposite same-context labels are valid model incompatibility, not malformed data.

Polls occur during validation, scans, recursion, witness-rule construction and final emit. The CLI includes input read/parse time in the deadline handed to solve. Cooperative polling does not interrupt native read/JSON parse or individual allocations; retain an outer process cap.

Nonblocking operational limitation: CLI json.dumps/print occurs after the solver’s final deadline poll and outside its resource-exception try block. Thus --seconds is not a hard cap on serialization/output; a serialization MemoryError or broken output pipe can terminate without structured unresolved JSON. This does not invalidate a completed solver decision, but the capture adapter must retain such process errors rather than treat missing output as incompatible or complete. Harden this boundary if structured resource exits through output are part of the promised CLI contract.

## Review findings and audit obligations
The source comment says “Adapted from tested C017 evaluate_block.” Historical C017 drafts were recorded unrun at pause. Unless a newer independent test record supports that wording, correct the provenance comment; this is a documentation issue, not an algorithmic bug. This reviewer makes no C017 test-pass claim.

Independent audit should compare full small partition families at each depth/K, replay witness rules and conflicts using direct projected histories, and exercise CE1–CE6, duplicate/empty traces, unknown history events, late malformed records, deadline zero and interruption mid-search. Verify caller-owned top8 selection, source-boundary conventions and protected-metadata separation independently: this solver accepts already-selected inputs and cannot establish those ingestion properties. It imports no C024 swap graph, envelope or bipartition shortcut, as required for finite depths.

## BGL provenance correction confirmed
The acquisition exists at C:\Users\Mahdi\Documents\ChatGPT\passive automata learning\results\2026-11-05\real_trace_checkpoint_v25\external\loghub_bgl_v1, pinned to dd61d0952749ee7963bde24220d1be5ede023033. All five ACQUISITION_V1.json-listed local SHA256 values previously matched independent recomputation. ADVISOR_NARRATIVE_V1.md and INPUT_LEDGER_V1.md already correct the earlier wrong repository-root path. The ledger records acquisition/README/license reads and raw/CSV hashing scope; this is integrity evidence, not BGL inference results.

## Smoke evidence qualification (supersedes provenance concern above)
Read-only follow-up inspected smoke_v1.py and smoke_results_v1.json. The script compares every evaluated block with an explicit tuple-history oracle and a copied C017 evaluate_block. The report records passed=true across162 fixture/depth/K rows, matching reviewed solver SHA256 and real_data_solver_runs=0. The copied C017 evaluator has the same SHA256 as historical contexts_v1.py. Therefore the source comment has limited developer-smoke support; it should be understood as tested on these fixtures, not independently audited or exercised on historical C017 actual data. The earlier conditional request to substantiate that wording is satisfied at this limited scope. No tests were run by this reviewer.
