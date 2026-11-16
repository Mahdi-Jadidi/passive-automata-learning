# V34 logic certificate milestone

The standalone logic engine now returns one maximum-block compatible partition with a checkable proof that no larger compatible partition exists, or a checkable infeasibility proof. The independent checker reconstructs constraints from the original instance and checks the complete refutation tree. This is an implemented, independently audited experimental milestone, with a bounded audit PASS; finite tests do not prove the entire implementation correct.

The manager used three GPT-6.1 Terra subagents at reasoning effort low, the available setting corresponding to the user's request for Terra light. The historical chats were inspected and observed idle; separate subagent folder ownership prevented competing writes.

## Delivered artifacts

- Solver: [implementation/logic/solver.py](implementation/logic/solver.py), with invocation and limits in its [README](implementation/logic/README.md).
- Independently authored checker: [implementation/checker/checker.py](implementation/checker/checker.py), with its [README](implementation/checker/README.md). It imports neither solver code nor prior partition engines.
- [Certificate specification](certification/CERTIFICATE_SPEC_R1_EN.md) and [deterministic JSON/CNF profile](certification/IMPLEMENTATION_PROFILE_R1_EN.md).
- [Implementation gate](LOGIC_IMPLEMENTATION_GATE.md), issued after the independent mathematical/profile reviews and before solver implementation or tests.
- [Independent audit report](audit/logic_milestone/AUDIT_REPORT_EN.md), [raw final evidence](audit/logic_milestone/audit_raw.jsonl), [oracle](audit/logic_milestone/oracle.py), and [audit runner](audit/logic_milestone/run_audit.py).
- [Source repair review](review/logic_review/IMPLEMENTATION_REVIEW_R1_EN.md); original source and earlier reviews/runs remain preserved.

## Validation and exact scope

On bundled Python 3.12.14, the final audit recorded **99 passing checks** plus one source-metadata record. It includes 39 solver comparisons against an independent recursive-insertion partition oracle, 39 independent certificate acceptances, and 21 targeted checks of tampered proofs/witnesses, instance binding, malformed input, exact integer limits and interrupted verification. Each subprocess had a 10-second audit timeout; none timed out. This timeout is an audit safeguard, not a runtime benchmark.

A source-review defect was repaired: parser recursion exhaustion now yields INCOMPLETE rather than INVALID_INPUT. The earlier source is retained under implementation/logic/history/. A separate failed audit expectation at JSON depth 1500 was a fixture error; the runtime parsed that value and correctly rejected its invalid envelope. All earlier logs, including that failure, are retained and explained in the audit report. The final source and audit were frozen after the repair.

Frozen final SHA-256:

| Artifact | SHA-256 |
| --- | --- |
| Solver | `8DDB5F63189DC24BAC7C267A92B75A6546D069E8AF935C2C1257B0CE4FB85EC6` |
| Checker | `69B56873D04654C14EC02515C7CF145D5D46960958EE8163A2F718BE78E239A3` |
| Audit report | `676991A891D1949B49E23DC124216C72E77DF030B5FA736F8F9E0AA83EED4DCA` |
| Final raw audit | `F7AAD7CE044DE3155A753C7E5FBED16C3C3454C753C1BFD2FF1DF90F91F1112D` |

This API uses alphabet, positive, negative. It supplies one optimum, without promising the canonical optimum. It does not return C, O, uniqueness or first-two witnesses and is not the historical C028 API, which uses Sigma, P, N. max_nodes limits Boolean-search/proof work and does not implement C028 max_candidates. Full counting and prefix-budget semantics remain separate work. CNF construction, search, proof output and verification can grow exponentially; documented implementation caps can return INCOMPLETE. Hard process termination can produce no response. No speed, novelty, public-default, or physical-ownership claim follows. No benchmark or publication/push was performed.

## Hypergraph decision and remaining work

The mixed-cover formulation and certificate argument are mathematically sound under the reviewed assumptions, including the profile's bound-first leaf rule. However, all remaining symbols have equal candidate-row degree, so minimum-degree branching always chooses the least remaining symbol. The proposed search is structurally anchored block enumeration. A separate implementation could avoid importing old solvers, but fundamental algorithmic distinction remains **OPEN**. See the [independence addendum](review/hypergraph_review/ADDENDUM_INDEPENDENCE_EN.md). No hypergraph solver was implemented.

The next research decision is whether to redesign the hypergraph algorithm to meet that stronger distinction, or to pursue a separately specified full-output extension of the logic engine. Neither should be silently reported as completed by this milestone. Original frozen designs, historical results and public entrypoints remain unchanged.

## توضیح فارسی

موتور منطقی مستقل و بررسی‌کنندهٔ جداگانه ساخته شدند و همهٔ ۹۹ بررسی نهایی گذشتند. خروجی این مرحله فقط یک جواب بهینه با گواه قابل بررسی یا گواه ناسازگاری است؛ شمارش کامل و بازیابی مالکیت واقعی ادعا نشده‌اند. مسیر ابرگراف به‌دلیل شباهت بنیادی جست‌وجوی آن به شمارش بلوک‌های لنگردار همچنان باز است.
