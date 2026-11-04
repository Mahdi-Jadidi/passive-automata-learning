# C1 source preparation before runtime adoption

The initial PROFILE_AND_SELECTION_V1.md proposed waiting for a baseline profile
before creating a candidate. The master subsequently requested C1 source soon
for parallel static review while the auditor prepares the approved fixtures.
This note preserves that change in staging; it is not an observed profile.

C1 was selected for source preparation by static necessity: an adjacent swap
cannot change length or Parikh counts, and validation has already computed all
these counts. Reusing them needs no new input-character pass and preserves the
original exact checker. Runtime adoption/performance claims still depend on
baseline profiling, independent correctness and preregistered comparison.

No profile/provider/generator was executed by this worker. The auditor owns
fixture generation and timing; no duplicate generator was implemented. The
approved A/B/C/D fixture definitions and six cells supersede the earlier
unimplemented world-generation discussion. No failed generation run exists.

C1 uses the first of at most two optimization slots. The second slot remains
unimplemented and conditional; rolling index, projection translation and RGS
envelope are not three implemented candidates. All C018 sources and the
public CLI remain immutable. Paper work stays paused.
