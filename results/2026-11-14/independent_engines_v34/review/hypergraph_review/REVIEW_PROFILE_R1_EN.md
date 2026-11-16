# Independent profile review R1: common JSON and hypergraph leaves

Reviewed `certification/IMPLEMENTATION_PROFILE_R1_EN.md`, SHA-256 `F99B909B5D52A5FAD2FF9FD94896B21A147D00B520E5A5A16C66721D130580D4`, against `certification/CERTIFICATE_SPEC_R1_EN.md`, SHA-256 `5EAFCBAD47D93703ED3055959B4164CA3C1FDC5E4689A202FB9E790DDB2DCEF8`, and the previous hypergraph R1 review. Scope is the common strict JSON envelope, limits and responses, and the hypergraph leaf-precedence repair. Logic CNF construction and its specific tree proof are not reviewed here. No implementation, test or benchmark was performed.

## Verdict

**PROVED — hypergraph leaf-precedence repair**, at the level of the mathematical verifier predicate. A bound leaf is first accepted exactly for OPTIMAL when q+|S|≤k, including an already feasible terminal node and empty alphabet. Other bound leaves fail; uncovered requires S=∅ and U≠∅; any other terminal state fails; a nonterminal must have all specified branches. INFEASIBLE cannot use the bound. This resolves the contradictory sentence identified in `REVIEW_R1_EN.md`, and supports its conditional soundness/completeness proof and stated resource bounds. It does not certify counts or uniqueness.

**PROVED — common representation and outcome rules are sufficiently specified for an implementation to be developed and independently audited**, with the scope and limitations below. JSON UTF-8, exact keys, duplicate-key detection after escape decoding, scalar-value strings, exact integer syntax and domain, complete input consumption, independent instance validation, tree and witness shape, no trailing data, and explicit resource failure semantics give a concrete interoperable profile. An accepted certificate is still contingent on implementing and checking the applicable mathematical proof. This approval of the common profile can apply to the logic engineering effort, but does not approve its CNF or logic certificate.

**OPEN — actual parser, checker, proof generation and tests.** No real certificate has been independently verified. Limits must be applied without confusing malformed data with inability to finish parsing: on inability to decide return INCOMPLETE; a detected invalidity can return REJECT. A hard termination can have no response. Producer self-check and consumer independent verification have distinct roles. Input strings in this JSON profile are Unicode scalar sequences, a stated wire-domain restriction; adapters handling a wider host-language string domain must validate or explicitly define a lossless mapping, never silently normalize or change IDs.

**OPEN — fundamental algorithmic independence of the hypergraph solver** as explained in `ADDENDUM_INDEPENDENCE_EN.md`; repairing its certificate does not resolve that gate or authorize its implementation. C028 interface, budget, counts, uniqueness and canonical witnesses remain outside this profile.

## Checks and scope

A branch entry serializes a block as increasing distinct indices and must match the complete list of subsets containing the least remaining index in numeric incidence-vector order. The checker reconstructs R(B) from the separately supplied original instance, rather than trusting coverage labels. At a bound node q+|S| is a valid upper bound because every new nonempty block consumes a distinct remaining symbol. A witness is independently validated before its k is used. S=U=∅ is a legitimate `bound` leaf for an OPTIMAL claim when q≤k and is never an `uncovered` leaf; for INFEASIBLE it cannot be closed. This includes the single empty partition.

`max_nodes=0` yields INCOMPLETE whenever verification requires entering the root, and the limit is independent for producer and checker. On an invalid request a solver returns INVALID_INPUT; a verifier's REJECT denotes failed validation, not mathematical infeasibility. Successful final status requires complete proof and input consumption. Explicit extra input, depth, memory and wall-time limits may prevent a decision and must be surfaced as INCOMPLETE. Arbitrary precision and exact Unicode comparison are part of the trusted implementation obligations, not facts established by this document review.

The profile does not require a polynomial certificate or checker: candidate rows, proof tree, parsing, and reconstruction may be exponential. Future implementation review should verify resource accounting, duplicate-member detection, node limit boundaries, malicious nesting and exact document consumption without conflating rejection with infeasibility.

## توضیح کوتاه فارسی

نمایه ترتیب بررسی برگ‌ها را اصلاح می‌کند و قالب JSON و وضعیت‌های خطا را برای پیاده‌سازی مشخص کرده است. این تأیید ریاضی و مشخصاتی است؛ بررسی‌کنندهٔ واقعی هنوز ساخته و ارزیابی نشده و استقلال بنیادی موتور ابرگراف همچنان باز است.
