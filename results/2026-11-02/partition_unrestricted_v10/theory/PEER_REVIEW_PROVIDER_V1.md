# C010 bounded static review — frozen provider v1

Decision: **REJECT exact per-k output in shortcut path; new version required.**
No provider execution, experiment or source edit. A mathematical source-level
counterexample is not reported as an observed run. Independent audit still
owns executable acceptance. Frozen snapshots are recorded in
peer_review_provider_v1/MANIFEST.json.

Reviewed SHA-256:

* unrestricted_solver_v1.py:
  e2d3e0df3e59acb7b359b4be7a41243d99e7c71f4743a2bb76192cbbebdded1c
* unrestricted_cli_v1.py:
  c558faea261e25fe5b4870bb905a20ada0b92dae56726657806330f3b01e5bf5
* API_PROTOCOL_V1.md:
  65a51adb94d70dee4b2e40e45c926bd1674cc777948f457b3f6eb5a14b0d3930

## B1: Bell-by-index substituted for the Stirling spectrum (blocking)

`_stirling_bell(r)` returns a dictionary of Bell(n), for n=0,...,r. It does
not return S(r,k). In `if atom_ok`, the code sets

    count_by_k = {str(k): (bell[k] if k <= r else 0) ...}

The required count is S(r,k), with r fixed and k variable. Bell(k) counts
all partitions of k objects and is a different quantity.

Minimal direct counterexample input (not executed):

    {"alphabet":["a","b"],"positive":[],"negative":[]}

There are two singleton atoms; the atom partition is feasible. The exact
family consists of a|b and ab, so total=2 and spectrum {1:1,2:1}. Source
evaluation instead sets total=Bell(2)=2 and spectrum {1:Bell(1),2:Bell(2)}
={1:1,2:2}; its spectrum sums to 3, contradicting its own total. The same
error occurs on larger shortcuts. For r=1 the error is masked because
Bell(1)=S(1,1)=1.

The total Bell(r), distinct-atom pair count Bell(r−1), same-atom total and
their constructive witnesses are mathematically the right formulas. Fixing
the spectrum needs retaining/recomputing the final Stirling row under a
new source version; it does not justify silently replacing frozen v1.

## Other correctness alignment

* Swap detector retains the first mismatch and permits only a second at
  the next position; any later mismatch sets −2 and rejects. The reversal
  comparison excludes a single unmatched position. Therefore accepted
  edges really are adjacent unequal swaps and are sound must-links.
* Union-find components include isolated symbols. Every feasible partition
  coarsens them, and expanded blocks preserve all projection tests.
* `atom_partition_feasible` checks the original positives and every negative.
  Only its successful branch uses the all-coarsenings family. No absent-edge
  independence is assumed in fallback.
* Shortcut optional `grow` is canonical set-insertion enumeration on atoms.
  Pair witnesses are the one-block expansion and, for distinct atoms, the
  verified atom partition. At r=1 there is no distinct-atom pair and all
  actual symbol pairs are correctly same-atom.
* Fallback lazy `reject` computes exact masks on unions of atoms. Canonical
  anchored subset recursion and joint pair aggregation match the proofs;
  child pair entries outside the child remainder are zero by induction.
* Remaining-coverage pruning is justified by mask monotonicity. The code
  also computes reject(0): if P is nonempty it is zero, so the empty-state
  prune enforces covered=ALL. If P is empty it equals ALL, but the atom
  partition is automatically feasible and fallback is unreachable on valid
  inputs. Thus this placement is not a demonstrated result bug in this API.
* Witness DFS excludes first separation for a same relation and excludes
  joint ownership for a different relation. Once decided, deletion of the
  chosen block preserves the decision. It may backtrack extensively; no
  fast witness-extraction bound follows from memoized counting.
* Explicit enumeration checks final length against total and a protected
  interruption returns unknown with counts/relations/witnesses omitted.

## L1: preprocessing is outside cooperative/interrupt protection

Swap extraction, union-find atom construction and their loops occur before
the protected `try` and before the first `_check(deadline)`. That work can
take O(|P|·|N|·word length) and does not poll the deadline. Even an expired
deadline first pays that work. KeyboardInterrupt during this preprocessing
can escape instead of returning structured unknown. Validation/setup is
also unprotected. This is stronger than merely excluding CLI read/output
cost and must not be described as whole-preprocessing cooperative protection.
No interrupt experiment was performed here.

The protected computation still returns no scientific finality when it catches
_Stop or KeyboardInterrupt. A late but truly complete result is not thereby
mathematically wrong; strict total-wall enforcement needs an outer capture.
Bell/Stirling arithmetic, some pair loops and cached returns do not poll at
every operation either. CLI creates deadline after reading input and prints
JSON outside solve, so CLI wall and provider clocks are distinct.

## L2: atom-count upper bound is not exact kmax in fallback

The protocol explicitly defines `k_max_upper_bound` as r, the atom count.
That is a sound upper bound but can be loose. On graph-empty doubled pairs
abcdef, the atom count is 6 while exact feasible maximum is 3. Do not label
this output as the computed exact sample kmax in reports/slides. The latter
can be derived from the largest positive entry of a correct completed
spectrum. On a successful shortcut, r is exact kmax.

## L3: timing and input scope caveats

`provider_seconds` is assigned before constructing the representative
`_witness` inside the returned dictionary, so it excludes that final work.
Fallback `search_seconds` ends before relation witnesses/enumeration;
shortcut search_seconds remains zero although combinatorial arithmetic and
pair output cost work. These are scoped internal metrics, not complete
end-to-end cost. Use captured process wall time for comparisons.

Any k/allowed_k key is explicitly rejected, as required. Other unknown keys
are ignored, so proposed prime/state constraints are not enforced. Neither
validation nor arbitrary resource exceptions have a universal totality claim.

## Acceptance action

Preserve v1 and this failed mathematical candidate. Correct B1 in a new frozen
version and rerun the required independent gate on that version. Master decides
L1's implementation versus documented scope; no metric-only source churn is
demanded here. L2 is an interpretation warning given the explicit API contract.
No empirical success, speed or scale claim is made by this static review.
