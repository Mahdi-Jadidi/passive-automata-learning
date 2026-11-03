"""Passive inventory of six authenticated files; no artifact code execution."""
import argparse
import ast
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import sys
import time

FIELDS = ['action', 'hostname', 'exploit_class', 'exploit_port', 'subnetname']


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def scalar_types(obj):
    keys = defaultdict(Counter)
    pending = [obj]
    visited = 0
    while pending:
        value = pending.pop()
        visited += 1
        if visited > 500000:
            raise ValueError('structural node budget exceeded')
        if isinstance(value, dict):
            for k, v in value.items():
                keys[f'{type(k).__name__}:{k}'][type(v).__name__] += 1
                pending.append(v)
        elif isinstance(value, list):
            pending.extend(value)
    return {k: dict(v) for k, v in sorted(keys.items())}


def processed(raw):
    tree = ast.parse(raw.decode('utf-8'), mode='eval')
    pending = [(tree, 0)]
    total = 0
    while pending:
        node, depth = pending.pop()
        total += 1
        if total > 200000 or depth > 50:
            raise ValueError('literal AST budget exceeded')
        if not isinstance(node, (ast.Expression, ast.List, ast.Tuple, ast.Dict, ast.Constant, ast.Load)):
            raise ValueError(f'unsupported literal node {type(node).__name__}')
        pending.extend((child, depth + 1) for child in ast.iter_child_nodes(node))
    data = ast.literal_eval(tree)
    if not isinstance(data, list):
        raise ValueError('outer episode container must be list')
    stream, endpoints, preview = [], [], []
    actions, successes, actors, field_types = Counter(), Counter(), Counter(), defaultdict(Counter)
    evaluator_differences = []
    for ei, episode in enumerate(data):
        if not isinstance(episode, list):
            raise ValueError('episode must be list of pairs')
        for si, pair in enumerate(episode):
            if not isinstance(pair, list) or len(pair) != 2 or not all(isinstance(x, dict) for x in pair):
                raise ValueError('step must contain exactly two event dictionaries')
            if [e.get('agent') for e in pair] != ['Blue', 'Red']:
                raise ValueError('actual actor order differs')
            if pair[0].get('episode') != pair[1].get('episode') or pair[0].get('step') != pair[1].get('step'):
                raise ValueError('pair indices differ')
            for event in pair:
                if event.get('success') not in ('TRUE', 'FALSE'):
                    raise ValueError('unknown/missing processed success representation')
                values = [event[f] for f in FIELDS if f in event]
                if any(not isinstance(v, (str, int, float, bool)) for v in values):
                    raise ValueError('unsupported token value type')
                before = len(stream)
                stream.extend(values)
                endpoints.append({'episode_container_index': ei, 'step_container_index': si,
                    'episode': event.get('episode'), 'step': event.get('step'), 'actor': event['agent'],
                    'token_start': before, 'prefix_end_exclusive': len(stream),
                    'positive': event['success'] == 'TRUE'})
                if len(preview) < 6:
                    preview.append({'raw_event': event, 'selected_token_fields': [f for f in FIELDS if f in event],
                                    'tokens': values, 'excluded_fields': [f for f in event if f not in FIELDS]})
                evaluated = ([event['action']] if 'action' in event else [])
                if 'hostname' in event:
                    evaluated.append(event['hostname'])
                elif 'subnetname' in event:
                    evaluated.append(event['subnetname'])
                if 'exploit_class' in event:
                    evaluated.append(event['exploit_class'])
                if evaluated != values:
                    evaluator_differences.append({'event_index': len(endpoints) - 1, 'learner_tokens': values, 'evaluator_tokens': evaluated})
                actions[event.get('action')] += 1
                actors[event['agent']] += 1
                successes[f'{event["agent"]}:{event["success"]}'] += 1
                for key, value in event.items():
                    field_types[key][type(value).__name__] += 1
    return {'format': 'Python_literal_episodes_steps_BlueRed_pairs', 'episode_count': len(data),
            'steps_per_episode': [len(x) for x in data], 'event_count': len(endpoints),
            'actions': dict(actions), 'actors': dict(actors), 'outcomes': dict(successes),
            'field_types': {k: dict(v) for k, v in field_types.items()}, 'preview': preview,
            'token_policy': FIELDS, 'token_stream': stream, 'prefix_endpoints': endpoints,
            'learner_evaluator_token_differences': evaluator_differences,
            'continuity': 'per-file cumulative preview matching learner default; no inter-file concatenation',
            'not_solver_input': True}


