# C006-T004: frozen v5 delta review (static only)

Reviewed solver_v5 SHA256:
e83c8d13e8eac248415160f6d29fb3309f19b5d447c932e00b69e24e7cb60792
and cli_v4 SHA256:
b824ca3751abfaaf424e31357d804f038f7eb79dad3c7a97048caacc240d7c8f.
Both match master's frozen hashes. V3 review and source remain preserved.
No test, provider import, benchmark, implementation edit or Git action occurred.

## Delta conclusion

No new blocking mathematical flaw identified. Relative to the snapshotted V3,
the changes are method version metadata, verifier expected-mask traversal, and
an explicit interruption flag. Original projection, graph-rule orientation,
quotient and collision-equality arguments carry over unchanged.

### Complete-cover verifier remains exact

V5 computes M=2^(r-1)-1 but does not materialize the expected-mask list/set.
It still rejects noninteger/bool/duplicate masks; first requires exactly M
unique provided masks, then iterates EVERY expected canonical mask and checks
membership and both projection witnesses. Cardinality plus membership proves
exact coverage, including exclusion of noncanonical/extra masks: replacing a
valid mask by an invalid one necessarily leaves a missing expected mask.
The change removes an avoidable exponential allocation before rejection of an
obviously short invalid cover; it does not make full certificate replay polynomial
in alphabet size. Proof length can still be exponential.

### Interrupted partial output now has the intended status

V5 sets interrupted=true on caught search-loop deadline or KeyboardInterrupt and
prioritizes status=incomplete even if solutions were saved. Thus V3 finding F3's
specific status ambiguity is repaired. Solutions remain preserved; existence is
decided if any answer is saved, and two distinct saved answers still certify
ambiguity. No unique/none conclusion is created by unfinished search. Deliberate
answer-limit stopping still returns found with enumeration_complete=false unless
the last canonical cut was actually checked. Root callers must distinguish
existence decision from completion of all/second-answer requests.

### CLI and remaining limits

cli_v4 imports solver_v5; it validates finite nonnegative --seconds, translates
the duration to an absolute provider-call deadline, reads/writes JSON and returns
3 for incomplete, 2 for invalid and 4 for runtime error. --all explicitly says
"all compatible bipartitions". It neither enumerates all k nor infers hidden k.
Its deadline starts after input parsing; external whole-process limits are still
needed. Invalid max_solutions values are handled as ValueError by the provider.

V3 finding F1 remains: verify_solution interprets blocks as sets without explicitly
rejecting duplicate symbols, and nested unhashable JSON members may raise. This
is a schema/totality limitation for malformed external witnesses, not a failure
of solver-produced sorted set blocks or of their language semantics. Validation
and some finalization/replay also remain outside cooperative interruption handling.
Record the independent gate's actual malformed-witness scope; do not infer it
from this static review. No additional runtime churn is requested by this note.

## Unknown-k interpretation and dormant rules

The binary solver exactly decides whether ANY nontrivial compatible partition
exists, because every feasible >=2-block partition has a feasible bipartition
coarsening. All-mode emits every feasible BIPARTITION; it does not emit all-k
partition sets, kmax or a maximal-refinement frontier. The trivial one-block
explanation is always possible for valid consistent data. not_decomposable means
no NONTRIVIAL decomposition, never impossibility of all regular models.

Only frozen C005 swap/rescue graph rules are active. Enhanced A/B in theory's
ENHANCED_RULES_PROOFS_v1.md are proved but DORMANT in production this cycle.
Do not attribute any observed pruning/result to A/B. The manager equal-length
counterexample remains beyond both the old graph and the proposed enhancement.

Independent provider gates and any final empirical claims are separate; at this
review, audit/READINESS still lists candidate comparison as held, while the
135-case independent oracle replay is accepted. This review does not promote
oracle acceptance to provider acceptance or invent missing performance results.
