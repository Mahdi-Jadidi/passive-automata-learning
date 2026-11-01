# C006 bounded performance proposal — v2

This version supersedes the proposed large-cell word shape in
`PROTOCOL_BENCHMARK_V1.md` before any benchmark input or provider run. The
primary job count, small cell and run procedure remain unchanged.

For `large_connected_m64`, let the center symbol be `c`, the other 63 symbols
be the leaf set `Y`, and fix the long context `C = c^128`. The one-factor
infinite regular target is `c^128 (cY)*`; visible positives are `C` and
`Ccy` for every `y` in `Y`, and the visible negative is `Cc`. This preserves
the same sound 63-edge connected star certificate while exercising 128-symbol
contexts and words of lengths 128–130. It is still one large representative,
not a parameter sweep.

All other definitions and limits are frozen by
`PROTOCOL_BENCHMARK_V1.md`: small four-symbol full-cover example, three fresh
serial repetitions per primary cell, alternating order, root CLI
`--all --seconds 28`, 30-second hard capture ceiling, full JSON capture and
independent grammar/certificate validation. The optional decision-mode
decomposable cell remains outside the primary six jobs.

