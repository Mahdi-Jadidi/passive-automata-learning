"""Generate actual shared-journal interchange for independent proof stream."""
import copy
import json
import sys
from pathlib import Path
from adapter import canonical, need
from shared_gateway import SharedGateway, sha
from test_adapter import RAW, NO, YES
from selector_v2.core import PartitionRef
from selector_v2.component_closure import component_closure, structural_record
from selector_v2.evidence_store import EvidenceLedger
from selector_v2.schema import scope


def produce(raw, with_observations):
    g = SharedGateway(raw)
    closure = component_closure(g.sample)
    need(g.append_raw(closure['records'] + [structural_record(g.sample, PartitionRef(tuple(closure['owner'])))]), 'raw append failed')
    if with_observations:
        q = g.register([0,1,2], 'r', 'attempt-0')
        need(g.ingest('attempt-0', None).status == 'UNKNOWN', 'unexpected observation')
        q = g.register([0,1,2], 'r', 'attempt-1')
        p = copy.deepcopy(NO); p['request'] = q
        need(g.ingest('attempt-1', canonical(p)).status == 'PROJECTION_NO', 'unexpected observation')
        q = g.register([0,0,2], 'r2', 'attempt-2')
        p = copy.deepcopy(YES); p['request'] = q
        need(g.ingest('attempt-2', canonical(p)).status == 'ACCEPT', 'unexpected observation')
        q = g.register([0,0,2], 'r3', 'attempt-3', capacities=[1,1])
        p = {'version': q['version'], 'request': q, 'origin': 'SIMULATOR', 'status': 'BOUNDED_NO', 'complete': True, 'receipt': 'fixture', 'exact': True}
        need(g.ingest('attempt-3', canonical(p)).status == 'BOUNDED_NO', 'unexpected observation')
        g.register([0,0,2], 'r4', 'attempt-4')  # registered, no response
    bundle = g.export()
    fresh = EvidenceLedger(g.sample)
    need(fresh.append(bundle['records']) and list(fresh.owner) == bundle['owner'], 'core replay failed')
    return {'raw': raw, 'scope': scope(g.sample), 'bundle': bundle}


def main(directory):
    out = Path(directory); out.mkdir(parents=True, exist_ok=True)
    multi = {'alphabet': ['a','b','c'], 'positive': [['a','b'],['c']], 'negative': [['b','a'],['a','b','c']]}
    full = [produce(RAW, True), produce(multi, False)]
    journal = [{'raw': c['raw'], 'scope': c['scope'], 'records': c['bundle']['records']} for c in full]
    for name, data in [('roundtrip_journal.json', journal), ('roundtrip_bundle.json', full)]:
        body = canonical(data) + b'\n'; (out/name).write_bytes(body)
        print(name, len(body), sha(body))
    for i, case in enumerate(journal):
        print('case', i, 'records', len(case['records']), 'owner', full[i]['bundle']['owner'], 'observations', [r['payload']['status'] for r in case['records'] if r['kind'] == 'OBSERVATION'])


if __name__ == '__main__': main(sys.argv[1])
