"""Fail-closed gate result, separate from the unchanged journal/2 schema.

Only a proof-stream verifier pinned by the integration owner may supply the
independent replay function. A successful core-authored audit is diagnostic.
"""


def assess_replay(raw, scope, journal, *, replay=None, invalid_error=ValueError,
                  independent=False):
    def outcome(status, reason, proof=None):
        return dict(status=status, reason=reason, proof=proof,
                    operational_status='INCOMPLETE')

    if replay is None:
        return outcome('INCOMPLETE', 'independent journal/2 verifier unavailable')
    try:
        result = replay(raw, scope, journal)
    except (MemoryError, TimeoutError, RecursionError, InterruptedError) as exc:
        return outcome('INCOMPLETE', type(exc).__name__)
    except invalid_error as exc:
        # A verifier may wrap resource exhaustion in its malformed-proof error.
        cause = exc.__cause__ or exc.__context__
        if isinstance(cause, (MemoryError, TimeoutError, RecursionError, InterruptedError)):
            return outcome('INCOMPLETE', type(cause).__name__)
        return outcome('INVALID', str(exc))
    except Exception as exc:
        return outcome('INCOMPLETE', 'verifier failure: ' + type(exc).__name__)
    if type(result) is not dict or type(result.get('proof')) is not dict:
        return outcome('INCOMPLETE', 'no complete replay result')
    if result.get('status', 'VERIFIED') != 'VERIFIED':
        return outcome('INVALID' if result.get('status') == 'INVALID' else 'INCOMPLETE',
                       'non-verified replay result')
    proof = result['proof']
    if proof.get('operational_status') != 'INCOMPLETE':
        return outcome('INVALID', 'unsupported operational conclusion')
    if proof.get('closure_state') not in ('FIXPOINT', 'LABEL_CONFLICT'):
        return outcome('INCOMPLETE', 'closure not independently completed')
    if not independent:
        return outcome('INCOMPLETE', 'core-authored outer audit is diagnostic only')
    return outcome('VERIFIED', 'independent closed journal replay', proof)
