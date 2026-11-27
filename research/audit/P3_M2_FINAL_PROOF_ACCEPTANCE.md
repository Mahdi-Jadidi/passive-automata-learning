# P3 M2 final proof-only acceptance audit

**Disposition — VERIFIED for Gate C on the four pinned producer certificates.** This is unrestricted structural exact search (B=0) on the two named raw inputs. Operational status remains **INCOMPLETE**. The benchmark gate and broader P3 integration sign-off remain separate.

## Sources and chain of custody

- The starting branch head was `d89bab4c005d17c8b27d4c1e6dd291135aca649a`. The proof jobs checked out that exact commit with only `tests/reference` materialized. The frontier verifier blob is `540a7cf9e7b048684d3ea03def744175ae629b65` and the independent RGS oracle blob is `da28e66ca4ff74388be79bf9549c8e02f0c60410`. The verifier imports the independent sample, journal and deletion replay kernels. The proof processes used the reference directory as their only project import path and had no producer checkout.
- The audit follows Integration Review 06 at `03634263d2c67b7496e55f194b5bf9e80ec87654` (blob `53b559f2409cfa62940064bd3ab0814225434469`) and the final flat, symbolic serialization contract at `ff61b1c56138c89fc0ad9a615f0b2a587b03393a` (blob `9dd487605f0dfdc6735f7d53a42627039fb57db8`). It follows up the earlier published-artifact, native replay, path coverage and RGS audits and the evidence in issues #2, #3, #5 and #11.
- The producer source checkout for all four was `391abf97df3b67661082c907d9ce20b4f69636c2`. The workflow checked the source metadata for `edr_search.py` blob `73da7bea551df73a8676b0adf0401cd7f2d307b5` and `edr_bb.py` blob `657c4e0e4059b32cd9e6477e61c7a3673290f36d`. The expanded workflow ran at `f8de4b6b14b3840d699d3c47ccc06a71eb5e04ae` (workflow blob `1bde518e6e2036a74295f7287e54fc926f404687`) and explicitly checked out the same producer source. Its `run_case.py` harness blob is `9dd3c684dcae20dc5dec946878d61ac9647eb535`.
- The [proof-only run](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45627330072) used [the audit workflow](https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/9cf730e711e3fa703c61eccc36dc1c9b72e0caa7/.github/workflows/p3-m2-final-proof-replay.yml) at `9cf730e711e3fa703c61eccc36dc1c9b72e0caa7` (workflow blob `51373ff3f79458976b97eba9dc3f48d66b609690`). Each job checked artifact ID, associated run and run head, then recomputed the ZIP SHA-256 before extraction. It streamed the exact members through SHA-256 and Git blob hashing and matched the raw and certificate pins independently of the producer manifest. It compared the exact journal and trusted-scope member pins to the manifest and rebuilt trusted scope byte-for-byte from the raw input and journal. Both pinned journals contain zero events and independently yield identity E0 over the full ordered alphabet. The certificate scope digest binds the independently reconstructed raw traces, original IDs, selector scope, exact journal digest and root owner.

| Input / mode | Producer run / artifact | ZIP SHA-256 | Proof job |
|---|---|---|---|
| tiny_choice / one | 45592454384 / 15011318454 | `6172c5f5b5107292ce48a9b0326b3797fa97b25f88034d8e105a561acd2bda92` | 139250899366 |
| tiny_choice / all | 45592454384 / 15012345186 | `a70e1874acd43f44b77bea97356eb91ed59e8557c4c116422ab5e9ee05ae3d2f` | 139250899673 |
| small_choice / one | 45592454384 / 15011812225 | `4f3642287acd18b12e183a4f8e2cf023ecfe2e1cc22c01a19627243025dd3387` | 139250899866 |
| small_choice / all | 45593819618 / 15013931205 | `ebbdf7655c7dd6b8935783c12f3d1f2165c00c88f1afc15a366654f45af9dd11` | 139250899671 |

