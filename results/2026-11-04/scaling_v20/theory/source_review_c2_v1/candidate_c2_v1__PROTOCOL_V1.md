# C020 candidate C2: C1 plus exact chunked projection

Same observational API, optional externally trusted --known-k, compact output
contract, logical proof routes, witness contents and CLI as C018/C1. No hidden
world/model file is read. Source is frozen before runtime; independent static
and correctness gates precede master-authorized timing.

After GO, from repository root:

```powershell
python -B -X utf8 results/2026-11-04/scaling_v20/implementation/candidate_c2_v1/partition_gate_v1.py INPUT.json --seconds 20
```

C2 preserves C1's exact validated Parikh grouping. The only additional
optimization is native str.translate projection using ord(symbol)->None for
declared symbols outside the current block. Tables are per mask computation,
words are projected in16384-code-point chunks with cooperative polling, and
chunks are joined in order. All original input validation remains mandatory.
No Unicode encoding or lexical interpretation of input symbols is used.

Source/motivation/proof and counter semantics are in
../C2_ARGUMENT_AND_PROFILE_V1.md. The CLI is byte-identical to C018/C1 and
loads its colocated gate_v1.py. C2 method label is
C020-parikh-native-projection-gate-c2-v1. Added work counters are
projection_chunks and deletion_tables_built; completed projection_characters
totals are logically identical to baseline. The rest of C1 metrics stay.

Only certified_unique releases a selected partition. Ambiguous still returns
two valid alternatives, incompatible requires complete proof, and unresolved
is computationally nonfinal. Assumptions and physical-interpretation caveats
are unchanged. No output field/evidence was dropped to improve timing.

Auditor owns existing fixtures, independent replay, capture and timings.
Keep20s soft/25s hard and <=600seconds/provider, including charged diagnostics
as preregistered. All censored/error/regression cells remain. This is the
second/final candidate slot; no third optimization or full heavy grid follows.
