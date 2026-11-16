# C025 counterexamples v1

All examples below are constructed, not claimed observed artifact violations. C016 supplies CE1’s provenance; C017 supplies the finite-depth boundary. No trace execution occurred here.

## CE1: AND acceptance rejects independent last-event behavior
Σ={x,y}; observe y→success, yx→failure, yxy→success. Separate one-state Mealy components x (always failure) and y (always success) realize these observations with partition x|y.

Under C024 AND acceptance, negative yx projects to x on block{x}, matching positive yxy, and to y on block{y}, matching positive y. Neither block rejects it, so x|y is infeasible. This is semantic mismatch, not physical coupling. The example needs neither an epsilon label nor a positive baseline. The conditional C016 Remove_Host1/PrivilegeEscalate_Host0 scenario is only a proposed source diagnostic, not an observed occurrence.

## CE2: old adjacent-swap must-link is unsound here
Observe xy→success and yx→failure. Independent components y always success, x always failure realize x|y. The words differ by one adjacent swap, which forces a must-link in the AND outcome-language model, but imposes no such ownership constraint in selected last-event output. Thus old swap atoms must not be imported.

## CE3: full-history coarsening must not be confused with arbitrary block monotonicity
Observe x→0 and yx→1. Block{x} conflicts (local x both times). Block{x,y} is compatible (x and yx differ). Thus a currently inadmissible partial block can be rescued by expansion.

Conversely observe x→0, y→0 and zy→1 over{x,y,z}. Block{x} is admissible, but block{x,y} conflicts on y; block{x,y,z} resolves it. Inclusion alone gives neither admissibility nor inadmissibility monotonicity. Partition coarsening remains valid because a compatible partition cannot contain the conflicting block{y} in this example.

## CE4: finite suffix coarsening fails
Two reset traces have events/outputs:
T1: y/0, x/0.
T2: x/0, y/0, x/1.
With depth1 (one PRIOR local event plus current), partition x|y fits: first x has empty prior context and output0, second x has prior x and output1; y always outputs0. After merging, the final x events both have prior y and current x but outputs0 and1. Thus oneblock fails at depth1 even though full-history oneblock fits. For depth d≥1 replace y by y^d. No unknown-K bipartition/coarsening theorem from full history applies to this finite-depth model.

## CE5: unknown events and shared starts matter
T1: x/0. T2: x/UNKNOWN, x/1. A deterministic x transducer can output0 first and1 second. Removing the unknown event from T2 creates contradictory first-x labels. Keep inputs whose outputs are unknown.

Two reset traces x/0 and x/1 make every partition incompatible under common initial state. Per-file private initial states could fit them, but that is a different model. Do not silently add trace IDs as symbols or initialization selectors.

## CE6: compatibility does not identify ownership
Observe x/0 and y/1 only. Both x|y and oneblock fit full-history selected output. No-K ambiguity is unavoidable from these observations; matching a known-host baseline only demonstrates its membership in the version space. Unknown future transitions can be completed differently by equally valid finite-state witnesses.

