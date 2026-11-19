# Independence addendum — hypergraph branching

This addendum preserves `REVIEW_R0_EN.md` unchanged and qualifies its design-independence verdict. It concerns `hypergraph/DESIGN_PROOFS_EN.md`, SHA-256 `648E2291E00DEDCD8304578BB324C967C821568AB0FE11FE441DDD71281088CC`, and `hypergraph/INDEPENDENCE.md`, SHA-256 `E87FE9C29744BC72BACC6922DDCE3F0D751D3B0F8E1A6C1ADB0BDC29FAB42527`.

## Degeneracy of the proposed degree choice

At a node with nonempty uncovered set S of size s, the design defines available rows to be **all** nonempty subsets of S. For each symbol a in S, precisely 2^(s−1) such rows contain a: choose any subset of S without a and add a. Thus every symbol has equal degree. The specified declared-order tie break therefore always chooses the least declared symbol of S. This is true irrespective of uncovered negatives U, because availability does not filter rows using U. The optional union-coverage prune may end a node but does not change this equality at any node that branches. The minimum-degree rule consequently cannot dynamically choose a different symbol in this formulation.

## Relationship to anchored subset recursion

At an unpruned node, the algorithm chooses a = min(S), iterates over every B ⊆ S with a ∈ B, and recurses on S minus B with uncovered negatives updated to U minus R(B). This is the same anchored block-choice recurrence structure as an exhaustive partition search anchored at the least remaining symbol, and the state transition underlying an anchored coverage-state subset DP. It enumerates paths and emits leaves, whereas a subset DP typically combines values associated with repeated states and may memoize them; identical branch structure alone does not prove identical code, resource use, or all output procedures. The hypergraph incidence vocabulary and coverage-union pruning do not establish a fundamentally different branching structure. This observation does not invalidate the mixed-cover bijection, unique histories, or exhaustion proofs in R0.

## Scoped independence verdict

**PROVED, conditional design-level non-invocation:** the pseudocode does not itself call, import, dispatch to, or fall back to the named previous implementations. Computing RGS solely to order emitted witnesses is not generating the search via an RGS enumerator. **OPEN, actual implementation independence:** no executable code or complete dependency record is available for inspection. **OPEN, stringent fundamental-independence requirement:** the handoff requests a fundamental independent method rather than an acceleration or dispatcher for old RGS/DP/hybrid methods. Although this design need not invoke an old solver and is not literally a memoized DP, its central branch decomposition is the same least-symbol anchored subset recursion underlying the prior DP foundation. On the supplied evidence, a separate representation and independent implementation do not establish the intended fundamentally distinct solving principle. The manager must decide whether that structural overlap is acceptable under the user's requirement; no claim is made that all hypergraph-based methods, all exact-cover searches, or every adaptation must have this overlap.

A future repair should state a mathematically precise distinction in search principle and state space, not just rename the same recurrence or replace its container. Review any new algorithm and dependencies against the unchanged contract, with new hashes. No solver code, tests, or benchmark were produced for this addendum.

## توضیح کوتاه فارسی

چون همهٔ زیرمجموعه‌های ناتهی نمادهای باقی‌مانده ردیف هستند، درجهٔ همهٔ نمادها برابر است و قاعده همواره کوچک‌ترین نماد را انتخاب می‌کند. بنابراین شاخه‌بندی همان انتخاب بلوکِ حاوی کوچک‌ترین نماد در بازگشت زیرمجموعه‌ای است. فراخوانی‌نکردن کد قدیمی به‌تنهایی تمایز بنیادی الگوریتم را ثابت نمی‌کند؛ این شرط در سطح سخت‌گیرانه باز می‌ماند.
