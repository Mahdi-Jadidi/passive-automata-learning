# Artifact discovery update: Zenodo 19828945

This supplements the earlier paper-only review without changing its historical
claims. The master/auditor located the matching software artifact, DOI
10.5281/zenodo.19828945. The locally saved Zenodo record identifies the title,
open access, publication date2026-04-27, and MIT license. No remote program,
installation, simulator or learner has been executed by this worker.

Read-only source copies and SHA-256:

| Path relative to C016 root | SHA-256 |
|---|---|
| data_audit/metadata_v1/zenodo_README.md | `061e91bf5fa5a0f21cec01a2d2963fd75d15511e6b124ca936e3682ee3976c63` |
| data_audit/metadata_v1/zenodo_record.json | `24e0e9934f9d51a6a23555c58bcd7838315472669bbc4cffa63656fe103ba0f8` |
| data_audit/metadata_v1/zenodo_LICENSE | `8f97c33b8f90039c844cd4a57f8b86f2c99cec7c5832841da040d033292edbbf` |

The record's source ZIP is cas-artifact-cav2026.zip,244813827bytes,
MD5 8390b436e7e2378b447558586d82d185. This is metadata, not a local ZIP integrity
claim. A Docker image is separate and unnecessary for read-only schema review.
README's approximate ZIP-size estimate differs from record bytes; use measured
record/download sizes for provenance rather than the rounded requirement.

## Newly documented serialization

README identifies data/cage2/cage2_raw_traces/ as5000 raw CAGE2 files,
data/cage2/convert_traces.py as converter, build_cage2_data.py and shuffles/ as
deterministic split machinery. It identifies data/one_host_network_validity_only/
as pre-generated Table3 input, separate from the raw CAGE2 collection.

The learner-facing file is documented as a single-line Python literal, not
JSON: outer list of episodes, each episode a list of steps, each step a Blue/Red
event pair. Its concrete example contains dict events with episode, step,
action, agent, hostname, ip_address, success; another event includes subnetname
and prefix_length. Example successes are the strings TRUE/FALSE, not Python
booleans. These are README examples, not yet observations of extracted files.
Raw CAGE2 format is still not established by that processed-format statement.

An stdlib ast.literal_eval reader may be appropriate for confirmed processed
files, with explicit structure/type validation and resource limits. It must
never eval/execute content. A raw-file reader must be separately based on an
actual raw specimen and converter. Do not treat raw and processed paths as one
format merely because both may have a .txt extension.

## Checks requiring actual selected files/source

- The processed example retains both hostname and numeric ip_address despite
  the paper's IP-to-hostname preprocessing description. Learner code must show
  whether IP is ignored, replaced or tokenized; emitting every dict value would
  risk including success/agent/indices and would not be a faithful parser.
- Read convert_traces.py and the learner's actual token extraction together.
  Confirm parameter ordering, action/exploit-class representation, prefix_length
  handling, missing outcomes and accepted primitive types from selected records.
- Read evaluator order/reset handling alongside the learner; the paper's global
  non-resetting semantics must not be assumed from the container shape alone.
- README describes Table3 evaluation500traces of length500. Paper p13 gives
  a one-host network-validity evaluation500traces of length50 in the appendix.
  These may be distinct experimental configurations; confirm source/dataset
  headers before claiming exact reproduction or declaring a contradiction.
- README says appendix experiments are not included in its replicated claims.
  Do not equate available main-text inputs to all20pages of experiments.
- README smoke numbers from one trial differ from paper mean/std over three
  trials by design; that is not by itself a failure. Preserve per-trial identity.
- The recorded exp1_master.txt ordering and exp2_trial1/2/3.txt files can resolve
  shuffle reproducibility missing from paper prose once actually extracted.

Pending milestone: auditor-provided selected raw/processed files and converter
source, with archive member path, size and hash. Until these arrive there is no
claimed actual-data inventory or trace-parser execution in this branch.
