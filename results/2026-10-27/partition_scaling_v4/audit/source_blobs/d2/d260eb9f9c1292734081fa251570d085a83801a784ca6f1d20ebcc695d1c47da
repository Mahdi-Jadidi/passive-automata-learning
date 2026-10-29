"""Graph-quotient continuing DFS with proved sound two-match cuts."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location('c003_general_support', Path(__file__).with_name('support.py'))
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)


def solve(data, *, deadline=None, max_solutions=1):
    return _support.search(data, deadline=deadline, max_solutions=max_solutions, learn=True)
