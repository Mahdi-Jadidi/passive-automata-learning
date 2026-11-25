# P3 serialization and independent verification contract v1

**Status: integration-lead freeze for P3 M2.** This file supersedes the draft serialization section in `research/audit/P3_REGION_COVERAGE_CONTRACT.md` for the first executable producer/verifier integration. It does not change selector-v2/1 or journal/2. Structural search only; unrestricted `ALL_PARTITIONS`, `B=0`. Operational status is always INCOMPLETE.

## 1. Mathematical object

Original ordered alphabet has IDs `0..n-1`; original positive and negative trace IDs are their positions in the raw ordered arrays (duplicates remain distinct IDs). For complete canonical owner array `p`, equal owners define blocks and each owner is the minimum original ID in its block. Structural compatibility is

`forall y_i in Y, exists block B in p: for every x_j in X, projection_B(y_i) != projection_B(x_j)`.

Cost is `n - number_of_distinct_owners`.

A region is `R(E,D) = {p : p coarsens E and p[a] != p[b] for every (a,b) in D}`. E is a complete canonical owner array over all original IDs; D is sorted, unique, unordered original-ID endpoint pairs. D is branch-local and never rewritten to ephemeral DSU roots. An E/D contradiction is an empty region.

The minimum-cost member of a nonempty region is E itself, with base lower bound `LB(E)=n-|classes(E)|`. Any strict coarsening has strictly greater cost. Therefore `FEASIBLE_MIN` is a valid region closure whenever E itself passes the literal structural test, even if the region has other members. This closure is important: it records E as the unique minimum-cost member of that region. `EXACT_NO` is allowed only when the region is a singleton.

## 2. Trusted scope bootstrap

Producer input and proof input are separate from the journal. The bootstrap artifact has exactly these fields:

```json
{
  "format": "p3-trusted-scope/v1",
  "sample_digest": "<64 lowercase hex>",
  "scope": {
    "version": "selector-v2/1",
    "sample_digest": "<same digest>",
    "family": "ALL_PARTITIONS",
    "regime": "UNRESTRICTED",
    "capacity_digest": null
  },
  "root_source": "IDENTITY",
  "journal2_sha256": null,
  "journal2_state": "IDENTITY",
  "root_owner": [0, 1, 2]
}
```

The example is schematic; owner length is exactly n.

Allowed root sources:
- `IDENTITY`: no P2 contraction is used. `journal2_sha256=null`, `journal2_state=IDENTITY`, and `root_owner=[0,...,n-1]`.
- `JOURNAL2`: exact canonical uncompressed journal/2 bytes are supplied separately to the verifier. `journal2_sha256` is SHA-256 of the exact byte string passed to independent `journal_v2_replay.verify_journal(raw, scope, journal_bytes)` (not the gzip/container bytes). The verifier requires that call to return VERIFIED, then derives `root_owner` from `result.proof.mandatory_owner` and `journal2_state` from `result.proof.closure_state`. Accepted states are OPEN, PARTIAL, FIXPOINT or LABEL_CONFLICT. Partial verified contractions are safe mandatory equalities; they need not be a fixpoint for search completeness. If journal replay is INVALID/INCOMPLETE, do not use it: restart from IDENTITY rather than trust producer-supplied contractions.

The verifier independently recomputes the sample digest from exactly the raw three-key object `alphabet, positive, negative`; validates the exact five-field selector scope above; replays journal/2 when root_source=JOURNAL2; and compares every bootstrap field. The producer never chooses or asserts root_owner. A LABEL_CONFLICT journal state is also rechecked directly against raw opposite-label traces.

The `scope_digest` referenced by the certificate is SHA-256 of canonical JSON bytes for the trusted-scope object above. Canonical JSON is UTF-8 `json.dumps(obj, ensure_ascii=True, separators=(',', ':'), sort_keys=True, allow_nan=False)`. The digest is over the object without a scope_digest field. Strict parsers reject duplicate keys, non-finite numbers, wrong types, unknown fields and noncanonical byte encodings. The proof implementation must implement canonicalization independently; it must not import producer `selector_v2.schema`.

## 3. Certificate header and common node grammar

The certificate has exactly these top-level fields in one-optimum mode:

