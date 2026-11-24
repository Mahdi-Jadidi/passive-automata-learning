"""Actual independent journal/2 replay of the four pinned producer exports."""
import copy
import json
import os
from pathlib import Path
import unittest

from bounded_deletion import DeletionBudget
from independent_replay import InvalidProof
from interface_artifact_replay import canonical, sha
from journal_v2_replay import verify_journal, replay_journal
from gateway import open_gateway
from selector_v2.core import Sample, Budget
from selector_v2.component_closure import component_closure
from selector_v2.schema import scope
from selector_v2.integration.replay_boundary import assess_replay


def gate_replay(raw, sc, journal, **kwargs):
    """Explicit proof-stream status; journal integrity alone is not closure."""
    out = verify_journal(raw, sc, journal, **kwargs)
    status = out.get('status')
    if status != 'VERIFIED':
        return dict(status='INVALID' if status == 'INVALID' else 'INCOMPLETE',
                    operational_status='INCOMPLETE')
    result = out.get('result', {})
    proof = result.get('proof', {})
    if out.get('operational_status') != 'INCOMPLETE' or proof.get('operational_status') != 'INCOMPLETE':
        return dict(status='INVALID', operational_status='INCOMPLETE')
    if proof.get('closure_state') not in ('FIXPOINT', 'LABEL_CONFLICT'):
        return dict(status='INCOMPLETE', operational_status='INCOMPLETE')
    return dict(status='VERIFIED', operational_status='INCOMPLETE', result=result)


def event(j, kind, aid=None):
    return next(e for e in j['events'] if e['event'] == kind and
                (aid is None or (e.get('attempt_id') or e.get('registered', {}).get('request', {}).get('attempt_id')) == aid))


def rewrite(e, transform, *, wire=True):
    obj = json.loads(bytes.fromhex(e['normalized_hex']))
    transform(obj)
    b = canonical(obj)
    e.update(normalized_hex=b.hex(), normalized_sha256=sha(b))
    if wire:
        b = canonical(obj['payload'])
        e.update(wire_hex=b.hex(), wire_sha256=sha(b))
        e['records'][0]['payload']['response_digest'] = sha(b)


