# C007 implementation protocol v1

## Model and API

Input is `{alphabet, positive, negative}`. Alphabet is known, nonempty and
consists of distinct one-character symbols. Labels are exact complete words;
the positive and negative lists must not conflict. There is no `k`, `q`, or DFA
state bound. A partition has nonempty disjoint alphabet blocks and may contain
one block. All regular local factors are allowed; finite positive projection
sets are existence witnesses, not a target-language assumption.

`solve(data, deadline=None, mode="adaptive", max_solutions=None)` has two exact
modes. `adaptive` finds compatible binary separators, refines their current
meet, and then proves a complete no-separator cover before returning a finest
partition. `reference` checks every canonical binary partition and returns the
complete compatible binary family plus its meet; a limit truncates it and
returns `incomplete`. Deadline uses an absolute `time.perf_counter()` value.

## Mathematical object

For a partition pi, let P|B be the set of projections of positive words to
block B. pi is sample-compatible iff every negative has a block whose
projection is absent from P|B. This is necessary and sufficient for arbitrary
regular factors. The set of feasible partitions is closed under coarsening.
The meet of all feasible partitions equals the meet of all feasible binary
partitions: any feasible multi-block partition separating a pair can group its
blocks into a feasible bipartition separating that pair. The empty binary
family has universal equivalence and therefore a one-block meet.

If the meet is compatible, it is the unique finest sample-compatible
partition. If the meet fails, finite-poset maximality implies at least two
incomparable maximal refinements. The result does not enumerate them and does
not claim a maximum block count or recover the hidden architecture.

## Adaptive separator invariant

Start at the one-block partition M0. Every recorded compatible cut is a
feasible bipartition; Mt is their meet. On each successful separator, Mt
strictly refines, so there are at most |alphabet|-1 successful refinements.
The must-link components are only a sound search quotient. If their direct
partition passes, it is a cheap unique-finest certificate because every
feasible partition coarsens it. If it fails, adaptive state still starts at
the one-block meet; components are never assumed feasible.

The final no-separator certificate covers every canonical cut of must-link
components. A cut record either has a negative plus a positive matching each
side (incompatible), or has full direct-projection witnesses and respects the
claimed meet (compatible nonseparator). Successful separator history contains
each feasible cut and its witnesses. The verifier reconstructs their exact
meet and checks the complete cover. No timed-out oracle call or omitted cut is
treated as exhaustion.

An early `multiple_maximal_exist` result is also possible: after at least two
feasible cuts, if their partial meet is already incompatible, no finest
feasible partition can exist. The result marks `meet_is_final=false`; the
partial meet is not presented as the exact meet of all answers.

## Statuses

- `finest_unique`: compatible unique finest partition with direct projection
  witnesses and a replayable finality proof.
- `one_block_only`: no nontrivial compatible partition; the one-block model
  remains compatible. Includes a C006-style impossibility certificate.
- `multiple_maximal_exist`: proof that no finest compatible partition exists;
  maximal refinements are not enumerated.
- `incomplete`: deadline/interruption/truncated reference enumeration. Partial
  separator history may be retained but is not finality proof.
- `invalid_input` / `runtime_error`: not scientific non-decomposability claims.

## Cost

With r must-link components there are `2^(r-1)-1` canonical component cuts.
Reference mode and a complete final no-separator proof may therefore be
exponential. The number of successful adaptive refinements is at most m-1,
but this does not bound the cost of finding a separator or proving none exists.
