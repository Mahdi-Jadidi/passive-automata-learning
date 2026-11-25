# P3 serialization and independent verification contract v1

**Status: integration-lead freeze, superseding the earlier draft and nested prototype.** This is the sole producer/proof/interface/benchmark wire contract for P3 M2. It does not change selector-v2/1 or journal/2. Structural search only; unrestricted `ALL_PARTITIONS`, `B=0`. Operational status is always INCOMPLETE.

## 1. Mathematical object

Original ordered alphabet IDs are `0..n-1`; original positive and negative trace IDs are their positions in the raw ordered arrays (P0.. and N0..). Duplicates remain distinct trace IDs. For canonical owner array p, equal owners define blocks and each owner is the minimum original ID in its block. Structural compatibility:

`for every negative y_i, exists block B: for every positive x_j, projection_B(y_i) != projection_B(x_j)`.

Cost is `n - number_of_distinct_owners`.

A region `R(E,D)` contains all partitions coarser than E and respecting every original-ID disequality pair in D. E is a complete canonical owner array over all original symbols; D is sorted, unique, unordered original-ID endpoint pairs and is branch-local. A region is empty iff a D pair has endpoints in one E class. Its minimum-cost member is E, with `LB(E)=n-|classes(E)|`. Any strict coarsening costs strictly more.

## 2. Trusted scope bootstrap (exact schema)

The trusted scope is a separate JSON artifact, passed to producer and verifier. It has exactly these fields:

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

The raw sample remains the exact three-key object `alphabet, positive, negative` and is supplied separately. Token arrays in the trusted scope are original alphabet integer IDs. P0.. and N0.. are stable original positional trace IDs because selector-v2/1 has no explicit trace-ID fields. The verifier recomputes and compares alphabet, token arrays, IDs and sample digest against raw input. The selector scope must be the exact five-field selector-v2/1 object above; no second scope authority is introduced.

The journal is the exact canonical uncompressed byte sequence passed to `journal_v2_replay.verify_journal(raw, selector_scope, journal_bytes)`; do not hash a gzip/container wrapper, parse-reserialize it, or normalize newlines. `journal2_digest` is SHA-256 of those exact bytes. An empty canonical journal/2 event list is allowed and yields the identity root. The verifier requires journal replay VERIFIED and sets `root_owner` from `result.proof.mandatory_owner`; producer-supplied E0 is never trusted. A verified OPEN/PARTIAL closure still contains individually checked sound contractions and is safe as a less-contracted root; a failed/INCOMPLETE journal replay cannot authorize contractions. If no usable journal is available, create a canonical empty journal/2 artifact and use identity E0 rather than invent a root.

The trusted-scope digest is SHA-256 of canonical JSON bytes for the entire trusted-scope object. Canonical encoding is UTF-8 `json.dumps(obj, ensure_ascii=True, separators=(',', ':'), sort_keys=True, allow_nan=False)`. The proof verifier must implement this encoding independently; do not import `selector_v2.schema` or any producer module. The same canonical encoding hashes the alternatives list. Strict parsing rejects duplicate JSON keys, non-finite numbers, wrong types, unknown fields and invalid UTF-8.

**Do not include `root_equalities` or a full pair closure of E0.** A complete pair closure can require O(n²) memory for one large component. The canonical length-n `root_owner` plus independently replayed journal is sufficient to bind E0 in O(n) space.

## 3. Certificate header

The certificate has exactly these top-level fields:

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
- `root_owner` must equal the independently replayed root E0.
- `incumbent`: null or exactly `{"owner":[...],"cost":integer}`. It is a structurally compatible complete partition, checked directly by the verifier and required to coarsen root E0. It is not an external ACCEPT.
- `optima`: sorted unique list of canonical owner arrays. It must be empty in one-optimum mode. In all-optima mode it is required only for EXHAUSTED and must equal the complete set of minimum-cost partitions proved by the certificate. PARTIAL never claims an all-optima list.

The verifier returns `VERIFIED` only for EXHAUSTED plus complete independent coverage and a correct optimum/infeasibility result. PARTIAL returns INCOMPLETE and no result.