```json
{
  "format": "p3-region-frontier/v1",
  "scope_digest": "<trusted scope digest>",
  "mode": "ONE_OPTIMUM",
  "search_status": "PARTIAL",
  "incumbent_node_id": null,
  "nodes": []
}
```

For `ALL_OPTIMA`, the header has the same fields and additionally `optimum_node_ids` only when `search_status=EXHAUSTED`. It is the exact sorted list of all feasible minimum-cost FEASIBLE_MIN node IDs; it is empty if no feasible partition exists. One-optimum certificates must not contain `optimum_node_ids`. PARTIAL certificates must not claim an all-optima list.

Every node has these common fields:
- `id`: deterministic path ID.
- `parent_id`: null only for root; otherwise exact parent path.
- `edge`: ROOT, CHILD or RESIDUAL descriptor.
- `owner`: complete canonical owner array over all n original IDs.
- `disequalities`: sorted unique list of sorted two-integer original-ID pairs.
- `kind`: OPEN, SPLIT or LEAF.

Root is exactly id `root`, parent_id null, edge `{"kind":"ROOT"}`, owner equal to independently derived root_owner, and empty D.

For child index j of parent id q: id is `q/cj`, parent_id=q, edge is `{"kind":"CHILD","index":j,"pair":[a,b]}`. For residual: id is `q/r`, parent_id=q, edge is `{"kind":"RESIDUAL"}`. IDs and parent/edge fields are recomputed; they are not trusted labels. Node array is strictly sorted by id and IDs are unique. Every nonroot node is referenced exactly once by its parent SPLIT; all nodes are reachable from root. Orphans, duplicate references, missing nodes and reparenting are INVALID.

The verifier independently reconstructs every node's E and D from its parent and edge, using its own simple graph/connected-component routine (not producer DSU), then compares the full serialized owner and D. Original unused symbols remain in every owner array.

## 4. SPLIT v1: complete all-pairs fallback

M2 initially accepts only `ALL_PAIRS_LEX_V1`. Given parent owner E and D:
1. Let C be the sorted distinct minimum-original-ID representatives in E.
2. Enumerate every unordered pair (a,b) in lexicographic combinations order.
3. A pair is blocked if some original disequality (u,v) in D has E-class endpoints {E[u],E[v]}={a,b}. Exclude blocked pairs because no member of R(E,D) can merge those classes.
4. The complete alternatives list L is every remaining pair, in that order.

The SPLIT node has exactly these additional fields:

```json
{
  "rule": "ALL_PAIRS_LEX_V1",
  "alternatives_sha256": "<sha256 of canonical JSON [[a,b], ...]>",
  "alternative_count": 2,
  "cursor": 1,
  "children": ["root/c0"],
  "cursor_log": [
    {"from": 0, "to": 1, "child_id": "root/c0", "pair": [0,1]}
  ],
  "residual_id": "root/r",
  "suffix": {
    "rule": "FIRST_TRUE_SUFFIX_V1",
    "start": 1,
    "stop": 2,
    "alternatives_sha256": "<same alternatives hash>"
  }
}
```

For each j in `[0,cursor)`, child j has owner equal to equivalence closure of parent E plus equality (a_j,b_j), and D equal to canonical union of parent D and alternatives `L[:j]`. The cursor log must contain exactly one step `j -> j+1` in order, naming the exact child and L[j]. Children must equal exactly the IDs `q/c0...q/c(cursor-1)`; no gaps or reordering.

Residual `q/r` has the same E and D equal to canonical union of parent D and all of L. It is always explicit, even when empty or immediately closable. It must never be omitted.

If cursor < |L|, suffix is exactly the symbolic union of first-true children with index in [cursor, |L|): all earlier pairs L[:cursor] are false and at least one pair in L[cursor:] is true, with the unique first true pair determining the child. The suffix hash binds the verifier-derived full L. If cursor=|L|, suffix is null. Cursor cannot exceed |L|. A resource stop leaves the suffix intact; it cannot be silently discarded.

Why this is complete: every strict coarsening of E merges at least one pair of distinct E-classes. Since the completion satisfies D, that merged pair is not blocked and occurs in L. It belongs to the child for its unique first true pair. E itself belongs to the residual. First-true children are pairwise disjoint and disjoint from the residual. Thus children plus residual partition the parent. If L is empty, the region is a singleton and must be a LEAF, not a zero-progress SPLIT.

