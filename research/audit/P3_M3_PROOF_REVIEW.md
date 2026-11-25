# M3 independent proof audit

The verifier implements Review 07 on the proof branch starting at
`a3b04c3d822ea445b77adc2b30d8984d3f5819b5`. It uses the frozen v1 header,
scope, exact journal replay, cutoff and result grammar. v2 adds only the
checked cross split and its atomically committed conflict residual.

For each current class, the smaller original ID from each support determines
its least internal normalized cross pair. Comparing that pair to the first
excluded alternative detects an internal prefix disequality. The verifier
uses the complete original support arrays after descendant merges. It checks
every emitted edge against the indexed family, retains the symbolic suffix,
and enforces a direct cross-parent bind for the conflict residual. No
producer code enters the proof process.

## Exact verifier gate

[Branch-push CI job](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45635333668/job/139279132881)
ran at `f24d34c6e812b23c3dbe8953a6f592653b44958e`. The verifier Git blob was
`2f66ef48353ce3c240e359b797b72bea352b2fc9`, v2 tests
`b52efbbe9aa1c87c3c405fbe0ba5c07279455a16`, and the n≤12 oracle
`da28e66ca4ff74388be79bf9549c8e02f0c60410`.

```sh
ulimit -v 1572864
PYTHONPATH=tests/reference python -B -m unittest discover -s tests/reference -p 'test_p3_frontier*.py' -v
PYTHONPATH=tests/reference python -B -O -m unittest discover -s tests/reference -p 'test_p3_frontier*.py' -v
```

| CPython 3.13.5 | Tests | Wall (s) | Peak RSS (KiB) |
| --- | ---: | ---: | ---: |
| Normal | 19/19 | 3.97 | 32,528 |
| Optimized | 19/19 | 4.21 | 33,904 |

Each mode enumerated 42,368 RGS partitions across the specified configurations
through alphabet size eight and compared membership in 1,628 reconstructed
regions with explicit original-ID constraints. Both orderings of mixed
ancestor rules occurred. The seeded sweep compared 305,186 minima-prefix
decisions with literal cross prefixes. The 20,000-symbol case verified three
nodes and two exact deletion checks for a symbolic 100,000,000-alternative
split before returning INCOMPLETE (2,014,181 charged work units). A real
nonempty RAW journal event in a test fixture proves a nonidentity root and
the v2 path lifts the deletion to the entire merged class.

Native acceptance uses the separately published producer archive, exact
byte comparisons of normal, optimized, checkpoint and resumed proofs, and
an independent original-alphabet RGS census. One-mode output is checked
against membership in the full optimum set, and all-mode output is checked
for exact set equality. Operational status remains INCOMPLETE.
