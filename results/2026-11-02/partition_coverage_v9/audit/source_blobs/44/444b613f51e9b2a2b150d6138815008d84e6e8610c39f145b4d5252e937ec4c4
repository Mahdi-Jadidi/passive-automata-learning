# C009 audit protocol amendment — v2

This amendment is append-only and preserves `PROTOCOL_AUDIT_V1.md` unchanged.

The Stage-A protocol's original Stage-B sentence says the auditor waits until a main correctness gate has already passed. That precondition is circular for the independent-auditor assignment: no prior runtime gate exists. The master's explicit readiness clarification is that Stage B **is** the main independent correctness gate, and authorizes the first comparison against the 129 frozen Stage-A oracle cases. The candidate remains only statically reviewed and source-frozen before this comparison; do not represent it as previously runtime-validated.

Apply this single sequencing clarification: run Stage B once on the frozen cases under `PROVIDER_GATE_PROTOCOL_V1.md`; accept it only after independent exact-set, count, relation, and witness checks pass. Stage C remains blocked until that acceptance. Keep the original V1 protocol and this amendment together in every capture manifest. No provider source edit, duplicate smoke run, or speed comparison is authorized by this amendment.

Master-supplied static-review note: `witness_search_branches` is initialized but not incremented, so treat it as uninstrumented rather than zero work. `search_seconds` covers the DP-count phase and excludes subsequent witness recovery/enumeration. Do not sum these as full elapsed time or make timing claims. The solver's core math was reported as having no defect in the static peer review; this does not replace the independent runtime gate.

Frozen candidate anchors:

* readiness: `e0c362047b3c63a1a0e25be52396357a900add60e37dde91c025a3c8fa2d0087`
* solver: `79255b0a306f8a30dffdd813c018bc4fd9368dad880c07489a86abd50968a5e7`
* CLI: `356ac0db3ca272403d95bc275e4babc48c5d7fc29caf00cb9685f8e49aed8507`
* independent corpus manifest: `bd4c76b389d87887504f624248940d9bb1d65d69542bca4c01da0714f5200fa1`
* independent full-set oracle: `01f7973358400f6e17d0b60ed6646e75f2244bfcba92d262d6149b5e0e9d35d2`