## 4. Flat node table (no recursive JSON tree)

The certificate contains one flat `nodes` array, strictly sorted by `id`, with unique IDs. This is mandatory: recursive nested trees can exceed JSON/Python recursion depth on long merge paths and are not accepted for v1.

Every node has:
- `id`: deterministic path ID.
- `parent_id`: null only for root.
- `edge`: ROOT, CHILD or RESIDUAL descriptor.
- `owner`: complete canonical owner array over all n original IDs.
- `disequalities`: sorted unique list of sorted two-integer original-ID pairs.
- `kind`: OPEN, SPLIT or LEAF.

Root is exactly id `root`, parent_id null, edge `{"kind":"ROOT"}`, owner=root_owner, D empty. Child j of parent q is id `q/cj`, parent_id=q, edge `{"kind":"CHILD","index":j,"pair":[a,b]}`. Residual is id `q/r`, parent_id=q, edge `{"kind":"RESIDUAL"}`. Every nonroot node must be referenced exactly once by its parent SPLIT. No orphans, duplicate references, missing nodes, cycles or reparenting. The verifier traverses the flat graph iteratively; no recursion proportional to search depth.

The verifier independently reconstructs each node's E and D from its parent and edge, using a proof-side graph/connected-component implementation (not producer DSU), then compares the complete serialized owner and D. D endpoints remain original IDs and are never rewritten to ephemeral DSU roots.

## 5. SPLIT v1: all-pairs first-true coverage

M2 initially accepts only `ALL_PAIRS_LEX_V1`. For parent owner E:
1. Let C be the sorted distinct minimum-original-ID representatives in E.
2. Alternatives L are every unordered pair of distinct members of C, lexicographic combinations order. V1 does not omit pairs; even D-blocked alternatives remain explicit and produce an EMPTY child.
3. Hash is SHA-256 of canonical JSON bytes for `[[a,b], ...]`.

A SPLIT node has exactly these additional fields:

```json
{
  "rule": "ALL_PAIRS_LEX_V1",
  "alternatives_sha256": "<hash of full alternatives>",
  "alternative_count": 1,
  "cursor": 1,
  "children": ["root/c0"],
  "cursor_log": [
    {"from": 0, "to": 1, "child_id": "root/c0", "pair": [0,1]}
  ],
  "residual_id": "root/r",
  "suffix": {
    "rule": "FIRST_TRUE_SUFFIX_V1",
    "start": 1,
    "stop": 1,
    "alternatives_sha256": "<same alternatives hash>"
  }
}
```

For each j in `[0,cursor)`, child j has E equal to the equivalence closure of parent E plus equality (a_j,b_j), and D equal to canonical union of parent D and alternatives `L[:j]`. Cursor log contains exactly one ordered step j->j+1 naming child q/cj and L[j]. Children IDs equal exactly q/c0..q/c(cursor-1); no gaps/reordering.

Residual q/r has the same E and D equal to canonical union of parent D and all L. It is always explicit and is a singleton region (or empty if parent was already empty). It cannot be omitted or recursively split.

The suffix object is always present, including the empty suffix where cursor=|L|. If cursor<|L| it denotes exactly the ungenerated first-true children j in [cursor,|L|): all earlier pairs L[:cursor] are false and at least one pair in L[cursor:] is true, with its unique first true pair determining the child. Hash binds the verifier-derived full L. If cursor=|L|, require start=stop=|L|. A cap/interruption retains the suffix.

Completeness: every strict coarsening of E merges at least one pair of distinct E classes; it belongs to the child for its unique first true merged pair. E itself belongs to the all-false residual. First-true children are pairwise disjoint and disjoint from residual. Children plus residual cover the parent. If |L|=0, region is a singleton and node must be LEAF, not a zero-progress SPLIT.

## 6. LEAF closure rules

A LEAF has exactly common fields plus `closure`. Unknown closure reasons are INVALID except UNKNOWN, which is unresolved and therefore INCOMPLETE.

