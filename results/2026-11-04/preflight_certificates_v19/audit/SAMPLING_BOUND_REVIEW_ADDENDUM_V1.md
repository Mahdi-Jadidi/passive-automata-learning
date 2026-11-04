# C019 independent addendum: sampling coverage bound

Reviewed only the new theory/SAMPLING_COVERAGE_BOUND_FA_v1.md. Decision: **accepted under its explicit distribution/model assumptions**. No tests, provider calls or prior-file modifications were performed; prior review/handoff remain unchanged. Source/review SHA256 are recorded separately in SAMPLING_BOUND_REVIEW_BINDING_V1.json.

For a fixed forest of E=m−K necessary within-true-block edges, independent trial outcomes and per-trial edge probability at least p_min imply, for each fixed edge e,

    Pr[e absent after M trials] <= product_t(1-p_e,t) <= (1-p_min)^M.

Identical trial distributions are not required; independence and the uniform lower bound suffice. The union bound over the E fixed edges needs no independence between different edges within a trial. Hence the probability of missing at least one edge is at most E(1-p_min)^M <= E exp(-M p_min). For integer E>=1, 0<delta<1 and p_min>0, the stated integer sufficient budget ceil(log(E/delta)/p_min) correctly makes the latter upper bound <=delta. This is sufficient and may be loose; no optimality is claimed.

Checked boundaries and interpretation:

- E=0 must be handled separately; log(0/delta) is inapplicable. K=m gives the sole singleton partition under the trusted-count constraint; existing observations still require schema/consistency validation.
- One valid adjacent-swap word comparison witnesses at most one forest edge. These edge outcomes are mutually exclusive within that comparison, so sum_e Pr[e witnessed] <=1 and E*p_min<=1 is a necessary feasibility condition for the promised distribution. It is not by itself evidence that such a collector exists. A language invariant under swaps may have no such positive/negative witness at all.
- E=2, p_min=1/4, delta=.05 gives ceil(4 log40)=15, as stated. This is an arithmetic illustration, not an empirical estimate of a dataset's coverage probabilities.
- M counts comparison trials, not distinct positives, distinct words or saved traces. Reusing a fixed positive is compatible with independent random comparisons only if the collector actually satisfies the stated independence/lower-bound assumptions. The theorem does not infer them from an observed histogram or from a passive log.
- After all sound edges are witnessed, every true block is connected and no sound edge crosses true blocks. The graph therefore has exactly the true K components. Correct model/noiseless labels imply their sample compatibility; trusted K then yields a unique compatible partition. The practical exact compatibility guard remains appropriate.
- Probability1-delta concerns obtaining this coverage certificate within M trials. Once its edges, compatibility and assumptions are valid, the conditional uniqueness deduction is exact. It is not an unconditional100-percent recovery guarantee, a count-only theorem for arbitrary data, or a bound on computational time.
- Dependent/adaptive acquisition without an additional justified conditional-probability argument, incorrect K, noise, or misspecified independence of physical components is outside the stated theorem. No implication of prime-factor identifiability is added.

No blocking mathematical issue found. This addition supplements the earlier no-universal-threshold result by explicitly adding a coverage-distribution promise; it does not contradict that result or resume the paused paper/real-data task.
