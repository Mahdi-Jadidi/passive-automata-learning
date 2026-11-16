# Independent solver source review — frozen initial implementation

## Scope and frozen files

- `implementation/logic/solver.py`: SHA-256 `63A78CE50E5AAEFEB2F703C6AEB026E9B5AD1FB93F1D53E087AE80D24A24D52D`.
- `implementation/logic/README.md`: SHA-256 `586D4F9A999C813D8A84C6CC477D6EF1318609623374565FA9443ED34CEA6FA4`.
- Bound implementation profile: `F99B909B5D52A5FAD2FF9FD94896B21A147D00B520E5A5A16C66721D130580D4`; certificate spec: `5EAFCBAD47D93703ED3055959B4164CA3C1FDC5E4689A202FB9E790DDB2DCEF8`.

Read-only source review of logic milestone only; no code changes or benchmarks. This review does not replace the independently commissioned functional and certificate audit. The author and independent checker are different writers; reviewer authored the latter and makes no claim of its independent operational audit here.

## Finding requiring repair

**REFUTED-SPECIFIC — parser recursion exhaustion is reported as INVALID_INPUT.** `parse_json` catches `RecursionError` together with malformed UTF-8 and JSON, then converts it to `Invalid`. Exceeding the JSON parser's recursion limit can prevent determining whether the document is valid; the profile explicitly requires INCOMPLETE when resource or nesting limits prevent a decision. Even if subsequent schema checking would reject a deeply nested value, that is not known at the point parsing aborts. Propagate `RecursionError` to the outer INCOMPLETE handler, and preserve malformed input rejection when malformedness is actually established. Recheck the frozen source after repair; this finding is not a claim of an unsound optimum proof.

## Scoped observations

**PASS — proof generation and objective, source-level reasoning.** The clause scan returns a conflict only when an unsatisfied clause has no unassigned literals; both values of a selected unassigned variable are explored before creating an UNSAT split. When all clauses are satisfied, the returned partial model satisfies them under every extension; the assignment clauses enforce a unique true slot for each symbol. Thresholds descend from m, so on the first SAT result the immediately preceding UNSAT tree is for k+1, while a first SAT result at m gets the explicitly rebuilt empty-clause bound at m+1. If no threshold is SAT, the last tree refutes F_0. The code directly validates the decoded witness and checks the proof against constructed clauses before an exact return. These are static observations, not tested or formal verification.

**PASS — profile expression structure as inspected.** Owner naming, left-associated operations, no operator constant folding, distinct gate variables and alias-aware truth tables correspond to the profile. Active and equality output aliases remain leaves; complete clause equivalences and threshold subsets are generated. Variable, clause and search caps can lead to INCOMPLETE without an exact claim. CNF and trees can be exponential, and these caps may prevent completion even on valid inputs.

**OPEN — independent assurance and complete operational conformance.** The solver's internal checker shares its own builder and cannot independently establish correct reconstruction. A separately built verifier must validate returned certificates against the original instance and profile. Functional oracle comparisons, malformed input and interruptions, named-gate interoperability, large-number behavior and actual source/dependency audit require the pending audit; no passing results are inferred here. `max_nodes` also caps discovery search and is documented as stricter than final-tree size; it is not the C028 prefix budget. Full C028, counts, canonicality, hypergraph and performance are outside this review.

## توضیح فارسی
جست‌وجو و ساخت درخت گواه در بررسی کد با منطق طرح سازگار دیده شدند، اما سرریز عمق تجزیهٔ JSON به‌اشتباه INVALID_INPUT گزارش می‌شود و باید INCOMPLETE باشد. این بررسی جانشین ممیزی اجرایی و بررسی گواه با ابزار مستقل نیست.
