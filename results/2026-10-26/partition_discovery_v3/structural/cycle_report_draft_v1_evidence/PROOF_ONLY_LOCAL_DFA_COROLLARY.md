# C003-S001 appendix: local words, complete DFAs and trace counts

**Proof only.** No runtime change, DFA experiment, RPNI run or new benchmark.
These are elementary automata consequences under the fixed-word assumptions,
not novelty claims or a general passive-learning efficiency guarantee.

## Assumptions and what is recovered

Let A=B0 disjoint-union B1 with both blocks nonempty, and let u in B0+ and v in
B1+. Write m=|u|, n=|v|. Symbols may repeat arbitrarily within either word; no
symbol belongs to both blocks. The global target is exactly the unrestricted
order-preserving shuffle L={u} shuffle {v}, not a restricted scheduler subset.
Automata below are **complete deterministic** automata, including a rejecting
sink, over each declared local alphabet Bi or global alphabet A respectively.

After C003-S001's certificate returns the unique partition within the fixed-word
class, any complete positive p determines the factors themselves:
u=pi_B0(p), v=pi_B1(p). They are unique up to the same side swap. Thus, if the
true system satisfies this class, the procedure recovers its two local WORDS
and allows direct construction of exact local DFAs; it is not merely finding an
alphabet partition. Without the true fixed-word assumption, these remain only
a class-compatible explanation. Positive prefixes would not determine the words.

## Exact minimal complete local sizes: m+2 and n+2

For {u}, make states 0,...,m and dead. Start at 0, accept only m. At i<m, the
next required letter u[i] leads to i+1; every other letter leads to dead.
Every transition from m leads to dead, and dead loops on all letters.

Each i is reachable by prefix u[:i]; dead is reachable by appending any local
letter after u. State i has a nonempty residual consisting of the single suffix
u[i:], whose length m-i differs for every i. Hence every two live states are
distinguishable; dead has empty residual and differs from all of them. All m+2
states are therefore necessary and sufficient. The same proof gives n+2 for {v}.
No assumption that letters occur only once is used.

## Exact minimal complete global size: (m+1)(n+1)+1

Use live states (i,j), 0<=i<=m, 0<=j<=n, plus dead; start (0,0), accept only
(m,n). A letter in B0 advances i iff it matches u[i] and i<m, otherwise goes
dead. A letter in B1 analogously advances j. Dead loops. Disjoint alphabets
make the choice of coordinate deterministic.

Every live pair is reachable by u[:i] followed by v[:j]. From (i,j), the suffix
u[i:] followed by v[j:] is accepted. Any accepted continuation from (i',j') must
contain exactly m-i' letters owned by B0 and n-j' letters owned by B1. That
particular suffix contains m-i and n-j such letters. If (i,j)!=(i',j'), these
two count requirements differ, so it is rejected from (i',j'). All live pairs
are distinguishable, even with repeated letters. Dead is reachable from the
accepting pair by any letter and has no accepted continuation. The construction
is complete, reachable and pairwise distinguishable, proving the exact count.

The raw product of the two complete local DFAs has (m+2)(n+2) states; states
with a dead local coordinate all have empty residual and merge into the one
global dead state. The formula above counts that merged sink ONCE. A partial
DFA omitting rejection transitions would instead count only the live pairs.

## Exact accepted-word count: binomial(m+n,m)

Choose the m positions assigned to u among m+n positions, put u there in its
fixed order and put v in the remainder. Every such schedule gives a shuffle and
every shuffle has such a schedule. Crucially, the resulting letters identify
their owners because B0 and B1 are disjoint. Thus two different schedules cannot
yield the same word, even if u or v internally repeats symbols. The map is a
bijection, and |L|=binomial(m+n,m).

## Boundaries and connection to the original motivation

For m=n=k, the local state total is 2k+4, whereas the complete minimal global
DFA has (k+1)^2+1 states and the global language has binomial(2k,k) distinct
traces. We can represent this identified target by the two local automata rather
than building its global DFA or listing all traces. With two factors this state
gap is quadratic versus linear in word length, **not** a demonstrated exponential
state reduction. The combinatorial number of accepted words is a different size
measure. No empirical speed/space improvement or RPNI performance follows here.

Disjoint ownership is essential to the exact formulas above. Preserve this
out-of-assumption counterexample: u=a, v=a. The global shuffle is {aa}, with
one distinct word and a four-state complete minimal unary DFA, rather than
binomial(2,1)=2 words or (1+1)(1+1)+1=5 states. This refutes extending these
counts to overlapping supports; it does not refute the stated disjoint theorem.
Nonempty support coverage is required for the uv/vu RECOVERY guarantee, not for
the state construction once the words and declared disjoint blocks are given.
Unknown local words, arbitrary regular factors, shared symbols, trace prefixes
or restricted scheduling require separate arguments.

Related primary source: Biegler, Daley and McQuillan, *On the Shuffle Automaton
Size for Words*, Journal of Automata, Languages and Combinatorics 15 (2010),
53–70, [author-hosted paper](https://www.cs.usask.ca/faculty/mcquillan/pubs/shuffle_automaton_size.pdf).
Checked preliminaries (reachable/distinguishable states imply minimality) and
Definition 1's position-pair shuffle NFA, explicitly incomplete in that paper.
Our disjoint-support complete-DFA count and schedule bijection are proved above;
general overlapping-word state complexity is not inferred from them. Accessed
2026-10-26. Core recovery audit and all frozen runtime sources remain unchanged.
