# P3 serialization and independent verification contract v1

**Status: integration-lead freeze for M2.** This is the sole P3 producer/proof/interface/benchmark wire contract. It supersedes all earlier nested or per-node-state drafts. It does not change selector-v2/1 or journal/2. Structural search only; unrestricted `ALL_PARTITIONS`, `B=0`. Operational status is always INCOMPLETE.

## 1. Mathematical object

Original ordered alphabet IDs are `0..n-1`; original positive/negative trace IDs are their positions in the raw ordered arrays (P0.. and N0..). Duplicates remain distinct trace IDs. For canonical owner array p, equal owners define blocks and each owner is the minimum original ID in its block. Structural compatibility:

`for every negative y_i, exists block B: for every positive x_j, projection_B(y_i) != projection_B(x_j)`.

Cost is `n - number_of_distinct_owners`.

A region `R(E,D)` contains all partitions coarser than E and respecting all branch-local original-ID disequalities D. E is a complete canonical owner array over all original IDs. D is a logical constraint set, not an ephemeral DSU-root set. Empty iff some D pair has endpoints in one E class. The minimum-cost member of a nonempty region is E itself, with `LB(E)=n-|classes(E)|`; any strict coarsening costs strictly more.

## 2. Trusted scope bootstrap

Trusted-scope JSON has exactly these fields:

```json
{
  "format": "p3-trusted-scope/v1",
  "selector_scope": {
    "version": "selector-v2/1",
    "sample_digest": "<recomputed sample digest>",
    "regime": "UNRESTRICTED",
    "family": "ALL_PARTITIONS",
    "capacity_digest": null
  },
  "journal2_digest": "<lowercase SHA-256 of exact journal bytes>",
  "alphabet": ["symbols in original order"],
  "positive": [{"id": "P0", "tokens": [0, 1]}],
  "negative": [{"id": "N0", "tokens": [1, 0]}],
  "root_owner": [0, 1]
}
```

Raw input is the exact three-key object `alphabet, positive, negative`, supplied separately. Token arrays in trusted scope are original alphabet integer IDs. P0.. and N0.. are stable positional trace IDs because selector-v2/1 has no explicit trace-ID fields. The verifier recomputes alphabet, ordered token arrays, IDs and sample digest from raw input. The selector scope is the exact five-field selector-v2/1 object above; no second scope authority.

The journal is the exact canonical uncompressed byte sequence passed to independent `journal_v2_replay.verify_journal(raw, selector_scope, journal_bytes)`; do not hash a gzip/container wrapper, parse-reserialize it, or normalize newlines. `journal2_digest` is SHA-256 of those exact bytes. An empty canonical journal/2 event list is allowed and yields identity E0. The verifier requires journal replay VERIFIED and derives `root_owner` from `result.proof.mandatory_owner`; producer-supplied E0 is never trusted. Verified OPEN/PARTIAL closure still contains individually checked sound contractions and is safe as a less-contracted root. Failed/INCOMPLETE replay cannot authorize contractions; use a verified empty journal and identity E0 rather than invent a root.

Trusted-scope digest is SHA-256 of canonical JSON bytes for the entire trusted-scope object. Canonical encoding is UTF-8 `json.dumps(obj, ensure_ascii=True, separators=(',', ':'), sort_keys=True, allow_nan=False)`. Proof code implements it independently; no `selector_v2` or producer import. Strict parsing rejects duplicate keys, non-finite numbers, wrong types, unknown fields and invalid UTF-8.

**Never include `root_equalities` or a complete pair closure of E0.** It is O(n²). The length-n `root_owner` plus independent journal replay binds E0 in O(n).

## 3. Certificate header

Top-level fields are exactly:

```json
{
  "format": "p3-region-frontier/v1",
  "scope_digest": "<trusted-scope digest>",
  "mode": "one",
  "declared_status": "PARTIAL",
  "root_owner": [0, 1],
  "incumbent": null,
  "optima": [],
  "nodes": []
}
```

