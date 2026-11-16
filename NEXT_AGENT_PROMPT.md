# Copy this prompt to the next agent

Continue this repository's research from the actual current checkpoint, without restarting or relying on prior chat access.

Repository: https://github.com/Mahdi-Jadidi/passive-automata-learning
Branch: `codex/teacher-handoff-v46` (the default `main` branch is older; explicitly check out this branch).

Read these in order:
1. `AGENTS.md`
2. `HANDOFF_NEXT_AGENT_2026-11-16.md` — current status, numbers, constraints, trust boundaries and incomplete work. The 2026-11-14 handoff is historical and is NOT the current task scope.
3. `docs/ALGORITHM_NOTATION.md`
4. `docs/CONTINUATION_PLAN_V46.md` — the concrete next steps, budgets, experiments, proof obligations and deliverables.
5. `results/2026-11-16/interactive_teacher_v45/README.md`, `PROOF.md`, `TEACHER_CONFORMANCE.md`, and actual code; its `sources/main.pdf` is the supplied manuscript.
6. V43/V44 evidence and `teacher_assessment_v46/STATUS.md` with its review/proof/literature drafts.

The user's current request is:

«نیاز نیست تیچر رو قوی کنیم. لیمیت زمانی رو بیشتر کن و الگوریتم رو تست کن. بعد که همه چی خوب بود یکبار از پایه بررسی کن و مطمئن شو همه چی خوبه. بعد یک داکیومنت در قالب مقالهٔ انگلیسی بده که هر بخش الگوریتم، نوآوری، ویژگی‌ها و کارهای انجام‌شده را توضیح بده و اثبات دقیق و کامل الگوریتم را داشته باشد؛ دقیقاً مثل یک مقاله. در آخر پیشنهادهایی برای قوی کردن تیچر بده.»

Execute the continuation plan autonomously. Do NOT strengthen/replace/internally optimize the teacher now, and do NOT implement the previously proposed fast adapter. Preserve the faithful V45 teacher and supplied main.pdf; suggestions go at the END of the final paper only. Any future teacher algorithm change requires explicit user approval. Caller-selected sufficient trie bounds are already proved equivalent for our unrestricted-state sample problem; they are not a new device-state assumption.

Task: given D=(S_plus,S_minus) over declared ordered Sigma, return ONE compatible alphabet partition maximizing its block count with a checkable optimum certificate. No state bound in the mathematical objective, no DFA-learning/counting-all-optima requirement, no heuristic answers and no physical-recovery guarantee. Follow the manuscript naming map. Retain unused opaque event IDs. A resource timeout is INCOMPLETE, not REJECT or infeasibility, and cannot generate a new cut from an unfinished teacher check.

V45 is operational and has accepted one-cut and two-cut diagnostic optimum certificates. It proposes a relaxation maximum, asks the unchanged exact teacher, learns a witnessed generalized false-cover cut on a completed no, and repeats. It does NOT eagerly mine all minimal witnesses or fall back to V43. However, the teacher's exhaustive DFA enumeration is a serious bottleneck, and the prefix-DAG projection microbenchmarks were slower than a dictionary-cached scanner. Preserve these negative results. In the 0.03-second corpus run, 1,052/2,261 results completed correctly and 1,209 were incomplete. At one second V45 completed three of ten fixed benchmark cases; V43 completed all ten. No higher-budget V46 benchmark was executed before this handoff. Do not claim those future tests already passed.

Use new result files/output directories; frozen scripts often use exclusive creation and some parent harnesses hardcode budgets. Follow the plan's 0.25-second full-corpus audit, 60-second sequential fresh-process benchmark/fixtures and at most two explicit 300-second diagnostic escalations. Record actual worker limits, hashes, native/Python environment, counters, verification and censored outcomes. Avoid concurrent heavy work while measuring timings. Test the same one-optimum-plus-checked-proof contract. Use separate processes per version because flat module names collide.

After experiments, review from first principles, not just test counts. Complete the exact lemmas/theorems, check correspondence to code/main.pdf, replay certificates and adversarial mutations, and document shared trusted encoder/normalization code. Existing V46 drafts are AI-assisted, not peer review or formal verification. If a test fails, preserve evidence and resolve/report it; do not assert that everything is good merely because time limits increased. Do not spend indefinitely on infeasible-to-finish enumeration: retain bounded INCOMPLETE results and finish the honest paper.

Deliver a full standalone English research paper with complete proofs, all algorithm components/pseudocode, precise innovation positioning against primary sources, exact complexity, reproducible methods/results (including negative and incomplete cases), limitations and an ending section of teacher-strengthening proposals. Keep source, references, scripts, raw evidence, configs, manifest and page QA in the repo; deliver a NEW PDF after inspecting every page. Do not overwrite V44/V45 papers. User confirmed no suitable real AND-model whole-trace data exist, so valid field trials remain zero; do not relabel old BGL/selected-output data.

Use available Terra subagents with low effort if supported and helpful, as previously requested; coordinate ownership and label AI-assisted review honestly. Do not automatically create/fork/transfer chats, message other chats, or archive/delete chats. The user is handing this repo to you manually. Keep the user informed during long runs.

The repository contains a historical .build dependency tree; unrelated local changes there are not algorithm results and must not be staged. This delivery branch contains the research snapshot; do not reset or rewrite unrelated work. Do not promise universal speedup, scientific-first novelty or defect-free software from bounded tests. Finish authorized testing, review and paper work rather than stopping at another plan.
