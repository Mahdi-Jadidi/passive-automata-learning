# Solver implementation review R1 — parser repair

## Frozen evidence

- Corrected `implementation/logic/solver.py`: SHA-256 `8DDB5F63189DC24BAC7C267A92B75A6546D069E8AF935C2C1257B0CE4FB85EC6`.
- Corrected `implementation/logic/README.md`: SHA-256 `67F693CD35D08CFE1718727E4E97BE82C9E88E3B43261F919B3ECA15C6EDB830`.
- Preserved `implementation/logic/history/solver_pre_parser_fix.py`: SHA-256 `63A78CE50E5AAEFEB2F703C6AEB026E9B5AD1FB93F1D53E087AE80D24A24D52D`.
- R0 review: `review/logic_review/IMPLEMENTATION_REVIEW_EN.md`, SHA-256 `09457BF1268F909FB0891E6379E983331F1296468CF4615A9AFC8D4EE89D2DC9`.

## Scoped result

**PASS — previously identified parser exhaustion defect repaired in source.** The diff removes `RecursionError` from `parse_json`'s malformed-input conversion; it propagates to `main`'s resource handler and returns INCOMPLETE rather than INVALID_INPUT. Actual Unicode and JSON decoding errors continue to map to INVALID_INPUT. Source comparison shows no changes to CNF construction, proof search, objective handling or internal proof check.

**PASS — caught keyboard interruption in the scoped handlers.** `KeyboardInterrupt` now maps to INCOMPLETE in both `solve` and `main` while processing the request; this cannot guarantee a response for hard termination or interruption during final output. Neither interruption behavior nor a resource failure implies infeasibility.

**OPEN — independent operational assurance.** This is a source-level, hash-bound repair review only. The pending independent audit must establish actual runtime behavior and independently check certificates and malformed inputs. Exact counts, full C028 compatibility, hypergraph, performance and physical ownership remain outside scope. No tests or benchmarks were run for this focused diff review.

## توضیح فارسی
ایراد گزارش‌شده در کد اصلاح شده است: سرریز عمق تجزیه به INCOMPLETE می‌رسد و ورودی واقعاً نامعتبر همچنان INVALID_INPUT است. ارزیابی اجرایی مستقل جداگانه در حال انجام است.