- `mode`: `one` or `all`.
- `declared_status`: `EXHAUSTED` or `PARTIAL`.
- `root_owner` equals independently replayed E0.
- `incumbent`: null or exactly `{"owner":[...],"cost":integer}`; it must be a canonical partition, coarsen E0, and pass literal structural compatibility. It is not external ACCEPT.
- `optima`: sorted unique canonical owner arrays. Empty in one mode. Required in all+EXHAUSTED and must equal every optimum. Forbidden in all+PARTIAL.

The proof result is VERIFIED only for EXHAUSTED plus complete independently replayed coverage and a correct optimum/all-optima or infeasibility result. PARTIAL returns INCOMPLETE and no result.

## 4. Flat compressed node table

The certificate contains one flat `nodes` array, sorted by `id`, with unique IDs. No recursive nested proof tree and no per-node copies of owner arrays or full D arrays. The verifier traverses iteratively; depth must not depend on Python recursion.

Every node has:
- `id`: deterministic path ID.
- `parent_id`: null only for root.
- `edge`: ROOT, CHILD or RESIDUAL descriptor.
- `kind`: OPEN, SPLIT or LEAF.

Root is id `root`, parent null, edge `{"kind":"ROOT"}`, and its state is (root_owner, empty D).

Child j of parent q: id `q/cj`, parent_id=q, edge `{"kind":"CHILD","index":j,"pair":[a,b]}`. Residual: id `q/r`, parent_id=q, edge `{"kind":"RESIDUAL"}`. Every nonroot node is referenced exactly once by its parent SPLIT. No orphans, duplicate references, missing nodes, cycles or reparenting.

The node table deliberately omits per-node E and D. The verifier reconstructs E and D from root_owner and the path:
- A CHILD edge merges its pair in E and adds the preceding alternatives of its parent split to D.
- A RESIDUAL edge preserves E and symbolically adds the parent's complete alternative family to D; this makes the residual a singleton region (or empty).
- Ancestor path constraints remain in force.
This path representation avoids O(n * number_of_nodes) owner copies and repeated D arrays. The proof verifier uses its own independent connectivity implementation, never producer DSU.

## 5. SPLIT v1 — lazy all-pairs first-true coverage

M2 initially accepts only `ALL_PAIRS_LEX_V1`. For parent E, let C be the sorted distinct minimum-original-ID representatives of E's classes. Alternatives L are all unordered pairs of C in lexicographic combinations order. Do not materialize all of L. If k=|C|, `alternative_count = k*(k-1)//2`.

The j-th pair is derived directly from C. For first index i, `start(i)=i*(2*k-i-1)//2`; find the unique i with `start(i)<=j<start(i+1)`, then second index is `i+1+(j-start(i))`. Pair is `[C[i],C[second]]`. This deterministic rule is the complete alternatives commitment; no O(k²) alternatives hash or list is serialized.

A SPLIT node has exactly:
- `rule: "ALL_PAIRS_LEX_V1"`
- `alternative_count`: exact k(k-1)/2
- `cursor`: integer in [0, alternative_count]
- `children`: IDs q/c0..q/c(cursor-1), exactly
- `cursor_log`: exactly cursor records `{"from":j,"to":j+1,"child_id":"q/cj","pair":[L[j]]}`
- `residual_id`: exactly q/r
- `suffix`: `{"rule":"FIRST_TRUE_SUFFIX_V1","start":cursor,"stop":alternative_count}`

The verifier checks each emitted pair with the direct j-th-pair function, not a producer list. If cursor<t, suffix denotes the exact ungenerated first-true children j in [cursor,t): all earlier pairs are false and the unique first true pair determines the child. If cursor=t, suffix is the empty range [t,t]. A cap/interruption retains the suffix; it cannot be dropped.

For child j, E is parent E plus equality L[j], and D is parent D plus all L[:j]. If any earlier disequality becomes internal to E, the child is EMPTY. Residual q/r is parent E with every pair in L false; it is a singleton region and must be explicit, even when it is immediately closed or OPEN. Residual is never recursively split.

Completeness: every strict coarsening of E merges at least one pair of distinct E classes; its unique first true pair selects exactly one child. E itself belongs to the all-false residual. Children and residual are pairwise disjoint and cover the parent. If t=0, the region is singleton and node must be LEAF, not a zero-progress SPLIT.

