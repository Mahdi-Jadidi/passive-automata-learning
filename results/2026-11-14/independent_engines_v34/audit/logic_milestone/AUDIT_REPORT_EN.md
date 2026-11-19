# Independent logic milestone audit

**Verdict: PASS for the bounded checks below, not a proof of implementation correctness.** Audit is limited to one optimum and its feasibility/optimality certificate or infeasibility certificate. It does not establish C028 counts, canonical witnesses, budget semantics, performance, physical ownership, or hypergraph independence. No benchmark or proof-assistant verification was performed.

## Frozen sources and evidence

- Solver `implementation/logic/solver.py`: SHA-256 `8DDB5F63189DC24BAC7C267A92B75A6546D069E8AF935C2C1257B0CE4FB85EC6`.
- Independent checker `implementation/checker/checker.py`: SHA-256 `69B56873D04654C14EC02515C7CF145D5D46960958EE8163A2F718BE78E239A3`.
- Audit `oracle.py`: `12C7E587D5D99BBEC7E64777A1A10597D0D27DE82C6F624CD9E2C690A9741049`; `run_audit.py`: `9DEA9E5F10A1CE1A4A5F9FD9F2401C17884A81BBEFC6BFD47EB7A0675082EE14`.
- Final `audit_raw.jsonl`: `F7AAD7CE044DE3155A753C7E5FBED16C3C3454C753C1BFD2FF1DF90F91F1112D`. Each record contains actual subprocess response or timeout; first record is source metadata, not a check.

Final run produced 100 records: one metadata record and **99 passing check records**. Each CLI process was bounded by a 10-second subprocess timeout; none timed out. The independent oracle recursively inserts each alphabet index into existing blocks or a new block, checks projection compatibility directly, and computes the maximum; it imports no engine, CNF builder, checker or historical oracle. The corpus has 27 ternary labelings of ε, a and b over a two-symbol alphabet, plus 12 targeted cases. All 39 solver answers matched oracle feasibility and optimum size, and every returned certificate was accepted by the independent checker: 78 passing records. Targeted cases include empty alphabets and words, empty labels, contradiction, duplicate words, repeated IDs/order sensitivity, unused IDs, multi-character atomic IDs and distinct composed/decomposed Unicode forms, and the three-symbol tied-optimum case.

The remaining 21 checks cover proof and witness tampering, rebinding a valid optimum proof to a contradictory instance, malformed and duplicate-key raw JSON including otherwise-valid envelopes, trailing data, Boolean and exponent node limits, a 4401-digit integer limit, interrupted solver and checker cases, and full schema validation before contradiction. Checker limits 0 and 54 returned INCOMPLETE and limit 55 ACCEPT for a 55-node certificate. A deeply nested syntactically valid JSON value exceeded parsing resources and returned INCOMPLETE for both processes. These are bounded examples, not an exhaustive schema or adversarial-parser audit.

## Source review and limitations

The checker uses Python standard library only and imports neither solver nor old solving engines. It validates the original instance and witness, reconstructs the formula and named gates, then checks each branch and conflict from the rebuilt clauses. The implementation's handling of logic certificates and resource outcomes was inspected against the profile; the checker deliberately returns INCOMPLETE for the out-of-scope hypergraph kind. A separate reviewer inspected the solver. No claim that finite tests exclude shared conceptual mistakes or prove parser correctness is made. Potentially huge CNF construction and proof trees, bounded memory/recursion and process-level hard termination can prevent a result.

## Preserved earlier runs

- `audit_raw_prerepair.jsonl` SHA-256 `96051ACE173CF761736FD48BE231CA36B97E09844C94C677B673367DAE97C315`: 82 partial passing records on the pre-parser-fix solver; the run was stopped and is not the final verdict.
- `audit_raw_depth1500.jsonl` SHA-256 `00D752CDAC0B639105567303547093CE2BB1E4FD0B048FA269203AF70C695EA2`: 96 records, one failed **audit expectation**. The 1500-deep JSON parsed successfully on this runtime and its invalid top-level array correctly returned INVALID_INPUT; expecting INCOMPLETE was unjustified. The fixture was increased to 10000 levels to reach the parser resource limit. This was not a newly found solver failure.
- `audit_raw_before_expansion.jsonl` SHA-256 `AF2B6790EA53567C93211A81399B5C67B54E9334C380FBEA77DCA604E153E1F0`: 96 records all passing. The final run added four targeted checks because earlier duplicate-key fixtures also had invalid envelopes, so rejection alone would not establish detection of duplicates in an otherwise-valid request; the final checks use valid envelopes and include verifier Boolean/exponent limits.

The pre-freeze solver's parsing-depth classification was separately identified and corrected by its author before this final frozen source; no source files owned by the authors were modified in this audit.

## توضیح کوتاه فارسی

در ۳۹ نمونه، بهینگی یا ناسازگاری با افرازساز مستقل مقایسه شد و گواه‌های خروجی را بررسی‌کنندهٔ جداگانه پذیرفت. همهٔ ۹۹ بررسی نهایی گذشتند؛ این نتیجه محدود به همین نمونه‌ها و تعهد یک جواب و گواه است و اثبات درستی کل پیاده‌سازی نیست.
