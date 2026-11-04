# C017 — selected-output local-memory factorization

Direct proofs, no scientific runs or upstream code imports. This temporary
restricted model is for the first actual-data HOST/DEVICE experiment, not a
replacement of the full host-recovery goal. Event IDs are opaque atomic types;
target qualification is a declared preprocessing assumption, not inferred
ownership. Truth/hostnames are withheld from inference.

## 1. Exact model and memory convention

Each file has an ordered sequence of event types a₁,...,a_t and outcomes
y_i∈{0,1,?}. Unknown outcomes are excluded from constraints, NOT from the
event stream: they still advance local memory. File boundaries initialize
context to epsilon in this temporary model; whether physical state truly
resets is a separate source/data assumption checked by the known-host baseline.
Original event/outcome alignment must be validated independently.

Let Σ be the modeled event-type alphabet and Π a partition of Σ. For an
event a∈B∈Π with prior full event history h in its file define

    κ_d(B,h,a) = (suffix_d(π_B(h)), a),
    κ_full(B,h,a) = (π_B(h), a).

d counts PRIOR local event IDs, with current ID stored separately. Thus d0
uses current type only, d1 uses previous local type plus current. Short
contexts retain their true lengths; no ambiguous padding/sentinel is added.
Each group has a deterministic function f_B from such contexts to outcomes.
The global prediction at a is only f_B(κ), where B owns a; inactive groups
make no acceptance vote. This is not the C015 DFA-AND language semantics.

For the selected subset Σ'⊆Σ, retain only labels whose current event belongs
to Σ', and use π_Bh for B⊆Σ'. Unselected and unknown-label events must be
counted in coverage reports. Unknown-label SELECTED events still enter context.
Ignoring unselected same-host types is an additional abstraction: even true
host ownership restricted to Σ' may become model-inconsistent.

## T1. Necessary and sufficient fixed-partition consistency

A proposed Π is consistent iff, for every B, no two labelled event positions
owned by B have identical κ_d but different outcomes.

Proof. A deterministic f_B cannot give different outputs to the same argument.
Conversely assign the recorded output to each observed context; absence of
conflicts makes this well-defined. Extend all unobserved contexts arbitrarily.
The resulting functions realize every known output, with no constraint imposed
by unknown labels. ∎

A conflict certificate consists of block B, d/convention, both file/event
indices, current ID, equal prior projected contexts and opposite aligned labels.
It refutes this group's chosen local-memory model on these observations.
It does NOT refute physical host identity: true dependencies can exceed d,
unselected events can carry state, boundaries may be wrong, observations
partial, labels misaligned or behavior stochastic.

## T2. Finite Mealy witness realization

For finite d, use group states all words over B of length at most d, initial
epsilon. On input a∈B output f_B(context,a), then transition to
suffix_d(context·a). Other groups do not update on this input. This deterministic
finite Mealy machine realizes T1; state count ≤Σ_{j=0}^d |B|^j (d0 has one
state). It is a witness upper bound, not the smallest physical state machine.

For full observed history, collect every finite local prefix of the observed
files in a trie. The current trie prefix identifies the full local history;
assign the consistent outputs on observed outgoing contexts. Add one fallback
state and arbitrary outputs/transitions for unseen extensions. Every observed
local-history prefix is present, so no observed requirement is lost. This
finite Mealy witness realizes the finite dataset despite the unbounded-history
specification. It proves finite-sample regular realizability, not a bound or
exact model of all future physical behavior.

## T3. Depth increases relax consistency, not necessarily improve identification

For fixed B, if d'≥d then κ_d is recovered from κ_d' by taking a shorter
suffix. Equal longer contexts imply equal shorter contexts. Therefore a
d-consistent partition remains d'-consistent; likewise it remains full-history
consistent. A conflict at d may disappear at a larger depth. The compatible
partition families grow (or stay equal) along 0,1,2,4,8,full for fixed data.
Uniqueness at one depth need not survive a relaxation.

At fixed depth, adding labelled observations only shrinks the compatible
family. These two directions must not be confused. Finite-label accuracy,
memory sufficiency and ownership identifiability are different questions.

## T4. Coarsening FAILS for every fixed finite d≥1

Take types x,y with candidate groups {x}|{y}. Observe two files:

    file1: y^d (each output0), x(output0)
    file2: x(output0), y^d (each output0), x(output1).

For group {x}, the first x in each file has empty local history and output0;
the second x in file2 sees prior local suffix x and output1. For any d≥1
these contexts differ. Group {y} always outputs0. Thus the fine partition
fits. After merging into {x,y}, the two final x events both have prior
suffix y^d and the same current x but opposite outputs. The merged group
fails T1. These observations can be produced by independent local Mealy
machines: x outputs0 on its first event and1 on later events; y outputs0.
No physical cross-group coupling is needed for the failure. ∎

