"""Bounded producer discovery for the experimental rank-cost closure."""

from collections import Counter, defaultdict
from fractions import Fraction
from math import ceil

from .edr_search import canonical

FORMAT_V3 = "p3-region-frontier/v3"
MAX_ENTRIES = 2_000_000
MAX_BYTES = 64 * 1024**2
DISCOVERY_WORK = 50_000


class DiscoveryLimit(Exception):
    pass


def payload_size(closure, budget):
    entries = 0
    for row in closure["packings"]:
        for deletion in row["deletions"]:
            count = 1 + len(deletion["support"])
            budget.charge_work(count)
            entries += count
    size = len(canonical(closure))
    budget.charge_work()
    return entries, size


def discover_rank(region, sample, budget):
    """Return a checked packing and absolute floor, or leave the region unchanged."""
    remaining = DISCOVERY_WORK

    def charge(units=1):
        nonlocal remaining
        if units > remaining:
            raise DiscoveryLimit
        budget.charge_work(units)
        remaining -= units

    owner = region.owner

    def residue(word, deleted):
        result = []
        for token in word:
            charge()
            if owner[token] not in deleted:
                result.append(token)
        return result

    rows = []
    try:
        for ni, negative in enumerate(sample.negative):
            charge(1 + len(negative))
            negative_atoms = {owner[token] for token in negative}
            used = set()
            deletions = []
            for pi, positive in enumerate(sample.positive):
                charge(1 + len(positive) + len(negative_atoms) + len(used))
                support = (negative_atoms | {owner[token] for token in positive}) - used

                def matches():
                    left = residue(negative, support)
                    right = residue(positive, support)
                    charge(1 + min(len(left), len(right)))
                    return left == right

                if not support or not matches():
                    continue
                charge(len(support))
                for atom in sorted(support):
                    support.remove(atom)
                    if not matches():
                        support.add(atom)
                if not 1 <= len(support) <= 4096:
                    continue
                deletions.append(dict(positive_id=f"P{pi}", support=sorted(support)))
                used.update(support)
                if len(deletions) == 64:
                    break
            if len(deletions) >= 2:
                rows.append((dict(negative_id=f"N{ni}", deletions=deletions), used))
                if len(rows) == 128:
                    break
    except DiscoveryLimit:
        # Only completed rows are eligible.
        pass

    if not rows:
        return None

    degrees = Counter()
    for _, atoms in rows:
        budget.charge_work(len(atoms))
        degrees.update(atoms)
    greedy = []
    occupied = set()
    fractional = []
    for row, atoms in rows:
        budget.charge_work(len(atoms))
        if occupied.isdisjoint(atoms):
            greedy.append((row, atoms, Fraction(1)))
            occupied.update(atoms)
        fractional.append((row, atoms, Fraction(1, max(degrees[a] for a in atoms))))

    def evaluate(packing):
        loads = defaultdict(Fraction)
        score = Fraction()
        for row, atoms, weight in packing:
            budget.charge_work(score.numerator.bit_length() + score.denominator.bit_length()
                               + weight.denominator.bit_length())
            score += weight * (len(row["deletions"]) - 1)
            for atom in atoms:
                load = loads[atom]
                budget.charge_work(load.numerator.bit_length() + load.denominator.bit_length()
                                   + weight.denominator.bit_length())
                loads[atom] = load + weight
                if loads[atom] > 1:
                    raise ValueError("rank packing exceeds atom capacity")
        budget.charge_work(score.numerator.bit_length() + score.denominator.bit_length())
        return ceil(score)

    greedy_rank = evaluate(greedy)
    fractional_rank = evaluate(fractional)
    chosen = fractional if fractional_rank > greedy_rank else greedy
    closure = dict(reason="RANK_COST", version="p3-rank-cost/v1",
                   packings=[dict(row, weight=[weight.numerator, weight.denominator])
                             for row, _, weight in chosen])
    return region.lower_bound + max(greedy_rank, fractional_rank), closure