- `EMPTY`: closure exactly `{"reason":"EMPTY"}`; valid iff some D pair is internal to E.
- `RAW_LABEL_CONFLICT`: closure exactly `{"reason":"RAW_LABEL_CONFLICT","positive_id":"Pj","negative_id":"Ni"}`; valid iff the original opposite-label words are token-identical. This is global structural infeasibility.
- `EXACT_NO`: closure exactly `{"reason":"EXACT_NO"}`; valid only if region is a singleton (for every pair of distinct E classes, D contains at least one original endpoint pair crossing those classes) and literal structural check says E is incompatible.
- `FEASIBLE_MIN`: closure exactly `{"reason":"FEASIBLE_MIN","owner":[...],"cost":integer}`; valid for any nonempty region, not just singleton. Owner must equal E, cost must equal `n-|classes(E)|`, and literal structural check must prove E compatible. E is the unique minimum-cost member of R(E,D), so this closes the whole region. This is the exact lower-bound attainment rule and is mandatory for useful branch-and-bound.
- `COST`: closure exactly `{"reason":"COST"}`; valid only with a checked incumbent. Check `LB(E)=n-|classes(E)|`: one-optimum permits LB >= incumbent cost; all-optima permits only LB > incumbent cost.
- `UNKNOWN`: closure exactly `{"reason":"UNKNOWN"}`; unresolved, never closes a region and forces INCOMPLETE.

An OPEN node has exactly one additional field `reason`: TIME_CAP, WORK_CAP, ENTRY_CAP, FRONTIER_CAP or USER_STOP. It remains unresolved.

The incumbent must be a canonical complete owner array, coarsen root E0, have the declared cost, and pass the verifier's literal structural compatibility check. In EXHAUSTED mode it must be no worse than every FEASIBLE_MIN leaf. For ALL_OPTIMA, because equal-cost branches cannot be pruned, incumbent owner must appear among FEASIBLE_MIN leaves and `optima` must equal all FEASIBLE_MIN owners at the minimum cost. For ONE_OPTIMUM, any one valid minimum-cost incumbent is sufficient; equal-cost regions may be cut.

## 7. Search status and verifier output

- EXHAUSTED requires no OPEN nodes, no UNKNOWN leaves, no nonempty suffix, every SPLIT cursor=alternative_count, every node reachable, and every leaf independently valid. EXHAUSTED with unresolved work is INVALID.
- PARTIAL requires at least one OPEN node, UNKNOWN leaf or nonempty suffix. PARTIAL with no unresolved work is INVALID. Verifier returns INCOMPLETE and no result.
- Malformed or mathematically false evidence is INVALID and returns no result.
- Verifier resource caps (journal/proof bytes, nodes, depth, work, exact projection checks, elapsed time, process memory) return INCOMPLETE and no result. Memory cap must be enforced by the benchmark/CI process sandbox; observed RSS and RLIMIT_AS are recorded separately.
- VERIFIED is reserved for EXHAUSTED complete coverage plus a checked structural optimum/all-optima set or full infeasibility proof. `operational_status` is always INCOMPLETE.

Result JSON exact fields: `status`, `operational_status`, `result`, `reason`, `nodes_checked`, `work_units`, `exact_checks`. `result` exists only for VERIFIED. INVALID/INCOMPLETE expose no result. PARTIAL may expose a separate `best_known`, never an optimum result.

## 8. Independent verifier requirements

Agent #3 owns `tests/reference/p3_frontier_verifier.py` and `tests/reference/test_p3_frontier_verifier.py`, with callable `verify_frontier(raw, exact_journal2_bytes, trusted_scope, proof, *, budgets)` and CLI:
`python -B tests/reference/p3_frontier_verifier.py --raw RAW.json --journal JOURNAL.json --scope TRUSTED.json --proof CERT.json`.

Allowed proof dependencies: existing independently authored P2 modules `independent_replay.py`, `journal_v2_replay.py`, `production_replay.py`, `ledger_replay.py`, `interface_artifact_replay.py`, `bounded_deletion.py`. Absolutely no import from `selector_v2`, producer search, producer DSU, producer pruning, cache, ranking or producer state. Canonicalization must be independently implemented. Strict CLI parsing must preserve duplicate-key detection (do not call plain json.loads before the verifier parser). Use iterative traversal of the flat node table. No assert for proof/security validation; normal and -O behavior must match.

