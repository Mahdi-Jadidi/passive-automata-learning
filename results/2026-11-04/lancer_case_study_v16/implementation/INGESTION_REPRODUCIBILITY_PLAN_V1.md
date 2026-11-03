# First actual-data milestone and ingestion plan

Status: paper-reviewed, artifact schema pending. No dataset was fabricated from
Fig2, no parser claims to accept an unknown source format, and no external code
or simulator was run. Source evidence and page references are in
PAPER_SCHEMA_REVIEW_V1.md. Master owns original downloads/source files; auditor
locates and authenticates artifacts. This plan only writes implementation/.

## Minimal useful actual-data milestone

Once an artifact is located, freeze its origin URL, release/commit, license,
download timestamp, file size and SHA-256 before interpreting records. Select
one actual trace file and deterministically inspect at most10 episodes or1000
events (whichever first), under a10MiB preview cap. Preserve the entire original
file separately; the preview cap does not authorize dropping its remainder.
If the artifact is only source code with no saved traces, report that fact and
seek separately authorized reproduction; generated traces must not be called
the paper's archived observations.

Deliverables for that first real file:

1. Inventory of actual encoding/container/record grammar, field paths/types,
   field absence, action/value domains, successes/failures/missing outcomes,
   episode/step/order/reset evidence and explicit unavailable fields.
2. Up to20 source-linked events mapped to candidate token sequences, with
   each raw record location and original types/order preserved. These are
   real selected records, not a reconstruction of a published figure.
3. A tiny, separately hashed prefix/label table at event endpoints, only after
   actor order, outcome representation and continuity/reset semantics are
   established. Include positive/negative and conflicting-history counts.
4. Independent auditor checks that all emitted tokens, labels, ordering and
   indices can be replayed from the selected raw file and policy version.
5. Explicit decision on whether C015 assumptions match this sample at all;
   no full solver run or physical-ownership result is part of this milestone.

## Parser/inventory tooling after schema confirmation

Implement a versioned stdlib reader for the observed format only. JSON/JSONL
or CSV can use their standard readers once containers/columns are known;
custom text requires a documented grammar plus rejected-record log. A pickle
or Python-object artifact requires a separate safe decoding decision; do not
execute downloaded loaders, unpickle unknown payloads or run simulator setup
as an inventory shortcut. Archive listings/metadata can be inspected first.

The inventory CLI should take a raw input path, explicit verified format,
policy file and fresh output directory. It should hash input before/after
reading, preserve unknown fields in a sidecar, and reject ambiguous/malformed
records without converting missing success to False. Its observations should
include source filename/hash, byte/line or container-record location, original
episode/step/actor/order values, action, ordered original parameter pairs,
outcome value/type, and whether each metadata field actually exists.
This is a proposed intermediate representation, not a claimed source schema.

Raw timestamps/process IDs/component IDs remain in provenance/evaluation
sidecars unless confirmed part of the legal learning observation. Host IDs
may be legal action targets but are not automatically owner labels. Persist
separate namespaces for raw facts, declared tokenization, labels, and external
truth; never pass the truth sidecar into a learner.

## Tokenization and boundary policy

First reproduce the paper-level action-plus-parameter-value tokenization after
its actual ordering/normalization rules are known. Do not split a literal
DecoyTomcat or hostname into characters. Preserve boundaries: event token
ranges, actor, episode, step, source record, and endpoint outcome. Do not append
success tokens, monitor IDs or simulator state. Maintain a reversible token
dictionary including original type and namespace/collision decisions.

An explicit alternative using atomic event tuples (action,host,parameters)
may help retain host binding, but must be a labelled new experiment with its
own alphabet and sample hashes. It must not replace the reproduction silently.

Paper p5 assumes global accumulated histories without resets. Before generating
samples decide, with artifact evidence, whether episodes are continuous or
reset. Preserve raw episode boundaries even if continuity is established;
do not join arbitrary files. For each event endpoint, prefix tokens form the
word and only its success supplies the label. An earlier failure does not
make all later prefixes negative. Mid-event parameter prefixes are unlabelled.

Store a single token stream plus prefix-end offsets/labels rather than copying
all cumulative histories quadratically. Materialize full words only for a
declared bounded first control when needed by an existing CLI. If C015 is later
appropriate, use a reversible one-symbol-per-token encoding with a frozen
dictionary; its string API must not turn token spellings into character events.
Declare whether vocabulary is training-only or transductive; unseen test
symbols cannot silently change the frozen alphabet/normalization policy.

## Reproducibility/evaluation prerequisites

Record exact raw source IDs, policy version, normalized mapping tables and all
changes induced by CIDR/IP/exploit handling. Split by source lineage before
prefix extraction, so truncations/extensions of one source do not cross splits.
For a genuinely continuous history, document temporal dependency and permitted
evaluation protocol rather than pretending shuffled prefixes are independent.
The paper's splits/truncations and seeds cannot be reconstructed uniquely from
its numerical trace counts alone.

Check byte/record preservation, token reversal, event endpoint labels, ordering,
failure frequencies, vocabulary overlap and conflicting duplicate words before
learning. Contradictions may expose partial observability or preprocessing
collisions; preserve both source records. No heuristic assignment of host/actor
to independent DFA is authorized. Global/shared-symbol monitors and last-event
success semantics require a separately justified model translation before any
C015 result is interpreted physically.

Current implementation decision: plan only for trace ingestion. The supplied
paper is sufficient to identify these requirements, but insufficient for a
truthful parser of an actual serialized trace file. Review/readiness can advance
as soon as the auditor supplies a small authenticated artifact specimen.
