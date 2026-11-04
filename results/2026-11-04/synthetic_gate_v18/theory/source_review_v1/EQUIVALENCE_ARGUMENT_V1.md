# C018 count-loop equivalence and review obligations

Static reasoning only. C015 is the frozen exact reference. No source import,
provider/test execution, timing, generated input or measured speed claim is
created by this argument.

For a word w, consecutive disjoint chunks w_1,...,w_j concatenate to w. For
every symbol a, count_a(w)=sum_i count_a(w_i). Counter adds exactly those
nonnegative integers, so every completed per-word count equals C015's direct
character loop. Empty words yield an empty count mapping in both versions.
No zero entries are introduced and no characters are dropped at boundaries.

A word is alphabet-valid iff every key in every chunk Counter is declared.
If a chunk has a foreign key, scanning only that chunk finds the same first
foreign occurrence that C015 would encounter: every earlier chunk was fully
validated. The error and old prefix-progress metric therefore agree. The
extra work counter explicitly records that Counter already scanned the full
foreign chunk. Deadline failure before finishing this proof remains unresolved.

Each chunk Counter orders keys by first occurrence. Updating the per-word
Counter retains earlier key positions and appends newly seen keys in chunk
order, so iteration order matches first occurrence in the whole word. This
preserves the chosen first distinguishing nonzero symbol, not only membership
truth. All subsequent code is copied unchanged from the frozen reference.

Thus nonzero count sets, positive-word presence and universal-positive support
are identical after validation. The zero-count criterion and handling of
duplicate positive words are unchanged. Contradiction checks still inspect all
validated labels; unknown symbols or malformed late words cannot be hidden by
an earlier mathematical shortcut. Both prechecks feed the same assumptions,
routes and inputs into the same graph/search/witness code.

With no interruption, status, family decision, known-K restriction, released
partition, alternatives and logical certificate match C015. Only method,
timers and added work diagnostics differ. With deadlines, different progress
and finality are allowed: fewer interpreter steps may complete a previously
censored case, and polling occurs at bounded new locations. No uncompleted
decision is promoted to certified_unique/ambiguous/incompatible.

Independent review should verify the exact diff, not infer unchanged search
from this prose. The only algorithmic edit is the counting loop and Counter
import/constant; the CLI bytes must match the reference. Pending audit cases:

- Empty P/N, epsilon, duplicate observations, conflicting labels and known K
  invalid/bool/interior/extremes; unary zeros/nonzeros and mixed-positive
  witnesses from different positives.
- Words of length16383/16384/16385 and multiple pieces; also65535/65536/65537
  since these are natural external chunk-boundary controls. Place a foreign
  symbol at first/last/boundary positions and in a late label, including after
  an earlier false unary predicate or known-K1-compatible prefix.
- Non-ASCII/BMP/non-BMP symbols and repeated characters across chunk boundaries;
  string code points must not be replaced by encoded-byte counts.
- Adversarial changed key first-occurrence order across chunks; certificate
  witness selection must remain valid and match the reference when complete.
- Zero/expired deadlines, interrupt/resource paths and native-operation hard
  cutoffs. Counters must not be presented as full T for unfinished validation.
- C015 exact small-family oracle cases, graph-failure-yet-knownK-unique examples
  and generated DFA-world cases before bounded long-data timings. Record every
  timeout/error/regression and compare the same compact output contract.

C017 drafts remain paused. The previous application usage-limit interruption
was not a scientific C018 failure; no missing code/runtime log is fabricated.
