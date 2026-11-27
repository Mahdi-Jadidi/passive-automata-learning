# Review 09 M4 sparse RAW pipeline

All 16 Actions jobs passed at benchmark commit
`18e724120f8b2151f1c485178d8ef2b56b589c05`. The 128 routes cover four original
fixtures, two journal origins, both process address-space caps, one/all,
normal/-O, and direct search or checkpoint/resume. All 128 independently derived
their trusted scope. The newly exported journals and scopes matched the retained
bytes across every fixture and route. Medium and huge each had one verified
mandatory merge. Both HDFS roots were identity.

All 128 routes remain **INCOMPLETE**. All 64 checkpoint proofs independently
replayed with an unresolved frontier and were resumed within their shared route
budgets. Final replay returned an unresolved frontier on 115 routes. Thirteen
huge checkpoint/resume routes reached the wall cap during final replay.

| Fixture | Stop reason | One nodes direct / resumed | All nodes direct / resumed | Peak route RSS range, KiB |
| --- | --- | ---: | ---: | ---: |
| Medium | Work cap | 265 / 267 | 265 / 267 | 24,692 to 28,176 |
| Huge | Frontier cap at sparse index allocation | 1 / 1 | 1 / 1 | 146,824 to 148,500 |
| HDFS | Work cap | 8,352 / 8,507 | 2,050 / 2,080 | 27,136 to 42,296 |
| HDFS holdout | Work cap | 7,463 / 7,585 | 2,110 / 2,170 | 27,348 to 40,332 |

Resume renews the per-invocation producer work allowance. The node totals
describe bounded exploration, and there are no completed proof pairs for resume
byte comparison or speed-to-optimum estimation. The CSV and JSON contain the
censored matrix and no expanded-budget runs. A verifier exit code of 2 with
an unresolved frontier is represented as INCOMPLETE in the verdict and CSV.
The generic process wrapper records any nonzero exit as PROCESS_ERROR.

The Review08 dense M3 evidence remains intact. The paired rank study awaits
the immutable rank producer pin and published proof-side replay pin.

[Actions run and retained job artifacts](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/46014832411)
