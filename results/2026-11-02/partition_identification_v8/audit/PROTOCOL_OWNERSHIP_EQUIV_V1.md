# C008 audit: exact same-k ownership counterexample

## Claim under test

Two physical ownership maps on the same four-symbol alphabet and with the same
number of devices can induce exactly the same global language, even though the
ownership partitions differ. This is a bounded counterexample to guaranteed
recovery of physical ownership from the complete global language under the
listed system model. It does not by itself show that either factor is prime.

## Frozen systems

The input is `ownership_models_v1.json`. Both systems have k=2. Their blocks
are `ab|cd` and `ac|bd`. Each local DFA tracks the parity of occurrences of
its two owned letters, accepting only even/even. Under interleaving, letters
outside a factor's block stutter in that factor. The resulting global language
is intended to be all words in which each of a,b,c,d occurs an even number of
times. The exact local DFA tables are in the input.

`ownership_mutants_v1.json` is a deliberately wrong variant: the `ac` factor
checks parity of `a` but ignores `c`. It must be rejected by an exact
counterexample, rather than hidden by finite-prefix agreement.

## Verification method

`verify_ownership_equivalence_v1.py` is a standalone standard-library Python
driver. It validates alphabet ownership, total deterministic local tables,
reachability and pairwise state distinguishability for the local DFAs. It
constructs each global product DFA directly on all symbols, with non-owned
symbols acting as identity transitions. Equality is decided by BFS over the
reachable product of the two global DFAs; a mismatch returns a shortest word.
This is exact finite-state equivalence, not a bounded-length test. It emits
the reachable global DFA tables for review.

The frozen run must be captured before launch with the copied C007
`evidence/capture.py`, snapshotting this driver, both JSON inputs, this
protocol, and the capture utility. Only Python standard library is used.

## Interpretation boundary

All four symbols are essential to the accepted language: ε is accepted, each
single symbol is rejected, and each double occurrence of one symbol returns
to an accepting state. The languages are infinite and non-universal. Each
four-state local even/even DFA is minimal (all four parity states are
reachable and pairwise distinguishable). Still, each such local language
decomposes further into one-letter even-count languages; therefore this
example does not refute a prime-factor restriction. No additional prime or
delayed-coupling model is introduced absent a theory-side assumption.
