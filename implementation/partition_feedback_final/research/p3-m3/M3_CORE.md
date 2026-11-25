# M3 core implementation and replay

Authoritative review is `2ddf8b89d01dec5b3eb321d166de29360ebd93c0`. Core starts at `cae63a8f2b5dc022825e417ca96a24df23e5f342`. Use the separate M3 producer module to keep the frozen M2 source blobs and entry point intact. The new module also defaults to the frozen v1 producer.

```sh
export PYTHONPATH=implementation/partition_feedback_final
python -B -m selector_v2.edr_m3 --split-rule CROSS_SUPPORT_LEX_V1 \
  --raw raw.json --scope trusted.json --mode all --out all.cert.json \
  --metrics all.metrics.json --seconds 30
```

Resume with the same mode, rule and trusted scope plus `--resume all.partial.json`. Per incompatible node, the producer visits negatives and positives in original array order, then tries singleton and pair supports in lexicographic order for those two words. It stops at the first completed disjoint pair for one negative or after 4,096 discovery work units. Discovery compares original token sequences after deleting entire current classes. A local discovery cap falls back to all-pairs. A global cap before split admission leaves the node OPEN. Cross families store sorted supports and one indexed row per endpoint. Typed ancestor prefixes preserve original IDs on mixed paths. Once admitted, the split and conflict residual are always present together and the cursor commits only with its child.

## Replay pins

- Independent verifier commit `f24d34c6e812b23c3dbe8953a6f592653b44958e`, verifier blob `2f66ef48353ce3c240e359b797b72bea352b2fc9`. The same checkout supplies journal replay and the full RGS oracle.
- `evidence/normal/manifest.json` gives exact SHA-256 pins and byte lengths for raw, exact journal, trusted scope, complete and one-entry partial proof, independent verdict and RGS result. `evidence/optimized-manifest.json` records the corresponding Python 3.13.5 `-O` run. Both modes matched all 40 per-case JSON files byte for byte. The gate reloaded the serialized partial checkpoint and compared the completed resume bytes with the uninterrupted certificate in both Python modes.
- The independent verifier returned VERIFIED for every complete certificate, INCOMPLETE for each one-entry partial and byte-cap control, and INVALID for each partial relabeled EXHAUSTED. The journal-root fixture contains one RAW event produced by the existing component closure. Independent journal replay derives `[0,0,2,3,4,5]`. Its native v2 certificate starts with a cross split at that contracted root. The mixed-path fixture starts with all-pairs and has cross descendants.

| Case | Optimum cost | All optima | RGS partitions | Nodes one / all |
| --- | ---: | ---: | ---: | ---: |
| tiny_choice | 2 | 4 | 203 | 10 / 10 |
| small_choice | 4 | 16 | 4,213,597 | 46 / 46 |
| journal_root | 2 | 2 | 203 | 4 / 4 |
| mixed_path | 1 | 3 | 52 | 18 / 35 |

For reproduction, add the pinned proof checkout's `tests/reference` to `PYTHONPATH`, then run `python -B implementation/partition_feedback_final/research/p3-m3/run_core_gate.py --output normal` and repeat with `-O`. The Linux CI matrix enforces separate 512 and 1536 MiB address-space limits and measures maximum RSS. The committed local manifests used the 30-second producer limit without an OS memory cap.

Both CI profiles passed for the producer and independent replay on all four fixtures and modes. Peak RSS covers the full gate process, including the RGS oracle, and is reported in KiB for normal / optimized Python. All 40 per-case files matched the committed evidence byte for byte in both profiles. [Actions run 45636477920](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45636477920)

| Address-space cap | Peak RSS | Entire gate wall time | Artifact ID |
| --- | ---: | ---: | ---: |
| 512 MiB | 21,468 / 25,516 KiB | 7.03 / 7.36 s | 15033895739 |
| 1536 MiB | 21,376 / 25,432 KiB | 4.08 / 4.08 s | 15032494625 |

In a separate capped smoke test, `medium_choice` and `huge_choice_active` from benchmark commit `369c0bc3` reached TIME_CAP at the OPEN root in both search modes (Python 3.13.5 normal, five-second producer limit and one-entry allowance). Independent verification returned INCOMPLETE throughout. The paired seven-case performance evaluation belongs to the benchmark stream.

## Checkpoint accounting

On frozen M2 `small_choice:one`, four admitted entries yielded five nodes and 565 charged bytes. A fresh 3,072-byte frontier cap yielded 19 nodes and 3,015 charged bytes. Resuming that checkpoint under the same cap yielded 21 nodes and 2,862 newly charged bytes, or 3,427 when the old 565 bytes are included. The retained proof table survives resume while M2's byte counter starts at zero. The v2 accounting restores retained admission payload before charging any new entries. A fresh and resumed v2 run at the same 5,000-byte payload cap produce identical partial bytes and retained-byte counts. Admission payload is a deterministic proxy covering split metadata, residual, child, child reference and cursor record. Process address space and RSS are measured separately.

An entry budget is an allowance for new entries in that invocation. Four plus four permits eight admissions, and matches fresh eight, while fresh four stops at five nodes including root. Work limits charge each invocation's actual work. On the same M2 fixture, fresh work 2,000 reached 13 nodes. Reserving 1,114 units for the initial checkpoint and granting 886 for its continuation reached nine nodes. Restart reconstructs the path, validates the incumbent when present, and skips closed projection work. V2 also restores payload charges and rebuilds committed pair families. Equal cumulative work and renewed work can therefore stop at different frontiers. The tests cover exact completion across single-entry renewals and work/byte interruptions. M2 accounting remains frozen for the baseline.
