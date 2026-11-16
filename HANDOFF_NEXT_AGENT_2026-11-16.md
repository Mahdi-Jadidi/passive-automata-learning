# Current research handoff — 16 November 2026

This is the current continuation entry point. It supersedes the **current-task instructions** in `HANDOFF_NEXT_AGENT_2026-11-14.md` and older checkpoints; those files remain historical evidence, not current prohibitions on implementation/testing.

Repository: `Mahdi-Jadidi/passive-automata-learning` (private).
Delivery branch: `codex/teacher-handoff-v46`.
Copyable next-agent prompt: [`NEXT_AGENT_PROMPT.md`](NEXT_AGENT_PROMPT.md).
Decision-complete continuation plan: [`docs/CONTINUATION_PLAN_V46.md`](docs/CONTINUATION_PLAN_V46.md).

## Latest user instruction, verbatim

> نیاز نیست تیچر رو قوی کنیم
> لیمیت زمانی رو بیشتر کن و الگوریتم رو تست کن
> بعد که همه چی خوب بود یکبار از پایه برسی کن و مطمین شو همه چی خوبه
> بعد یه داکیومنت در قالب مقاله بده بهم که انگلیسی باشه و هر بخش الگوریتم رو توضیح بده و نو اوریش رو توضیح بده و فیچر ها و کارایی که انجام شده براش و ... و بعد اثبات دقیق و کامل الگوریتم رو داشته باشیم
> دقیقا مثل یه مقاله
> در اخر هم پیشنهاداتی برای قوی کردن تیچر بده

The user then requested publishing the complete current results and this continuation plan to GitHub so a different agent can continue. Do not interpret earlier suggestions for a fast adapter as approval: **do not strengthen, replace or internally optimize the teacher now**. Recommendations belong at the end of the final paper, not in production.

## Objective and notation

Read `AGENTS.md` and `docs/ALGORITHM_NOTATION.md`. Given declared ordered Sigma and D=(S_plus,S_minus), return ONE compatible partition P maximizing |P|, plus a checkable optimum certificate. Local DFA state counts are mathematically unrestricted. No local DFA learning, optimum counting, enumeration of all optima, prefix-label assumptions or physical-device-identification guarantee is required. Declared IDs are opaque strings; retain unused IDs.

For a block B, H_B=pi_B(S_plus). It can reject negative y_i iff pi_B(y_i) is absent from H_B. Every negative needs at least one rejecting block. In the latest manuscript R_B is the relation of realizable local rejection behaviors: do not reuse it for a rejection bitmask. W_i denotes minimal rejecting atom sets only in versions using them.

## Implementations and exact status

### V43: faster historical baseline, frozen

`results/2026-11-16/exact_optimizer_v43/` implements mandatory atoms, singleton/atom shortcuts, the one-negative q-d+1 route, complete region-based W_i extraction, incremental equivalence/count SAT and structural/DRUP certificates. It does not invoke the manuscript teacher.

Its 2,261 oracle/certificate audits completed, all mined witness families matched the old exhaustive extractor. Separate audits include 167 four-atom antichains, 4,000 propagation comparisons, 14 boundaries and three legacy proof replays. Its benchmark has 120 fresh-process trials: enumeration, DP, V42 and V43, ten synthetic cases and three repetitions. All completed with matching optimums and accepted certificates. V43 is NOT universally fastest: DP wins overlap_8 and V42 wins oneblock_8.

Frozen SHA-256:

- encoding.py: `38da943c28419cb02c7b2aecff56c9ce189ed57ec51e39d2e19b74afab50727e`
- optimizer.py: `a4dcb3f1dfa6a84d5743276a9d8d584ab6e17d79fda1da95d3aa0ba976d8da63`
- verify.py: `e42c85a2cddb61797856114292f3577a2356c6bebcdf6bb7933ba6ca71af0dad`

### V44: assessment and first English article, frozen

