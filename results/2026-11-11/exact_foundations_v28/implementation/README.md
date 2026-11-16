# C028 exhaustive reference solver

`reference.py` is a dependency-free Python 3 library, not a standalone CLI. The caller supplies a single record to `solve`. The exact keys are `alphabet`, `positive`, and `negative`. An alphabet ID is any distinct nonempty string; every word is an array of whole IDs, and `[]` is epsilon. Input alphabet order controls canonical block labels. Repeated traces within a label are deduplicated in first-occurrence order. Witness negative indices refer to that deduplicated `negative` order.

From PowerShell, in the repository workspace root, run this exact example (replace the Python executable path if needed):

```powershell
& 'C:/Users/Mahdi/AppData/Local/Python/pythoncore-3.14-64/python.exe' -c 'import importlib.util,json; s=importlib.util.spec_from_file_location("ref", "results/2026-11-11/exact_foundations_v28/implementation/reference.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); data={"alphabet":["door.open","µ sensor"],"positive":[[]],"negative":[["door.open"]]}; print(json.dumps(m.solve(data),ensure_ascii=False,indent=2))'
```

The example has two compatible partitions and one two-block optimum; the canonical recommendation is the singleton partition. `compatible_count` counts all fitting partitions, while `optimal_count` counts only maximum-block partitions. `UNIQUE_COMPATIBLE`, `AMBIGUOUS`, and `INCOMPATIBLE` classify the full compatible family. `optimal_unique` is a separate statement about the best partitions. Each witness supplies its RGS, blocks, finite local factor languages, and one rejecting-block index for each deduplicated negative. These are sample witnesses, not assertions about real-world ownership or the true number of devices.

`solve(data)` has no candidate budget. Its exhaustive mathematical procedure terminates for finite inputs with unbounded resources, but actual memory and time may be insufficient. `solve(data, max_candidates=10)` requests a limit of ten inspected partitions; if work remains at the limit, the status is `INCOMPLETE` with null mathematical fields. `INVALID_INPUT` and internal witness-check `ERROR` also return null mathematical fields. Contradictory labels give `INCOMPATIBLE` after validation. For empty alphabet the one empty partition has zero blocks; it is compatible exactly when there are no negative examples.

A short reproducible developer smoke check, separate from the independent audit and any official experiment:

```powershell
& 'C:/Users/Mahdi/AppData/Local/Python/pythoncore-3.14-64/python.exe' -c 'import importlib.util; s=importlib.util.spec_from_file_location("ref", "results/2026-11-11/exact_foundations_v28/implementation/reference.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); e={"alphabet":[],"positive":[],"negative":[]}; assert m.solve(e)["max_blocks"]==0; d={"alphabet":["door.open","µ sensor"],"positive":[[]],"negative":[["door.open"]]}; r=m.solve(d); assert (r["compatible_count"],r["optimal_count"],r["max_blocks"])==(2,1,2); assert m.solve(d,max_candidates=1)["status"]=="INCOMPLETE"; print("developer smoke: PASS")'
```
