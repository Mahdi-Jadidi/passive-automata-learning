# C028 specification amendment 1: serialized schema and error status

This additive versioned amendment supersedes only the affected statements in frozen `SPEC.md` and `PROOFS.md`; those files remain unchanged. It requires independent re-review before implementation/provider experiments. Biggest overlooked point? The mathematical variable names and actual serialized field names must never be mistaken for each other.

1. The exact serialized input keys are `alphabet`, `positive`, and `negative`, and no other keys are allowed. They represent mathematical Sigma, P, and N respectively. All previously specified types, validation, normalization and semantics remain unchanged. For example:

```json
{"alphabet": ["opaque.a", "multi char"], "positive": [[], ["opaque.a"]], "negative": [["multi char"]]}
```

IDs are distinct nonempty strings, words are arrays of IDs, and `[]` is epsilon. The array order of `alphabet` defines the canonical RGS order. This amendment does not reintroduce the old single-character string-word input format.

2. If internal witness verification fails, return `ERROR`, with counts, recommendation, max_blocks and uniqueness fields null. `ERROR` is not a mathematical classification. An external interruption returns `INCOMPLETE` with the same null mathematical fields. `INVALID_INPUT` likewise has no mathematical conclusion. Completed outcomes remain `INCOMPATIBLE`, `UNIQUE_COMPATIBLE`, and `AMBIGUOUS`.

3. Conceptual pseudocode function parameters Sigma, P, N denote the values of these three serialized keys after validating the entire record; they are not alternate accepted JSON field names. In particular, the input is a single record, not three independently validated scalar arguments. The contradiction check takes place only after successful full-record validation.

The proof in `PROOFS.md` is unaffected by renaming the external keys: it quantifies over the corresponding validated mathematical objects. The ERROR rule is a conservative nonclaim when an internal check fails, and hence does not establish a mathematical result. The full amended contract is `SPEC.md` plus this amendment, with `PROOFS.md` and the reference pseudocode. A renewed reviewer verdict must explicitly cover this amendment.