`results/2026-11-16/final_assessment_v44/` retains the article, sources/build/rendering, proof/claim ledger and evidence. Additional checks: 100 samples / 15,664 pair-assignment-threshold checks, replayed with every expected/actual outcome; nine structured ab/ba families up to 256 symbols; two AI-assisted Terra reviews. The strict family separation is relative to a specified exhaustive traversal, not every exact algorithm.

PDF: `output/pdf/Certified_Maximum_Component_Alphabet_Partitioning_EN.pdf` (eight pages).

### V45: CURRENT interactive algorithm and faithful teacher

`results/2026-11-16/interactive_teacher_v45/` contains:

- `teacher_main.py`: reference implementation of main.pdf Sections 5.1–5.3: exhaustive named-DFA local tables with witnessed rows, Q_i relations, positive-forced zeros, feedback-edge conditioning, upward/downward semijoins and reconstruction. Source conformance is documented; no original executable was supplied for byte-identical comparison.
- `sources/main.pdf`: unchanged supplied 11-page manuscript. This is available inside the repo; Downloads paths are not needed on another machine.
- `projections.py`: exact shared prefix DAG, projection from cached supersets, per-mask images/rejection masks and positive witnesses.
- `spec.py`: normalization, limits and necessary mandatory-atom contraction.
- `master.py`: pair equivalence/counting, learned false-cover cuts. No eager W_i extraction.
- `optimizer.py`: maximum-relaxation candidate -> unchanged teacher -> external failure explanation -> generalized cut -> repeat. No hidden V43 fallback.
- `verify.py`: direct original-data feasibility/cut-witness checks plus reconstructed CNF/DRUP checking. It imports no teacher, projection store or SAT solver, but shares normalization/atom/master specifications as a trusted base.

Teacher parameters: for H_B empty, m(B)=1; otherwise number of distinct positive-projection prefixes including epsilon, plus a rejecting sink. A finite-language trie fits this bound, proving it does not remove any unrestricted-state sample-compatible partition. The bound is sufficient, not minimal or a new physical state assumption. Exhaustive enumeration up to it can be extraordinarily costly.

On a completed teacher rejection, choose a negative not separated by any block. Grow each failed block into a maximal non-rejecting atom region U, keeping an original positive projection match as witness. Learn: some block of the next partition must escape EVERY U. Encode that with equivalent Boolean gates. It preserves all compatible partitions and eliminates the rejected candidate, often others too. It does not force an arbitrary particular merge.

The master proposes a MAXIMUM-BLOCK partition under current necessary cuts. The first teacher-accepted such partition is globally optimal because the master is a relaxation containing all true solutions. Mere acceptance of an arbitrary candidate would not suffice. A fresh proof of impossibility at k+1 certifies the upper bound. `INCOMPLETE` is never a rejection and supplies no new cut from an unfinished check.

V45 evidence:

- Four saved test scripts passed (`test_runs.jsonl`). Teacher includes six tests and thirty raw Cartesian-join comparisons; projection includes three tests and 5,000-symbol words; master tests all covers/pair assignments through four atoms (16,384 covers and 64 assignments at q=4); cut tests check 167 monotone families, 758 cuts and 5,218 preservation comparisons plus fourteen-line DRUP/tamper/boundary fixtures.
- At **0.03 seconds per instance**, frozen-reference corpus: **1,050 OPTIMAL, 2 INFEASIBLE, 1,209 INCOMPLETE**. All 1,052 completed results matched the reference and were consumer-accepted. The incomplete instances are NOT successes. This resource audit overlapped an initial benchmark batch and is not a clean speed measurement.
- Clean one-second benchmark: sixty trials (ten cases, two methods, three repetitions). V43 finished thirty; V45 finished nine (three easy cases), twenty-one were incomplete. First contended timing batch is preserved separately and excluded from clean summary. Twenty single-trial process peak-memory records are separate measurements.
- Two production interaction examples have accepted optimum certificates. Ordinary three-symbol example: one cut, k=2, about 5.01 seconds on this machine. Model-dependent diagnostic: TWO cuts, k=3, about 10.17 seconds. Diagnostic input generation mirrored SAT query order after an initial fixture tie-breaking mistake; history is retained.
- Projection microbenchmark: twenty-four paired records, exact outputs/checksums agree. Shared prefix-store medians were SLOWER than a dictionary-cached direct scanner in all four selected workload comparisons. Repeated computation for already cached masks is avoided, but measured general speedup was not established.
- The faithful teacher dominates runtime: the final ordinary example call enumerated over one million named DFA representations.
- Duplicate-literal normalization in the new DRUP consumer was fixed following AI-assisted review; the regression passes. No teacher optimization was made.