| Exact member | Bytes | SHA-256 | Git blob identity |
|---|---:|---|---|
| tiny_choice raw | 228 | `1c064aa4c7ce111ec8c403e8b6a05b64de5acdec2ef564861f06c2e2e2e42f23` | `ef3f41b4c5e27da6ffd4882804399abf454d51a7` |
| tiny_choice journal | 130 | `290c8490b2a4ab5b4c6f49012c7580152ecc6eb7c4bad036bcf71b91925c48f5` | `3a50ce7567b563fa87dc54395451af58b19d75fa` |
| tiny_choice trusted | 560 | `9a43619ffabac9c44e65e69ccc0fc7e5c30033e021625582aa6e31668bdcd172` | `adf7723aa76cdf9bed09e9d42c65511c8c1e8ae8` |
| small_choice raw | 416 | `10b0c3534ddf42369db003bca6b323c9fdaa33cd36aa15031360c3428949931b` | `b361642873a73bae454d388cbfb2284559dbd69b` |
| small_choice journal | 130 | `3d4ae1a0cff38cbc7b1bf7a2269c29a256abe205b7efc8f7ed3a31eb17334019` | `191247f1112e15ccc571656026e6591b42a13d3b` |
| small_choice trusted | 754 | `89ade477b7f9029acdf8c44b4fe5d1f724038cd795c28b289cd2154e387c841b` | `616e0b864a0119a333bcb8d3248bec0d871bc6f4` |
| tiny_choice / one complete certificate | 46,588 | `91996d9bc6a3d7e88b5c89fc44158bc1cd89cf778256ec67839e1d38555e7ec8` | `bce55d7db1ddbcf6140b2a841f74bb51dad8f2f0` |
| tiny_choice / all complete certificate | 99,931 | `1be8394e233fe2c5a337766d73a1385145ab82b95d75273d5d548f60b2b781c0` | `eafd651d28fc1f06f60bdbc4c0a4095a04dc390b` |
| small_choice / one complete certificate | 264,463,193 | `dafa72f9e8ec4cc63330d4a7cd420cd478237dd7431c7e488267345ed810471e` | `d1539a0a9ed03d208a88c515c51f6e6473126c3c` |
| small_choice / all complete certificate | 1,399,367,871 | `9fb5f5bbc1c64e90bc955f73d2325a1d159224e91258e8a8758a34595102e2a7` | `e2f00717be846336b1f3287a8dd58070272434fd` |
| tiny_choice / one one-entry checkpoint | 574 | `038c9089d72afe3d13e2f42b37366d235070ecf98c33e2940641fd094e0b3f3c` | `a74b5b92d7e8adf1c8b2da0b8b0acb7f5b0619ed` |
| tiny_choice / all one-entry checkpoint | 574 | `c8cfad9031f63526871ed806d3a45c36d81a068f416b3046bbf8da19705e06a2` | `ba8bd669c6e8b24127711109fa57cf9312a46dfa` |
| small_choice / one one-entry checkpoint | 588 | `8c0293e8f9cdc56db18d64f23a98e3d0208bcda5541a98f8d5fe9d8b5571a395` | `cd0a7fb4a3c11450661238ddf88eabecdc32e397` |
| small_choice / all one-entry checkpoint | 588 | `160a07dbccceeb7d24ecdbfea951da0691d22c0bde277457b041fb1b17dd3e27` | `d73c3d206dc3a5c626a8138c9727f915d4c75542` |

## Replay and exhaustive comparison

Ubuntu 24.04 and CPython 3.13.5. Each job ran fresh proof and oracle processes in both modes. The verifier replayed every certificate node and reconstructed first-true coverage from the checked emitted prefix, symbolic suffix and explicit residual. For every strict coarsening the first true pair is unique. The all-false residual retains E itself. The verifier checked the literal closure predicates and compatible incumbent. Base cost is `n - |classes(E)|`. A strict coarsening costs more, so FEASIBLE_MIN closes at E. The cost cutoff allows equality only in one mode.

