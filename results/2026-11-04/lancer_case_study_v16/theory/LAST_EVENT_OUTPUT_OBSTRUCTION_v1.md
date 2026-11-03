# C016 priority semantic obstruction: local outputs versus DFA acceptance

Direct theorem and conditional application to paper pp5/12. No observed
dataset violation or source execution is claimed. P5 defines last-event
success labels; p12 states PE fails without successful ERS, blue actions
succeed with network-validity-only monitors, and Remove resets its target host.

## Formal obstruction without needing an epsilon label

Let x,y be target-qualified atomic events assigned to different hypothesized
host blocks X,Y. Suppose an actual logged sequence has these labelled prefixes:

    y: success,     yx: failure,     yxy: success.

Then no disjoint independent DFA-acceptance product with x,y separated fits
those labels. Proof: let n=yx. On X its projection is x, identical to the
positive yxy projection. On Y it is y, identical to the positive y projection.
Any other block sees epsilon in all three words. Thus every block projection
of n is forced accepted by a positive. The product must accept n, contradiction.
This proof avoids assuming epsilon is positively labelled or an inactive
factor's initial acceptance is known. It also applies if x/y represent
multi-token encodings whose symbol supports belong wholly to the respective
blocks. An encoding with shared action tokens does not meet that premise
until a separate target-qualification transformation is defined.

The example can arise with completely independent local state updates:
one event always fails and the other always succeeds. Therefore observing
it would refute the proposed AND-acceptance **representation** of host
outcomes, not demonstrate physical host coupling.

## Paper-aligned conditional witness

In the two-host network-validity-only setting, consider

    y=Remove_on_Host1,    x=PrivilegeEscalate_on_Host0.

Conditional on initial Host0 not having satisfied ERS, and on Remove_Host1
not changing Host0, the three steps y,x,y have the success/failure/success
pattern: blue Remove succeeds, premature PE fails, blue Remove succeeds
again. These premises match the paper's described local-monitor setting
(p12) and the first three blue/red/blue event positions respect its order
(p5). Nevertheless exact raw initialization, targeting and repeated-action
behavior must be checked in the actual source/log; this is a proposed
diagnostic witness, not an assertion that the dataset already contains it.

If a positive neutral baseline z is available whose projection on each
host is epsilon, one can instead use z positive, z·PE0 negative and
z·PE0·DNS1 positive, provided that DNS1 actually succeeds and the encoding
assigns the baseline to neither host. That positive baseline prevents an
inactive host's rejecting start from spuriously explaining the negative.
Without such a baseline/other positive witness, n=PE0 and p=PE0·DNS1 alone
do NOT rule out a product: the Host1 factor could reject its empty projection
and accept DNS1. Do not claim a contradiction from only those two labels.

## What must change in the staged model

A Mealy-style local output depends on the current action and the active host's
state. A monitor may vote True when the current action is unrelated to it,
even if its last own action failed. A disjoint async DFA product instead
retains each inactive factor's acceptance flag and ANDs them. Those semantics
are different. Removing global monitors or qualifying host tokens alone does
not fix this last-event selection problem.

The first application baseline should predict the active component's output
from its local history after the relevant event, conditional on verified
locality. Unknown component discovery for such selected-output semantics
needs a new admissibility/identifiability theorem. C015's projection criterion
has not been proved for it. If keeping C015 unchanged, restrict the goal
honestly to factorization of the observed outcome-language, or explicitly
define a different joint-state acceptance target and label it as a new task.

The paper's non-resetting global histories (p5) and its multi-trace/trial
experimental descriptions (pp6–8/appendix) do not settle actual collector
reset behavior; source/provenance is needed before choosing histories.
No arbitrary episode concatenation or resetting is authorized by this note.
