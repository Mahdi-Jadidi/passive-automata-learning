# Presentation build record

The final deck is a local, editable PPTX because the preferred Spaces creation tools were unavailable. The task applied the bundled presentations skill, with @oai/artifact-tool authoring, native tables, editable text/formulas, speaker notes, first-party reimport, package/layout/font checks, and actual Microsoft PowerPoint rendering. PowerPoint's explicit RTL paragraph setting is applied in a saved post-processing script. The conceptual cover was generated using the built-in image_gen tool; it is not research evidence.

Retained attempts:

- R1 source/candidate: the local-path image import produced an empty cover media entry. Retained. R2 repairs image embedding using a byte blob.
- Artifact Tool preview rendered Persian word order incorrectly. A probe exported to native PowerPoint rendered correct Persian; native PowerPoint is the visual QA target. No text is rasterized.
- R2/R3 source, candidates, localized candidates and native slide renders are retained. Mixed Latin/Persian captions were replaced with separate formula/table cells or pure Persian in R3. The R3 draft uses C009 experimental data and is not the final scientific presentation.
- The first R3 preview-finalizer call failed because RUNTIME_NODE_MODULES was missing. The actual tool output reported `Exact staged presentation failed first-party Artifact Tool import` and `RUNTIME_NODE_MODULES or CODEX_PRIMARY_RUNTIME_NODE_MODULES is required.` A standalone raw log was not captured for that call; this record preserves the observed error without recreating a log.
- Preview-finalizer attempt2 failed because private receipt and output shared a directory. Full actual log: private/preview_finalize_attempt2.log.
- Preview-finalizer attempt3 failed because the new output directory had not been created. Full actual log: private/preview_finalize_attempt3.log.
- Preview-finalizer attempt4 passed after creating the directory. Full actual log and receipt: private/preview_finalize_attempt4.log, private/preview_validation_R3.json. Its output is a validated draft, not the final delivery.

Final candidate will use accepted C010 experimental results and a separate build version. No failed attempt is overwritten.

Reproduction uses the saved Node builder, the bundled @oai/artifact-tool package, local Arial/Consolas/Cambria Math fonts, and Microsoft PowerPoint COM for localization/rendering. PowerShell script files are loaded using `[scriptblock]::Create((Get-Content -LiteralPath ... -Raw))` because direct script execution is disabled by the host policy; the policy was not changed.