The independent RGS oracle read only the exact raw input. It visited 203 partitions for tiny_choice (cost 2, four optima) and 4,213,597 for small_choice (cost 4, sixteen optima). One-mode incumbents belong to the independently enumerated optimum set. Each all-mode list matched the complete sorted RGS set. The oracle enumerates every restricted-growth string and evaluates compatibility using literal projection tuples cached per possible block. One-mode results leave the optima list empty as required by the wire contract. Normal and optimized verifier and oracle result JSON matched byte-for-byte.

| Input / mode | Nodes | Proof work | Exact checks | Proof normal s / KiB | Proof `-O` s / KiB | RGS normal s / KiB | RGS `-O` s / KiB |
|---|---:|---:|---:|---:|---:|---:|---:|
| tiny_choice / one | 221 | 60,140 | 215 | 0.05 / 20,880 | 0.15 / 23,772 | 0.02 / 12,300 | 0.11 / 16,532 |
| tiny_choice / all | 461 | 131,556 | 677 | 0.05 / 21,256 | 0.13 / 23,836 | 0.02 / 12,360 | 0.09 / 16,360 |
| small_choice / one | 1,091,642 | 457,570,571 | 659,914 | 72.08 / 2,026,092 | 72.49 / 2,028,568 | 6.80 / 12,596 | 6.91 / 16,532 |
| small_choice / all | 5,496,670 | 2,494,969,001 | 4,460,579 | 274.43 / 10,341,004 | 276.99 / 10,342,652 | 4.68 / 12,628 | 4.81 / 16,548 |

Per-case result JSON, full optimum owner lists, source pins and timing logs are available in [tiny_choice / one](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45627330072/artifacts/15028951137), [tiny_choice / all](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45627330072/artifacts/15029685868), [small_choice / one](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45627330072/artifacts/15029796231), [small_choice / all](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45627330072/artifacts/15028957880).

GNU `time` wall seconds and peak RSS KiB are per subprocess. Verifier work includes charging for the proof input bytes and is distinct from producer work. Oracle work was 2,140 units per tiny run and 28,579,558 per small run.

Commands from the pinned proof checkout, with each producer artifact extracted to `incoming`. The workflow records hashes, rebuilt scopes, result JSON, timings and exit statuses.

```sh
export PYTHONPATH="$PWD/tests/reference" PYTHONNOUSERSITE=1 PYTHONSAFEPATH=1
ulimit -v 13631488
ref="$PWD/tests/reference"
input="$PWD/incoming"
python -B "$ref/p3_frontier_verifier.py" --make-trusted-scope \
  --raw "$input/raw.json" --journal "$input/journal.json" \
  --out independent-trusted.json --seconds 30
cmp "$input/trusted.json" independent-trusted.json
# Repeat each timed invocation with python -B -O.
# The archive retains normal.json when optimized producer bytes are identical.
/usr/bin/time -f 'wall=%e RSS_KiB=%M' timeout -k 2s 660s \
  python -B "$ref/p3_frontier_verifier.py" --raw "$input/raw.json" \
  --journal "$input/journal.json" --scope "$input/trusted.json" \
  --proof "$input/normal.json" --seconds 600 --max-work 4000000000 \
  --max-exact-checks 200000000 --max-nodes 6000001 --max-entries 6000001 \
  --max-proof-bytes 2147483648
/usr/bin/time -f 'wall=%e RSS_KiB=%M' timeout -k 2s 120s \
  python -B "$ref/p3_rgs12_oracle.py" --raw "$input/raw.json"
```

The verifier also retained the default 64 MiB raw/journal limits and 10,000 path depth limit. The oracle defaults are 30 seconds cooperative, 4,213,597 partitions, 150,000,000 work and 100,000 entries. RLIMIT_AS was 13,312 MiB. RSS is measured separately. JSON decoding and allocation run between cooperative checks. The outer timeout bounds subprocess execution, and externally killed processes provide no proof result. These are enlarged validation limits. The 30-second/1,536-MiB benchmark profile is outside this disposition.

