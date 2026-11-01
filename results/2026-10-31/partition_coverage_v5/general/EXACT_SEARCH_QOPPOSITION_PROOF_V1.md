# C005 q-aware exact-search provider v1

## Interface and semantic classes

`known_k_qexact_v1.py` is standard-library code for a known finite alphabet and known `k`-way partition. Its API is `solve(data, *, k=None, local_word_cap=None, deadline=None, max_solutions=None, use_q_opposition=True, use_contextual_must_links=True)`. `deadline` is an absolute `time.perf_counter()` value. `max_solutions=None` enumerates every compatible partition; a positive limit may stop early. The CLI reads JSON and emits one JSON result.

`local_word_cap=q` declares that each factor has a finite local language of at most q strings. `q=None` means unrestricted regular factors. For a fixed partition, the direct witness uses each factor's set of observed positive projections. This accepts all positives and rejects each negative when some block's negative projection is absent from that set. The unrestricted finite-sample mode is valid because finite languages are regular.

`status` is `found`, `infeasible`, or `incomplete`. `search_exhausted` reports whether enumeration ended. `uniqueness` is `unique` only after exhausting with one partition, `ambiguous` after finding at least two, `none` after exhausting with zero, and `unknown` otherwise. A limit can yield `found`, `search_exhausted=false`, and `uniqueness=unknown`.

## Pruning arguments

1. **Contextual must-links.** When enabled, the implementation reuses adjacent-swap and insertion-rescue witnesses proved in the C004 `contextual_swap_proof.md`. If such a pair is separated, every local projection of the negative equals a projection from an observed positive. Every compatible partition must therefore keep the symbols together. This holds for regular factors and q-capped factors. Disabling the option affects pruning only; direct compatibility validation remains on.
2. **q-opposition cannot-links.** For a pair `{a,b}`, distinct observed positive pair projections are a function of the observed projections onto any block containing both. More than q such pair projections requires more than q strings in that block, so the symbols must be separated. More than q unary projections for one symbol proves global infeasibility, since that symbol must belong to some block. Disabling this option affects pruning only. It is naturally inactive at `q=None`.
3. **Contradictory links.** A cannot-link inside a must-link component proves no q-compatible partition exists. Link witnesses and the contradiction are recorded.
4. **Restricted-growth enumeration.** Must-link components are assigned in sorted order. The first gets block 0; a later component may use an existing block or the next unused block. This gives each unordered component partition exactly once. It rejects only assignments violating a q-cannot-link or assignments that cannot reach k nonempty blocks.
5. **Projection-cap monotonicity.** Distinct projections on a partial block remain distinct after extending the block, since projecting the extended words back recovers the original. Thus a partial block with more than q positive projections cannot have a q-feasible completion. At every complete leaf all positive caps and every negative witness are directly checked.

Every returned solution contains full block projection languages and direct negative witnesses. Pair counts are constraints for pruning, not a substitute for the full-block cap or negative checks.

## Boundaries and CLI

The bounded mode describes finite local projection languages of size at most q; it does not claim arbitrary regular-language recovery. Uniqueness concerns sample-compatible unordered partitions only within the declared known-k class. Exact labels and a known alphabet are required. Empty positive samples work under the chosen witness semantics: observed projection sets are empty, and every negative has an unseen projection. No opposition edge is inferred from the empty set. Alphabet symbols absent from all examples remain partitioned. Empty strings and repeated events are preserved.

```powershell
python -B -X utf8 known_k_qexact_v1.py input.json --k 2 --local-word-cap 2 --max-solutions 2
python -B -X utf8 known_k_qexact_v1.py input.json --k 2
```

Omitting `--local-word-cap` selects unrestricted regular-factor semantics. Omitting `--max-solutions` requests exhaustive enumeration. Invalid input emits an `invalid_input` JSON status and returns code 2.
