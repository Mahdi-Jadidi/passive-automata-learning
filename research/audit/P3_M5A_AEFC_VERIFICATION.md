# M5-A independent named AEFC verification

Contract commit `e7a5993e3593d99e7d19ac30ebf31e9b6bbde92e`.
Proof baseline `98e913a7e15d32638319832fc69edb36edb2f505`.
Native producer `3fcb278d6562b76e5c75936425b39c57d02f2409`, module blob
`eeaa1226c5294c8c0752d68b4995113a4ec0acda`, retained fixture tree
`cf9a4522baf790b48aa3e62cb02d6972d5397731`, gateway interface
`edc6425b4560652b66d3342a6d9ec53b9c307efc`.

The independent checker replays the exact journal/2 bytes, reconstructs
original source blocks from the validated registrations and checks cited
table identities. It requires canonical JSON, one entry per target block
and one negative throughout. Each ATOM_MATCH checks every unary and binary
atom in order, a simple path to a common positive for that block, licensed
named-zero or free-group edges, and literal ordered projections on both
the source and the final target. ZERO_CONTAINMENT checks the table zero
and an independent literal lookup without assigning an ID to anonymous
evidence. Only a complete proof yields VERIFIED with STRUCTURAL_NO.
Invalid inputs and exhausted replay budgets carry no result.

| Fixture | RGS targets | Literal NO | Containment NO | Verified named NO |
| --- | ---: | ---: | ---: | ---: |
| named | 15 | 10 | 4 | 5 |
| cross-id | 52 | 37 | 9 | 10 |

All 15 emitted sidecars verified. Each distinguished stitching target was
outside the independently counted containment closure. The cross-ID path
uses N0 to N1 on a free group and N1 to P0 on a named zero, with N0 and N1
distinct positional IDs for duplicate words. The proof tests also reject
a guessed anonymous edge even where the guessed projection is literally
equal, a bounded observation on a compatible repeated-symbol target, and
the use of different negatives on different blocks of a compatible
target. The producer export is separate from the checker. It uses genuine
offline registrations and simulator observations and made zero external
learner calls.

Exact bytes and hashes are in [m5a-native](m5a-native) and
[M5A_SHA256SUMS](M5A_SHA256SUMS). The eight primary artifacts match the
producer's retained files. Those eight, the two complete target matrices
and the four control inputs were reproduced byte for byte under both
interpreters.

From the proof checkout, set PYTHONPATH to the pinned producer implementation
directory, pinned interface p2 directory and proof tests directory for the
separate export processes.

    python research/audit/p3_aefc_export_native.py NORMAL
    python -O research/audit/p3_aefc_export_native.py OPTIMIZED

Clear that producer PYTHONPATH for proof-only verification. Use Python
3.13.5 for all commands.

    python -B -m unittest discover -s tests/reference -v
    python -B -O -m unittest discover -s tests/reference -v

The proof-only workflow runs each full suite with a 1536 MiB Linux
address-space limit. The existing exhaustive minima-prefix test now has
a 120-second test budget because its 30-second budget expired in the first
local optimized run. Search and verifier defaults retain their original
budgets.

The snapshot check is mathematical replay of the recorded bytes. It does
not authenticate remote observations. In-process limits are cooperative
and a hard deadline and address-space limit require a process boundary.
The two small-alphabet histories measure soundness of emitted proofs and
incremental containment coverage. They do not establish completeness or
large-scale performance. No pruning, registration, acceptance, or journal
schema change is attached to the verifier.
