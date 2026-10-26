# C002 integration and preservation contract

The parent chat is the coordinator. All three child chats are explicitly authorized by the user. Shared-directory Codex forks are used; no child may modify another owner's files, the baseline, the coordinator journal, or Git state. No external dependency installation. Python: C:/Users/Mahdi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe (3.12.14); use -B -X utf8.

## Ownership

- A owns approaches/eager/. It supplies engine_candidate.py, eager_solver.py, common_helpers_candidate.py, driver_candidate.py, PROOFS.md and SOURCES.md.
- B owns approaches/lazy/. It supplies lazy_solver.py, PROOFS.md and its attempt records.
- Auditor owns audit/. It supplies capture.py FIRST, corpus construction, independent checker, correctness and benchmark runners, reports and raw runs.
- Coordinator alone promotes reviewed shared candidates into common/engine.py and common/helpers.py, installs root solver.py, freezes hashes, records child IDs and makes Git commits. Children propose changes to shared code under their own directory; never edit common/ directly.
- Baseline reference: baseline/partition_solver.py, copied byte-for-byte from the previous cycle. It remains authoritative and unchanged.

## Fixed model and CLI

Known finite alphabet of 2..10 distinct single-character symbols, exactly two nonempty disjoint blocks, noise-free positive and negative samples, unrestricted regular factors. No RPNI, state bounds, new labels, target-generator access by solvers or k>2.

Root CLI: python solver.py INPUT.json --method baseline|eager|lazy [--timeout-seconds 30]. Default method baseline. JSON input keeps alphabet, positive, negative exactly as v1. Providers expose solve(data, *, deadline=None), where deadline is an absolute time.perf_counter() value or None. Do not use competing parameter names. Root adds parsing/preprocessing/output timing through the external runner; provider solve covers all its own preprocessing.

Completed results retain v1's alphabet, k, status, sample_size, graph, search, feasible_partition_count, feasible_partitions, limitations and interpretation. Add method, complete=true, and metrics. Normalize complete feasible sets as sorted unordered nonempty bipartitions. Records retain blocks, positive_projection_languages, negative_witnesses. These witnesses describe POSSIBLE rejection locations, not causal target labels.

Interrupted results: complete=false, status=incomplete, feasible_partition_count=null, found_partition_count equal to stored feasible_partitions length; never report unique/infeasible on a partial enumeration. Invalid input exits 2 with invalid_input. No unknown letters or contradictory labels are silently accepted.

## Shared engine v1 (A proposes; audit reviews; coordinator promotes)

Expressions are immutable tuples: ('const', bool), ('lit', index, side), ('and', tuple(children)), ('or', tuple(children)). Empty AND=true; empty OR=false. assignment is a sequence of -1 (unknown), 0 or 1. eval_expr(expr, assignment) returns True, False or None.

iter_models(num_vars, constraints, *, deadline=None, stats=None) yields tuples of 0/1 ownership values in fixed lexicographic symbol order, with variable 0 fixed to 0, other variables branching 0 then 1, and at least one variable 1. Partial false constraints prune; unknown constraints never prune. Stats accumulate nodes_visited, complete_assignments, pruned_nodes, constraint_evaluations; include restarts for lazy. find_model(...) returns the first model or None. SearchInterrupted is raised on deadline expiration. No third-party SAT solver. Both approaches use exactly this frozen engine.

## Shared helpers v1 (A proposes)

validate(data), project(word, block), witness_graph(alphabet, positive, negative) match v1 semantics. distinguishers(alphabet,n,p) returns a deterministic tuple of index-tuples of size 1 or 2 with unequal projections. Keep all distinguishing singletons; omit a pair containing a distinguishing singleton. Expose graph_constraints(alphabet, edges), partition_record(alphabet,positive,negative,assignment), result_from_records(...), and load_baseline(). A documents exact helper signatures in its README before B integrates; root approves this interface once. Helpers may load immutable baseline by absolute path derived from this cycle root. No cwd-dependent imports.

## A exact constraint

D(n,p) is the distinguisher family. T_s(n,p) = OR_{U in D(n,p)} AND_{a in U} [x_a=s]. For each negative n, require (AND_{p positive} T_0(n,p)) OR (AND_{p positive} T_1(n,p)). Include sound graph equalities as shared constraints. The rejecting side is shared across ALL positive words for one negative. Proof must establish word reconstruction from singleton/pair projections and exact equality to F2(S), including empty class cases. This is not a novelty claim.

## B lazy constraint

Start with graph equalities and canonical/nonempty ownership. Evaluate a proposed complete assignment using the independent direct projection criterion. For an infeasible assignment, choose lexicographically first offending negative n and lexicographically first matching positive p0,p1 in each side. Add T_0(n,p0) OR T_1(n,p1). This globally sound cut excludes the current assignment. Cache identical cuts. For a feasible assignment, emit its record and add ONLY its exact ownership-blocking clause OR_i [x_i != value_i]. Enumerate projected ownership models only; no duplicate models from witness variables. Restart shared find_model after each cut/blocker and count all work.

## All results preserved

No experimental run may have terminal-only evidence. Until capture.py is supplied, save any smoke run's exact command, full stdout/stderr, exit code and source hashes in a uniquely named attempt directory BEFORE interpreting results. Afterward use the capture runner. All attempts are immutable; fixes produce a new attempt linked to the previous one. Do not delete failed scripts, raw examples, minimized examples, timeouts, environment failures, or superseded proofs. Status of execution is separate from scientific status. Only coordinator appends central journal; child attempt logs are in owned folders.

Corpus and baseline are frozen before comparisons. No code edits during measured execution; runner snapshots source versions. Audit must compare COMPLETE F2 sets and validate witness payloads, not merely status/one winning answer. Keep full-generator graph tests separate from sample-only learner inputs. Performance includes preprocessing and output; no unmeasured speed claims.

## Completion gates

G1 capture + corpus manifests and A engine candidate; G2 independent engine review and coordinator promotion; G3 both providers smoke-correct with frozen interface; G4 correctness tiers pass or refutations archived; G5 repeated performance and separate memory runs; G6 Persian final report, complete evidence index, supervisor decision, all files committed. Baseline remains default.
