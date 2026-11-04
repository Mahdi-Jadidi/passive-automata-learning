# Baseline profile B/knownK8: partial counting evidence

Read-only interpretation of auditor capture
20261104T115044.098333Z_bf17ed56cb. No new runtime was launched by this worker.
Profile source42af21debce9e878584c322ed361221de558f86fa287e8f9760d46fbc40e4969
and baselinec288448f4a11849f74293b13201fdc578a79e6fbbe24165684807bd32ceeb83d
were bound in the auditor receipt. Input B hash is
c5f3e08d5891207b8fe27ba540c1ee73c375883238cdf73cd0b16d4a326ef107.

Sources under ../audit/profile_baseline_B_K8_v1/:

| File | SHA-256 |
|---|---|
| receipt.json | `f13f147055fee7419a6e0d59cdd4412d47c77cb5c18e306772fc64ef8fd9eff2` |
| functions.json | `b8215bc2b8cc903f3d31a9425fa6c65e6e28a3dbb150379ea4055e3118a920ba` |
| result.json | `1f3c1690fcd2d5ca5ff5ee29b5bfc04e9d6f16e4ba30dfd6496144884c01db20` |

Soft deadline5seconds includes reading/import. The gate returned unresolved;
its solver timer was4.3422273seconds. It committed13145172 valid characters,
completed817count chunks, and Counter had processed13160606characters at
interruption. No graph pair, projection, complete candidate or DFS node was
reached. This is computational incompleteness, not a data-insufficiency finding.

The top-own profile entry _collections._count_elements took4.0502933seconds
inside profiled solve cumulative4.342257seconds. solve-own was0.1412606,
Counter.update-own0.0342237 and poll-own0.0278209. The outer profile process
receipt is5.0186046seconds; auditor capture cost additionally includes capture
overhead and is separately charged. These boundaries must not be conflated.

This establishes that count work dominated THIS TRUNCATED PREFIX under
cProfile. It says nothing about graph/projection/search dominance after the
count pass and cannot justify projection translation as candidate2 by itself.
Profiling overhead is not an end-to-end benchmark. No general speed claim or
asymptotic conclusion follows.

Master authorized exactly one further auditor profile of A/knownK4 with20soft/
25hard to observe later stages. Candidate2 selection waits for that result;
there is no additional worker run, candidate2 source or third optimization.
If counting remains the observed target, native repeated str.count for a
bounded alphabet could be a mathematically exact second-slot alternative, but
its O(mT) work and first-occurrence/validation costs may lose. It is not assumed
faster and has not been implemented or tested here.