Pass explicit resource budgets into journal replay and all raw projection/structural checks. Time/work caps must be checked inside long loops, not only between nodes. Count projection symbols/comparisons and exact checks. Cap journal bytes, proof bytes, nodes, frontier entries/work and depth. Catch MemoryError/timeout as INCOMPLETE. The hard RSS/address-space cap is imposed by a separate process runner.

## 9. Core producer requirements

Agent #2 implements deterministic DFS/branch-and-bound and serializer on the existing branch, using current RegionState/RollbackDSU but not changing the proof grammar:
- Input raw sample + trusted scope; root owner comes from scope, not producer-derived counters.
- Evaluate E literally. If E is compatible, emit FEASIBLE_MIN and close region.
- If E/D is empty, emit EMPTY.
- If raw opposite-label duplicate exists, emit RAW_LABEL_CONFLICT.
- If E is incompatible and region singleton, emit EXACT_NO.
- Otherwise emit SPLIT ALL_PAIRS_LEX_V1, preserve residual, generate first-true children lazily and serialize exact cursor/suffix.
- Apply only base LB and exact one/all cutoffs.
- Produce PARTIAL checkpoints with all OPEN nodes and unconsumed suffix; resume must preserve exact certificate coverage and node identities.
- No conflict-based pruning, no canonical merge-parent restriction, no symmetry pruning, no rank/AEFC/dead-cover/CDAQ or bounded rule in M2.

## 10. Optional EDR-BB evidence-directed split (M3, not enabled)

After M2 all-pairs search/verifier integration passes, a later reviewed extension may add `CROSS_SUPPORT_LEX_V1`. For one negative y, two nonempty disjoint sets S,T of current E-class representatives, and positive witnesses x_s,x_t, independently verify that deleting the union of classes S from x_s and y gives identical ordered sequences, and likewise for T. Every separating block must intersect both supports, so at least one cross-support pair is merged. Alternatives are the complete lexicographically sorted Cartesian cross-pair family. The residual is closed only by a separately verified CONFLICT_RESIDUAL referencing that exact conflict. No omitted pair unless verifier proves it impossible under D. This rule is NOT enabled until dedicated exhaustive and mutation tests plus lead approval. It is the first evidence-directed optimization after the universal proof spine.

## 11. Required tests and non-goals

Proof: exhaustive RGS comparison n<=8; literal region membership and optimum/all-optima comparison; first-true child/residual coverage; mutations of root/scope/journal digest, owner, D, parent/path/edge, cursor/log/suffix/hash, missing child/residual, orphan/duplicate node, false incumbent/witness, wrong one/all cutoff, false EXHAUSTED/PARTIAL, duplicate JSON keys, caps, normal/-O parity. Add a large-n linear-space root-scope test; no O(n²) root equality list.

Core: full search on tiny_choice and small_choice; complete certs and exact verifier replay; all-optima/one-optimum comparison to literal RGS; deterministic repeated runs; restart/resume equivalence; work/entry/time caps; original unused symbols, duplicates, epsilon and empty positive/negative sets. Then medium/large fixtures with honest INCOMPLETE where resource limits hit.

Interface: preserve canonical owner array as candidate boundary; candidate identity remains (sample_digest, tuple(owner)); request_id and global attempt_id remain separate. Certificate stays outside journal/2. Offline integration only; no live calls.

Benchmark: use native producer/verifier CLI, not fake adapters, for integrated P3. Seven raw-only fixtures are input-only; evaluation index remains separate. Report solver and verifier phases separately, exact source/input/certificate hashes, work/entries/frontier/exact checks, wall, RSS and caps. P2 huge journal/2 replays remain NOT RUN until the exact original journal bytes are supplied; raw closure is a separate phase.

No learner/baseline modification, external endpoint calls, second ledger, journal schema change, bounded optimization, CDAQ, P4-P7 or operational acceptance. Every validated milestone is committed/pushed with exact blobs, commands, logs, counters, caps and VERIFIED/INVALID/INCOMPLETE/NOT RUN status. PRs remain draft/unmerged pending integration lead sign-off.
