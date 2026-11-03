# C013 frozen generator v1 — bounded static review

Disposition: **STATIC CLEARANCE FOR CAPTURED GENERATION AND INDEPENDENT AUDIT**.
No correctness run, generation, inference or timing was performed by theory.
No frozen source was changed. Prior usage-limit interruption was an execution
availability issue, not a mathematical counterexample or generator failure.

Authoritative freeze: implementation/READINESS_V1.json. Verified generator hash:
`0b649344035f449b0a17cd6410dd41db67c6b1e06025b78262807740b93ba410`.
Protocol hash:
`747c1e7313bcdf2c483415e6a386a7a4eeea42cdd08e6bf0be7fdac65f5c41e4`.
Snapshots and review hash are recorded in static_generator_review_v1/MANIFEST.json.

## 1. Stable complete worlds and saved truth

build_world uses only seed, K and m through the `world:K:m` substream. Neither
sample count nor length/mode/profile affects its calls. The shuffled alphabet
is distributed round-robin, ensuring disjoint full coverage and at least two
symbols/device after CLI m≥2K validation. ownership and device alphabet tables
are constructed together. Each state has a transition on every local symbol;
all targets are in range. connected checks reachability from every state.
Bounded rejection sampling conditions complete random tables on strong
connectivity; exhaustion raises rather than inventing a world. State0 accepts
and a nonempty subset of the remaining states rejects.

world.json stores all model states, starts, accepting sets, local alphabets,
complete transitions, ownership, root seed, RNG purpose and table-attempt
counts. The **model fields** are identical for fixed seed/K/m across cells;
whole world.json bytes are not identical, because generation metadata and
wall-clock time vary. Compare model subtrees/hashes when asserting same world.

solver_input is constructed with exactly alphabet, positive and negative.
No transitions, ownership, true count, world path or repair state enter it.
The master has selected the previous no-K default for this round; the frozen
protocol's historical sentence that clarification is pending does not imply
any count is sent. There is no solver import or C011 inference acceleration.

## 2. Repair, length and label correctness

shortest performs BFS with one visit per state and checks acceptance against
the requested target. Strong connectivity and nonempty accept/reject sets
guarantee termination with a shortest path of at most states_i−1 characters.
prefix_limit binary-searches the monotone inequality
`b+min(K,b)*max(states_i−1)≤cap`, returning the largest safe b.

With b>0 the active set is nonempty. Positive generation repairs all active
devices to accept; negative generation uniformly chooses one active device
to reject and repairs all other active devices to accept. Inactive devices
remain at accepting state0. The emitted word keeps the drawn global prefix
and appends an interleaving of repair suffixes only. Thus local final states
match the targets and length≤cap by the reserve proof. The explicit replay
and assertion check these consequences before accepting the candidate.

interleave chooses a ticket uniformly among remaining events and selects
its owner's next event. It implements remaining-length weights, not uniform
choice among active devices. This is conditionally uniform over schedules
of the fixed local repair suffixes and preserves local order; it does not
sample accepted or rejected global languages uniformly.

## 3. Zero/short caps and bounded uniqueness

When b=0, the source falls back to direct random sampling and uses actual
replay labels, not an unsupported claim that a reserve failure proves a
label impossible. For cap0 and requested negatives>0, generation explicitly
skips negative attempts and records the proved impossibility (all starts
accept). Multiple unique positives at cap0 produce duplicate shortfall;
count0 is legitimately complete without requesting either label.

Each label gets a finite retries budget, wrong-label and duplicate counters,
actual generated count and shortfall. A set forbids duplicates across the
sample; disjoint exact labels prevent legitimate cross-label reuse. Output
is saved even on shortfall and CLI returns3, distinct from success0. Other
shortfalls establish only that this sampler exhausted its attempt budget,
not that no requested word exists mathematically.

Raw failed-attempt **counts** are saved; failed word strings are not separately
listed. Candidate purposes/indices and seed allow deterministic reconstruction
under the same Python RNG implementation. Do not describe accepted sample
records as a log containing every attempted word.

## 4. Reproducibility and distributions

Candidate prefix/repair/length substreams depend on seed,K,m,label,index,
profile, not requested sample count or cap. For fixed world/cap/mode/profile,
accepted traces for count2 prefix the corresponding count8 per-label stream,
subject to explicit attempt-budget shortfalls. Generating positives before
negatives does not invalidate this: different labels cannot collide in the
global seen set. Different caps preserve candidate event-stream prefixes,
but can change target state, active set, selected repair target and suffix.

Near-max means largest reserve-safe prefix, not a guarantee the final trace
equals the cap or is uniformly distributed near it. Uniform mode samples
prefix length, with a separate direct-sampling rule at zero; it does not
yield uniform final lengths. The protocol states these conditions.

Uniform profile is device-uniform then local-event-uniform, not necessarily
global-event-uniform for unequal alphabet sizes. Skewed gives device0 weight4
and others1, also only for the prefix. Saved event frequencies describe
retained repaired traces. They must not be misreported as unconditional
sampling probabilities of the final words. Model/repair/uniqueness conditioning
is explicitly documented; no uniform-over-all-DFAs claim is made.

## 5. Evidence and resource scope

Internal replay twice validates each retained label/state, but it is the same
source routine, so independent saved-table replay is still mandatory. Correct
labels and truth-compatible ownership do not certify the solver's complete
partition set, count or recovery. Small independent RGS controls and the
planned large-case audit must preserve that distinction. For no-K true K>1,
the one-block model remains an alternative regardless of successful generation.

Retries and the10000-table cap are attempt bounds, not wall-time bounds.
Long-word creation, RNG, BFS, interleaving, repeated replay, run/frequency
statistics and JSON writing may be expensive. generation_seconds measures
observation generation/replay only; it excludes world construction, final
serialization and inference. External captured process timing must label
its own scope. Partial/killed outputs cannot be treated as complete datasets.
No efficiency or million-character capacity is established by static review.

## Decision and required next evidence

No exact counterexample or blocking source defect found in these reviewed
paths. Proceed with immutable captured generation and independent label/world/
boundary tests. Preserve shortfalls and all actual failed captures. Static
clearance does not substitute for those gates or authorize hidden truth to
enter the exact C010 no-K solver.
