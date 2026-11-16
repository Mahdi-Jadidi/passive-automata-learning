# C025 actual-data results — reading correction V2

Manager documentation correction after the completed independent audit. No solver/oracle reruns, changed classifications, or edits to frozen V1 JSON. V1 Markdown remains archived. Its unqualified constancy sentence applies to BGL and Baby random15, not to all arms. The worker's correction-only followup was interrupted before producing V2; the manager completed this note.

All 42 cells match independent complete RGS classification. Output functions and conflict references replayed; a separate integrity pass checked distinct complete partitions, one function per block, recorded outcomes/current IDs, and certificate completion. Zero reported errors. Small independent controls: 435 calls.

| Representation | d0 | d1 | d2 | d4 | d8 | full |
|---|---:|---:|---:|---:|---:|---:|
| BGL | 4140 | 4140 | 4140 | 4140 | 4140 | 4140 |
| Baby heuristic15, either representation | 0 | 35 | 35 | 44 | 58 | 58 |
| Baby random15, either representation | 877 | 877 | 877 | 877 | 877 | 877 |
| CAGE2 action-only | 0 | 0 | 0 | 0 | 0 | 738 |
| CAGE2 target-qualified | 0 | 0 | 0 | 9 | 244 | 372 |

Counts are complete compatible-family sizes in training on the selected alphabet. Zero means incompatible; all positive cells are ambiguous. None is unique. Target-qualified simulator arms and BGL are primary; action-only simulator arms are diagnostic.

BGL's existing full-training diagnostic found 86 EventIds and zero mixed-label EventIds. All eight selected types therefore have constant training output, so depth0 admits all Bell(8)=4140 partitions. Baby random15 uses all seven observed training types and admits Bell(7)=877 partitions at depth0; under the depth0 criterion this establishes constancy for each of those seven training types. These are dataset-specific statements. CAGE2 and Baby heuristic15 fail depth0 and do not satisfy this constancy condition. No assertion is made about constancy of all 120 BGL EventIds across future data or the complete operational corpus.

Both returned alternatives have frozen-training heldout diagnostics; unseen contexts abstain. Baby heuristic15 depth1 has four opposite-label conflicts for each alternative. Low CAGE2 selected-event/context coverage and zero full-history BGL heldout context coverage prevent broad predictive claims. Neither compatibility nor label constancy establishes physical subsystem recovery.

Exact retained/omitted labels/types/actions/scopes: POSTHOC_INTEGRITY_COVERAGE_V1.json. Full-alphabet partial observed-host diagnostics, original family results and heldout outputs: ACTUAL_RESULTS_V1.json. Raw process results and source identities remain versioned under attempts and the freeze manifests.
