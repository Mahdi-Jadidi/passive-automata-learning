# Post-run audit clarification v2

The six authorized provider invocations are complete and immutable. This
clarification concerns only parsing their captured manifests and output; it
does not authorize or request any provider rerun.

The first post-run auditor was captured as
`20261101T160912.215501Z_caa009375c`. It failed at source-anchor validation
because its expected input path omitted the `inputs/` directory. It stopped
before parsing provider JSON or replaying any certificate; all six raw
outputs remain unchanged. The failed summary is preserved at
`benchmark_results_v1.json`.

Auditor v2 changes only the expected source path to
`audit/benchmark_v1/inputs/<input>` and writes a separate
`benchmark_results_v2.json`. All pass criteria, six attempt IDs, provider
source, captures, and cell ordering remain frozen. Auditor v2 SHA256:
`5536eaf0b06f9204347e05fde4a4118213d0bdccb260478cc525fa1b5b811411`.

