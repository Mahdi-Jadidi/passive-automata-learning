"""Offline M4-A rank proof primitives. No frontier rule uses this module."""
from dataclasses import dataclass
from fractions import Fraction

from p3_frontier_verifier import Budget, need


@dataclass(frozen=True)
class Deletion:
    positive: int
    # Original alphabet IDs. Each touched quotient class is deleted in full.
    symbols: tuple[int, ...]


@dataclass(frozen=True)
class Packing:
    negative: int
    deletions: tuple[Deletion, ...]


def rank_cost(owner, positives, negatives, packings, weights, budget=None):
    """Return (mandatory base, local (support, floor) rows, packed cost)."""
    b = budget if budget is not None else Budget()
    need(1 <= len(packings) == len(weights) <= 128, "packing count")
    atoms = set()
    for i, rep in enumerate(owner):
        b.debit()
        need(type(rep) is int and 0 <= rep <= i and owner[rep] == rep, "owner")
        if rep == i:
            b.entries(len(atoms) + 1)
            atoms.add(rep)

    def trace_at(traces, index):
        need(type(index) is int and 0 <= index < len(traces), "trace ID")
        return traces[index]

    def remaining(word, removed):
        out = []
        for token in word:
            b.debit()
            if owner[token] not in removed:
                b.entries(len(out) + 1)
                out.append(token)
        return out

    total = Fraction()
    loads = {}
    local = []
    witness_entries = 0
    for proof, weight in zip(packings, weights):
        b.debit()
        need(type(weight) is Fraction and 0 <= weight <= 1 and
             max(weight.numerator.bit_length(), weight.denominator.bit_length()) <= 32,
             "weight")
        y = trace_at(negatives, proof.negative)
        need(2 <= len(proof.deletions) <= 64, "deletion count")
        support = set()
        for witness in proof.deletions:
            b.debit()
            need(1 <= len(witness.symbols) <= 4096, "deletion size")
            witness_entries += 1 + len(witness.symbols)
            b.entries(witness_entries)
            removed = set()
            for symbol in witness.symbols:
                b.debit()
                need(type(symbol) is int and 0 <= symbol < len(owner), "symbol ID")
                removed.add(owner[symbol])
            for rep in removed:
                b.debit()
                need(rep not in support, "overlapping quotient deletions")
                support.add(rep)
            x = trace_at(positives, witness.positive)
            b.check_exact()
            px, py = remaining(x, removed), remaining(y, removed)
            b.entries(len(px) + len(py))
            b.debit(1 + min(len(px), len(py)))
            need(px == py, "false ordered deletion")
        floor = len(proof.deletions) - 1
        for rep in support:
            b.debit()
            load = loads.get(rep, Fraction()) + weight
            need(load <= 1, "overloaded atom")
            loads[rep] = load
        local.append((frozenset(support), floor))
        total += weight * floor
    base = len(owner) - len(atoms)
    b.debit(0)
    return base, tuple(local), base + (-(-total.numerator // total.denominator))


def closes(mode, bound, incumbent):
    """Offline cutoff spec. The caller must separately verify the incumbent."""
    need(mode in ("one", "all"), "mode")
    return incumbent is not None and (bound > incumbent or
                                      (mode == "one" and bound == incumbent))