## 5. LEAF closure rules

A LEAF has common fields plus `reason` and only the reason-specific fields below. Unknown closure reasons are INVALID.

- `EMPTY`: no extra fields. Valid iff some D endpoint pair is already in one E class.
- `RAW_LABEL_CONFLICT`: fields `negative_id, positive_id`. Valid iff those exact raw words are byte/token-identical across opposite labels. This is global structural infeasibility.
- `EXACT_NO`: fields `failed_negative, positive_by_class`, where positive_by_class is a sorted array of `[class_rep, positive_id]`, exactly one for every current E class. Valid only if region is a singleton: for every pair of distinct E classes, D contains at least one original endpoint pair crossing those classes. The verifier checks for the selected negative and each class that the named positive has exactly equal ordered projection on that class. If n=0 and a negative exists, the class list is empty and the existential block condition is false.
- `FEASIBLE_MIN`: fields `separating_groups`, exactly one class representative per negative trace, in original negative ID order. Valid for any nonempty region. The verifier checks that E itself is a member of R(E,D), and for each negative the named E block's ordered projection differs from every positive projection. This closes the whole region because E is its unique minimum-cost member; every strict coarsening costs more. With no negatives the witness list is empty and E is vacuously compatible.
- `COST`: field `incumbent_node_id`, equal to the header incumbent_node_id. It must reference a FEASIBLE_MIN leaf. Verify the base lower bound `n - |classes(E)|` against the incumbent cost U: ONE_OPTIMUM permits LB >= U; ALL_OPTIMA permits only LB > U. No other bound is accepted in v1.

For a nonempty region the incumbent is always a checked FEASIBLE_MIN leaf, never a mock ACCEPT or BOUNDED_NO. If there are feasible leaves, header incumbent_node_id is the minimum-cost FEASIBLE_MIN node among all represented leaves (ties may choose any one in ONE_OPTIMUM). If there are none it is null. A PARTIAL certificate may report this best-known incumbent but never an optimum result. In EXHAUSTED ONE_OPTIMUM, incumbent must be a global minimum among all FEASIBLE_MIN leaves. In EXHAUSTED ALL_OPTIMA, optimum_node_ids must equal every FEASIBLE_MIN node at the minimum cost; COST pruning is strict, so equal-cost regions cannot be omitted.

## 6. OPEN nodes and search status

OPEN nodes have exactly one extra field `reason`: TIME_CAP, WORK_CAP, ENTRY_CAP, FRONTIER_CAP or USER_STOP. They remain unresolved tasks.

