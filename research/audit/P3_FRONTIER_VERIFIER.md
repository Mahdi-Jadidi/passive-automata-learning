# Independent P3 region/frontier verifier

Status: implemented on the proof-audit branch; producer integration is pending an actual serialized EDR-BB certificate. This verifier does not authorize a merge, external learner change, or operational acceptance.

## Trust boundary and callable interface

The public call is:

    verify_frontier(raw_sample, exact_journal2_bytes, trusted_scope, proof, ...caps)

The verifier independently replays the exact journal/2 byte stream before inspecting the producer proof. It does not import EDR-BB search, producer DSU, pruning, caches, ranking, or producer state. Its only selector-v2 runtime dependency is the frozen schema canonicalizer; journal replay is delegated to the already independent proof-side journal/2 kernel.

Raw sample is the original three-key object with ordered alphabet, positive word arrays and negative word arrays. Token IDs in the proof scope are integer positions in that original alphabet. The selector-v2/1 sample has ordered arrays but no explicit trace-ID field, so stable original positional IDs are P0, P1, ... and N0, N1, .... If the input schema later adds explicit trace IDs, the wire contract must be revised rather than silently renumbering them.

Trusted scope has exactly these fields:

    {
      "format": "p3-trusted-scope/v1",
      "selector_scope": {
        "version": "selector-v2/1",
        "sample_digest": "<independently recomputed sample digest>",
        "regime": "UNRESTRICTED",
        "family": "ALL_PARTITIONS",
        "capacity_digest": null
      },
      "journal2_digest": "<lowercase SHA-256 of exact journal bytes>",
      "alphabet": ["<original ordered symbols>"],
      "positive": [{"id": "P0", "tokens": [0, ...]}],
      "negative": [{"id": "N0", "tokens": [1, ...]}],
      "root_equalities": [[0, 2], ...],
      "root_owner": [0, 1, 0, ...]
    }

The selector scope is the exact selector-v2/1 unrestricted all-partitions scope. Its sample digest is recomputed from the raw sample by the independent sample-data routine. journal2_digest is SHA-256 over the exact supplied bytes, without parse/reserialize or newline normalization. The verifier calls tests/reference/journal_v2_replay.verify_journal(raw_sample, selector_scope, exact_journal2_bytes). The root owner must equal that independent replay's mandatory_owner. root_equalities is the complete sorted pair closure of that owner array and is checked redundantly. The full trusted-scope digest is SHA-256 of selector_v2.schema.canonical(trusted_scope); alternative suffix digests use the same canonical byte encoding.

The proof header is p3-region-frontier/v1 with scope_digest, mode (one or all), declared_status (EXHAUSTED or PARTIAL), root_owner, incumbent, optima and root. Root is R(E0, empty D), where E0 comes only from the independently replayed journal/2 mandatory owner.

## Region and frontier semantics

A region R(E,D) contains all partitions coarser than equality E and respecting every original-ID disequality in D. Equality owners are canonical minimum-original-index owner arrays. Disequalities are always original alphabet index pairs, sorted and unique.

The only accepted split rule is ALL_PAIRS_LEX_V1: all unordered pairs of distinct current E-classes in lexicographic order. For alternatives e[0..t-1], child i is:

    E_i = closure(E union {e_i})
    D_i = D union {e_0, ..., e_(i-1)}

The residual is:

    R(E, D union {e_0, ..., e_(t-1)})

The verifier independently reconstructs every child owner and disequality set. It checks that the first-true children and residual are disjoint and cover the parent. The suffix record must bind the full alternatives digest and exact cursor interval; cursor history must be contiguous, ordered and non-skipping. An OPEN node, unprocessed suffix or unresolved UNKNOWN cannot complete a proof.

