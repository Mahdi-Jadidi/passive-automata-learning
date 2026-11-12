# Independent review: V33 structural hybrid

**Verdict: PASS** for the stated full-contract composition and source, conditional on frozen dependencies, successful import and sufficient resources. The proof and source reviewed are:

- `candidate_dp/hybrid/candidate.py` SHA-256 `6377CCD75281567BE11AF5820AE52668612A069240C31D2A5AEE0CF4F1022063`.
- `candidate_dp/hybrid/PROOF.md` SHA-256 `27094F9595D2F04034718667712098839B8D882C970491C81E297E5C348BB219`.

The candidate verifies hashes of C028, C030, DP, graph source and graph's reference copy prior to loading. Missing or changed dependency fails import rather than producing a C028 result; this operational limitation and stable-files assumption are documented. The source performs no public entrypoint change.

For any non-None budget the same data and budget are sent directly to C028, including invalid budgets and contradiction/validation precedence. Unlimited execution uses C028 validation and contradiction handling. A successful C030 `_certified_all` covers exactly the singleton-compatible full-family case, including empty Σ; a replay ERROR is returned directly. On failure, the graph computes must-link components. The implementation tests the component partition itself with the exact projection criterion before returning Bell(q), k*=q, O=1 and lifted canonical witnesses; these are justified by the frozen graph proof and helper replay. When this test fails it invokes the frozen DP on the original record; **it never calls the graph solver or its exhaustive fallback**. The separate DP proof and prior review establish complete counts and prefix witness ordering. Error and resource outcomes contain no partial optimality claims; external kill or import-time error may produce no result. Redundant preprocessing on DP fallback is included in solve time and can make this hybrid slower.

Independently compared complete outputs with the C028 independent set-insertion oracle on 2,206 edge/exhaustive binary-labeling cases and compared 13 invalid/edge unlimited records plus 104 budget calls against the baseline: all passed. These bounded checks and source review are not formal verification, an official audit, or performance measurements. The locked original timing remains unchanged and provides no measurement of this hybrid. No speedup is claimed before the separate appended audit and timing.

Biggest overlooked issue: the necessary forced-pair graph is not itself a compatible partition certificate; the graph shortcut is sound only after the component partition passes. The source correctly performs this test, and it preserves canonical witness serialization through the frozen helper.
