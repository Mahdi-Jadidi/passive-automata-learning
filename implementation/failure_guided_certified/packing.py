"""Discover projection deletion witnesses and construct feasible incumbents."""
from collections import Counter
from itertools import combinations


class DeletionWitnesses:
    def __init__(self, S_plus, S_minus, tick):
        self.S_plus = S_plus
        self.S_minus = S_minus
        self.tick = tick
        self.counts_plus = [Counter(word) for word in S_plus]
        self.counts_minus = [Counter(word) for word in S_minus]

    def bound(self, partition, matches):
        owner = {a: i for i, block in enumerate(partition) for a in block}
        candidates = []
        for i, y in enumerate(self.S_minus):
            self.tick()
            found = {}
            for j, x in enumerate(self.S_plus):
                self.tick()
                different = (self.counts_plus[j] - self.counts_minus[i]).keys() | (
                    self.counts_minus[i] - self.counts_plus[j]).keys()
                atoms = tuple(sorted({owner[a] for a in different}))
                if not atoms or atoms in found:
                    continue
                deleted = {a for k in atoms for a in partition[k]}
                observed = owner.keys() - deleted
                if matches.project(x, observed) == matches.project(y, observed):
                    found[atoms] = j

            minimal = {}
            for atoms in sorted(found, key=lambda t: (len(t), t)):
                mask = frozenset(atoms)
                if all(not other <= mask for other in minimal):
                    minimal[mask] = atoms
                self.tick()
            loads = Counter()
            weights = Counter()
            for _ in range(2):
                for atoms in minimal.values():
                    self.tick()
                    if all(loads[a] < 2 for a in atoms):
                        weights[atoms] += 1
                        loads.update(atoms)
            if not weights:
                continue

            # Connected components of the support, using union by atom.
            groups = {a: {a} for a in loads}
            for atoms in weights:
                group = groups[atoms[0]].union(*(groups[a] for a in atoms))
                for a in group:
                    groups[a] = group
                self.tick()
            totals = Counter()
            for atoms, weight in weights.items():
                totals[min(groups[atoms[0]])] += weight
            d = sum((total + max(loads[a] for a in groups[k]) - 1) //
                    max(loads[a] for a in groups[k]) for k, total in totals.items())
            if d > 1:
                record = {"negative": i, "deletions": [
                    {"atoms": atoms, "positive": found[atoms], "weight": weight}
                    for atoms, weight in weights.items()]}
                candidates.append((d, i, set(loads), record))
        used = set()
        chosen = []
        for d, i, support, record in sorted(candidates, key=lambda c: (-c[0], c[1])):
            self.tick()
            if used.isdisjoint(support):
                used.update(support)
                chosen.append((d, i, support, record))
        return sum(d - 1 for d, _, _, _ in chosen), chosen


def propose(partition, chosen, matches):
    if not chosen:
        return None
    merged = []
    covered = set()
    for d, i, support, _ in chosen:
        atoms = tuple(sorted(support))

        def rejecting(indices):
            matches.tick()
            block = tuple(sorted(a for j in indices for a in partition[j]))
            return block if matches.row(block)[i] is None else None

        if d == 2:
            for pair in combinations(atoms, 2):
                if block := rejecting(pair):
                    atoms = pair
                    break
            else:
                return None
        else:
            if not rejecting(atoms):
                return None
            for atom in atoms:
                remaining = tuple(a for a in atoms if a != atom)
                if len(remaining) >= d and rejecting(remaining):
                    atoms = remaining
            block = rejecting(atoms)
        merged.append(block)
        covered.update(atoms)
    candidate = tuple(sorted(merged + [block for i, block in enumerate(partition) if i not in covered]))
    return candidate if matches.first_failure(candidate) is None else None
