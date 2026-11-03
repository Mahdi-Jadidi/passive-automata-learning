# C013 generator design

Use separate seeded RNG streams for the world and observations, so changing
length/sample count preserves the world. Shuffle the global alphabet, allocate
at least two symbols to each device, and rejection-sample complete random
transition tables conditioned on strong connectivity. Choose 2–4 states;
start 0 accepts and at least one state rejects.

Generate a random prefix of length b with b + min(K,b)*3 <= maxL. Repair only
active devices with BFS shortest continuations, choosing one active device to
reject for a negative target. Interleave repair paths uniformly among their
locally order-preserving interleavings. Inactive devices stay in accepting 0.
When no prefix fits the reserve, bounded direct sampling handles short words.
Save exact labels/final states, retries, uniqueness shortfall and distributions.
world.json includes every model; solver_input.json contains observations only.
No generator or provider execution precedes source/protocol freeze and review.
