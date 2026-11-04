"""Read only 3 or100 exact CAGE2 YAML members; export opaque local-output traces."""
import argparse
from collections import Counter
import hashlib
import hmac
import json
from pathlib import Path
import sys
import time
import zipfile

ARCHIVE_SHA = '06039a2cb4c8a5e2230aa7681f2b7e09914ce7ce44a7721b272a437ce2daef76'
SEED = 2026110417
PREFIX = 'artifact/data/cage2/cage2_raw_traces/'


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def region(host):
    if host.startswith('Subnet_') and len(host.split('_')) >= 2:
        return '_'.join(host.split('_')[:2])
    if host.startswith('User'):
        return 'User'
    if host.startswith('Enterprise') or host == 'Defender':
        return 'Enterprise'
    if host.startswith('Op_'):
        return 'Operational'
    return None


def initial_maps(data):
    ip_hosts, subnet_names = {}, {}
    for host, info in data[0]['Blue']['obs'].items():
        if not isinstance(info, dict) or not info.get('Interface'):
            continue
        interface = info['Interface'][0]
        ip, subnet = interface.get('IP Address'), interface.get('Subnet')
        if ip:
            if ip in ip_hosts and ip_hosts[ip] != host:
                raise ValueError('ambiguous initial IP-to-host map')
            ip_hosts[ip] = host
        name = region(host)
        if subnet and name:
            if subnet in subnet_names and subnet_names[subnet] != name:
                raise ValueError('ambiguous subnet map')
            subnet_names[subnet] = name
    return ip_hosts, subnet_names


def event_type(actor, action, ip_hosts, subnet_names):
    name = action.get('type')
    if not isinstance(name, str) or not name:
        raise ValueError('missing/nonstring action type')
    host, ip, subnet = action.get('hostname'), action.get('ip_address'), action.get('subnet')
    discrepancy = bool(host and ip and ip in ip_hosts and host != ip_hosts[ip])
    if host:
        target = {'kind': 'host', 'value': host}
    elif ip:
        target = {'kind': 'host', 'value': ip_hosts[ip]} if ip in ip_hosts else {'kind': 'unresolved_ip', 'value': ip}
    elif subnet:
        target = {'kind': 'subnet', 'value': subnet_names.get(subnet, subnet), 'prefix': str(subnet).split('/')[-1]}
    elif name in ('NoOp', 'Sleep', 'Monitor'):
        # Explicit policy choice, not proof that the action has no physical effect.
        target = {'kind': 'global', 'value': None}
    else:
        target = {'kind': 'unspecified', 'value': None}
    return {'actor': actor, 'action': name, 'target': target,
            'exploit_class': action.get('exploit_class'), 'exploit_port': action.get('exploit_port')}, discrepancy


def strict_label(code, present):
    if present and type(code) is int and code == 1:
        return True, 'known_success'
    if present and type(code) is int and code == 3:
        return False, 'known_failure'
    if present and type(code) is int and code == 2:
        return None, 'unknown'
    return None, 'missing' if not present else 'unsupported_status'


