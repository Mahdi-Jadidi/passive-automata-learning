import copy
import unittest
from selector_v2.core import Budget, PartitionRef, Sample
from selector_v2.schema import VERSION, identity, raw_record, request, scope
from selector_v2.component_closure import component_closure, structural_record
from selector_v2.evidence_store import EvidenceLedger


def observation(s, req, status, feedback=None, origin='SIMULATOR', receipt=None):
    return dict(version=VERSION, origin=origin, sample_digest=s.sample_digest, kind='OBSERVATION',
                payload=dict(request_digest=identity(req), status=status, response_digest='1'*64,
                             receipt_digest=receipt, feedback=feedback))


class LedgerTests(unittest.TestCase):
    def test_epochs_atomic_and_replay(self):
        s = Sample(('a','b','c'),((0,1),(2,)),((1,0),(0,1,2)))
        result = component_closure(s)
        records = result['records'] + [structural_record(s,PartitionRef(tuple(result['owner'])))]
        for mutator in (
            lambda r: r[1]['payload'].update(owner=[0,1,2]),
            lambda r: r[1]['payload']['edges'][0].update(negative=0),
            lambda r: r[0]['payload']['facts'][0].update(group=True),
            lambda r: r[0]['payload'].update(result_owner=[0,0,0]),
            lambda r: r[-1]['payload'].update(separating_groups=[0,2]),
            lambda r: r[0].update(sample_digest='0'*64),
            lambda r: r[0]['payload'].update(edges=[]),
        ):
            bad = copy.deepcopy(records); mutator(bad)
            ledger = EvidenceLedger(s)
            self.assertFalse(ledger.append(bad))
            self.assertEqual(ledger.records, ()); self.assertEqual(ledger.owner,(0,1,2))
            self.assertEqual(len(ledger.quarantine),1)
        ledger = EvidenceLedger(s)
        self.assertTrue(ledger.append(records)); self.assertEqual(ledger.owner,(0,0,0))
        snapshot = ledger.records; snapshot[0]['payload']['owner'][0] = 2
        self.assertEqual(ledger.records[0]['payload']['owner'][0],0)
        other = EvidenceLedger(s); self.assertTrue(other.append(list(ledger.records)))
        self.assertEqual(other.owner,ledger.owner)
        self.assertFalse(ledger.append([records[0]]))
        partial = component_closure(s,Budget(work=0))
        ledger = EvidenceLedger(s); self.assertTrue(ledger.append(partial['records']))
        self.assertFalse(ledger.append(result['records']))
        conflict = Sample(('a',),((0,),),((0,),)); ledger = EvidenceLedger(conflict)
        self.assertTrue(ledger.append(component_closure(conflict)['records']))
        self.assertFalse(ledger.append([raw_record(conflict,'LABEL_CONFLICT',dict(negative=0,positive=True))]))

    def test_observations_and_binding(self):
        s = Sample(('a','b'),((0,),(1,)),((0,1),(0,0),(0,0),()))
        part = PartitionRef.singletons(2); req = request(s,scope(s),part,'r','a')
        register = raw_record(s,'REQUEST',req)
        table = dict(kind='UNRESTRICTED_COMPLETE',failed_negative=0,tables=[
            dict(group=0,named_zeros=[dict(negative=0,positive=0)],anonymous_zeros=[3],free_groups=[[1,2]]),
            dict(group=1,named_zeros=[dict(negative=0,positive=1)],anonymous_zeros=[1,2,3],free_groups=[])])
        obs = observation(s,req,'PROJECTION_NO',table)
        for mutate in (
            lambda o: o['payload']['feedback']['tables'][0].update(free_groups=[[1],[2]]),
            lambda o: o['payload']['feedback']['tables'][0].update(anonymous_zeros=[]),
            lambda o: o['payload']['feedback']['tables'][0]['named_zeros'][0].update(positive=1),
            lambda o: o['payload']['feedback']['tables'][0].update(free_groups=[[1,2,3]]),
            lambda o: o['payload'].update(request_digest='0'*64),
            lambda o: o['payload'].update(status='UNKNOWN'),
            lambda o: o.update(origin='EXTERNAL'),
        ):
            bad = copy.deepcopy(obs); mutate(bad); ledger=EvidenceLedger(s)
            self.assertFalse(ledger.append([register,bad])); self.assertEqual(ledger.records,())
        ledger = EvidenceLedger(s); self.assertTrue(ledger.append([register,obs]))
        self.assertFalse(ledger.append([obs]))
        self.assertFalse(ledger.append([register]))
        req2 = request(s,scope(s),part,'r','a2')
        self.assertTrue(ledger.append([raw_record(s,'REQUEST',req2),observation(s,req2,'UNKNOWN')]))
        wrong = request(s,scope(s),PartitionRef((0,0)),'r','a3')
        self.assertFalse(ledger.append([raw_record(s,'REQUEST',wrong)]))
        req3 = request(s,scope(s,'BOUNDED','0'*64),part,'b','a3')
        self.assertTrue(ledger.append([raw_record(s,'REQUEST',req3),observation(s,req3,'BOUNDED_NO',dict(kind='CONDITIONED_OPAQUE',artifact_digest='2'*64))]))
        req4 = request(s,scope(s),part,'r','a4')
        self.assertFalse(ledger.append([raw_record(s,'REQUEST',req4),observation(s,req4,'BOUNDED_NO')]))
        self.assertTrue(ledger.append([raw_record(s,'REQUEST',req4),observation(s,req4,'ACCEPT',origin='EXTERNAL',receipt='3'*64)]))
        req5 = request(s,scope(s),part,'r','a5')
        self.assertFalse(ledger.append([raw_record(s,'REQUEST',req5),observation(s,req5,'ACCEPT',origin='EXTERNAL',receipt='3'*64)]))
        self.assertEqual(ledger.owner,(0,1))  # Observations never imply merges or operational ACCEPT.
