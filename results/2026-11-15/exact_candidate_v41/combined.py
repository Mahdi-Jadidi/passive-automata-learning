"""V33 structural hybrid; see PROOF.md; experimental, not a public default."""
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_RESULTS = _HERE.parents[1]
_V33 = _RESULTS / '2026-11-13' / 'exact_candidates_v33'
_REF_HASH = '5f60b27447b37ec07f1fd6bce75be6199b898573d4b32e90413e900e3a615a94'
_PATHS = {
    'ref': (_RESULTS / '2026-11-11/exact_foundations_v28/implementation/reference.py', _REF_HASH),
    'c030': (_RESULTS / '2026-11-11/review_optimization_v30/optimization/candidate_v1.py', '7501901c6de5d7bb78ffc60f152b818733e3bd4460c9a655b8d783f384e8fc2b'),
    'dp': (_HERE / 'candidate.py', '3ac3eb85e91e496dc936e812e211e381ebdfaa00af559b87874dbf81f905c762'),
    'graph': (_V33 / 'candidate_graph/candidate.py', '71204f44840353ad5bd1f1bbfbb6365f6aabda5fff788f335ae788928f7cc242'),
    'graph_ref': (_V33 / 'candidate_graph/baseline_contract.py', _REF_HASH),
}
for _name, (_path, _digest) in _PATHS.items():
    if sha256(_path.read_bytes()).hexdigest() != _digest:
        raise ImportError('hybrid frozen dependency hash mismatch: ' + _name)


def _load(name):
    spec = spec_from_file_location('_v33_hybrid_' + name, _PATHS[name][0])
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_ref = _load('ref')
_c030 = _load('c030')
_dp = _load('dp')
_graph = _load('graph')


def solve(data, *, max_candidates=None):
    if max_candidates is not None:
        return _ref.solve(data, max_candidates=max_candidates)
    try:
        try:
            alphabet, positives, negatives = _ref._normalize(data)
        except _ref.InvalidInput as exc:
            return _ref._blank('INVALID_INPUT', str(exc))
        if set(positives) & set(negatives):
            result = _ref._blank('INCOMPATIBLE')
            result.update(compatible_count=0, optimal_count=0,
                          compatible_witnesses=[], optimal_witnesses=[])
            return result
        singleton_result = _c030._certified_all(alphabet, positives, negatives)
        if singleton_result is not None:
            return singleton_result
        owners, q = _graph._components(alphabet, positives, negatives)
        finest = _graph._expand(owners, tuple(range(q)))
        if _ref._candidate(alphabet, positives, negatives, finest) is not None:
            all_rgs = [_graph._expand(owners, (0,) * q)]
            if q > 1:
                all_rgs.append(_graph._expand(owners, (0,) * (q - 1) + (1,)))
            return _graph._finish(alphabet, positives, negatives, _graph._bell(q),
                                  q, 1, all_rgs, [finest])
        return _dp.solve(data)
    except (KeyboardInterrupt, MemoryError):
        return _ref._blank('INCOMPLETE', 'execution interrupted or resources exhausted')
