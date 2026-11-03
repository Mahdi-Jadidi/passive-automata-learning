# LANCER: paper-grounded schema review

Reviewed all 20 extracted PDF pages. This is a document review, not an
inventory of an acquired dataset. No trace file or external code was executed.
The exact artifact/file schema remains unconfirmed; an implementation of a
trace parser is not justified from this PDF alone.

Source bindings:

| Source | SHA-256 |
|---|---|
| ../source/CAV_2026_LANCER_Case_Study.pdf | `6a12434a6153277431a1eb00533eaa2cd343cc70ea9e54a92e4bcede9c79dbee` |
| ../source/paper.txt | `f53a9fee118538a8042269fc020b08e68f4963ba3fc2bbf2c74407e1a0edd198` |
| ../source/pages.json | `6ae1dbc60d58235623061c40bfff6424859d9064585009dd6a1810440ae98532` |

Page numbers below are the PDF's 1-based page numbers, also the 1-based entries
of pages.json. Paper title: The Simulator’s Blueprint: Automata Learning from
System Event Logs. The local filename uses LANCER; no software/package identity
or dataset repository is inferred from that filename.

## What the paper actually specifies

| Pages | Evidence and implementation consequence |
|---|---|
| 3–4, section3/Fig2/Def1 | Events belong to Blue/Red, with an action, parameter key/value pairs and success outcome. Example parameter names include hostname, ip_address and subnet. Episode/step headings and ordered pairs are shown. These are conceptual records; Fig2 has unquoted keys, TRUE/FALSE and ellipses, so it is not a documented JSON file grammar. |
| 5, Def2/order | Order is episode, step, Blue before Red. Preserve actual raw order and all identifiers to check this against the artifact; do not silently reorder a different source. No wall-clock timestamps, timezone, process ID or thread ID fields are specified. |
| 5, tokenization | Alphabet consists of action tokens and parameter-value tokens. Action names, IPs and hostnames are whole symbols, not sequences of characters. An example event produces three tokens. Parameter keys, success, actor and episode/step are not listed as emitted tokens in phi. |
| 5, Def3–5 | Each sample is an accumulated history ending at an event. Its label is that final event's success. Failures do not terminate the history or label every continuation negative. Only event endpoints receive these labels; arbitrary mid-parameter prefixes are not labelled by this definition. |
| 5, reset premise | The text assumes non-resetting state across episodes and accumulates a global history. This premise is explicit, not an observed artifact fact. Verify actual reset behavior before joining episodes or adopting this construction. |
| 6, collection | Augmented CybORG records chosen actions, agent observations and simulator true state (sessions, decoys etc.). The latter is information agents cannot perfectly know. These are distinct information sources and must not be mixed into learning tokens. No actual field names for the hidden-state payload are given. |
| 6, preprocessing | CIDRs map to User/Enterprise/Operational names; IPs map to hostnames; actions are augmented with exploit class (examples SSHBruteForce/Eternalblue). These operations require concrete mappings and extraction code. The paper does not define every lookup, parameter order or exact serialized action spelling. |
| 6–9, experiments | 5000 CAGE2 raw traces; a once-shuffled five-way split of 1000, with900 train/100 test and same sources truncated at30/50/100 steps. A separate4500/500 experiment truncates30 steps. Seeds, exact trace IDs, shuffle implementation and preprocessing artifacts are not specified in the supplied text. |
| 12–13, BabyCyborg | Separate controlled simulator with host monitors and additional blue_action_limit/red_impact_blocks_blue monitors; chaos/heuristic policies produce action-success histories. This is not automatically the same raw dataset/schema as the CAGE2 experiment. |
| 15–18, appendices | One-host and multi-host action parameterization differs; 5-step/10-step/15-step variants can share or extend source traces. Keep source lineage across truncated/extended variants. |
| 19–20 | Failure rates depend on topology, monitors and agent. Preserve actual class frequencies; do not balance/drop failures without declaring a new experimental arm. |

## Field inventory: known semantics versus unknown serialization

| Information | Supported by paper | Still required from an actual artifact |
|---|---|---|
| episode/step | Explicit ordinal indices | Actual field names/types, start index, resets, missing steps, duplicate keys |
| actor | Blue/Red in formal event tuple | Whether explicit field, container position, or derivable action set; do not fabricate absent actor fields |
| action | Whole action symbol | Exact spelling/namespace/parameters and exploit-class augmentation |
| host/IP/subnet | Example named parameters and normalization | Complete schema, stable identifier scope, mapping version and collisions |
| success | Formal binary outcome | Actual booleans/enum/null/partial-success encoding, absent values and exceptions |
| observations | Raw collection includes agent views | Actual nesting and which fields are legal learning observations |
| true state/component/monitor IDs | True simulation state collected; monitor architecture described | Actual fields/IDs, whether present per event, and provenance; these are not certified passive ownership labels |
| wall time/process/thread | Not specified in the supplied schema | Presence/units/order must be observed, otherwise report unavailable |
| file format | Not specified | JSON/JSONL/CSV/pickle/custom grammar, compression, encoding and version |

The formal parameter container is a set of pairs, whereas tokenization uses an
ordered value list. Its ordering rule is not supplied. Choosing sorted keys,
Python insertion order or raw text order without checking the artifact would
invent a reproducibility detail. Token value types, delimiters and collisions
(e.g. action/value using the same literal) also need explicit source evidence.

## Leakage and model-translation risks

Success is the target label. Neither the final success nor previous success
fields should be silently included in phi; doing so changes the observation
model and may trivially expose the target. Likewise true sessions, decoys,
monitor votes and component IDs are evaluation/configuration data unless a
separate oracle-assisted experiment is declared. An exploit class might be an
observable action choice or an internally chosen result; its causal availability
before outcome must be checked rather than assumed.

Hostnames and actor identity are not ground-truth independent components. The
paper's action/value tokenization has shared action tokens and global actions;
splitting an action token from its hostname can also destroy event binding.
Creating atomic (action,host) symbols would be a new tokenization experiment,
not an exact reproduction of phi. CIDR/IP normalization can be legitimate but
adds mapping/configuration knowledge, changes collisions, and needs a reversible
sidecar plus raw preservation.

The BabyCyborg monitor conjunction is not proof of disjoint ownership alphabets.
blue_action_limit observes repeated blue actions and red_impact_blocks_blue
couples red Impact to the next blue action across hosts (p12); several monitors
can observe one event. Shared NoOp/DRS further require scope checks. DRS is
called global on p12 while p17 counts five red actions per host; this detail
must be resolved from implementation/data. Do not silently apply the C015
independent-disjoint-factor semantics to these monitors or equate actor/host
count with known_k.

Splitting histories rather than source traces can put overlapping prefixes or
truncations from the same source in train and test. Split source lineage first
under an explicit continuity/reset convention, then derive prefixes/truncations.
If observations omit state and produce identical token histories with opposite
success labels, report the conflict and raw provenance; do not delete examples
or add hidden state to make the labels artificially deterministic.

No data/artifact availability statement or release URL was located in the full
supplied20-page extraction; references link related work and CybORG. This is a
finding about this document only, not a claim that no artifact exists online.
Artifact discovery/download is assigned to the master/auditor, not inferred here.
