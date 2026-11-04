# Final C020 control review v1

Scientific status: verified under the stated sample-consistency model and trusted K=20. Review type: static inspection of recorded scripts, proofs and results; no fresh provider, verifier or benchmark run. Existing attempts and earlier theory reviews remain unchanged.

## Uniqueness obligation

Let F be the connected-component partition of the independently replayed adjacent-swap forest. Each edge is supported by a positive p and negative n differing only by swapping adjacent distinct symbols a,b. If a and b belonged to distinct ownership blocks, every block projection would be unchanged between p and n. Independent factor acceptance would then assign identical global labels, a contradiction. Hence each sound edge forces coownership, and every sample-compatible partition coarsens F.

The recorded control reconstructs F from the full alphabet, checks exact swapped-word equality for every forest edge, forbids cycle edges, and obtains exactly 20 components. Under trusted K=20, a coarsening of these 20 nonempty components into 20 blocks must equal F. The independent witness routine checks that its blocks form a partition of the whole alphabet, reconstructs the local positive-projection languages, and checks rejection of every negative. This establishes feasibility of F, hence existence and uniqueness. Passing {key} as the witness expected-set is not the uniqueness proof; the forest argument supplies uniqueness and the projection checks supply existence.

No enumeration of all 40-symbol partitions is required by this proof. No truth-model file is passed on the recorded solver command. This proves exact sample-consistent uniqueness under trusted K and disjoint independent factors, not general recovery from arbitrary logs. In particular, the unknown-K C cell remains ambiguous.

## Recorded evidence and its limits

The accepted functional attempt is 20261104T121357.281706Z_b2e145f2ec, input SHA256 5b4db148b017d23c35171e38775cdd740980ec0f7eb7ad81e9a54a8f494d3499. Its subprocess wall time is 5.284430799998518 s and internal input-and-solver time 5.02204470000288 s. This is one post-main functional run, explicitly not a benchmark row, speed comparison, or accuracy-rate estimate.

The field minimal_states_per_device=1024 is a literal in the control script, not a proof furnished by that script. The separate fixture audit C reports 20 factors with certified_minimal=1024 and the complete a-cycle/single accepting state argument. See PLANTED_ANCHOR_PROOF_v1.md for the distinguishing-suffix proof. Fixture C has T=32338004 and 53 labelled words (17 positive, 36 negative). Deliberately informative planted swap anchors can make ownership inference easy even when each generator has many minimal states.

The functional capture explicitly snapshots the control script, provider source, CLI, input and preregistered plan. The imported replay helper and capture module are not explicitly in that source_paths list. This review preserves their current source hashes and copies separately; it does not retroactively assert that these helper bytes were independently frozen by that earlier capture. The recorded command uses the Python executable in started.json; no alternative runtime is inferred.

## Master decision input

The main validation report is accepted_with_censoring with zero errors and 5130 small-gate rows; closure reports validation_success. These are recorded acceptance findings, not fresh independent executions by this reviewer.

C2 improves completion on the fixed B/C cells and wall time on A, but D_K4 is a material end-to-end regression: baseline median subprocess 0.8118160999947577 s, C2 0.9735870999938925 s. C2 takes about 19.93% more wall time. The inverse ratio baseline/C2=0.8338402388444243 is about 16.62% below one; calling this a 17% increase in time would be numerically incorrect. Internal D pipeline time improves (0.247363000002224 to 0.06958160000067437 s), which does not erase the measured subprocess regression. The available evidence does not isolate its cause.

Stop this bounded optimization round after the two authorized candidate slots and record the material-regression review. Do not introduce a third candidate or extra favorable benchmark cells. The results do not establish a global performance plateau, optimality, universal speedup, or universal hardware recovery. Keep negative and censored outcomes visible and separate the K20 functional control from the six-cell comparison matrix.
