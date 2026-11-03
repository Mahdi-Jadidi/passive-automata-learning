"""Exact no-K ownership family: unary-count theorem, else frozen C010."""
import hashlib
import importlib.util
import math
from pathlib import Path
import time

METHOD = 'C014-exact-unary-or-C010-v1'
BASELINE = Path(__file__).resolve().parents[3] / '2026-11-02/partition_unrestricted_v10/implementation/unrestricted_solver_v2.py'
BASELINE_SHA256 = '4c7959e96c02023d85943c8c52fae3f198c0de67ea172a72ad0669485f60c502'


class Stop(Exception):
    pass


def check(deadline):
    if deadline is not None and time.perf_counter() >= deadline:
        raise Stop


def scan(word, symbols, deadline, metrics):
    if not isinstance(word, str):
        raise ValueError('positive/negative entries must be strings')
    counts = {}
    for i, ch in enumerate(word):
        if i % 1024 == 0:
            check(deadline)
        if ch not in symbols:
            raise ValueError('word contains a symbol outside alphabet')
        counts[ch] = counts.get(ch, 0) + 1
        metrics['characters_scanned'] += 1
    return counts


def precheck(data, deadline, metrics):
    if not isinstance(data, dict) or set(data) != {'alphabet', 'positive', 'negative'}:
        raise ValueError('input must contain exactly alphabet, positive, negative; no count constraint')
    alphabet = data['alphabet']
    if (not isinstance(alphabet, list) or not alphabet or
            any(not isinstance(a, str) or len(a) != 1 for a in alphabet) or
            len(set(alphabet)) != len(alphabet)):
        raise ValueError('alphabet must be nonempty distinct one-character symbols')
    if any(not isinstance(data[label], list) for label in ('positive', 'negative')):
        raise ValueError('positive and negative must be lists')
    alphabet = sorted(alphabet)
    symbols = set(alphabet)
    observed = {a: set() for a in alphabet}
    presence = {a: 0 for a in alphabet}
    positive_words = set()
    for word in data['positive']:
        check(deadline)
        counts = scan(word, symbols, deadline, metrics)
        positive_words.add(word)
        for a, count in counts.items():
            check(deadline)
            observed[a].add(count)
            presence[a] += 1
    universal = [a for a in alphabet if presence[a] == len(data['positive'])]
    certificates = []
    predicate = True
    for index, word in enumerate(data['negative']):
        check(deadline)
        counts = scan(word, symbols, deadline, metrics)
        if word in positive_words:
            raise ValueError('contradictory_labels')
        rejecting = None
        for a, count in counts.items():
            check(deadline)
            metrics['nonzero_membership_checks'] += 1
            if count not in observed[a]:
                rejecting = (a, count)
                break
        if rejecting is None:
            for a in universal:
                check(deadline)
                metrics['zero_membership_checks'] += 1
                if a not in counts:
                    rejecting = (a, 0)
                    break
        if rejecting is None:
            predicate = False
        else:
            certificates.append({'negative_index': index, 'symbol': rejecting[0],
                                 'negative_count': rejecting[1]})
    return alphabet, predicate, certificates


def bell_spectrum(m, deadline):
    row = [1]
    previous_bell = 1
    for n in range(1, m + 1):
        check(deadline)
        previous_bell = sum(row)
        new = [0] * (n + 1)
        for k in range(1, n + 1):
            check(deadline)
            new[k] = row[k - 1] + (k * row[k] if k < len(row) else 0)
        row = new
    return sum(row), previous_bell, {str(k): row[k] for k in range(1, m + 1)}


def solve(data, *, deadline=None):
    started = time.perf_counter()
    metrics = {'characters_scanned': 0, 'nonzero_membership_checks': 0,
               'zero_membership_checks': 0, 'precheck_seconds': None,
               'closed_form_seconds': None, 'total_solver_seconds': None}
    result = {'method': METHOD, 'schema_version': 1, 'metrics': metrics}
    if deadline is not None and (isinstance(deadline, bool) or
            not isinstance(deadline, (int, float)) or not math.isfinite(deadline)):
        return {**result, 'status': 'invalid_input', 'complete': False, 'error': 'deadline must be finite absolute perf_counter time or None'}
    try:
        check(deadline)
        alphabet, predicate, certificates = precheck(data, deadline, metrics)
        metrics['precheck_seconds'] = time.perf_counter() - started
        result.update(alphabet=alphabet, all_partitions_predicate=predicate)
        if not predicate:
            check(deadline)
            if hashlib.sha256(BASELINE.read_bytes()).hexdigest() != BASELINE_SHA256:
                raise RuntimeError('frozen C010 source integrity mismatch')
            spec = importlib.util.spec_from_file_location('_c014_frozen_C010', BASELINE)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            check(deadline)
            payload = module.solve(data, deadline=deadline, enumerate_partitions=False)
            check(deadline)
            result.update(branch='frozen_C010', representation='C010_expanded_default', baseline_result=payload)
            if payload.get('complete') is not True or payload.get('status') == 'unknown':
                raise Stop
            result.update(status=payload['status'], complete=True,
                          partition_count=payload.get('partition_count'),
                          partition_count_by_k=payload.get('partition_count_by_k'))
            return result
        arithmetic_started = time.perf_counter()
        total, same, spectrum = bell_spectrum(len(alphabet), deadline)
        witnesses = [
            {'id': 'all_one_block', 'partition': [alphabet],
             'local_language_rule': 'positive_projections_from_input'},
            {'id': 'singletons', 'partition': [[a] for a in alphabet],
             'local_language_rule': 'positive_unary_counts_from_input'}]
        pairs = []
        for i, a in enumerate(alphabet):
            check(deadline)
            for b in alphabet[i + 1:]:
                check(deadline)
                pairs.append({'symbols': [a, b], 'relation': 'ambiguous',
                              'same_partition_count': same, 'different_partition_count': total - same,
                              'same_witness_id': 'all_one_block', 'different_witness_id': 'singletons'})
        metrics['closed_form_seconds'] = time.perf_counter() - arithmetic_started
        result.update(branch='unary_closed_form', representation='compact_exact_family', complete=True,
                      status='identified_unique_partition' if total == 1 else 'partial_ownership_identification',
                      partition_count=total, partition_count_by_k=spectrum, k_max_compatible=len(alphabet),
                      family={'kind': 'all_set_partitions', 'base_atoms': [[a] for a in alphabet],
                              'enumerated': False, 'certificate': 'every_negative_has_missing_positive_unary_count'},
                      negative_count_certificates=certificates, witness_pool=witnesses,
                      representative_witness_id='all_one_block', pair_relations=pairs)
        check(deadline)
        return result
    except ValueError as exc:
        return {**result, 'status': 'invalid_input', 'complete': False, 'error': str(exc)}
    except (Stop, KeyboardInterrupt):
        # Partial certificates/counts are deliberately not returned as a final family.
        return {'method': METHOD, 'schema_version': 1, 'status': 'incomplete', 'complete': False,
                'partition_count': None, 'partition_count_by_k': None, 'pair_relations': None,
                'reason': 'deadline_or_interruption', 'metrics': metrics}
    finally:
        metrics['total_solver_seconds'] = time.perf_counter() - started
