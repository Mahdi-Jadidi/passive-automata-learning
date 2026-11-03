# CAV 2026 Artifact

**Paper title:** The Simulator's Blueprint: Automata Learning from System Event Logs

**Claimed badges:** Available + Functional + Reusable

**DOI (Zenodo):** [10.5281/zenodo.19828945](https://doi.org/10.5281/zenodo.19828945)

**License:** MIT (see `LICENSE`)

## Justification for the badges

No justification needed for Available (see the DOI link in HotCRP).

### Functional

The artifact replicates all main-text results of the paper. Source code for the BabyCyborg simulator, the RPNI-based automata learner, and the DFA evaluator is included, together with the raw CybORG traces and the recorded random orderings used to construct the paper's trials.

- **replicated:**
    * Figure 4: point (1)
    * Figure 5 and Table 2: point (2)
    * Figure 6: point (3)
    * Table 3: point (4)
- **not-replicated:**
    * Appendix experiments: out of scope for this submission; not part of the main-text claims.

### Reusable

The artifact is released under the MIT license. All Python dependencies are pinned in `requirements.txt`. The simulator, learner, and evaluator are independently reusable: scenarios, agents (YAML or Python), and monitors are drop-in extension points, demonstrated concretely in the "Example Runs Beyond the Paper" section. The reproduction pipeline also runs outside the Docker image via `install.sh`.

## Requirements

- **RAM:** 8 GB minimum (the large-scale learner in phase [4/6] can peak at several GB)
- **CPU cores:** 4
- **Disk:** 20 GB free (artifact .zip ~500 MB, extracted source tree ~7.6 GB, loaded Docker image ~8 GB, generated outputs ~1 GB; rest is slack)
- **Time (smoke test):** ~15 minutes
- **Time (full review):** ~12 hours

**external connectivity:** NO

We developed and tested the artifact on macOS (arm64). You need Python 3.9 or newer (the code uses `tuple[...]` type hints that require 3.9+).

If using Docker Desktop, verify that at least 8 GB RAM, 4 CPUs, and 20 GB disk are allocated under Settings → Resources → Advanced.

## Artifact Information

- `cage0/` — our small cybersecurity simulator (called BabyCyborg in the paper), used to generate the interaction traces for Table 3.
- `yaml_files/` — configuration files for the simulator: the network topology, the red and blue agents' behaviors, and the monitor rules that govern which actions succeed or fail.
- `sim_learn/` — the automata learner. `learn_automata.py` runs the RPNI algorithm to build a finite-state automaton from a set of traces; `visualize_dfa.py` turns an automaton into a PNG image.
- `evaluation/` — code for evaluating a learned automaton. `evaluator.py` replays traces through the automaton and reports how often its predictions match reality; `incremental_learning.py` repeatedly trains the learner on growing batches of traces to show how accuracy evolves with more data.
- `scripts/` — small command-line helpers: run a single simulated episode, generate or truncate traces, reproduce Table 3, and so on.
- `data/cage2/` — everything related to Figures 4, 5, 6 and Table 2. Contains the 5000 raw CAGE2 traces we used (`cage2_raw_traces/`), the script that preprocesses them (`convert_traces.py`), the script that slices them into training and evaluation sets (`build_cage2_data.py`), recorded random orderings that make those splits deterministic (`shuffles/`), and the cross-evaluation and plotting scripts (`tests/`).
- `data/one_host_network_validity_only/` — the training and evaluation traces used for Table 3, pre-generated and organized into three trials and four trace lengths.
- `install.sh`, `run-smoke.sh`, `run-all.sh` — the top-level scripts referenced throughout this document.

---

## SMOKE TEST

**All commands in this document run from the artifact root — the directory that contains `install.sh`, `run-smoke.sh`, and `run-all.sh`.** If you are using Docker, the interactive shell from the Docker step below already puts you there. If you are not, `cd` into that directory first.

### Setup — getting the 4 files into one folder

The artifact is published on Zenodo as four separate files:

- `cas-artifact-cav2026.zip` — source code, scripts, raw traces, and Table 3 input data
- `image.tar.gz` — the Docker image
- `README.md` — this file
- `LICENSE` — MIT license text

Download all four into the same working directory, then extract the zip:

```
unzip cas-artifact-cav2026.zip
mv image.tar.gz README.md LICENSE artifact/
cd artifact/
```

You should now be in the artifact root with `install.sh`, `run-smoke.sh`, `run-all.sh`, `image.tar.gz`, and the source dirs all present.

### Docker

The artifact is distributed as a Docker image (`image.tar.gz`). All Python
dependencies, the Graphviz system binary, and the artifact source code are
pre-installed inside the image — no additional setup is needed.

**Step 1.** Install Docker if you do not already have it:

- macOS: <https://docs.docker.com/desktop/install/mac-install/>
- Linux: <https://docs.docker.com/engine/install/>
- Windows: <https://docs.docker.com/desktop/install/windows-install/>

If using Docker Desktop (macOS / Windows), open Settings → Resources → Advanced
and verify that at least **8 GB RAM**, **4 CPUs**, and **20 GB disk** are
allocated.

**Step 2.** Load the Docker image from the archive:

```
docker load < image.tar.gz
```

This registers the image `cas-artifact:cav2026` locally. You can verify with
`docker images | grep cas-artifact`.

**Step 3.** Run the container. There are two options:

**Option A — run a script directly** (recommended for reproducing results):

```
docker run --rm -v "$PWD/output:/artifact/output" cas-artifact:cav2026 bash run-smoke.sh
```

Swap `run-smoke.sh` for `run-all.sh` to do the full reproduction.

Explanation of the flags:

- `-v "$PWD/output:/artifact/output"` mounts the `output/` folder in your
  current directory to `/artifact/output` inside the container. All generated
  data — final results (figures, tables) and intermediary data (converted
  traces, learned DFAs, per-trial JSONs) — is written here and persists on
  the host after the container exits.
- `--rm` creates a disposable container that is automatically deleted upon
  exit.
- `bash run-smoke.sh` (or `bash run-all.sh`) is the command executed inside
  the container.

**Option B — interactive shell** (for exploring the source code, running
individual scripts, or debugging):

```
docker run --rm -it -v "$PWD/output:/artifact/output" cas-artifact:cav2026
```

The `-it` flags allocate an interactive terminal. This drops you into a bash
shell at `/artifact`, where you can run:

```
bash run-smoke.sh
bash run-all.sh
```

or any of the individual scripts described in the "Example Runs Beyond the
Paper" section below.

**Note:** Skip `install.sh` inside the container — all dependencies are
already baked into the image.

### Installation (without Docker)

If you'd rather run the artifact directly on your host, from the root of the artifact:

```
bash install.sh
```

This checks the Python version, makes sure the `graphviz` system binary is installed (installable with `brew install graphviz` on macOS), runs `pip install -r requirements.txt`, and verifies the imports. If you want to use a specific Python binary, run `PYTHON=/path/to/python3 bash install.sh`.

### Running the smoke test

You can run the smoke test by invoking:

```
bash run-smoke.sh
```

The smoke exercises five pieces of the pipeline in sequence: imports, matplotlib, the CybORG trace converter (on 10 raws), a tiny `incremental_learning` run on the pre-shipped one-host data, and a reduced Table 3 convergence experiment on four configurations for trial 1 (chaos and heuristic agents × 15/50-step traces). Runtime: ~15 minutes.

If everything runs successfully, the script prints intermediate progress similar to:

```
[1/5] Verifying imports...
  ok: SimulatorLearner and DFAEvaluator import cleanly

[2/5] Matplotlib sanity check...
  ok: matplotlib stack works; wrote output/results/smoke/matplotlib_check.png

[3/5] Converting 10 raws (exercises convert_traces.py)...
[convert] converting 10 raw traces with 4 worker(s)...
  10/10 (ok=10, fail=0)

[4/5] Tiny incremental_learning run on the pre-shipped one-host data...
  ... (verbose RPNI progress elided) ...
  [10 traces] 17 states, 91.88% accuracy
  [20 traces] 27 states, 94.78% accuracy

[5/5] Exp 3 smoke: 2 agents x 2 lengths (15, 50), trial 1, --cpus 4 --step 10...
Running 4 configurations with 4 worker(s)...
  ... (the 4 configs run in parallel; per-checkpoint lines interleave) ...
  [random_15steps_trial1] n= 3180  acc=1.0000  states=8

==========================================================
Table 3: Number of traces required for 100% accuracy
==========================================================
Agent              Trace Length       Mean    Std Dev
----------------------------------------------------------
Chaos (Random)     15-step          3180.0        0.0
Chaos (Random)     50-step           420.0        0.0
Chaos (Random)     100-step              -          -
Chaos (Random)     200-step              -          -
Heuristic          15-step           670.0        0.0
Heuristic          50-step           600.0        0.0
Heuristic          100-step              -          -
Heuristic          200-step              -          -
==========================================================

=== Smoke test passed ===
```

**The smoke test passed if the final line printed is `=== Smoke test passed ===`** and no exception or traceback appeared along the way. The convergence numbers in the Table 3 won't match Table 3 in the paper yet.

To sanity-check the individual steps, you can confirm the following files exist after the run:

(1) `output/results/smoke/matplotlib_check.png` — from step 2 (matplotlib sanity)
(2) `output/results/smoke/converted_check/output_10.txt` — from step 3 (conversion)
(3) `output/results/smoke/incremental_check/incremental_results.json` — from step 4 (incremental learning)
(4) `output/results/table3/table3_summary.json` — from step 5 (Table 3 convergence)

A preprocessed trace file (step 3 output) is a single-line Python-literal of the form `[[[step_1, step_2, ...]]]`, where each step is a `[blue_action, red_action]` pair. The first step of `output_1.txt` looks like:

```
[[[{'episode': 1, 'step': 1, 'action': 'DecoySSHD', 'agent': 'Blue',
    'hostname': 'Op_Server0', 'ip_address': '10.0.83.238', 'success': 'FALSE'},
   {'episode': 1, 'step': 1, 'action': 'DiscoverRemoteSystems', 'agent': 'Red',
    'success': 'TRUE', 'subnetname': 'User', 'prefix_length': '28'}],
  ...]]
```

---

## FULL REVIEW

Assuming the smoke test passed, reproduce the paper's main-text results by running:

```
bash run-all.sh
```

The script runs six phases in sequence. Each phase is resumable: reruns skip work whose outputs already exist. Total runtime is ~12 hours.

At the end, the figures land in `output/results/figures/` and Table 3 lands in `output/results/table3/`. Table 2 is printed to stdout during the cross-evaluation phase and is also derivable from the per-trial `eval_on_*.json` files under `output/cage2/tests/`. For a direct comparison of the generated outputs to the paper's reported numbers, refer to Figures 4, 5, 6 and Tables 2, 3 in the paper itself.

Phase [1/6] deserves a brief note: it reconstructs the per-trial training and evaluation directories from the raw traces in `data/cage2/cage2_raw_traces/`, using the fixed orderings recorded in `data/cage2/shuffles/`. Figures 4, 5, and Table 2 all share a single master ordering (`exp1_master.txt`) sliced into five contiguous 1000-trace trials; within each trial, the *same* source traces are reused for the 30-, 50-, and 100-step variants — only the truncation length differs, matching the paper's description. Figure 6 uses its own three fixed orderings, one per trial (`exp2_trial{1,2,3}.txt`), each drawn from the same 5000-trace pool.

**(1) Figure 4 — state count vs. training traces.** Produced by phases [2/6] and [5/6] of `run-all.sh`. Phase [2/6] runs `incremental_learning.py` for every combination of 5 trials × 3 trace lengths (30, 50, 100), training RPNI at every 50 traces up to 900. Phase [5/6] plots the resulting state-count curves.

Output: `output/results/figures/cage2_state_count_comparison.png`

**(2) Figure 5 and Table 2 — cross-evaluation.** Produced by phases [2/6], [3/6] and [5/6] of `run-all.sh`. Once the learning for point (1) has finished, phase [3/6] runs `cross_evaluate.py` to evaluate each trained DFA against evaluation traces of every other length, producing the 3×3 accuracy matrix. Phase [3/6] also prints Table 2 (accuracies at 900 training traces). Phase [5/6] then plots the matrix.

Output: `output/results/figures/cage2_accuracy_matrix.png` (Figure 5); Table 2 is printed to stdout during phase [3/6].

**(3) Figure 6 — large-scale learning.** Produced by phases [4/6] and [5/6] of `run-all.sh`. Phase [4/6] runs `incremental_learning.py` at 30-step truncation on three independent 4500-train / 500-eval splits, with 90 checkpoints each. Phase [5/6] plots the resulting accuracy and state-count curves.

Output: `output/results/figures/cage2_large_scale_learning.png`

**(4) Table 3 — chaos vs. heuristic convergence.** Produced by phase [6/6] of `run-all.sh`, which runs `scripts/reproduce_table3.py`. For each of the 24 configurations (2 agents × 4 trace lengths × 3 trials) the runner trains RPNI at increasing checkpoints and stops as soon as the DFA reaches 100% accuracy on a held-out eval set (500 traces of length 500). The mean and standard deviation across trials are printed to stdout.

Output: `output/results/table3/table3_summary.json`; Table 3 is also printed to stdout during phase [6/6].

---

## Example Runs Beyond the Paper

These examples demonstrate experiments beyond the paper — in particular, the BabyCyborg simulator lets you generate traces quickly for testing without the setup weight of CAGE2. The artifact is YAML-driven, so new experiments don't require editing Python. Examples 3 and 4 assume `bash run-smoke.sh` has already run.

### 1. Simulate one episode

```
python scripts/eval_cage0.py \
    --scenario yaml_files/config/one_host_random_red_random_blue.yaml \
    --max-steps 20
```

Prints a 20-step trace to stdout.

### 2. Swap the monitor set

Scenarios pick their monitors through the `monitors:` line. There are two sets: `active/` (the paper's per-host network-validity monitors) and `all_monitors/` (adds `blue_action_limit` and `impact_blocks_blue`, which further restrict blue). Copy a scenario into a new file under `yaml_files/config/` — for example, `cp yaml_files/config/one_host_random_red_random_blue.yaml yaml_files/config/one_host_all_monitors.yaml` — change its `monitors:` line from `../monitors/active` to `../monitors/all_monitors`, and rerun example 1 with the new scenario. The trace changes because blue is now constrained more.

### 3. Visualize a learned DFA

```
python sim_learn/visualize_dfa.py <path-to-any-.dot-file-produced-by-smoke>
```

Produces a PNG next to the `.dot` file. Requires the Graphviz system binary.

### 4. Train and evaluate on your own traces

Generate some traces, then learn a DFA from them:

```
python scripts/generate_traces.py \
    --scenario yaml_files/config/one_host_heuristic_red_random_blue.yaml \
    --output-dir tmp_traces/ --num-traces 20 --max-steps 30

python -c "
from sim_learn.learn_automata import SimulatorLearner
import glob
learner = SimulatorLearner()
learner.learn_logs(sorted(glob.glob('tmp_traces/output_*.txt')))
print('states:', len(learner.get_dfa_sim().states))
"
```

### 5. Two-host scenario

```
python scripts/eval_cage0.py \
    --scenario yaml_files/config/two_host_heuristic_red_random_blue.yaml \
    --max-steps 30
```

The simulator, the per-host monitors, and the agents all scale past the paper's one-host setup.

### Extending further

- New scenarios, agents (YAML or Python), and monitors are all drop-in: add a YAML (or a Python file plus a stub YAML for complex agents) and point an existing scenario at it.
- The learner and evaluator are independent of the simulator: `SimulatorLearner().learn_logs(paths)` accepts any list of traces in the `[[[{blue}, {red}], ...]]` format, and `DFAEvaluator(dot_path).evaluate_trace(trace_path)` scores a learned automaton against one trace.
- Docker is one supported environment, not the only one — `install.sh` installs directly onto the host.

---

## Troubleshooting

- `ModuleNotFoundError`: `install.sh` did not complete successfully — rerun and inspect the output.
- `dot: command not found`: install the Graphviz system binary; this is only required for DFA visualization.
- `SyntaxError` mentioning `tuple[...]` or `list[...]`: your Python is older than 3.9.
- Out of memory in phase [4/6]: reduce `--cpus` in `run-all.sh` or run on a machine with more RAM — the large-scale learner can peak in the several-GB range.

## License

MIT, see `LICENSE`. The raw CybORG traces under `data/cage2/cage2_raw_traces/` originate from the [CybORG cage-challenge-2](https://github.com/cage-challenge/cage-challenge-2) project and are redistributed under their (MIT-compatible) terms.