This is O(k) scope/state plus O(cursor) emitted proof metadata, not O(k²) alternative storage. Full EXHAUSTED search can still require exponential work; caps must fail closed.

## 6. LEAF and OPEN closure rules

LEAF has exactly `id,parent_id,edge,kind,closure`. Unknown closure reasons are INVALID except UNKNOWN, which is unresolved and INCOMPLETE.

- `EMPTY`: `{"reason":"EMPTY"}`; valid iff reconstructed D contains an equality internal to E.
- `RAW_LABEL_CONFLICT`: `{"reason":"RAW_LABEL_CONFLICT","positive_id":"Pj","negative_id":"Ni"}`; valid iff those original opposite-label words are token-identical.
- `EXACT_NO`: `{"reason":"EXACT_NO"}`; valid only if region is singleton and literal structural check says E is incompatible.
- `FEASIBLE_MIN`: `{"reason":"FEASIBLE_MIN"}`; valid for any nonempty region when E itself is structurally compatible. E is the unique minimum-cost member, so the whole region closes. Verifier computes cost; no producer-supplied owner/cost is trusted here.
- `COST`: `{"reason":"COST"}`; valid only with checked incumbent. Base LB `n-|classes(E)|`: one-optimum permits LB>=U; all-optima permits only LB>U.
- `UNKNOWN`: unresolved, never closes and forces INCOMPLETE.

OPEN has exactly one additional field `reason`: TIME_CAP, WORK_CAP, ENTRY_CAP, FRONTIER_CAP or USER_STOP. It remains unresolved.

The incumbent must be canonical, coarsen root E0, have correct cost and pass literal structural compatibility. In EXHAUSTED mode it cannot be worse than any FEASIBLE_MIN leaf. For ALL_OPTIMA, equal-cost branches cannot be pruned: incumbent must appear among FEASIBLE_MIN leaves and optima must equal all FEASIBLE_MIN owners at minimum cost. For ONE_OPTIMUM, one minimum-cost incumbent is enough and equal-cost regions may be cut.

## 7. Status and resource semantics

- EXHAUSTED requires no OPEN nodes, no UNKNOWN leaves, no nonempty suffix, every SPLIT cursor=alternative_count, every node reachable, and every leaf independently valid. EXHAUSTED with unresolved work is INVALID.
- PARTIAL requires at least one OPEN node, UNKNOWN leaf or nonempty suffix. PARTIAL with no unresolved work is INVALID. It returns INCOMPLETE/no result.
- Malformed or mathematically false evidence is INVALID/no result.
- Verifier resource caps (journal/proof bytes, nodes, work, exact projection checks, elapsed time, process memory) return INCOMPLETE/no result. Check caps inside long loops, not only between nodes. Pass explicit DeletionBudget into journal replay. Hard RSS/address-space cap is imposed by process runner; report RSS separately from RLIMIT_AS.
- VERIFIED is reserved for EXHAUSTED complete coverage and a checked optimum/all-optima set or full infeasibility proof. `operational_status` is always INCOMPLETE.

Verifier result JSON includes `status`, `operational_status`, `result`, `reason`, `nodes_checked`, `work_units`, `exact_checks`. `result` exists only for VERIFIED. PARTIAL may expose best-known candidate separately but never as optimum result.

## 8. Independent verifier and trusted-scope builder

Agent #3 owns `tests/reference/p3_frontier_verifier.py` and tests. Required callables:
- `build_trusted_scope(raw, exact_journal2_bytes)`: independently replay journal/2, derive sample/scope/alphabet/traces/root_owner and return the exact trusted-scope object. Fail closed on INVALID/INCOMPLETE; never accept producer root_owner.
- `verify_frontier(raw, exact_journal2_bytes, trusted_scope, proof, *, budgets)`.

CLI:
- `python -B tests/reference/p3_frontier_verifier.py --make-trusted-scope --raw RAW.json --journal JOURNAL.json --out TRUSTED.json`
- `python -B tests/reference/p3_frontier_verifier.py --raw RAW.json --journal JOURNAL.json --scope TRUSTED.json --proof CERT.json`

