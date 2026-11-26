# Review08 M4 core evaluator

The immutable evaluator source is commit `140b4e51f89baf8c3e38e18d704d8c4d36c24f39`.
Its driver blob is `fc9ea03e0bd008d528bf115a5b5b8e7eb13ce2b8`. The evaluator blob
is `9aa23be274907a9c178869670abf6bef982fed23`. The separate entry point uses
the M3 traversal with two evaluator calls instrumented and independently selectable.
The frozen M3 producer blob remains `6dd0bdbc2d9436c2eeb15cc0812cf8a6fcf18655`
at source commit `9a361f6fa59414cc0ac262154d87c37f5aed0403`. The original v1
entry point and M3 CLI keep their existing defaults.

| Experimental flags | Compatibility | Witness discovery |
| --- | --- | --- |
| none | frozen dense | frozen literal |
| `--sparse` | sparse | frozen literal |
| `--join` | frozen dense | singleton join with frozen fallback |
| `--sparse --join` | sparse | singleton join with frozen fallback |

For positive words the sparse evaluator stores nonempty ordered projections of
original IDs and counts each word occurrence in the presence totals. For a
negative word its touched groups are checked against the corresponding sets.
An untouched universal positive group rejects that negative's epsilon
projection. Comparing the count of touched universal groups with the full
universal count accounts for all untouched groups. Empty label sets and the
empty alphabet are checked explicitly. Scratch estimates are deterministic
admission charges with a separate 64 MiB default. The existing frontier cap
bounds serialized admissions. The Linux CI address-space cap is a separate
process constraint. Work counts report the native charging of each evaluator,
so equal numbers do not imply equal wall time.

The optional SDJ-IDA pass indexes the three singleton-deletion join cases
(touched on both words, on the negative alone, or on the positive alone).
Full raw equality is tested by the existing label-conflict preflight.
Equal signatures only select candidate pairs. The pass checks each proposed
witness by deleting entire quotient classes and comparing literal original-ID
sequences. It needs two distinct classes for the same negative and then emits
the existing cross-support witness. The local work default is 250,000 units.
On a local cap or a miss, frozen discovery still runs, including its size-two
supports. Join arms may choose a different valid witness and therefore a
different certificate or one-mode optimum. Save the flags and local limits
alongside a checkpoint when testing deterministic resume.

## Reproduction

Use CPython 3.13.5 and independently pin the proof checkout to
`316d4430538b8a9ef0c707b8c46727a830d42321`. Its frontier verifier and oracle
blobs are `52e83aa9fdc952aacd7955e6d4ec1783e2fa4030` and
`da28e66ca4ff74388be79bf9549c8e02f0c60410`. Pin the raw fixtures to
`8484b8bff5b93e1be3a7924697161efc34e481d8`. Use a source-only proof directory
and the raw-only fixture directory. No expected answers go to the producer.
From the core checkout, with those independent directories staged:

```sh
M4=implementation/partition_feedback_final/research/p3-m4
export PYTHONPATH=implementation/partition_feedback_final:independent-proof/tests/reference
python -B -m unittest discover -s "$M4" -v
python -B "$M4/run_native.py" --memory-mib 512 --output native-512
python -B "$M4/profile_raw.py" --memory-mib 512 --case hdfs_1024 \
  --fixtures frozen-fixtures/benchmarks/v2/p3/inputs --output profile-512
```

Repeat with 1536 MiB and `python -B -O`, and run the raw profile for
`hdfs_holdout_1024_uncapped`, `medium_choice`, and `huge_choice_active`.
The raw profile runs both search modes and the four evaluator combinations.
Linux CI retains native proof, partial and resumed bytes, raw profile proofs,
and phase metrics. [Core gate 45831657443](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45831657443)

The separately measured RAW pipeline uses the `RegisteredLedger` blob `092507fc156e604be242e3100117fedc27b96d04` and
the adapter and strict parser from `122844ee5668f1c898f85b08133a562f31719718`
(adapter blob `c38e441c7327a44adad8a0fe1125d45c93e8ef69`, parser blob
`a66975de137e3ec556b8c7aacd108cf975c46344`). Put that checkout's
`research/interface/p2` on `PYTHONPATH`, then run:

