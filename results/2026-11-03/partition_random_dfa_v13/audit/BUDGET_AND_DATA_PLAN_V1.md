# C013 audit: feasible construction and timing plan

Status: preregistered proposal before generator/provider execution. Await generator readiness, static clearance and final source/input hash freeze. No old-cycle files change. C010 exact reference only; no-K is the default until the master resolves the count-information question. If changed before launch, preserve this plan and bind a versioned amendment.

## Dataset construction and independent validation

The primary grid is exactly 240 cells: K=1..20, maximum length [8,64,512,4096,65536,1000000], positives/negatives each [2,8], alphabet size 40. World seed is a deterministic function of 20261103 and K, independent of length/sample count. Save all complete transitions, accepting states, starts, local alphabets and ownership. Solver input contains only the declared alphabet and labeled words. Record actual K, lengths, run counts, observed symbols, repair lengths, retries and uniqueness shortfalls in sidecars unavailable to the provider.

Prefer generate eight samples per label once for each K/length, deriving the two-sample input as a deterministic prefix subset, if this matches the frozen generator API and preserves its documented conditional distribution. This saves duplicate construction and gives a nested sample-count comparison. If unsupported, record independent cell seeds rather than pretending nested samples. Length caps are maxima, not claims of exact lengths. A short-cap failure must be saved and fixed under a new generator version before claiming all-grid coverage; never silently substitute another cap or world.

Independently replay every saved trace from the transition tables. A single pass routes each event by saved ownership, updates that device's state, and finally conjoins local acceptance. Avoid a separate full-word scan per device. Check declared/local alphabets partition the global alphabet, DFA table totality, start/accepting validity, raw/unique label counts, no label conflicts, actual lengths <= cap, and input hashes. Report conditioning/repair bias; the data are not uniform over all labeled traces or DFAs. Generation, repair and independent replay times are separate from inference.

Inputs and raw outputs use content-addressed lossless storage or deterministic gzip where needed. Preserve exact CLI bytes and checksums; archive splitting/compression must not change their scientific content. Capture source snapshots include only actual provider/harness dependencies, that input and its world/sidecars, not all 240 large inputs on every job.

## Honest budget and execution order

Three full repetitions at the hard ceiling cost 240*3*7=5040 seconds before generation/overhead, so they cannot be guaranteed within 45 minutes. Plan all 720 timing slots but prioritize complete first-pass coverage. Never report budget-unstarted repetitions as attempted.

Total elapsed budget is 2700 seconds from start of captured dataset construction through provider captures (generation/validation/harness included). Reserve up to 720 seconds for construction plus label replay, 1680 seconds for the first 240 hard-capped calls, 180 seconds for capture overhead and controls, and 120 seconds initially uncommitted. Actual savings can fund repeat calls. If preparation exceeds its reserve or measured overhead threatens first-pass coverage, report the conflict immediately rather than silently abandoning cells or exceeding the budget.

1. Generate and independently validate all 240 cells and the small controls before the broad inference pass.
2. Run eight prespecified small controls: K=1..4, alphabet=2K, caps [8,64], two samples per label, full partition enumeration. Compare the entire family to independent RGS/projection feasibility; capture at cooperative 5/hard 7 seconds. A failed/censored validation control is not a correctness acceptance.
3. First pass: attempt every broad cell once, cooperative 5/hard 7 seconds, full default semantic output, no partition enumeration. Fixed order is cap ascending, sample count ascending, K ascending. This reaches every K/length/count stratum without selecting apparent winners.
4. Optional longer confirmations, only after all 240 first-pass calls: exactly K=[1,20], cap=1000000, count=8, one additional fresh call each, cooperative20/hard22. These are separate confirmation jobs, not substitutions for broad repetitions. Skip and label budget-censored if they cannot fit.
5. Attempt repetition 2 then 3 of all 240 in the same fixed order while the all-in budget permits. Before every launch reserve its full hard cap plus observed capture overhead. Unstarted slots get explicit budget-censored records. No retry of a failed/timed-out slot.

Generation/replay must be bounded and partial files/raw failures retained. Fresh-process CLI time includes startup, input, preprocessing, witnesses, and serialization. Report all three timings only where three broad calls completed. Otherwise report the actual repetition count, individual observations and censoring, not an uncensored median of three. No memory probes in this round; no extra skew cells before the primary grid. Event-frequency effects are recorded from actual traces; sample-count changes are not described as event-frequency experiments.

## Independent semantic checks and evidence limits

For large cells the saved physical partition must be compatible, but it is not a full-family oracle. Recheck its finite-sample feasibility directly. For every complete result inspect required fields, status, nonnegative spectrum, sum spectrum=total, kmax=max nonzero spectrum index, kmax <= upper bound <= atom count <=40, and true K <= kmax. In the no-K consistent-label model, one-block count is 1 and model_inconsistent is invalid.

Replay representative projection payloads and every same/different witness against actual labeled samples. Memoize feasibility only by canonical partition within a fixed sample; inspect every pair row and its together/apart relation. Check same+different=total, relation/count consistency, witness presence, every forced_same against actual co-ownership and every forced_different against actual distinct ownership. Replay available contraction certificates independently. These checks can detect errors but do not independently prove every reported large-family count exact; preserve that limitation explicitly.

For timeout/incomplete output require no final uniqueness/incompatibility/count claims. Retain raw output and classify cooperative incomplete, hard timeout, program/environment error, and budget-unstarted separately. Physical recovery, multiple compatible ownerships, and nonfinal runs are separate outcomes. Under no-K, merging physical blocks preserves consistency, so K>1 cannot be uniquely recovered from these labels alone. Do not call true-partition-in-version-space exact recovery.

Deliver machine ledger, source/world/input hashes, generation/replay outcomes, exact small-control family comparisons, large-result witness audit, per-cell timing/coverage, prespecified confirmation results and Persian report. No asymptotic inference or uncensored regression from timeout-heavy data. Master owns final byte manifest and private Git archive.
