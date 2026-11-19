# Exact partition learning from finite observations — C028

## Result and scope

An exhaustive reference algorithm returns a globally maximum-block partition compatible with the supplied finite observations, exact counts of all compatible partitions and of optimal partitions, and replayable factor witnesses. It uses no supplied K or target machine. The answer is exact for the declared sample and model if the computation completes. The exhaustive method may require impractical time or memory; finite-input mathematical termination assumes sufficient resources. It does not establish correct predictions on unseen words or recover the physical ownership or original factor count.

The model is a finite explicitly declared alphabet and finitely many finite full-word positive and negative labels, with independent disjoint regular factors and AND acceptance, noiseless observations, and no state bound. It covers epsilon, empty samples, unused alphabet IDs and contradictory samples. It does not claim to cover all log semantics, noise, bounded-state or prefix-closed factors, infinite input, or physical-device identity. "Best" means maximum number of nonempty blocks, not a probability or physical confidence. Counts refer to distinct partitions, not machines.

A unique optimal proposal can coexist with multiple compatible partitions. For example, with alphabet [a,b], positive [epsilon], negative [a], both {a}|{b} and {a,b} fit, but only the two-block partition maximizes the number of blocks. More fundamentally, one universal factor on {a,b} and two universal singleton factors generate exactly the same full language, so even unlimited membership data cannot distinguish these physical partitions under the unconstrained model. If the actual system satisfies the stated model and there is exactly one compatible partition, its partition is conditionally determined within that model; device names and machine implementations are not.

## Input, output, and usage

The concrete API accepts one record with exactly `alphabet`, `positive`, `negative`; each alphabet ID is a distinct nonempty string and each word is an array of whole IDs. `[]` is epsilon. IDs are not split into characters. Input alphabet order supplies canonical ordering; duplicate traces within a label are removed in first-occurrence order. The empty alphabet has one empty partition, and its empty conjunction accepts epsilon, so it is compatible exactly when the negative list is empty.

From the workspace root in PowerShell, the standalone **library** entry point can be exercised as follows (adjust the Python path if necessary):

```powershell
& 'C:/Users/Mahdi/AppData/Local/Python/pythoncore-3.14-64/python.exe' -c 'import importlib.util,json; s=importlib.util.spec_from_file_location("ref", "results/2026-11-11/exact_foundations_v28/implementation/reference.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); data={"alphabet":["door.open","µ sensor"],"positive":[[]],"negative":[["door.open"]]}; print(json.dumps(m.solve(data),ensure_ascii=False,indent=2))'
```

On completed runs, `INCOMPATIBLE`, `UNIQUE_COMPATIBLE`, and `AMBIGUOUS` classify the full compatible family; `optimal_unique` classifies its maximum-block subset. The canonical recommendation is the lexicographically least optimal restricted-growth string in alphabet order; this deterministic tie break is not a confidence measure. Each witness records its blocks, the finite projected-positive language per block, and a rejecting block index per *deduplicated* negative, in first-occurrence order. These witnesses can be replayed without hidden truth metadata.

`INVALID_INPUT` is reserved for malformed schema or unknown/invalid IDs. A well-formed word carrying both labels is `INCOMPATIBLE`. `INCOMPLETE` on candidate-budget exhaustion, interrupt or resource exhaustion, and `ERROR` on failed internal witness verification, have null mathematical result fields. A timeout or budget is never interpreted as a property of the data. The optional Python argument `max_candidates` is a computation limit; it is not a K, state, alphabet, trace-count or trace-length cap and cannot certify partial counts.

## Algorithm and proof dependencies

Full pseudocode is in `PSEUDOCODE.md`. It validates the whole input, enumerates each partition exactly once by canonical restricted-growth string (RGS), tests each using projections, and retains exact arbitrary-precision counters plus up to two witnesses for each relevant family. It resets the optimal counter and optimal witnesses whenever a strictly better number of blocks appears. It performs no greedy merge, forced-atom inference, DP, pruning, or sampling.