## Status and checkpoint audit

| Evidence | Observed proof disposition in both Python modes |
|---|---|
| Four exact EXHAUSTED products | Exit 0, VERIFIED, complete coverage and optimum evidence |
| Four exact one-entry PARTIAL checkpoints | Exit 2, INCOMPLETE, unresolved frontier, two nodes checked, no optimum result |
| Same checkpoints with only declared status changed to EXHAUSTED | Exit 1, INVALID, coverage contradicts declared status, no optimum result |
| Each complete artifact with a 1-byte proof cap | Exit 2, INCOMPLETE, input byte cap before any nodes were checked, no optimum result |

The one-entry checkpoints retain a root SPLIT with cursor 0, an explicit residual and a symbolic suffix [0,15) or [0,66) over the still-unemitted children. All four checkpoint members matched the producer manifest's exact size, SHA-256 and Git blob identity. The pinned producer logs and manifests report successful normal, optimized and resumed production and identical complete certificate hashes and lengths. The producer harness removed duplicate optimized and resumed copies after comparing SHA-256. Independent replay covered the retained complete bytes and the exact partial bytes under both interpreters. Resumption execution itself was observed through the producer run evidence. Its native unit job also passed the one/all restart test at every entry boundary of a small fixture in both Python modes.

The [earlier small/all product](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45592454384/job/139129871278) from run 45592454384 hit the four-million-entry cap and was PARTIAL. Its earlier verifier ran out of memory before checking nodes, and its capped fresh and resumed hashes differed. The expanded run establishes equivalence for the one-entry checkpoint resumed to completion under the enlarged budget. Equivalence for censored runs at every cap or arbitrary large restart points remains unestablished. The earlier 64 MiB frontier/proof limit runs also remain censored.

The pinned verifier and reference unit suite passed 12/12 in both Python modes locally and in [reference CI](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45627342359). The CI proof and test blobs were `540a7cf9e7b048684d3ea03def744175ae629b65` and `03f1a1f0bf4fe2026a5b23806d14d586e7128592`. Under its 1,536 MiB address-space limit, the reference suite took 1.23 s / 28,572 KiB normal and 1.58 s / 29,828 KiB with `-O`. The suite covered OPEN, UNKNOWN, a nonempty symbolic suffix, false PARTIAL, missing or forged child/residual/suffix, nonidentity journal binding and invalid root/journal, one/all cutoff differences, duplicate keys and the seven explicit cap tests (time, work, nodes, proof bytes, journal bytes, exact checks and entries). A separate local run of the pinned path audit with the full verifier budget implementation passed 981,816 membership checks over 5,385 regions in both modes. These expand coverage beyond the actual empty-journal inputs and one-entry checkpoints.

## Interface evidence and remaining scope

[Interface run 45597784081](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45597784081) succeeded at `e38e8015384e570f38f07e851001ba695fdb92e2`. Its gateway/contract suite passed 18/18 in each mode and its native suite passed 2/2 in each mode. The normal native step exercised all four artifacts and took 329.82 s at 10,341,116 KiB peak RSS. The optimized native step took 51.43 s at 2,028,580 KiB peak RSS. Its optimized native step exercised tiny one/all and small one. The interface tests verified proof before offline registration, matched the all-mode lists against the RGS oracle, preserved owner/sample identity and distinct request/attempt IDs, kept proof data outside journal/2, and checked invalid proof and UNKNOWN handling. The proof-only run above independently exercised all four artifacts in both Python modes.

This audit covers only the pinned M2 structural certificate acceptance gate under the measured budgets. Larger completed instances, nonempty-journal producer certificates at native scale, benchmark-profile completion, and operational learner acceptance remain outside the evidence. PR #8 remains draft and unmerged. The branch changes consist of the proof workflow and this audit report. The large input certificates are retained in Actions rather than Git. Reproduction depends on access to those artifacts and their retention windows.
