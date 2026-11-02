# C007-T003: proposed adaptive unique example beyond old graph shortcut

Status: direct mathematical derivation; independent oracle acceptance PENDING.
No new scientific execution, provider feature or performance measurement here.
The auditor is checking separately. Do not label this as an accepted test result.

Preserved original:

```json
{"alphabet":["a","b","c","d","e","f"],
 "positive":["","aabb","ccdd","eeff"],
 "negative":["bbaa","ddcc","ffee"]}
```

## Forced same-owner pairs and unique finest

Suppose a,b are in distinct blocks of ANY compatible partition, with arbitrary
unknown k and unrestricted regular factors. The positive aabb and negative bbaa
then have exactly the same projection on EVERY block: aa on a's owner, bb on
b's owner, and epsilon elsewhere. Every negative local projection is therefore
positively forced, contradiction. Hence a,b must co-own. Applying the same
argument to ccdd/ddcc and eeff/ffee forces c,d and e,f respectively.

Thus C={a,b}|{c,d}|{e,f} refines every compatible partition. It is itself
compatible: on the respective pair block, the negative reversed doubled word
is absent from the positive-projection language {epsilon, forward doubled word}.
Every negative has that rejecting block. Consequently C is the unique finest
sample-compatible partition by T4, independently of whether these semantic
must-links can be found by the production graph extractor.

The three infinite regular factors (aabb)*, (ccdd)*, (eeff)* also fit these labels;
this is not a fixed-word example. Coarsening those factors retains the same
global language, so finest convention still does not identify hidden architecture.

## Why the OLD graph is empty

Only the adjacent unequal pair in positive aabb is its ab boundary. Swapping it
gives abab, not any listed negative. Likewise ccdd gives cdcd, eeff gives efef;
epsilon has no adjacent positions. Thus no positive/negative adjacent-swap edge.
Every negative has length four, but insertion rescue requires a length-three
positive base and length-five positive rescue; neither exists. Even the dormant
alternative-insertion/deletion A/B rules cannot fire on these equal-length words.

Therefore the old graph has six singleton components. Its component partition
fails T1: negative bbaa's singleton images aa,bb,epsilon,... are all seen.
The cheap component-feasibility certificate is unavailable. If the production
adaptive algorithm returns the proved unique three-block answer, it must justify
it through separator/cover machinery rather than this empty old graph shortcut.
This implication does NOT claim any such provider run, its oracle-call count,
or timing has yet been observed.

An extended semantic must-link engine could derive these pair constraints, but
that is not activated or proposed as a new runtime task in this note. The present
example separates mathematical forced coownership from completeness of the
specific implemented local witness rules.