| Claim | Dependency / argument |
|---|---|
| Validation and normalization | Finite type and membership scans reject malformed records; first-occurrence deduplication preserves the label sets. A word in both sets is a direct contradiction. |
| Projection criterion | Every consistent factor must contain the projections of all positives; each negative must have one block whose projection matches none of them. Conversely the finite projected-positive languages are regular and realize every partition satisfying that condition. |
| Enumeration | First-occurrence block labeling and RGS decoding are inverse maps; the empty RGS covers the empty alphabet. Thus every partition is visited exactly once. |
| Compatibility | The direct evaluator checks the projection condition for every negative against every positive, with the same block required for all positives of that negative. |
| Maximum, ties, counts | Enumeration and counter invariants count every compatible partition once; the reset/equal rules count exactly all maximizers, and lexicographic order selects the canonical optimum. |
| Witnesses | Projected-positive finite languages accept all positives, and each stored negative-block index exhibits rejection. The serialization and normalized index order are fixed in amendment 2. |
| Termination | A finite alphabet has finitely many partitions, and each projection check is finite. The proof assumes enough time and storage and gives no practical bound. |
| Failures and interruption | Malformed data, contradiction, incomplete execution and witness-verification errors have separate outcomes; a partial search never certifies a count, maximum, or uniqueness. |

A minimal quantifier counterexample is alphabet [a,b], positives [a] and [b], negative [a,b]. Each positive differs from the negative on some singleton block, but neither singleton distinguishes that negative from *both* positives. The singleton partition fails, while the oneblock partition fits. Compatible-cut intersection and merge-only update failures are separately replayed in the audit. Proofs and scope are in `theory/SPEC.md`, `theory/PROOFS.md`, and amendments 1–2; older documents are read together with those additive amendments.

## Review and experimental evidence

The mathematical specification, proof and pseudocode were reviewed by a separate coordinated AI agent, followed by an independent AI audit of the frozen implementation. These are not a human proof review or a formal proof-assistant verification. Proof and amendment 1 review preceded provider implementation; source was frozen before independent testing. The original reviewed specification required first-occurrence deduplication but did not explicitly define the serialized witness index domain. Amendment 2 subsequently and prospectively clarified that domain; it did not change the provider. Review verdicts are under `review/`, source freeze under `implementation/FREEZE.md`, and the detailed test evidence under `audit/`. The frozen `implementation/reference.py` SHA-256 is `5f60b27447b37ec07f1fd6bce75be6199b898573d4b32e90413e900e3a615a94`.

The independent oracle generates set partitions by symbol insertion rather than the provider's RGS generation and independently checks witnesses and counts. The final audit passed 2,187 exhaustive three-way labelings of the seven words of length at most two over a two-symbol alphabet, 60 seeded cases over alphabets of sizes 3–8, 19 edge records, 11 malformed-schema controls, and three withheld-DFA sample controls. It also checked renaming, reordering, deduplication, a changing optimal recommendation after sample extension, and budget behavior including a 1,200-ID incomplete case. For the exhaustive fixtures, maximum raw trace count was 7 and ID length 1; for seeded fixtures, maximum raw trace count was 26, word length 8 symbols, and ID length 5; the schema-shaped edge records reached word length 10,000, raw trace count 4, alphabet size 8 and ID length 7. The 1,200-ID budget case is a separate interruption control, not a completed large-alphabet exact solve. These are observed fixture limits, not theoretical input restrictions or an all-finite-input empirical test.

An initial audit run failed in the *checker*: it compared witness indices to raw duplicate negatives instead of the implementation's deduplicated list. The original specification prescribed deduplication but left the serialized witness index domain implicit; amendment 2 clarified that convention prospectively. The original failure is retained in `audit/audit_stderr_v1.txt`; the checker was repaired and the successful rerun is retained as v2. The candidate source and expected mathematical outcomes did not change. The successful audit and its commands, fixture hashes, environment (Windows 11 and CPython 3.14.6), and exact results are in `audit/AUDIT_REPORT_V2.md`, `audit/INDEPENDENT_AUDIT_RESULTS_V2.json`, and `audit/AUDIT_MANIFEST_V2.json`. After amendment 2 was reviewed, the full suite was run again against the unchanged frozen source; the successful final captures are `audit/audit_stdout_v4.txt` and `audit/audit_stderr_v4.txt`. The audit proves no general runtime bound and tests do not replace the mathematical proof.

Biggest overlooked point? An exact, uniquely optimal sample recommendation can still coexist with different compatible physical generators; a deterministic RGS choice is not evidence of which physical generator produced the data.



