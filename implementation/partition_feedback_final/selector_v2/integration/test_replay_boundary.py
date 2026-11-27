"""Status-boundary tests; actual core artifacts plus injected resource failures."""
import unittest
from independent_replay import InvalidProof
from selector_v2.core import Budget, Sample
from selector_v2.component_closure import component_closure
from selector_v2.registered_ledger import RegisteredLedger
from selector_v2.schema import scope
from selector_v2.integration.audit_journal import replay_journal, encoded
from selector_v2.integration.test_journal_audit import fixture, event
from selector_v2.integration.test_roundtrip import RAW
from selector_v2.integration.replay_boundary import assess_replay
import adapter
from strict_ledger import parse


class BoundaryTests(unittest.TestCase):
    def test_actual_closed_diagnostic_not_authority(self):
        s, ledger = fixture()
        result = assess_replay(RAW, scope(s), ledger.export(), replay=replay_journal,
                               invalid_error=InvalidProof)
        self.assertEqual(result['status'], 'INCOMPLETE')
        self.assertIsNone(result['proof'])
        self.assertEqual(result['operational_status'], 'INCOMPLETE')

    def test_actual_false_exhaustion_invalid(self):
        import json
        s, ledger = fixture()
        bad = json.loads(ledger.export())
        next(r for r in event(bad, 'RAW')['records'] if r['kind'] == 'COMPONENT_EPOCH'
             and not r['payload']['edges'])['payload']['facts'].pop()
        result = assess_replay(RAW, scope(s), encoded(bad), replay=replay_journal,
                               invalid_error=InvalidProof)
        self.assertEqual(result['status'], 'INVALID')
        self.assertIsNone(result['proof'])

    def test_actual_partial_not_closed(self):
        s = Sample.from_input(RAW)
        ledger = RegisteredLedger(RAW, adapter=adapter, parse=parse)
        ledger.append_raw(component_closure(s, Budget(work=0))['records'])
        result = assess_replay(RAW, scope(s), ledger.export(), replay=replay_journal,
                               invalid_error=InvalidProof)
        self.assertEqual(result['status'], 'INCOMPLETE')
        self.assertIsNone(result['proof'])
        self.assertIn('closure not independently completed', result['reason'])

    def test_resource_and_missing_verifier(self):
        s, ledger = fixture()
        for error in (MemoryError, TimeoutError, RecursionError, InterruptedError, RuntimeError):
            def fail(*args):
                raise error('injected test failure')
            result = assess_replay(RAW, scope(s), ledger.export(), replay=fail,
                                   invalid_error=InvalidProof, independent=True)
            self.assertEqual(result['status'], 'INCOMPLETE')
            self.assertIsNone(result['proof'])
        def wrapped(*args):
            try:
                raise MemoryError()
            except MemoryError as exc:
                raise InvalidProof('wrapped resource error') from exc
        result = assess_replay(RAW, scope(s), ledger.export(), replay=wrapped,
                               invalid_error=InvalidProof, independent=True)
        self.assertEqual(result['status'], 'INCOMPLETE')
        self.assertIsNone(assess_replay(RAW, scope(s), ledger.export())['proof'])

    def test_contract_positive_is_unit_only(self):
        # Exercise the result contract, not independent proof verification.
        s, ledger = fixture()
        result = dict(proof=dict(closure_state='FIXPOINT', operational_status='INCOMPLETE'))
        def stub(*args): return result
        verified = assess_replay(RAW, scope(s), ledger.export(), replay=stub, independent=True)
        self.assertEqual(verified['status'], 'VERIFIED')
        for state in ('PARTIAL', 'OPEN', None):
            result['proof']['closure_state'] = state
            self.assertEqual(assess_replay(RAW, scope(s), ledger.export(), replay=stub,
                                          independent=True)['status'], 'INCOMPLETE')
        result['proof'].update(closure_state='FIXPOINT', operational_status='ACCEPT')
        self.assertEqual(assess_replay(RAW, scope(s), ledger.export(), replay=stub,
                                      independent=True)['status'], 'INVALID')
