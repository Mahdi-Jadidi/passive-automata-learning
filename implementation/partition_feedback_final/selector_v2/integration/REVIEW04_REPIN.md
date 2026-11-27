# Review 04 — post-hardening P2.1 combined regression

**Decision:** core combined structural gate VERIFIED (exit 0), operational INCOMPLETE. No P3 implementation, merge, schema revision or external learner calls. Independent proof-stream review and lead authorization remain separate.

## Exact execution and publication

- Prior gate: c5e7e170add6f92e129099bf7444f5fd7a29eb3a (old proof pin; historical evidence retained).
- Repin commit: 7953d0665b2e1160ef54faedb945c2d65b16449e. Exactly three substitutions in run_final_gate.py; resulting runner blob 82b84b544894bd344436511a3778a26995bb6523.
- Actual checkout: a218ef37f4ad255ec5a9dde6e5a2cc650ceec4a3. Core dependency pin 796a83a5f8f69c4dc7c0db619e1cdb130ddc0b33; interface 0eb1050ad103bad2f93d3b9feb732bf94184f2a2; proof cf5a007571853b6cdf6259fa2a9a95f5c1e351f8.
- Exact hardened proof blobs verified in stdout: bounded_deletion.py e1fc61b6f03484d4428642ca157e2dac43f0572d; test_bounded_deletion.py 6de549b9b4d208be99a419c88fd903a1ce1a6dcc. All other pins unchanged; all listed source/artifact Git blob checks passed.
- Actual workflow [45562082178](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45562082178), Ubuntu 24.04, Python 3.13.5; job 139027944275 completed successfully. Output commit d578044a9ac91806d792b5e6cca7d65b86bd9370. Full outputs under [repin-cf5a007/](repin-cf5a007), including gate.json, stdout.log (exact blob checks), execution-pins.txt, exit-code.txt, time.txt, both modes' complete logs and artifacts. gate.json blob a289adef85a316961caf3f582582480ea8f9d888.
- Local git DNS failed; network-enabled GitHub Actions clean sparse checkouts were used instead. Initial workflow [45562037206](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45562037206) failed at Python setup because Ubuntu 26.04 had no matching 3.13.5 distribution; no tests ran then. Changed only runner image to Ubuntu 24.04, not Python version or semantics. Branch-scoped CI workflow added for reproduction and publication.

## Actual measured results

| Check | Normal | Optimized (-O) |
|---|---:|---:|
| Combined unittest | 40/40 (12.480s) | 28/28 (0.796s) |
| Independent boundary unittest | 3/3 (0.088s) | 3/3 (0.085s) |
| Total unittest methods | 43/43 | 31/31 |
| Hardened bounded deletion tests (included above) | 6/6 | 6/6 |
| Actual published artifacts independently replayed | 4/4 | 4/4 |
| Independent outer + delegated mutations rejected | 24 + 7 | 24 + 7 |
| Resource caps INCOMPLETE | 5 | 5 |

Both modes: false EXHAUSTED rejected; actual PARTIAL fails closed; operational INCOMPLETE throughout. Published-artifact audit output identical across modes (blob bd8fe292986140cd1aac340c13b1e7ab205abdf3). Synthetic hardened deletion: 4374 corpus-owner cases, 13122 filter checks, 500 random collision cases, 20000 diverse symbols, 20001 index entries, 2 exact checks, 200010 work units. Overall gate elapsed 15.34s, observed max RSS 147252 KiB; not an enforced memory cap or solver benchmark.

| Actual artifact | SHA-256 (uncompressed, both modes) | Structural optimum |
|---|---|---:|
| roundtrip | 14f0dc4cb606ca7f1b20a5cd575a937dd6471da594d983d86254e210573e5ab8 | 2 |
| adversarial | 1b78c4aefe974db58409cb186528af75b1981752ba0a3778634fe3bcb406e97c | 2 |
| interface-journal2 | caf40422d9d3e6d0cd8257da4b757cacd71cda1e6db089493421c912515edf94 | 1 |
| interface-journal2-epochs | adabd0b274ebaa2ce55aab7f874f6485664399d4b0df59b013d158cfb2338491 | 2 |

All four FIXPOINT, VERIFIED, operational INCOMPLETE. Exact byte agreement against committed originals and between modes. All ten subprocess checks exit 0; blockers empty.

## Reproduce in fresh worktrees

Use exact checkout a218ef37f4ad255ec5a9dde6e5a2cc650ceec4a3 for core, interface and proof commits listed above. From implementation/partition_feedback_final in core, on Python 3.13.5:

```sh
/usr/bin/time -f 'elapsed=%e maxrss_kib=%M' env PYTHONPATH=. python -m selector_v2.integration.run_final_gate \
  --interface-dir /absolute/interface/research/interface/p2 \
  --proof-dir /absolute/proof/tests/reference \
  --core-artifacts selector_v2/integration \
  --output-dir /absolute/fresh-gate-directory
```

The runner itself invokes normal and optimized subprocesses. Output directory must not exist; the CI publication workflow is a one-shot path for this checkpoint (manual reproduction uses a new directory; do not overwrite committed evidence). Historical final-gate.json and REVIEW03_FINAL.md remain historical old-pin outputs. The current machine-readable result is repin-cf5a007/gate.json.

## Remaining boundary

This is actual full combined regression, not merely isolated proof unit tests. It does not establish live external acceptance, transport authentication, cryptographic receipt trust, bounded-capacity optimization, durable recovery or huge planted-case scale results. Huge-case benchmark work is separate; independent proof-stream review of these exact executed pins is requested. P3 remains unstarted pending lead coordination. No changes outside the core runner, CI workflow and reproducible checkpoint evidence.
