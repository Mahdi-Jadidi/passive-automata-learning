# C013 generator v1 (frozen before execution)

`generate_v1.py` uses only the Python standard library. No C011 solver is
imported. The generator writes two files to a fresh output directory and
refuses to overwrite either file. No generation run has yet been performed.

Example reproduction command, to be executed only after independent review:

```powershell
python -B results/2026-11-03/partition_random_dfa_v13/implementation/generate_v1.py --devices 3 --alphabet-size 40 --max-length 64 --samples-per-label 8 --seed 20261103 --length-mode near-max --out results/2026-11-03/partition_random_dfa_v13/audit/example_k3_l64
```

Use `--allowed-devices 1 2 3` instead of `--devices 3` to select a seeded
uniform count from the distinct allowed values. This is generation metadata,
never a solver constraint. Default alphabet size is twice selected K; explicit
alphabet size must be at least 2K (and at most 10000). The planned sweep uses
40 symbols. `--max-length`, `--samples-per-label`, `--seed`, and `--out` are
required. Optional `--max-attempts-per-label` defaults to max(100,100*count).
`--event-profile uniform` selects a device uniformly, then a local event
uniformly. `skewed` gives device 0 weight 4 and every other device weight 1,
still with uniform local events. These probabilities govern the prefix only;
BFS repair changes final event frequencies. Actual probabilities/frequencies
are saved. The broad grid uses uniform; any skewed subset must be preregistered.

## Saved artifacts and observational boundary

`world.json` stores every device's complete transition table, local alphabet,
states, accepting set, start, ownership, root seed, RNG derivation purpose,
transition-table rejection counts, and generation statistics. Its sample
records point to label/index in solver input and contain final states, actual
length, run count, prefix/repair lengths, active count, selected negative target
device, and strategy. Event frequencies and the observed alphabet are recorded.

`solver_input.json` contains exactly `alphabet`, `positive`, and `negative`.
It contains no world path, ownership, true K, transitions, or generator state.
The count-information decision is pending; this version exports no allowed_k
even when an allowed count list was used to generate a world. The solver must
read this observational file alone; it must not read world.json.

## Conditional world distribution and reproducibility

The alphabet is shuffled and distributed round-robin, giving at least two
symbols per device, with randomized ownership and nearly equal group sizes.
Each device has independently selected 2–4 states. Complete transition tables
are sampled with independent uniform target states and rejected unless strongly
connected; at most 10000 tables per device are tried, otherwise generation
fails explicitly. Start state 0 accepts. A nonempty rejecting subset of the
other states is chosen uniformly. This is a conditional distribution, not a
uniform distribution over all DFAs or accepted trace languages.

Separate SHA-256-derived RNG streams select count, world, and observations.
For fixed root seed, K and alphabet size, changing length/sample-count/mode
preserves the complete device tables and ownership. Candidate streams depend
on seed, K, alphabet size, target label, candidate index, and event profile;
they exclude requested sample count, length and length mode. Prefix, length
selection and repair use separate substreams. For a fixed world/length/profile,
the retained first two samples per label are subsets of the retained first
eight (subject to their respective explicit attempt budgets). Across length
caps a candidate draws the same prefix event stream; its repair may differ.
Timings in world.json are nondeterministic;
the scientific models, words, counters and final states are reproducible for
the same Python random implementation and parameters.

## Length reserve and label construction

Let R=max(states_i-1). Choose largest prefix bound b satisfying
`b + min(K,b)*R <= max_length` by binary search. A prefix activates at most
min(K,b) devices. Each active device has a shortest path of at most R events
to an accepting or rejecting state because its graph is strongly connected.
Inactive devices stay at accepting start 0. For positives all active devices
are repaired to accept; for negatives one uniformly selected active device is
repaired to reject while the others accept. Thus repair length is at most
min(K,b)*R, and the final word never exceeds the cap.

The prefix chooses events according to the configured device profile and
uniform local events. Near-max mode uses the
largest safe prefix; uniform mode chooses its length uniformly in [0,b].
Final lengths are not uniform and may fall below the cap because BFS paths
can be shorter than the reserved worst case. BFS ties follow sorted local
symbol order, so traces are conditioned and biased rather than uniformly
sampled from a label's language.

Repair paths are interleaved by selecting a device proportionally to its
remaining path length. This gives uniform labelled interleavings of the fixed
local repair paths while preserving each device's local order. Because
alphabets are disjoint, interleaving preserves all intended final states.

When the selected prefix length is zero, use bounded direct random sampling
at a length equal to the cap in near-max mode or uniform in [0,cap] in uniform
mode. Labels are accepted only after exact replay. In particular cap zero
allows only epsilon, which is positive; negative generation is explicitly
skipped with an impossibility message. More than one unique positive at cap
zero cannot be supplied and produces a uniqueness shortfall. Other short-cap
shortfalls mean exhaustion of the sampling budget, not a proof that the target
language is empty.

## Counters, shortfalls and review gate

Each label has an independent attempt budget. Wrong-label and duplicate
attempts are counted, and output words are unique across the whole sample.
The generator does not pad a shortfall with duplicates. Exit 0 means both
requested unique sample counts were met; exit 3 means a saved, explicit
shortfall. Invalid CLI arguments exit 2. DFA conditioning exhaustion is a
program failure with a traceback, not a fabricated dataset.

All retained labels and final states are replayed from complete transition
tables; independent auditor replay is still required. `generation_seconds`
covers observation generation and replay, not world construction, output
serialization or inference. It must not be reported as total process cost.
There is no inference code in this candidate. Correctness and performance
claims remain pending frozen-source review and captured execution.
