# Stage 1 measurement scope clarification

This note supplements, and does not rewrite, `stage1_performance_report_v2.json` and `STAGE1_PERFORMANCE_REPORT_FA.md`.

The active protocol `stage1_protocol_freeze_v4.json` specifies a fresh-child wall scope through startup, input read, provider import, solve, and “normalized summary serialization.” Its `full_provider_outputs_and_independent_checks` field explicitly keeps full correctness captures separate and says the timed stdout uses the same normalized summary schema for compared methods. The runner `timed_provider_run_v1.py` serializes one canonical first answer and summary/status/metrics fields; it does **not** serialize each provider's full API result, graph, or full search evidence. Therefore these wall measurements are end-to-end for the frozen first-answer-summary task, not full-result/API serialization timings.

The five allocation rows are separate `tracemalloc`-instrumented child runs and are excluded from the standard-plus-stress elapsed totals and timing budget. Their own child wall times and peak traced Python bytes are listed in the v2 JSON. C003 on alphabet 128 / length 1024 reached its internal deadline in that memory run; its recorded peak is an incomplete-run observation and must not be ranked against completed S001 memory rows. `tracemalloc` peaks are not RSS.
