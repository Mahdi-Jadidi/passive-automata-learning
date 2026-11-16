# Scoped logic implementation authorization

The coordinating manager authorizes independent implementation and a subsequent correctness/certificate audit of the separate V34 logic milestone. This decision follows independent mathematical approval and is within the user's request to continue the project. No solver code, solver tests or benchmarks were run before this decision.

Approved specification composition:

- Original logic design SHA-256 7223A0B5F50DB30A1C0F96ECBA9C42FC6BF9BA03DB54766AB36304DA190EB855.
- certification/CERTIFICATE_SPEC_R1_EN.md SHA-256 5EAFCBAD47D93703ED3055959B4164CA3C1FDC5E4689A202FB9E790DDB2DCEF8.
- certification/IMPLEMENTATION_PROFILE_R1_EN.md SHA-256 F99B909B5D52A5FAD2FF9FD94896B21A147D00B520E5A5A16C66721D130580D4; this profile resolves prior naming/folding and wire ambiguities and takes precedence where stated.
- Independent logic profile review SHA-256 234CE01A1BED49BE57544E6E3AF3EEC9B89699B75E0FB7DDD8C0D8D07DCFC789.
- Independent common-envelope review SHA-256 788D40A517179239125FADD60CA020DFF58B0F222E683ED5E1ECDAE0E919F1A9.

Scope: one compatible partition maximizing block count with independently checkable feasibility and exhaustive optimality proof, or independently checkable infeasibility proof. Use standalone CNF Boolean search; do not call/import/dispatch to any historical partition engine. Develop the independent checker in a separate owned directory without importing solver code. The checker rebuilds the formula from the original instance and validates the complete tree. Use the frozen reference only as a disclosed audit oracle, if needed.

This is authorization to implement and audit, not a claim that an implementation has passed. Full C028 schema, C/O counts, canonical witnesses, max_candidates semantics, novelty, speed comparisons and physical truth remain outside this milestone. Hypergraph implementation is not authorized because fundamental algorithmic independence remains OPEN. Historical results and the original frozen V34 documents must remain unchanged.

Writer ownership: solver author implementation/logic/; independent checker author implementation/checker/; audit author audit/logic_milestone/. Each author records dependencies, costs, limits and actual outcomes. No benchmark or public default change is authorized. Failures and raw audit evidence must be preserved. Manager integration follows independent source and operational checks.
