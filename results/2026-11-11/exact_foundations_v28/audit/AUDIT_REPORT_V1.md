# C028 independent audit report v1

## Finding

**PASS for the frozen finite reference implementation on the specified contract.** The implementation agreed with an independently written set-insertion oracle on every tested record, including exact compatible and optimal counts, all-K status, canonical least optimal RGS, the retained witness RGS lists, and direct replay of every returned finite-factor and negative-rejection witness. No implementation defect was found.

This finite experiment does not establish correctness for every finite input. General correctness and mathematical termination follow from the reviewed proof and exhaustive RGS argument. The implementation makes no practical completion or finite-resource guarantee; its optional candidate budget returns `INCOMPLETE` with null mathematical fields.

The claim concerns sample-compatible behavior under independent disjoint regular factors and full-word labels. It does not identify the physical ownership partition. The withheld-DFA controls assert that each generating partition fits its samples; they do not expect the recommendation to recover it.

## Independent method and coverage

The oracle enumerates set partitions by recursively inserting each next symbol into an existing block or a new block. This is independent of the provider's iterative RGS generator. It computes canonical RGS only after a partition is generated and projects words as tuples of atomic IDs.

- 2,187 exhaustive three-way labelings of all seven words over `{a,b}` of length at most two.
- 60 deterministic seeded cases, ten per alphabet size 3–8.
- 19 edge records: empty alphabet/product, epsilon, empty positive/negative sets, unused symbols, quantifier counterexample, C026 counterexamples, opaque/multicharacter/Unicode/punctuation IDs, raw-concatenation collision trap, duplicate traces, contradiction, a 10,000-symbol long trace, and a sparse 8-symbol case. The empty-ID record was correctly classified `INVALID_INPUT`.
- 11 malformed-schema controls, each returned `INVALID_INPUT`.
- Three finite samples generated from withheld independent DFA factors with mixed factor counts and state counts. The targets were not passed to the solver; only the generated positive and negative samples were. The true partitions were independently checked for sample compatibility.
- Metamorphic checks for injective symbol renaming, positive/negative input ordering, within-label deduplication, and a sample extension. In the extension fixture, the maximum stayed at two while the canonical optimum changed from `[0,0,1]` to `[0,1,0]`.
- A 1,200-ID run with candidate budget one returned `INCOMPLETE` with null counts. Source review confirmed iterative RGS generation, so no recursion is performed per alphabet symbol.
- Candidate-budget controls checked incomplete output after partial enumeration and completed output at an exact Bell(3)=5 candidate budget.

All successful comparisons had zero mismatches and zero witness replay failures. See `INDEPENDENT_AUDIT_RESULTS_V1.json` and the captured successful stdout/stderr.

## Freeze and commands

Proof review and amendment review were approved before implementation testing. Raw source hashes were checked against the freeze and verdict: `reference.py` SHA-256 `5f60b27447b37ec07f1fd6bce75be6199b898573d4b32e90413e900e3a615a94`; SPEC `c42eedb77ee7f78aa0303fc4d568b73f24c547cfbf82a8a615688ffbf067d669`; PROOFS `96afde6cc60c51b2f247ea19f5ce4f9ba2131b05c6a65567fb927d1ca57392cb`; amendment 1 `6a6004b9a8bbca4c120dc03f25cb2310ce5e570de4fd25c60f7d0401910c9193`. Exact hashes for every artifact are in the manifest.

Environment: Windows 11 (`10.0.26300`), CPython 3.14.6 64-bit (`MSC v.1944`).

Commands, from this audit directory:

```powershell
& 'C:\Users\Mahdi\AppData\Local\Python\pythoncore-3.14-64\python.exe' build_fixtures_v1.py
& 'C:\Users\Mahdi\AppData\Local\Python\pythoncore-3.14-64\python.exe' run_independent_audit_v1.py 1> audit_stdout_v2.txt 2> audit_stderr_v2.txt
```

Fixture JSONL counts and hashes are recorded in `FIXTURE_MANIFEST_V1.json`. The successful run's raw stdout is `audit_stdout_v2.txt`; stderr is `audit_stderr_v2.txt` (empty). The first run exposed an assertion bug in the auditor's witness replay on duplicate negative input: the checker initially compared against the unnormalized duplicate list. The source contract explicitly deduplicates each label set preserving first occurrence, so the checker was corrected to replay against the required normalized lists. The original failure is retained as `audit_stderr_v1.txt`; no candidate source or expected semantic result changed.

## Biggest thing overlooked?

An exact maximum over compatible partitions is a result about the finite observations. It must not be presented as a physical-truth certificate. Also, uniqueness of the best recommendation is distinct from uniqueness of all sample-compatible partitions. The reviewed contract and output keep those claims separate.
