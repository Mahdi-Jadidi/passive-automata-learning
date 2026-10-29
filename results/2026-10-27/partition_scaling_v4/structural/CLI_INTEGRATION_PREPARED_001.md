# Structural provider integration guidance (prepared, not accepted Stage2)

Date 2026-10-27. Execution status: no runtime integration or Stage2 provider execution. Stage2 must pass the independent gate before promotion. Frozen S001 v1 is not edited. All paths below are relative to this C004 root.

## Dependencies and loading

- `structural/singleton_solver_v1.py` is standalone stdlib code.
- `structural/singleton_solver_v2.py` imports `singleton_solver_v1` by module name.
- `structural/singleton_solver_v3.py` imports both `singleton_solver_v1` and `singleton_solver_v2` by module name.

The simplest root CLI loading policy is to put the resolved C004 structural directory on sys.path before loading the selected module. This must be derived from the CLI's own __file__, not from process cwd. An importlib loader may alternatively load dependency v1 into sys.modules['singleton_solver_v1'] first, then v2 into sys.modules['singleton_solver_v2'], and finally v3. Loading v2/v3 by file path alone without either policy will fail to resolve their sibling imports. Do not depend on a globally installed package or the parent C003 directory. Do not substitute the similarly named C003 solver.

Capture source lists must contain the CLI/driver, every loaded structural source, every observation input, and any additional imported research source. For v2 include v1+v2; for v3 include v1+v2+v3. Hash the on-disk candidates at acceptance; the prepared v2/v3 hashes have not yet been promoted. Their imported v1 must retain the accepted S001 hash.

## API and mode mapping

Common API: `solve(data, *, k=None, deadline=None, max_solutions=1)`.

The known-k value is the explicit argument if provided; otherwise data['k'] if present; otherwise 2. Alphabet entries are one-character strings; all blocks are nonempty. Structural v1 accepts 1<=k<=m, beyond the official k=2,3,4,6,8 experiment grid. `max_solutions` is a positive integer or None (all answers). An integer limit is a search/output bound, not a uniqueness request. A deadline is an absolute finite time.perf_counter() value, not a duration: the CLI should convert a duration with time.perf_counter()+seconds. External capture supplies the hard deadline.

V1 mode: certificate-only singleton product. V2 mode: known-k singleton product, certificate-first with exact coloring fallback. V3 default: same known-k behavior as v2. V3 optional `infer_k=True`: unknown-k combined must-link/opposition certificate; omit explicit k in this mode. This option is mutually exclusive with explicit k; it is not an instruction to enumerate arbitrary unknown-k regular models. In inference mode the observation object's k field is ignored because no k is assumed. A root unknown-k flag should be routed explicitly to `infer_k=True`, not to `k=None` alone. The latter retains historical known-k default semantics.

Structural methods do not take `local_word_cap`: exactly-one local word is distinct from general at-most-q finite language semantics. Route q options only to the general provider. With a nonempty positive set q=1 feasibility is equivalent to exactly-one local words; with an empty positive set the semantics differ. No-positive structural input remains insufficient_coverage.

## Result/status handling

All versions expose method, model_class, k, status, solutions, search_exhausted, decision_complete, uniqueness, uniqueness_scope, assumptions and metrics. Solutions use canonical sorted blocks, local_words, singleton positive_projection_languages, and negative_witnesses. The latter include the negative word, block index, projection and all blocks with unseen projections. Graph/certificate fields preserve checkable evidence.

- `found`: one or more compatible partitions returned. Report unique only if the uniqueness field explicitly certifies it. V2 first-answer results typically have uniqueness='unknown' and search_exhausted=False.
- `infeasible`: incompatibility proved within the declared singleton class, by count contradiction, a forced certificate failing labels, or exhaustive known-k coloring. Do not transfer this to arbitrary regular factors.
- `insufficient_coverage`: deliberate unresolved result. V1 supports only complete-k-partite or connected-bipartite(k2) certificates. V2 preserves no-positive unresolved cases. V3 unknown-k returns unresolved when the combined quotient-clique certificate is absent.
- `incomplete`: cooperative deadline or interruption. Never present as unique, infeasible or exhaustive. Previously returned solutions remain usable witnesses, and decision_complete can be true if existence was already proved.

V1 emits uniqueness='unique' only on a successful structural certificate, otherwise 'unknown'. V2 may emit 'unique', 'multiple', 'none', 'unknown'; 'multiple' can follow finding two solutions even without exhaustion, while 'none' requires exhaustion. V3 inference emits 'unique' on its combined certificate, 'none' on its proved contradiction and 'unknown' on unresolved/incomplete outcomes. The general provider uses 'ambiguous' instead of 'multiple'; normalize labels for display only, preserving raw provider output.

The root should serialize the full result for correctness/artifact output. A benchmark summary must be a separately documented mode, used identically across methods; do not truncate graph/sample/witness fields silently. The CLI should not claim planted recovery from a first compatible partition. Unknown-k certificates remain conditional on singleton local languages even though their contextual must-link sublemma holds for general factors.

## Known implementation qualifications

These candidates are prepared and require captured smoke/full-set audit. V2 exact fallback is exponential and currently uses sorted-symbol DFS; max_solutions=None can produce large output. V3 must-link discovery compares positive/negative word pairs, with work up to O(|P|*|N|*L), and has coarse operations inherited from v1. Empty-positive inference is intentionally unresolved. Review COMPLEXITY_SCOPE_S001_NOTE_001.md for the certificate finder sorting bound and pair-extraction scope. Malformed argument exceptions should be caught by the CLI and displayed as input errors; no provider error should be relabeled as infeasibility.