Allowed proof dependencies: existing independently authored P2 modules `independent_replay.py`, `journal_v2_replay.py`, `production_replay.py`, `ledger_replay.py`, `interface_artifact_replay.py`, `bounded_deletion.py`. No import from `selector_v2`, producer search, producer DSU, pruning, cache, ranking or producer state. Canonical JSON implemented independently. CLI strict parser preserves duplicate-key detection; do not plain-json.loads first. Flat traversal is iterative. No assert for proof validation; normal/-O match.

Use explicit budgets for journal replay and raw projection loops: journal/proof byte caps, node count, exact projection checks/work, elapsed time, frontier entries and process memory. MemoryError/timeout/cap -> INCOMPLETE.

## 9. Core producer requirements

Agent #2 implements deterministic DFS/branch-and-bound and flat serializer:
- Input raw sample + trusted scope; root owner comes from trusted scope, not producer counters.
- Generate all-pairs alternatives lazily using pair-at/cursor, never materialize O(k²) list.
- Evaluate E literally. If E compatible, emit FEASIBLE_MIN. If E/D empty, EMPTY. If opposite-label duplicate, RAW_LABEL_CONFLICT. If E incompatible and region singleton, EXACT_NO. Otherwise SPLIT, preserve residual and generate first-true children lazily.
- Checkpoint/resume preserves exact flat node IDs, cursor_log, suffix and unresolved nodes.
- Apply only base LB and exact one/all cutoffs.
- No CROSS_SUPPORT, rank/AEFC/dead-cover, symmetry/canonical merge-parent, CDAQ or bounded rule in M2.

## 10. Later EDR-BB evidence-directed split (M3, not enabled)

After M2 all-pairs producer/verifier integration passes, a reviewed extension may add `CROSS_SUPPORT_LEX_V1`: one negative y, two nonempty disjoint sets S,T of current E-class representatives, and positive witnesses x_s,x_t. Independently verify deleting the union of classes S from x_s and y gives identical ordered sequences, and likewise for T. Any separating block must intersect both supports, so at least one cross-support pair is merged. Alternatives are the complete lexicographic Cartesian cross-pair family, streamed lazily. Residual closes only by verified CONFLICT_RESIDUAL. No omitted pair without proof. This rule is M3 only after exhaustive and mutation tests and lead approval.

## 11. Required tests and non-goals

Proof: exhaustive RGS n<=8; literal region/optimum/all-optima comparisons; first-true disjointness/coverage; corrupt root/scope/journal, owner transitions, path/edge/cursor/log/suffix, omitted child/residual, orphan/duplicate, false incumbent/witness, wrong one/all cutoff, false status, duplicate JSON keys, budgets, normal/-O; large-n linear root binding and no O(k²) materialization.

Core: full search on tiny_choice and small_choice; complete certs and exact verifier replay; one/all compared with literal RGS; deterministic repeats; restart equivalence; caps; unused symbols, duplicate traces, epsilon, empty positive/negative and n=0. Then medium/large fixtures; capped runs honestly INCOMPLETE.

Interface: preserve canonical owner candidate boundary; identity remains (sample_digest, tuple(owner)); request_id and attempt_id separate; certificate outside journal/2. Offline only.

Benchmark: native producer/verifier CLI, not fake adapters. Harness must pass raw, exact journal, trusted scope and certificate; raw-only fixtures use a canonical empty journal/2 and independently built identity scope. Seven input-only fixtures; evaluation index separate. Solver/verifier phases separate, hashes/counters/caps preserved. P2 huge journal replay remains NOT RUN until exact original journal bytes supplied.

No learner/baseline modification, external calls, second ledger, journal schema change, bounded optimization, CDAQ, P4-P7 or operational acceptance. Every milestone committed/pushed with exact blobs, commands, logs, counters, caps and VERIFIED/INVALID/INCOMPLETE/NOT RUN. PRs remain draft/unmerged pending integration sign-off.
