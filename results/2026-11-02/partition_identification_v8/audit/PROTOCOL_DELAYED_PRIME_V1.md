# C008 audit: delayed finite-prefix ambiguity with locally prime factors

## Exact model

For two distinct letters x,y and integer M>=1 define

`E_xy = {w : |w|_x and |w|_y are even}` and
`F_xy(M) = E_xy \ { x^(2M)y^(2M) }`.

Compare k=2 systems on alphabet abcd:

- A: `F_ab(M) || F_cd(M)`, ownership `ab|cd`.
- B: `F_ac(M) || F_bd(M)`, ownership `ac|bd`.

Each block has two symbols. The systems use the same k and distinct
ownerships. The exact construction and M values 1,2,3 are frozen in
`delayed_prime_models_v1.json`.

## Why the local factors are symbol-prime

`F_xy(M)` is regular and infinite, and is a proper subset of `E_xy`. Its
unary projections are exactly `{x^(2n): n>=0}` and `{y^(2n): n>=0}`: the
even unary words themselves belong to F, while parity excludes odd powers.
If F factored across the only nontrivial partition `{x}|{y}`, the projected
factor languages would therefore both have to be the unary even languages;
their shuffle is E_xy, which contains the removed word. Contradiction. Thus
F_xy is indecomposable with respect to a nontrivial disjoint symbol partition.

## Claims and exact verification

Both global languages are subsets of the all-even-count language. They agree
on every word shorter than 4M: a removed projection needs 2M occurrences of
each letter and hence length at least 4M. The word `a^(2M)b^(2M)` is rejected
by A's `ab` factor and accepted by both factors of B. Therefore their shortest
symmetric-difference word has length exactly 4M. Choosing M with 4M above the
maximum trace length makes the different ownerships indistinguishable on that
finite prefix.

`verify_delayed_prime_v1.py` constructs complete DFAs for F_xy(M) using parity
bits and a prefix tracker for the one forbidden word. It constructs each
global shuffle product and uses reachable-product BFS to find a shortest
symmetric-difference witness for M=1,2,3. It also checks the analytical
projection/prime argument against the exact local automaton observations.
The DFA product BFS, rather than finite enumeration, is the proof that each
reported shortest witness is globally shortest. It checks for every alphabet
symbol that a singleton occurrence is rejected and a double occurrence is
accepted, and verifies both products are sublanguages of the all-even
reference. The all-M proof above is symbolic and separate from this finite
implementation check.

The first C008 experiment remains separate at
`ownership_models_v1.json` / `verify_ownership_equivalence_v1.py`: it proves
complete-language ambiguity but has locally decomposable factors. This second
construction has locally indecomposable two-letter factors and establishes
finite-prefix ambiguity for arbitrarily large delays.

## Claim boundary

This refutes a universal guarantee of recovering true ownership from an
arbitrary finite passive trace set over this unrestricted model class: for
any finite maximum observed length L, choose M with 4M>L. It does not claim
that every particular finite dataset is ambiguous, nor does it produce a
procedure for identifying ownership from infinite data. It assumes unlimited
local regular languages/state counts; a known DFA state bound or a primeness
assumption may change the theorem and must be stated separately. No RPNI or
noise assumption is added.

The experiment must be captured before launch, including this protocol,
driver, input, and capture utility. It uses only the Python standard library.
