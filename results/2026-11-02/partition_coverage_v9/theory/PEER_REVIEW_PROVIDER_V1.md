# C009 bounded static peer review — provider v1

Status: no mathematical counting/witness defect found in the reviewed paths;
independent executable gate remains required. This is not test acceptance.
Read-only review; no provider executions or provider edits.

Reviewed source (SHA-256):

* implementation/ownership_solver_v1.py:
  `79255b0a306f8a30dffdd813c018bc4fd9368dad880c07489a86abd50968a5e7`
* implementation/ownership_cli_v1.py:
  `356ac0db3ca272403d95bc275e4babc48c5d7fc29caf00cb9685f8e49aed8507`
* implementation/API_PROTOCOL_V1.md:
  `111226b52eef31fd67dc599082e10ca53ae941f4527e8db48063809a85fd761b`

Snapshots and hashes are in peer_review_provider_v1/MANIFEST.json.

## Proof alignment

1. Lines 110–120 construct exactly R(B) from the original positive and
   negative words. Negative masks may overlap; symbol submasks are disjoint.
2. DP uses `covered` rather than the proof's `uncovered`. The substitution
   U=T\covered gives identical transitions: OR with R(B) versus removing it.
   Base case requires exactly zero blocks and all negatives covered.
3. Lines 133–147 enumerate each submask containing the least remaining
   symbol once, then recurse on the disjoint remainder with one fewer block.
   The canonical count proof applies without a k! divisor.
4. Line 141 adds every entry of the child pair vector without an explicit
   remainder-membership condition. This is **correct**, not a double-counting
   defect: by induction, any pair with a symbol outside the child's remainder
   has entry zero. Lines 142–146 add child totals only to pairs inside the
   newly selected block. Split pairs receive zero from both contributions.
5. Lines 150–153 sum literal sorted distinct allowed counts. Noncontiguous
   K is retained; no interval hull is introduced.
6. `any_suffix` follows positive DP branches. `relation_suffix` disallows
   the first separation for a same request and disallows a joint block for
   a different request. Once either relation is decided, any suffix remains
   valid; deleting already chosen symbols prevents reversal. The manual
   submask update before `continue` skips exactly the rejected branch,
   rather than advancing twice.
7. Pair counts and witness existence are cross-checked at lines 228–229.
   Pair witnesses are partitions, not full projection records, but the
   protocol explicitly permits reconstructing H(B) from the fixed input.
   The representative and optional complete enumeration additionally carry
   direct projection records.
8. Zero total returns model_inconsistent before pair classification, with
   no vacuous forced relation. A stopped protected computation returns
   unknown, complete=false, no exact count or pair/ownership fields.
9. Enumeration follows only positive DP branches, with canonical covers,
   and asserts final enumeration length equals the exact total. A stop
   during enumeration discards finality instead of reporting a truncated
   family as exhaustive.

## Bounded limitations / findings

**R1 — Interrupt protection is not whole-call protection.** The protected
try begins at solver line 107. Input validation (lines 93–96), deadline/type
validation, alphabet masks and pair allocations (103–106) run before it.
A KeyboardInterrupt there propagates rather than returning structured unknown.
CLI input reading, JSON serialization and printing are also outside the
provider's handler. Thus the narrow correct statement is that interrupts
inside the protected compute/witness/enumeration region are handled;
arbitrary-time interruption of the entire call/CLI is not established.
This does not invalidate a completed DP answer. No interruption was injected
by theory, and no universal interrupt guarantee is inferred from static review.

**R2 — Cooperative deadline is not a strict whole-process wall bound.**
The CLI creates its deadline after input reading. `_project` polls every
1024 positions and recursive functions poll at entry. Cached DP returns
bypass function-body polling; branch scans and output serialization do not
poll on every operation. There is no terminal deadline check immediately
before returning a completed result. A fully completed correct proof may
therefore be returned after the nominal cooperative deadline. Scientific
finality and strict wall-budget enforcement are different properties; the
external bounded capture remains needed. This is a scope limitation, not
an assertion that an exact returned answer is mathematically unsound.

**R3 — Counters/timer labels need reporting care.** `witness_search_branches`
is initialized but never incremented, so its zero value does not mean zero
witness search work. Successful `search_seconds` ends after count DP, before
representative/pair witness extraction and optional enumeration. On a stop
after DP, the catch overwrites it with time through the stop, including
those later phases. Do not compare these as consistently scoped identical
phases or use the unused counter as a workload fact. `provider_seconds`
includes successful provider work through witness/enumeration construction,
but excludes CLI read/serialization/output; use external whole-process wall
time for complete CLI cost. No performance conclusion is accepted here.

**R4 — Unsupported extra fields are not active restrictions.** Validation
explicitly rejects legacy `k`, and validates allowed_k, but other unknown
dictionary keys are not inspected. Therefore fields such as a proposed
prime/state restriction must not be presented as enforced input constraints.
The declared model is unrestricted regular factors; this review does not
require a new restricted-class feature. Whether to reject unknown fields
is an input-contract decision for the master, not an established counting bug.

The code does not wrap every possible resource/program exception in a
runtime-error record. No totality claim on arbitrary malformed Python objects
or unlimited input size is made by this review.

## Decision

Core DP, pair aggregation, relation witness search, exact enumeration, and
zero-version semantics align with the proofs. Proceed to independent complete
set and pair-count gate. Retain R1–R4 as precise scope/measurement findings;
master decides whether any require a new implementation version. Source
freezes are not changed or silently repaired by this reviewer.
