"""Producer-only component closure and serializable raw proof epochs."""
from .core import Budget, PartitionRef, SymbolDSU
from .sparse_analysis import discover_deletions, raw_check, replay_deletion_facts
from .schema import raw_record


def component_closure(sample, budget=None, *, hash_bits=64):
    """Restart-only, frozen epochs. Partial verified edges remain necessary.

    No structural optimum claim on conflict; fixpoint is rule-class only.
    """
    budget = budget if budget is not None else Budget()
    dsu = SymbolDSU(len(sample.alphabet))
    records = []
    epoch = 0
    while True:
        before = dsu.snapshot()
        result = discover_deletions(sample, before, budget, hash_bits=hash_bits)
        replay_deletion_facts(sample, result)
        if result.label_conflict is not None:
            i, j = result.label_conflict
            records.append(raw_record(sample, 'LABEL_CONFLICT', dict(negative=i, positive=j)))
            return dict(state='LABEL_CONFLICT', owner=list(before.owner), records=records)
        first, edges = {}, []
        facts = [dict(negative=f.negative, group=f.group, positive=f.positive) for f in result.facts]
        for f in result.facts:
            a = first.setdefault(f.negative, f)
            if dsu.union(a.group, f.group):
                edges.append(dict(negative=f.negative, a=a.group, positive_a=a.positive,
                                  b=f.group, positive_b=f.positive))
        after = dsu.snapshot()
        records.append(raw_record(sample, 'COMPONENT_EPOCH', dict(epoch=epoch, owner=list(before.owner),
                       facts=facts, edges=edges, result_owner=list(after.owner),
                       state='EXHAUSTED' if result.exhausted else 'PARTIAL',
                       cursor=list(result.cursor) if result.cursor is not None else None)))
        if not result.exhausted:
            return dict(state='PARTIAL', owner=list(after.owner), records=records)
        if not edges:
            return dict(state='FIXPOINT', owner=list(after.owner), records=records)
        epoch += 1


def structural_record(sample, partition):
    result = raw_check(sample, partition)
    return raw_record(sample, 'STRUCTURAL_CHECK', dict(owner=list(partition.owner),
                      compatible=result.compatible, separating_groups=list(result.separating_groups),
                      failed_negative=result.failed_negative))