Hence do not inherit C015's coarsening closure, atom contractions, rejection
mask monotonicity, one-block alternative theorem at finite d, or swap mustlinks.
Adding other-group events can evict informative older local events. Conversely
adding symbols can also resolve a conflict by adding relevant context, so
neither block admissibility nor inadmissibility is monotone under inclusion.

At d0, partition choice is irrelevant: each current type must have a constant
known outcome. If so every partition fits; if not no partition fits.
This is an informative boundary control, not a useful ownership estimator.

At full history coarsening closure is restored: from a merged group's entire
history one can project to the old owner group's history, with current a
selecting the old owner function. Thus every consistent fine partition has
a consistent one-block coarsening. For finite samples whose complete input
histories/current IDs never conflict, a one-block trie always fits. Full-history
no-K uniqueness can only be one-block; a finite-d nontrivial unique result
is conditional on that specific external memory restriction, not a general
hardware recovery guarantee.

## 2. Why swapping is not the old must-link rule here

Different labelled histories no longer mean one word is globally forbidden.
Two independent components may output differently at different current events;
their inactive output states do not veto the active output. A positive/negative
adjacent swap in an outcome-language therefore does not by itself force its
symbols to coown in this selected-output model. Any proposed pruning must
be proved for T1, rather than imported from DFA intersection acceptance.

## T5. Exact next algorithm on bounded m

For a fixed nonempty block B⊆Σ', test T1 by scanning each file in order,
keeping its local context and a cross-file dictionary mapping (context,current)
to one known outcome and source index. On a known-labelled event in B,
check/insert that key. Then append the event type to local memory, whether
its label is known or unknown. Reset memory only at the declared file boundary.
Return conflict witness or a compatible block's finite function/trie witness.

A partition fits iff ALL its blocks pass this independent test. Thus on m≤8
one can test at most 2^m−1 blocks lazily, or precompute this small admissibility
table, and enumerate canonical RGS partitions. Accept only partitions of
admissible blocks. This preserves the full compatible family, exact counts
and unique/ambiguous/incompatible status; deadline gives incomplete. Alternatively
exact-cover DP over admissible disjoint blocks counts without listing, with
the least-remaining-symbol anchor giving a unique path per partition.

Crucial pruning limit: an inadmissible CURRENT partial RGS block may later
become admissible when symbols are added, so do not reject partial RGS nodes
on that basis. Only test final blocks, or use a separate proved extension
bound. In a block-first exact-cover recursion a selected block is final, so
discarding an inadmissible selected block is safe. No all-Bell shortcut except
special T1/T3-proved cases is assumed.

For finite small d, a direct tuple-copy scan of E events costs O(E(d+1))
per block plus hashing; full-history tuple copying can be quadratic in file
length. Prefix/trie IDs can avoid copying but require an exact representation
proof. Worst-case partition enumeration remains Bell(m); m≤8 is the explicit
experimental bound, not a general speed claim. No true group membership may
select promising blocks or tune d after viewing test performance.

## 3. Actual-data evaluation and assumption ladder

Use training-only frequency to choose opaque IDs and fixed file splits from
the contract. Ground-truth host maps evaluate only after inference. Report:
known-host full-alphabet baseline consistency; restricted-subset host baseline
consistency separately; all compatible subset partitions; whether restricted
host truth belongs to that family; uniqueness; pair relations if requested;
labelled-event/type/file coverage and excluded/unknown counts.

Known-host baseline is a prerequisite diagnostic, not inferred recovery. If it
fails, a unique alternative does not count as recovered physical hosts. If it
fits and an inferred unique partition equals it, this is correct identification
within the sampled bounded-memory/subset class only. It does not establish
unseen host event types, full dataset or full physical behavior.

Heldout unseen contexts have unspecified output under T1's arbitrary extensions.
Do not treat an arbitrary witness's default output as a uniquely determined
prediction. Report known-context coverage, accuracy/contradiction on covered
contexts and abstention/unconstrained contexts, or preregister a specific
generalization rule as a distinct learner. Validation/test must not choose the
partition from the training family covertly.

Temporary assumptions to relax visibly: fixed opaque target-qualified event
types → aliasing/shared events; file-initial empty history → persistent/contextual
starts; finite local suffix → longer/full history; selected m≤8 types → complete
type stream; deterministic outcome → missing/stochastic/observation ambiguity;
verified output alignment → separately audited label policy. Every relaxation
changes the version space and needs its own conflict/coverage measurements.
Target qualification itself uses observed target metadata to define symbols;
opaque IDs prevent inference reading host names but do not erase that temporary
preprocessing assumption. Hardware identity remains the target, never monitor
groups substituted for it.

No algorithm, actual trace or source collector was executed for these proofs.