def prepare(archive, count, out, seconds=300, reference=None):
    if count not in (3, 100):
        raise ValueError('count must be3(reference) or100(authorized main sample)')
    out.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    def check():
        if time.perf_counter() - started >= seconds:
            raise TimeoutError('preparation deadline exceeded')
    report = {'schema_version': 1, 'seed': SEED, 'count_requested': count,
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'python': sys.version, 'archive_expected_sha256': ARCHIVE_SHA,
              'original_artifact_code_executed': False, 'files': [], 'status': 'started'}
    try:
        import yaml
        loader = getattr(yaml, 'CSafeLoader', yaml.SafeLoader)
        report.update(yaml_version=yaml.__version__, safe_loader=loader.__name__)
        h = hashlib.sha256()
        with archive.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                check()
                h.update(chunk)
        report['archive_actual_sha256'] = h.hexdigest()
        if h.hexdigest() != ARCHIVE_SHA:
            raise ValueError('archive integrity mismatch')
        vocabulary, traces, audit_events = {}, [], []
        ids_to_keys = {}
        with zipfile.ZipFile(archive) as z:
            names = Counter(info.filename for info in z.infolist())
            for number in range(1, count + 1):
                check()
                member = PREFIX + f'raw_{number}.yaml'
                if names[member] != 1:
                    raise ValueError('missing/duplicate exact numeric archive member: ' + member)
                info = z.getinfo(member)
                if info.file_size > 2 * 1024 * 1024:
                    raise ValueError('selected member exceeds2MiB limit')
                raw = z.read(member)  # ZIP reader checks member CRC.
                data = yaml.load(raw.decode('utf-8'), Loader=loader)
                if not isinstance(data, list) or len(data) < 2:
                    raise ValueError('raw trace must contain at least2 step dictionaries')
                ip_hosts, subnet_names = initial_maps(data)
                events, status_counts, label_counts = [], Counter(), Counter()
                root_keys = Counter()
                for step in data:
                    check()
                    if not isinstance(step, dict):
                        raise ValueError('step is not dictionary')
                    root_keys.update(map(str, step))
                for si in range(len(data) - 1):
                    for actor in ('Blue', 'Red'):
                        check()
                        action = data[si][actor]['action']
                        obs = data[si + 1][actor]['obs']
                        if not isinstance(action, dict) or not isinstance(obs, dict):
                            raise ValueError('unexpected action/observation schema')
                        present = 'prev_action_status' in obs
                        code = obs.get('prev_action_status')
                        label, label_reason = strict_label(code, present)
                        compatible_label = False if code == 3 else True
                        # Missing/unsupported codes are explicitly separate from this
                        # original converter-compatible default-success policy.
                        description, discrepancy = event_type(actor, action, ip_hosts, subnet_names)
                        key = canonical(description)
                        opaque = 'e' + hmac.new(str(SEED).encode(), key.encode('utf-8'), hashlib.sha256).hexdigest()[:24]
                        if opaque in ids_to_keys and ids_to_keys[opaque] != key:
                            raise ValueError('opaque ID collision')
                        ids_to_keys[opaque] = key
                        vocabulary[opaque] = description
                        position = len(events)
                        events.append({'id': opaque, 'outcome': label})
                        status_counts[f'{actor}:{code if present else "__MISSING__"}'] += 1
                        label_counts[label_reason] += 1
                        audit_events.append({'file_id': number, 'event_index': position,
                            'raw_step_index': si, 'next_observation_index': si + 1, 'actor': actor,
                            'raw_status_present': present, 'raw_status': code,
                            'strict_reason': label_reason, 'converter_compatible_label': compatible_label,
                            'hostname_ip_discrepancy': discrepancy})
                traces.append({'file_id': number, 'events': events})
                report['files'].append({'file_id': number, 'archive_member': member,
                    'raw_sha256': hashlib.sha256(raw).hexdigest(), 'raw_bytes': len(raw),
                    'raw_step_count': len(data), 'raw_step_keys': dict(root_keys),
                    'events_emitted': len(events), 'next_observation_status_codes': dict(status_counts),
                    'strict_outcomes': dict(label_counts), 'last_raw_step_discarded': True})
        observations = {'alphabet': sorted(vocabulary), 'traces': traces}
        truth = {'seed': SEED, 'event_type_map': vocabulary, 'event_label_audit': audit_events,
                 'warning': 'evaluation/preprocessing metadata only; not observations or inferred ownership',
                 'target_normalization_assumption': 'explicit hostname else first Blue observable-interface IP map, else subnet class, else role'}
        splits = {'train': [i for i in range(1, count + 1) if i <= 60],
                  'validation': [i for i in range(1, count + 1) if 61 <= i <= 80],
                  'test': [i for i in range(1, count + 1) if i >= 81]}
        report.update(status='prepared', vocabulary_size=len(vocabulary), events=sum(len(t['events']) for t in traces),
                      splits=splits, observation_schema='alphabet and file_id/events(id,outcome) only',
                      vocabulary_policy='type-keyed seeded HMAC; stable across3/100; no labels in vocabulary mapping')
        if reference:
            previous = json.loads(reference.read_bytes())
            old = {f['archive_path']: f for f in previous['files']}
            comparisons = []
            for f in report['files']:
                entry = old[f['archive_member']]
                inv = entry['inventory']
                fields = {'raw_sha256': f['raw_sha256'] == entry['sha256'],
                          'raw_step_count': f['raw_step_count'] == inv['raw_step_count'],
                          'raw_step_keys': f['raw_step_keys'] == inv['raw_step_keys'],
                          'status_codes': f['next_observation_status_codes'] == inv['next_observation_status_codes']}
                comparisons.append({'file_id': f['file_id'], 'checks': fields})
            report['reference_equivalence'] = {'reference_sha256': hashlib.sha256(reference.read_bytes()).hexdigest(),
                'comparisons': comparisons, 'passed': all(all(c['checks'].values()) for c in comparisons),
                'scope': 'raw bytes/structure/next-status histogram; not original converter execution equivalence'}
            if not report['reference_equivalence']['passed']:
                raise ValueError('three-file reference equivalence failed')
        for name, payload in [('observations.json', observations), ('protected_truth_map.json', truth)]:
            check()
            (out / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
        report['output_hashes'] = {name: hashlib.sha256((out / name).read_bytes()).hexdigest()
                                  for name in ('observations.json', 'protected_truth_map.json')}
    except Exception as exc:
        report.update(status='failed_preserved', error=f'{type(exc).__name__}: {exc}')
    finally:
        report['wall_seconds'] = time.perf_counter() - started
        (out / 'preparation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--archive', type=Path, required=True)
    ap.add_argument('--count', type=int, choices=(3, 100), default=3)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--seconds', type=float, default=300)
    ap.add_argument('--reference-inventory', type=Path)
    args = ap.parse_args()
    if args.seconds <= 0 or not __import__('math').isfinite(args.seconds):
        ap.error('seconds must be finite and positive')
    if args.reference_inventory and args.count != 3:
        ap.error('C016 reference equivalence applies only to first3files')
    result = prepare(args.archive, args.count, args.out, args.seconds, args.reference_inventory)
    print(json.dumps({'status': result['status'], 'events': result.get('events'), 'vocabulary': result.get('vocabulary_size')}))
    return 0 if result['status'] == 'prepared' else 1


if __name__ == '__main__':
    raise SystemExit(main())
