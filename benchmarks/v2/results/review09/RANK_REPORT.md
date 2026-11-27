# Review 09 paired sparse-v2 and rank-v3 results

The 20 CI jobs used producer `579a6b3b860854b158a8d71f61855228f0c70873` and
independent verifier `98e913a7e15d32638319832fc69edb36edb2f505`. Each job ran
both proof formats with matched limits in one/all and normal/-O, with direct
and checkpoint/resume routes. The raw-only arm comparison uses the independently
derived identity scope for every fixture. The earlier authoritative journal
pipeline has its own results and scope provenance.

On the seven originals, 96 routes verified and 128 remained incomplete.
Tiny, small and cover completed in both arms with equal objective, all-mode
optimum sets, node counts and proof lengths. Rank admitted zero leaves on all
seven originals. Direct cover search charged 105,571 rank work units in one mode
and 356,366 in all mode. Direct HDFS and holdout rank search charged about
2.25 to 2.59 million rank work units. Both arms exhausted the work budget on
medium, HDFS and holdout. Huge stopped at the sparse compatibility index cap.
The node counts and proof sizes for those four fixtures describe capped
exploration.

All 96 targeted routes independently verified and agreed with literal RGS.
Each completed resume matched its own direct proof bytes. The table shows
direct search. Both address-space profiles and interpreter modes reproduced
these counts.

| RAW case | Mode | Verified rank leaves | Nodes, v2 to v3 | Proof bytes, v2 to v3 | Charged rank work |
| --- | --- | ---: | ---: | ---: | ---: |
| Equality | One | 1 | 10 to 7 | 2,659 to 2,046 | 801 |
| Equality | All | 1 | 12 to 10 | 3,293 to 2,860 | 1,475 |
| Strict | One | 0 | 50 to 50 | 10,224 to 10,224 | 935 |
| Strict | All | 14 | 190 to 92 | 41,060 to 21,941 | 10,901 |
| Fractional | One | 1 | 10 to 8 | 2,855 to 2,860 | 1,321 |
| Fractional | All | 0 | 10 to 10 | 2,868 to 2,868 | 1,321 |

The completed original routes, censored original routes and targeted routes
have separate CSV and JSON exports. They include independently checked proof
fingerprints, observed rank leaves, benchmark RSS and wall times, checkpoint
and final replay outcomes, and completed resume parity. Rank discovery is
measured in native charged work and calls. No expanded budgets were used.

[Rank CI jobs and raw evidence](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/46016360030)
