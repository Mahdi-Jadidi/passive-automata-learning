# C007-T004: staged swap-only sufficient shortcut

Status: mathematical approval under the EXISTING T4 component theorem; proposed
production v4 still requires a fresh independent gate. No provider edit, run,
performance measurement or long-case success is claimed by this note.

Let H contain ANY subset of individually validated universally sound must-link
edges. Adjacent positive/negative swaps are one such rule. Its component
partition C_H refines every sample-compatible partition, because every H edge
forces common ownership for arbitrary unknown k and unrestricted regular factors.
If a COMPLETE direct projection check establishes C_H is sample-compatible,
then C_H itself is a feasible lower bound on every feasible partition. Hence it
is the unique finest sample-compatible partition by PROOFS_v1 T4.

H need not include all swap edges, rescue edges or other potential sound rules.
There is no graph-completeness requirement in this certificate. Indeed any
additional sound edge crossing C_H would contradict C_H's established feasibility,
so computing it is unnecessary on success. This is an exact sufficient early
return, not an approximation or new assumption about data coverage.

For the proposed staged implementation:

1. Derive swap edges with exact label/context replay. If hashing selects edge
   candidates, exact string equality must still validate each one.
2. Reconstruct components over ALL declared symbols, including isolated/unused
   ones, and apply the complete T1 check to every positive and negative.
3. If compatible, emit the same must_link_components_compatible certificate
   with those actual edges/components and the full direct witness. Existing
   verifier logic suffices mathematically because it replays supplied edges;
   it must not require or assume extraction of an exhaustive graph.
4. If incompatible, do NOT assert multiple maximal refinements, no decomposition,
   or any exact meet. Fall back to the unchanged full V3 graph/search path.
   The temporary component partition must never initialize adaptive meet state
   as if it were the meet of compatible answers. Preserve V3's one-block start
   when the complete fallback shortcut also fails.

If time expires before feasibility is fully verified, no unique-finest shortcut
claim follows. A verified subset of edges is sound evidence but not, by itself,
a complete finality decision. Metadata must accurately distinguish a sufficient
subset graph from a claimed complete swap/rescue extraction.

The master-reported V3 m16/length65536 preprocessing timeout motivates this
staging, but does not prove V4 finishes that case or improves time. Swap scanning,
direct projection checks, output serialization and any fallback can still be
expensive. The observed V3 attempt and a future V4 attempt must remain separate;
no long-case solved claim is authorized until its captured result is validated.
The core target remains the sample-finest convention, never hidden architecture.