```sh
python -B "$M4/profile_pipeline.py" --mode one \
  --raw frozen-fixtures/benchmarks/v2/p3/inputs/hdfs_1024.json \
  --output pipeline-hdfs-one
```

The pipeline has a 30-second hard limit per stage and a 120-second total
limit. It measures closure, ledger export, independent scope derivation,
sparse search and independent replay. It feeds only the emitted journal
to the independent scope stage. The resulting huge journal is newly generated
evidence.

## Accepted core evidence and remaining review

The four native cases cover tiny and small choice, a genuine merged journal
root and a mixed-rule path. In each of normal Python and `-O`, all 32
case/mode/arm combinations verified and matched their own completed resume.
On these cases, all four arms produced the same complete bytes per case and
mode. The independent checker also verified the complete and resumed
artifacts, returned INCOMPLETE for each genuine partial, and matched the
literal RGS optimum and optimum sets. The byte pins for the three artifact
types are in [native-pins.json](evidence/native-pins.json).
[Independent replay and RGS report](https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/a563e1b54f5e3c57edcb7d74cde96259fc7d3fc1/research/audit/P3_M4A_INDEPENDENT_REPLAY.md)

A separate Windows one-mode pipeline reached a RAW fixpoint on all four
fixtures. Independent scope derivation succeeded on medium and both HDFS
inputs. Their sparse searches were partial, and independent replay was
INCOMPLETE. The huge run produced a 3,333,809-byte authoritative journal
with one contraction. Independent scope derivation hit its deadline before
search began. [Local pipeline records and hashes](evidence/local-pipeline.json)
The benchmark pipeline independently rebuilt the contracted medium and huge
scopes under Linux. Its frozen M3 search and independent replay remained
incomplete at the stated caps. [Benchmark pipeline report and retained roots](https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/a07ae8ebd7365a01f411524f1feb10e939d3d03c/benchmarks/v2/results/review08/REPORT.md)
[Benchmark pipeline CI](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45832542233)

The original huge raw run reached the 64 MiB scratch admission cap before
finishing the sparse root check. In the separate Windows one-mode diagnostic
with 256 MiB scratch allowance, the root resolved as incompatible after
732,013 charged units at a 70,426,528-byte scratch peak. Search subsequently
reached its 25-second cap and retained a partial frontier with 17 nodes.
This diagnostic had no Linux process address-space cap. The frozen proof
reason `FRONTIER_CAP` represents the memory stop in the default-scratch run.
Check the index and frontier counters to attribute that stop.
[Expanded scratch record](evidence/local-huge-expanded-scratch.json)


Agent #4 independently profiled the exact producer pin on all seven raw fixtures
with the guarded sparse verifier. Both verifier modes returned INCOMPLETE on
all 96 large-fixture runs. The root work below is charged work in the producer.
A completed root check establishes the predicate only at that owner.

| Fixture | Dense root work | Sparse root work | Result of sparse root check |
| --- | ---: | ---: | --- |
| Medium | 9,963,699 | 69,472 | Incompatible |
| Huge | 9,691,999 | 477,452 | Scratch-capped |
| HDFS | 939,070 | 87,509 | Incompatible |
| HDFS holdout | 897,461 | 88,444 | Incompatible |

Dense root checking was work-capped on medium and huge. Sparse reached
discovery on medium, where the join found a witness but consumed more of
the search budget. Across the HDFS runs, join spent about 6.4Ã¢â‚¬â€œ6.8 million
charged discovery units and yielded zero or one hit per run. These profiles
admit no time-to-optimum conclusion. A forced-signature-collision control
also confirmed that the join rejects unequal complements and still accepts
genuine equalities. [Benchmark ablation report](https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/4e89007654ef0ca4ceaed255199ab046577e9bb1/benchmarks/v2/results/review08/REPORT.md)
