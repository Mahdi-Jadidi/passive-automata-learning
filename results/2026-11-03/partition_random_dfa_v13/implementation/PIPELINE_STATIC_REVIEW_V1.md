# Frozen pipeline static review

Reviewed `run_case_v1.py` without executing the helper, generator or provider.
Source SHA-256 is
`d4972b7074e550352eb3c7ad63bda990e7cfb9a13b755da3fb3ceb3ffded91f4`,
matching PIPELINE_READINESS_V1.json. No frozen source was changed.

No runnable-path or source-binding defect was found by inspection:

- HERE resolves to C013 implementation/. HERE.parents[2] resolves to results/,
  so BASELINE selects results/2026-11-02/partition_unrestricted_v10/implementation/.
  Both selected C010 files exist, and their hashes match the constants:
  solver `4c7959e96c02023d85943c8c52fae3f198c0de67ea172a72ad0669485f60c502`;
  CLI `3140df25bab5d60c6c2705098029db9061e3c9d76743bf1dfd48d46aaf2d5eaa`.
- The generator binding matches its unchanged SHA-256
  `0b649344035f449b0a17cd6410dd41db67c6b1e06025b78262807740b93ba410`.
- Explicit script paths and the calling interpreter are passed as an argument
  list with no shell. The C010 CLI imports its colocated unrestricted_solver_v2;
  C011 is not selected. Observational input uses an absolute path.
- The wrapper passes all required generator arguments, then only the
  solver_input.json path and time/enumeration flags to the baseline. It never
  opens world.json. In reuse mode no generation command is issued.
- Each invocation uses a fresh UUID run directory and saves raw streams.
  The subprocess timeout path records a hard timeout; it cannot set complete
  true without a zero exit code and complete JSON result. Enumeration is
  explicit, and full_partition_listing additionally requires a list result.

This is static inspection, not a smoke-run result. Existing auditor controls
validate their own saved executions and cannot be attributed to this helper
without a captured helper run. Preflight CLI/integrity failures occur before a
run directory is created, as documented by the distinct exit-2 behavior.
