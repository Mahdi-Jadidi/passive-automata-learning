# P3 raw-only fixture recovery

The seven-fixture manifest is the existing `input-manifest.json` (Git blob `68d2414bd7e1f9294a850268369a55559d440b06`; raw SHA-256 `b69986b320ea9f328e0c107696e6ff4d9f2c71efc0624a6859c98295f16389ba`). Its entries match the original bytes recovered from the two source archives below. The raw JSON files are input-only: exactly `alphabet`, `positive`, and `negative`.

| Fixture | Input SHA-256 | Alphabet | Positives | Negatives |
|---|---|---:|---:|---:|
| `tiny_choice` | `1c064aa4c7ce111ec8c403e8b6a05b64de5acdec2ef564861f06c2e2e2e42f23` | 6 | 2 | 2 |
| `small_choice` | `10b0c3534ddf42369db003bca6b323c9fdaa33cd36aa15031360c3428949931b` | 12 | 4 | 4 |
| `medium_choice` | `abdce6ec6d39f21d845dabe409e6978f38f4bcb4871854cf82e55507ccb9862f` | 1,000 | 1,000 | 1,000 |
| `huge_choice_active` | `0be60da81326bcd8974da1df07e018e60dcd62714123b884c873ed3be782beba` | 100,000 | 10,000 | 10,000 |
| `hdfs_1024` | `7d076991e9ba118b98226a64d9551cd5c6df5d0797183d2e8a95ed896b057075` | 29 | 1,024 | 1,024 |
| `hdfs_holdout_1024_uncapped` | `238d37c4588f1a8506275859ede5cf6a5225630bb3454c016568ff7e2ae5ff6c` | 29 | 1,024 | 1,024 |
| `cover_path_8` | `948f306e7509babd3d054a02e8df4b1232a30147305183edb8f7937e3ccc6fc7` | 16 | 8 | 7 |

## Exact source and recovered archive identities

- Original planted source archive: `partition-planted-benchmark.zip`, SHA-256 `5d2dae2ca718cc65d48e5fbcb62480baeae0da35d37edb9184ba2b61d91e1dc4`.
- Original pinned-evidence source archive: `partition-scale-handoff-a3a4afba.zip`, SHA-256 `79791dea6e84370ef852709edd6680bb8d371299f2a84bea58e0d4ad4efc6541`.
- Original enhanced-scale archive (validated by the committed recovery script, not used to construct these seven inputs): `partition-scale-improved.zip`, SHA-256 `595f928ef085f8decc9533404eeb3a8b458ff4e82e527e80d889c20fa55946ca`.
- Recovered input-only ZIP: SHA-256 `a280e093aa298af359f0e30408b633eefb0283e02471dba52f3d78f1e4059220`; Library path `/Passive learning research/p3-exact-search-inputs-recovered.zip`.
- Recovered evaluation-only ZIP: SHA-256 `8d3da1c67975edd2209fd69f7fa9c403d613c97bf55293bb57dd2c8012a30982`; Library path `/Passive learning research/p3-evaluation-recovered.zip`.
- Evaluation index remains the committed file `evaluation/index.json` (Git blob `289b7bf33b9d5e47eb863fb7099d1c22722f0722`; raw SHA-256 `c76b45136570f839a32d75e3138c56d23b0728e4c145354a08b88a91c1b32ccb`). It contains reference hashes/costs and must remain evaluation-only.

The recovered ZIPs are newly assembled containers; the seven member input bytes are the original bytes and match the committed input-manifest SHA-256 values. Do not confuse a new ZIP-container hash with the hash of the historical ZIP container.

## Reproduction

From the repository root, use the already committed extraction scripts and the original source archives:

```sh
python -B benchmarks/v2/recover_inputs.py /path/to/original-archives /tmp/recovered
python -B benchmarks/v2/review03/prepare_p3.py /tmp/recovered /tmp/p3-fixtures
```

`/path/to/original-archives` must contain the three exact archives pinned in `recover_inputs.py`. The first command verifies archive digests and pinned Git blobs; the second verifies all seven raw input hashes and reference costs, then writes `inputs/` and `evaluation/` separately. Only `inputs/*.json` may be passed to the solver. Never pass the evaluation directory or index to a solver process.

The benchmark runner and measurement-only adapter envelope are documented in `benchmarks/v2/P3_BENCHMARK_PROTOCOL.md`. Integrated P3 runs remain gated on Agent #2's producer CLI and Agent #3's independently replayable proof interface; do not benchmark a mock adapter as an algorithm result.