- `search_status=PARTIAL` iff at least one OPEN node or nonempty SPLIT suffix exists. Verifier returns INCOMPLETE with no certified optimum; it may report the checked best-known feasible candidate separately.
- `search_status=EXHAUSTED` iff there are no OPEN nodes, no nonempty suffixes, every SPLIT has cursor=alternative_count, and all leaves pass their closure checks. EXHAUSTED with any unresolved suffix/OPEN node is INVALID.
- PARTIAL with no unresolved work is INVALID (the artifact's status contradicts its frontier).
- Invalid schema/evidence/coverage is INVALID; verifier time/work/memory cap is INCOMPLETE. No result is returned on INVALID or INCOMPLETE.
- VERIFIED is reserved for an EXHAUSTED certificate whose entire frontier is independently covered and whose incumbent/optima or infeasibility conclusion is checked.
- `operational_status` is always INCOMPLETE. Structural optimum is not external learner ACCEPT or operational acceptance.

## 7. Independent verifier entry point and independence

Agent #3 owns a standalone module and stable CLI, proposed:
- `tests/reference/p3_frontier_verifier.py`
- callable `verify_p3(raw, scope, journal2_bytes_or_none, trusted_scope, certificate, *, budget)`
- CLI: `python -B tests/reference/verify_p3_frontier.py --raw RAW.json --scope SCOPE.json --trusted-scope TRUSTED.json --certificate CERT.json [--journal2 JOURNAL.json]`

The verifier may import the existing independently authored P2 proof modules (`independent_replay.py`, `journal_v2_replay.py`, and their proof-only dependencies) to re-establish trusted scope. It must not import producer `selector_v2.edr_bb`, producer DSU, producer pruning, caches, or solver state. It must implement owner/equality closure, alternatives, split transitions, lower bounds, structural compatibility and all leaf checks independently. Do not import producer `selector_v2.schema`; reproduce canonical JSON independently and add byte-parity tests against known canonical fixtures. Explicit fail-closed checks must work under python -O; no assert for security/proof validation.

Result JSON is exactly versioned and includes `status=VERIFIED|INVALID|INCOMPLETE`, `operational_status=INCOMPLETE`, and `result` only on VERIFIED. VERIFIED result includes mode, optimum cost, one owner or all optimum owners, and visited/closed node counts. INVALID/INCOMPLETE expose no result. PARTIAL may expose `best_known` separately but never under `result`.

## 8. Optional evidence-directed split extension (not enabled until separately reviewed)

The v1 producer/verifier must first pass the all-pairs exact search gate. A later reviewed extension may add `CROSS_SUPPORT_LEX_V1`: for one negative y, two nonempty disjoint sets S,T of current E-class representatives, and positive witnesses x_s,x_t, independently verify `projection_(A minus union(S))(x_s) = projection_(A minus union(S))(y)` and the analogous equality for T. Every separating block must intersect both supports, so at least one cross-support pair is merged. Alternatives are the complete lexicographically sorted Cartesian cross-pair family, with D-blocked pairs removed only after independently checking why they are impossible. Its residual is closed only by CONFLICT_RESIDUAL referencing that exact split/conflict. This rule, support discovery, and any omitted-pair proof are NOT authorized in M2 until the verifier has dedicated exhaustive and mutation tests and the lead approves it. No canonical merge-parent restriction, symmetry pruning, rank/AEFC, advanced dead-cover, CDAQ or bounded rule is permitted.

## 9. Required tests before P3 integration

Proof side:
- Exhaustive RGS comparison for n<=8; compare every region's literal members, structural optimum and all-optima set.
- Independently replay every parent/child/residual transformation; verify first-true disjointness and coverage.
- Corrupt owner, D, parent, path, cursor, cursor log, alternatives hash, omitted/reordered child, missing residual, orphan/duplicate node, wrong scope/root/journal digest, false incumbent, false witness, wrong one/all cutoff and EXHAUSTED/PARTIAL status.
- Verify duplicate/empty/unused symbols, epsilon, no positives/no negatives, opposite-label duplicate, n=0 local semantics, and normal/-O parity.
- Run resource-capped checker and ensure cap -> INCOMPLETE/no result.

Core side:
- Implement serializer exactly to this contract, not a competing schema.
- Implement full DFS/branch-and-bound over ALL_PAIRS_LEX_V1, using current region algebra and complete original alphabet.
- Evaluate E literally. If compatible, close FEASIBLE_MIN. If empty, EMPTY. If raw opposite-label duplicate, RAW_LABEL_CONFLICT. If E is NO and region singleton, EXACT_NO. Otherwise split; residual is singleton and gets exact checked. Apply only base LB and exact cutoff semantics.
- Add checkpoint/resume preserving exact cursor/suffix and node identities. No restart that drops frontier.
- Produce real certificates for all seven raw-only fixtures when resources permit; small cases must exhaust.
- Both modes normal/-O; exact work/entry/frontier counters; memory payload cap distinguished from process RSS/RLIMIT_AS.

Interface side:
- Keep canonical owner array as the candidate boundary and journal/2 as the only observation ledger. Certificate remains a separate proof artifact.
- After actual producer and verifier CLI are frozen, add one offline end-to-end fixture: producer candidate -> open_gateway registration -> exact owner/scope binding -> proof verifier. Use mock observations only. Never treat observation verdicts as region closures.

Benchmark side:
- Use the frozen native producer/verifier CLI, not the measurement-only fake adapter, for integrated P3 runs. Keep solver input and evaluation reference separate. Report raw solver, proof verification and (if ever available) journal replay phases separately.

## 10. Versioning and non-goals

This contract does not authorize external evaluator calls, learner/baseline changes, a new journal schema, a second ledger, bounded optimization, CDAQ, AEFC/rank/dead-cover pruning, or operational acceptance. The proof certificate is not a journal/2 event. Every validated milestone is committed/pushed with exact Git blob IDs, commands, logs, resource limits and status. Keep PRs draft/unmerged until the integration lead's independent gate passes.