def raw_yaml(raw):
    import yaml  # Existing audited runtime package only; no install.
    data = yaml.safe_load(raw.decode('utf-8'))
    if not isinstance(data, list):
        raise ValueError('raw root is not list')
    root_keys, act_types, status_codes = Counter(), Counter(), Counter()
    preview = []
    for i, step in enumerate(data):
        if not isinstance(step, dict):
            raise ValueError('raw step is not dictionary')
        root_keys.update(map(str, step))
        for actor in ('Blue', 'Red'):
            event = step.get(actor, {})
            action = event.get('action', {})
            act_types[f'{actor}:{action.get("type")}'] += 1
            # Converter labels action[i] from obs[i+1], discards final step.
            if i + 1 < len(data):
                code = data[i + 1].get(actor, {}).get('obs', {}).get('prev_action_status', '__MISSING__')
                status_codes[f'{actor}:{code}'] += 1
            if len(preview) < 4:
                preview.append({'step_container_index': i, 'actor': actor, 'action': action,
                                'actor_record_fields': list(event),
                                'current_observation_prev_action_status': event.get('obs', {}).get('prev_action_status', '__MISSING__')})
    return {'format': 'YAML_list_of_step_dictionaries', 'yaml_version': yaml.__version__,
            'raw_step_count': len(data), 'raw_step_keys': dict(root_keys),
            'action_types': dict(act_types), 'next_observation_status_codes': dict(status_codes),
            'nested_key_value_types': scalar_types(data), 'preview': preview,
            'converter_code_policy': '3->FALSE; 2->TRUE; all_other_values->TRUE; missing defaults1; final raw step discarded',
            'converted_or_labelled_here': False, 'raw_truth_fields_not_used_as_tokens': True}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--manifest', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    raw_manifest = args.manifest.read_bytes()
    manifest = json.loads(raw_manifest)
    report = {'archive_sha256': manifest['archive_sha256'], 'manifest_sha256': digest(raw_manifest),
              'script_sha256': digest(Path(__file__).read_bytes()), 'python': sys.version,
              'external_artifact_code_executed': False, 'files': [], 'errors': []}
    for item in manifest['files']:
        path = args.manifest.parent / item['local_path']
        if not ('cage2_raw_traces/' in item['archive_path'] or 'one_host_network_validity_only/' in item['archive_path']):
            continue
        entry = {'archive_path': item['archive_path'], 'local_path': str(path), 'expected_sha256': item['sha256']}
        try:
            raw = path.read_bytes()
            if len(raw) > 2 * 1024 * 1024 or digest(raw) != item['sha256']:
                raise ValueError('member size budget or integrity check failed')
            entry.update(bytes=len(raw), sha256=digest(raw))
            entry['inventory'] = raw_yaml(raw) if path.suffix == '.yaml' else processed(raw)
            if digest(path.read_bytes()) != entry['sha256']:
                raise ValueError('file changed during read')
            entry['status'] = 'inventoried'
        except Exception as exc:
            entry.update(status='failed_preserved', error=repr(exc))
            report['errors'].append(entry['archive_path'])
        report['files'].append(entry)
    report['wall_seconds'] = time.perf_counter() - started
    report['status'] = 'complete_selected_six_file_inventory' if len(report['files']) == 6 and not report['errors'] else 'partial_or_failed_inventory'
    (args.out / 'inventory.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'status': report['status'], 'files': len(report['files']), 'errors': report['errors']}))
    return 0 if report['status'] == 'complete_selected_six_file_inventory' else 1


if __name__ == '__main__':
    raise SystemExit(main())