Allowed leaf reasons are EMPTY, RAW_LABEL_CONFLICT, EXACT_NO, EXACT_FEASIBLE, COST and UNKNOWN. EMPTY requires an E-D contradiction. RAW_LABEL_CONFLICT requires original positive/negative trace IDs whose original token sequences are identical. EXACT_NO and EXACT_FEASIBLE require a singleton region and literal structural compatibility replay; feasible witnesses must carry the exact canonical owner and cost. COST uses only the equality-class lower bound n - number_of_E_classes. Its cutoff is >= incumbent cost in one-optimum mode and strictly > incumbent cost in all-optima mode. No advanced pruning rule is accepted.

## Strict result semantics

- VERIFIED: the entire root region has been independently covered and the structural optimum or full infeasibility result is valid.
- INVALID: malformed evidence, a false mathematical claim, invalid transition, duplicate/orphan child, forged witness, bad digest or false EXHAUSTED declaration.
- INCOMPLETE: time/work/memory cap, oversized journal, missing suffix under PARTIAL, OPEN region, unresolved UNKNOWN or incomplete frontier.

Every return retains operational_status=INCOMPLETE. Structural verification is not external ACCEPT or operational acceptance. The CLI returns exit code 0 for VERIFIED, 1 for INVALID and 2 for INCOMPLETE.

## Commands

From the repository root:

    PYTHONPATH=tests/reference:implementation/partition_feedback_final python -m unittest -v test_p3_frontier_verifier
    PYTHONPATH=tests/reference:implementation/partition_feedback_final python -O -m unittest -v test_p3_frontier_verifier

CLI:

    PYTHONPATH=tests/reference:implementation/partition_feedback_final python tests/reference/p3_frontier_verifier.py --raw raw.json --journal journal2.json --scope trusted_scope.json --proof frontier.json

The CLI reads journal bytes without normalization. The workflow runs both normal and optimized modes.

## Validation record and exact dependency pins

Local unit suite: 11 tests passed in normal and optimized Python modes. The independent RGS oracle reported Bell counts B(0..8) = 1, 1, 2, 5, 15, 52, 203, 877, 4140; independent label enumeration through n=5; and 7,065 literal region-membership checks. Structural examples, duplicate/empty/unused symbols, malformed tokens and caps passed.

Pinned source Git blob hashes:

- tests/reference/p3_frontier_verifier.py: 50f2749bec56cf73eaa69d297bd6b88f2ca9dfa1
- tests/reference/test_p3_frontier_verifier.py: 43077d65cb4f24cd1f59856935e5a581d56bb301
- tests/reference/rgs_oracle.py: 375c36bfb2602894ce783055d1edf31f265aafa0
- tests/reference/journal_v2_replay.py: 6c49013e809b5ac4d2b2a37850e6e6cece513072
- tests/reference/independent_replay.py: aa09243fa7ccc941c37609e959aefb419075df32
- tests/reference/production_replay.py: 4666c3f1aca6189331a83ff2f00de0e376e2a710
- tests/reference/ledger_replay.py: 0b615b6c17258e621d73147baa262d791985d8d0
- tests/reference/interface_artifact_replay.py: 51f928ee2311ab8995f88f0e9f195ac7c659e469
- tests/reference/bounded_deletion.py: e1fc61b6f03484d4428642ca157e2dac43f0572d
- implementation/partition_feedback_final/selector_v2/schema.py at core M1: 65a7522a8442a184c14f7a0fa74fc307ce60229f

The local temporary test harness used a small replay shim because the proof-side replay modules were not mounted in that temporary directory. The committed tests and CI import the pinned independent journal/2 replay modules above; CI is the required integration confirmation. The producer branch at the inspected M1 commit had no serialized frontier output, so no actual producer certificate has yet been replayed. Request a real raw sample + exact journal/2 bytes + trusted scope + serialized frontier from Agent #2 before claiming producer integration.

## Explicit limitations

Only generic all-pairs fallback and the basic equality-class lower bound are enabled. The verifier is fail-closed and resource-bounded by journal byte cap, node cap, depth cap, time checks and MemoryError handling; this is not a hard RSS sandbox. The oracle is exhaustive for small alphabets, not the seven recovered benchmark inputs. No PR is merged, no external learner or baseline is modified, and no operational acceptance is claimed.