PDF: `output/pdf/Interactive_Partition_Learning_Unchanged_Teacher_V45_EN.pdf` (six pages), with retained Markdown/build/QA/render artifacts. This is a prior report, NOT the requested new full higher-budget article.

### V46: STARTED, NOT FINISHED

`results/2026-11-16/teacher_assessment_v46/` contains new review/proof/literature drafts as they are finalized for this handoff. See its `STATUS.md` for exact files present. These are AI-assisted contributions, not independent peer review. No higher-budget V46 benchmark/corpus run was launched before the user switched to this handoff request. There is no completed V46 final article/PDF or passing extended-test verdict. The next agent must execute the continuation plan rather than imply these tasks already passed.

## Reproducibility and safe continuation

- Use fresh processes for different versions: flat module names such as optimizer/verify/spec can collide in sys.modules. Do not load V43 and V45 in one interpreter.
- V45 `solve_optimal(D, limits)` preserves result fields status, blocks, max_devices, certificate. `solve_profiled` also returns metrics and trace. General proof type is `teacher_cut_drup`; use its own consumer, not V43's.
- Recorded runtime: Windows CPython 3.12.14; local pinned python-sat 1.9.dev22 / Glucose3 and six1.17.0 under `results/2026-11-14/sat_candidate_v37/vendor`. Native binaries are Windows-specific. Provision a matching runtime on another platform and test dependency compatibility before experiments; do not silently alter solver semantics.
- PDF builder dependencies: reportlab, pypdf/pypdfium2, pdfplumber, Pillow; embedded Times fonts currently reference Windows font paths. New paper build should use portable available fonts or document the Windows requirement.
- Frozen scripts often create evidence with open('x'). Never blindly rerun them in their old output directories. V45 experiments.py hardcodes one-second main trials even though --seconds affects worker calls; write a new V46 harness, do not merely change the outer CLI flag and assume limits increased.
- Never overwrite frozen evidence. Validate manifests read-only; old freeze/summarize scripts regenerate their own outputs, so inspect before using them as a purported read-only checker.
- Old selected-last-event Mealy experiments/BGL data are different semantics. The user confirmed no suitable whole-trace AND field data; valid AND field tests remain zero. Do not relabel old data or imply real-device recovery.
- No universal speed/memory ranking, scientific-first novelty or defect-free software proof is established. Formal algorithm proofs are conditional on exact computations and sound complete SAT; finite tests and AI-assisted reviews do not discharge the full software trust base.

## Publication and workspace boundaries

This handoff snapshot publishes research results, source, raw evidence, documents, supplied manuscript copy and final existing PDFs. Unrelated .build dependency churn is intentionally NOT included. Historical root CLIs (partition.py and partition_events.py) are retained for archival continuity; the current interactive entry point is the V45 API, not those old CLIs.

Do not create/fork/transfer chats or message other chats automatically. The user will give this repo/prompt to another agent. Do not archive/delete chats. Subagents were explicitly requested earlier using Terra at low reasoning effort when available; disclose AI review as such and coordinate file ownership. Do not stop solely because suitable field data are unavailable: complete the authorized synthetic/theoretical work and state that limitation.