class FinalGateTests(unittest.TestCase):
    def artifact(self, name):
        return json.loads((Path(os.environ['P21_GATE_ARTIFACT_DIR']) / (name + '.json')).read_bytes())

    def test_four_actual_exports(self):
        for name, cost in [('roundtrip', 2), ('adversarial', 2), ('interface-journal2', 1),
                           ('interface-journal2-epochs', 2)]:
            with self.subTest(name=name):
                obj = self.artifact(name)
                records = obj.get('records', obj.get('result', {}).get('records'))
                journal = canonical(obj['journal'])
                status = gate_replay(obj['raw'], obj['scope'], journal, expected_records=records)
                self.assertEqual(status['status'], 'VERIFIED', status)
                result = status['result']
                self.assertEqual(canonical(result['records']), canonical(records))
                self.assertEqual(result['proof']['structural_optimum'], cost)
                self.assertEqual(result['proof']['operational_status'], 'INCOMPLETE')
                if name == 'interface-journal2':
                    self.assertEqual(result['attempt_status'], {'a':'UNKNOWN','b':'PROJECTION_NO','c':'BOUNDED_NO',
                        'd':'ACCEPT','e':'ACCEPT','f':'UNKNOWN','g':'UNKNOWN','h':'PENDING'})
                    self.assertEqual(result['pending_candidates'], ('bounded','ext','pending','r','sim'))
                if name == 'adversarial':
                    self.assertEqual(result['attempt_status'], {'a':'UNKNOWN','b':'PROJECTION_NO','c':'BOUNDED_NO','d':'ACCEPT','e':'PENDING'})
                print('independent /2', name, 'VERIFIED structural cost', cost, 'operational INCOMPLETE', flush=True)

    def test_independent_invalid_and_caps(self):
        obj = self.artifact('adversarial'); raw, sc = obj['raw'], obj['scope']; original = obj['journal']
        def receipt_reuse(z):
            e = event(z,'OBSERVE','d'); rewrite(e,lambda o:o['payload'].update(receipt='r1'))
            e['receipt_ref'] = sha(b'r1'); e['records'][0]['payload']['receipt_digest'] = sha(b'r1')
        def attempt_reuse(z):
            e = event(z,'REGISTER','e'); e['registered']['request']['attempt_id']='a'; e['records'][0]['payload']['attempt_id']='a'
        def map_rebound(z):
            m=event(z,'REGISTER','b')['registered']['maps']['positive']; m['p0'],m['p1']=m['p1'],m['p0']
        mutations = [
            lambda z:z.update(version='selector-v2-journal/1'),
            lambda z:z.update(sample_digest='0'*64),
            lambda z:event(z,'REGISTER','b')['registered'].update(origin='SIMULATOR'),
            lambda z:event(z,'REGISTER','a')['registered']['maps']['positive'].update(p0=True),
            map_rebound,
            lambda z:event(z,'REGISTER','c')['registered']['capacities'].__setitem__(0,2),
            attempt_reuse,
            lambda z:event(z,'OBSERVE','b').update(wire_sha256='0'*64),
            lambda z:event(z,'OBSERVE','b').update(normalized_sha256='0'*64),
            lambda z:rewrite(event(z,'OBSERVE','b'),lambda o:o.update(operational=True)),
            lambda z:rewrite(event(z,'OBSERVE','b'),lambda o:o['payload'].update(receipt='changed'),wire=False),
            lambda z:event(z,'OBSERVE','b')['records'][0]['payload'].update(receipt_digest='0'*64),
            lambda z:event(z,'OBSERVE','b')['records'][0]['payload']['feedback'].update(tables=[]),
            receipt_reuse,
            lambda z:rewrite(event(z,'OBSERVE','d'),lambda o:o['payload']['dfas'][0]['transitions'].pop()),
            lambda z:event(z,'QUARANTINE','a')['records'].clear(),
            lambda z:event(z,'QUARANTINE','e')['records'].append(event(z,'QUARANTINE','a')['records'][0]),
            lambda z:event(z,'OBSERVE','b').update(request_id='wrong'),
            lambda z:event(z,'RAW')['records'].append(event(z,'REGISTER','a')['records'][0]),
            lambda z:next(r for r in event(z,'RAW')['records'] if r['kind']=='COMPONENT_EPOCH' and not r['payload']['edges'])['payload']['facts'].pop(),
            lambda z:event(z,'OBSERVE','b').update(status='ACCEPT'),
            lambda z:z['events'].append(event(z,'OBSERVE','b')),
        ]
        for i, mutate in enumerate(mutations):
            with self.subTest(i=i):
                bad=copy.deepcopy(original); mutate(bad)
                result=verify_journal(raw,sc,canonical(bad))
                self.assertEqual(result['status'],'INVALID',result); self.assertNotIn('result',result)
        for data, kw in [(b'{"version":1,"version":2}',{}),(canonical(original),{'expected_records':[]})]:
            result=verify_journal(raw,sc,data,**kw)
            self.assertEqual(result['status'],'INVALID'); self.assertNotIn('result',result)
        for kw in [dict(deletion_budget=DeletionBudget(work=0)),dict(deletion_budget=DeletionBudget(entries=0)),
                   dict(deletion_budget=DeletionBudget(word_length=0)),dict(deletion_budget=DeletionBudget(seconds=0)),
                   dict(max_journal_bytes=1)]:
            result=verify_journal(raw,sc,canonical(original),**kw)
            self.assertEqual(result['status'],'INCOMPLETE',result); self.assertNotIn('result',result)
        print('independent outer mutations INVALID: 24; resource caps INCOMPLETE: 5',flush=True)

    def test_actual_partial_and_forged_exhaustion(self):
        obj=self.artifact('interface-journal2-epochs'); raw=obj['raw']; s=Sample.from_input(raw); sc=scope(s)
        g=open_gateway(raw); partial=component_closure(s,Budget(work=0))['records'];g.append_raw(partial)
        status=gate_replay(raw,sc,g.export());self.assertEqual(status['status'],'INCOMPLETE');self.assertNotIn('result',status)
        # A journal may be internally consistent while its closure is incomplete.
        self.assertEqual(verify_journal(raw,sc,g.export())['result']['proof']['closure_state'],'PARTIAL')
        bad=copy.deepcopy(partial);bad[0]['payload'].update(state='EXHAUSTED',cursor=None)
        g=open_gateway(raw);g.append_raw(bad)
        self.assertEqual(gate_replay(raw,sc,g.export())['status'],'INVALID')
        # Exercise the already committed raising-boundary consumer with actual independent code.
        good=canonical(obj['journal'])
        def replay(r,c,b): return replay_journal(r,c,b,deletion_budget=DeletionBudget())
        status=assess_replay(raw,sc,good,replay=replay,invalid_error=InvalidProof,independent=True)
        self.assertEqual(status['status'],'VERIFIED');self.assertEqual(status['proof']['structural_optimum'],2)
        def capped(r,c,b): return replay_journal(r,c,b,deletion_budget=DeletionBudget(work=0))
        status=assess_replay(raw,sc,good,replay=capped,invalid_error=InvalidProof,independent=True)
        self.assertEqual(status['status'],'INCOMPLETE');self.assertIsNone(status['proof'])


def report_exports(directory):
    rows={}
    for name,cost in [('roundtrip',2),('adversarial',2),('interface-journal2',1),('interface-journal2-epochs',2)]:
        body=(directory/(name+'.json')).read_bytes();obj=json.loads(body)
        records=obj.get('records',obj.get('result',{}).get('records'))
        status=gate_replay(obj['raw'],obj['scope'],canonical(obj['journal']),expected_records=records)
        row=dict(status=status['status'],sha256=sha(body),operational_status='INCOMPLETE')
        if status['status']=='VERIFIED':
            proof=status['result']['proof'];row.update(structural_optimum=proof['structural_optimum'],closure_state=proof['closure_state'])
            if row['structural_optimum']!=cost: row=dict(status='INVALID',sha256=sha(body),operational_status='INCOMPLETE')
        rows[name]=row
    overall='INVALID' if any(x['status']=='INVALID' for x in rows.values()) else ('VERIFIED' if all(x['status']=='VERIFIED' for x in rows.values()) else 'INCOMPLETE')
    return dict(status=overall,operational_status='INCOMPLETE',artifacts=rows)


if __name__=='__main__':
    import sys
    result=report_exports(Path(sys.argv[1]));print(json.dumps(result,sort_keys=True))
    raise SystemExit({'VERIFIED':0,'INVALID':1,'INCOMPLETE':2}[result['status']])
