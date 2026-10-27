# Candidate protocol: wait until the auditor's active benchmark ends

Status: NOT EXECUTED. Do not import/run these scripts during the auditor's timed
suite. Master/auditor decides when to freeze a new independent extension and run
it serially. This task writes source/proof/protocol only, not new frozen fixtures.

1. Preserve and capture the exact generator, checker, this protocol, theorem and
   all relevant provider/graph/runtime dependencies using C003 audit/capture.py.
   Call generate.py --output NEW_UNIQUE_DIRECTORY only after timing has ended.
   Existing destinations are refused; never modify earlier frozen C003 artifacts.
2. The candidate creates 24 inputs: four deterministic cases for each alphabet
   size 4,8,16,32,64,128, with seed base 2026102604. Per size, variants use a
   balanced split, singleton left, singleton right and an unbalanced split; symbol
   order is deterministically shuffled and tree edges have randomized orientation.
   Every local tree is a path. Hidden truth includes blocks, trees and explicit
   local DFA tables, written to truths.jsonl, separate from inputs.jsonl.
3. Capture check.py INPUTS TRUTHS with both input files and checker code supplied
   as source_paths. It verifies DFA token construction, every target label, the
   sample rescue-graph components, state bounds and 24-case size coverage without
   importing/calling a candidate solver. This checker is still a proposal; the
   auditor should inspect it independently rather than treating shared family
   reasoning as empirical certification of the entire pipeline.
4. Pass ONLY each visible row's input object to general/fair-reference through
   normal provider/CLI calls. Target DFAs/blocks/trees and expected uniqueness
   must never enter solver arguments. Record full raw result BEFORE comparison.
   Use equal max_solutions tasks (1 and 2 are sufficient for the proposed
   demonstration), hard limits and separate statuses. Since graph r=2, exhaustion
   is expected even at the first-answer limit; the sole valid result should be
   unique in general_regular_product, not a fixed-word-only claim.
5. A saved result JSONL for check.py --results must contain {case_id,result}, one
   case per row, and all 24 IDs. This format checks one method/task at a time.
   The checker validates partition equality, complete uniqueness/exhaustion and
   each positive language/negative witness. Keep any incomplete result separately;
   checker rejection of it is not a mathematical refutation or automatic program
   error. Preserve the original raw output, input and code before diagnosing or
   minimizing a genuine mismatch. Never replace a failed attempt with a rerun.
6. Report actual capture artifacts/counters only after execution. No times or
   success rates exist from this task. If timing is later authorized, use a small
   frozen serial subset with repeated fresh-process jobs and accurately scoped
   memory instrumentation; do not silently append work into the active benchmark.

Capture dependencies: generator/checker source and their actual JSONL inputs;
provider modules plus general/support.py, root CLI, runtime manifest, read-only
C002 baseline graph source, and capture.py. The checker does not execute provider
code, and generator imports none. Their unexecuted state must remain explicit
until a uniquely captured attempt exists.
