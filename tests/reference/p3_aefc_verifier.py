"""Independent checker for Review10 named AEFC sidecars."""
from itertools import chain, combinations

from independent_replay import InvalidProof
from p3_frontier_verifier import Budget, Incomplete, _scope, canonical, fields, need, owner, parse

FORMAT = "feedback-aefc-named/v1"
MAX_BYTES = 16 * 1024**2
MAX_BLOCKS = 100_000
MAX_PATHS = 200_000
MAX_EDGES = 1_000_000


def _blocks(partition, budget):
    blocks = {}
    for symbol, group in enumerate(partition):
        budget.debit()
        blocks.setdefault(group, set()).add(symbol)
    return blocks


def _project(word, symbols, budget):
    budget.check_exact()
    budget.debit(len(word))
    return tuple(symbol for symbol in word if symbol in symbols)


class _Sources:
    def __init__(self, events, budget, index_limit):
        self.events = events
        self.budget = budget
        self.index_limit = index_limit
        self.size = 0
        self.requests = {}
        self.blocks = {}
        self.tables = {}
        for event in events:
            budget.debit()
            if event["event"] == "REGISTER":
                self.charge(1)
                request = event["registered"]["request"]
                self.requests[request["attempt_id"]] = request

    def charge(self, size):
        self.budget.debit(size)
        self.size += size
        if self.size > self.index_limit:
            raise Incomplete("source index cap")

    def get(self, event_id, group):
        need(type(event_id) is int and 0 <= event_id < len(self.events), "source event index")
        need(type(group) is int, "source group type")
        key = event_id, group
        if key in self.tables:
            return self.tables[key]
        event = self.events[event_id]
        need(event["event"] == "OBSERVE" and event["status"] == "PROJECTION_NO",
             "source is not a projection NO observation")
        request = self.requests[event["attempt_id"]]
        need(request["scope"]["regime"] == "UNRESTRICTED", "source scope")
        if event_id not in self.blocks:
            self.charge(len(request["owner"]) + 1)
            self.blocks[event_id] = _blocks(request["owner"], self.budget)
        symbols = self.blocks[event_id].get(group)
        need(symbols is not None, "source group")
        # Full independent journal replay checked that this record is the exact
        # projection of the bound original normalized and wire bytes.
        feedback = event["records"][0]["payload"]["feedback"]
        table = None
        for row in feedback["tables"]:
            self.budget.debit()
            if row["group"] == group:
                table = row
                break
        need(table is not None, "source table")
        named = {}
        zeros = set()
        free = {}
        self.charge(1)
        for pair in table["named_zeros"]:
            self.charge(2)
            negative = "N" + str(pair["negative"])
            named[negative] = "P" + str(pair["positive"])
            zeros.add(negative)
        for index in table["anonymous_zeros"]:
            self.charge(1)
            zeros.add("N" + str(index))
        for cluster, members in enumerate(table["free_groups"]):
            self.budget.debit()
            self.charge(len(members))
            for index in members:
                free["N" + str(index)] = cluster
        self.tables[key] = symbols, named, zeros, free
        return self.tables[key]


def _path(path, atom, negative, positive, sources, words, budget):
    fields(path, "atom edges")
    actual = path["atom"]
    need(type(actual) is list and len(actual) == len(atom) and
         all(type(item) is int and item == expected for item, expected in zip(actual, atom)),
         "atom coverage or order")
    edges = path["edges"]
    need(type(edges) is list and edges, "empty or malformed path")
    previous = negative
    seen = {negative}
    for edge in edges:
        budget.debit()
        fields(edge, "event group from to")
        start, end = edge["from"], edge["to"]
        need(type(start) is str and start == previous and type(end) is str and
             end in words and end not in seen, "broken or nonsimple path")
        symbols, named, _, free = sources.get(edge["event"], edge["group"])
        need(all(symbol in symbols for symbol in atom), "source does not contain atom")
        need(named.get(start) == end or named.get(end) == start or
             (start in free and end in free and free[start] == free[end]), "unlicensed edge")
        need(_project(words[start], symbols, budget) == _project(words[end], symbols, budget),
             "false raw source equality")
        seen.add(end)
        previous = end
    need(previous == positive, "wrong path endpoint")


def _wire_counts(entries, budget):
    paths = edges = 0
    for entry in entries:
        budget.debit()
        need(type(entry) is dict, "target block object")
        if entry.get("kind") == "ZERO_CONTAINMENT":
            fields(entry, "group kind event source_group")
        else:
            fields(entry, "group kind positive_id paths")
            need(entry["kind"] == "ATOM_MATCH" and type(entry["paths"]) is list,
                 "block kind or paths")
            paths += len(entry["paths"])
            need(paths <= MAX_PATHS, "wire atom path limit")
            for path in entry["paths"]:
                budget.debit()
                fields(path, "atom edges")
                need(type(path["edges"]) is list, "path edges")
                edges += len(path["edges"])
                need(edges <= MAX_EDGES, "wire edge limit")
    budget.entries(len(entries) + paths + edges)


def verify_aefc(raw, journal, sidecar, *, budgets=None, max_index_entries=2_000_000):
    """Check canonical bytes against exact journal bytes and original ordered words.

    Pass lower limits via Budget options, including max_proof_bytes, max_entries,
    max_depth (path length), max_exact_checks, max_work and seconds. Run in a
    process with an OS address-space limit for a hard memory bound.
    """
    try:
        budget = Budget(**(budgets or {}))
        need(type(max_index_entries) is int and max_index_entries >= 0, "index budget")
        need(type(sidecar) is bytes and len(sidecar) <= MAX_BYTES, "sidecar bytes/wire limit")
        proof = parse(sidecar, budget.max_proof_bytes, budget)
        need(canonical(proof) == sidecar, "noncanonical sidecar")
        fields(proof, "format sample_digest journal_sha256 owner negative_id blocks")
        need(proof["format"] == FORMAT, "sidecar format")
        entries = proof["blocks"]
        need(type(entries) is list and 0 < len(entries) <= MAX_BLOCKS, "target block wire limit")
        _wire_counts(entries, budget)
        scope, _, positives, negatives = _scope(raw, journal, budget)
        need(proof["sample_digest"] == scope["selector_scope"]["sample_digest"] and
             proof["journal_sha256"] == scope["journal2_digest"], "sidecar snapshot binding")
        n = len(scope["alphabet"])
        need(n > 0, "empty target alphabet")
        budget.entries(n + len(positives) + len(negatives))
        partition = owner(proof["owner"], n, budget)
        blocks = _blocks(partition, budget)
        need(len(entries) == len(blocks), "target block coverage")
        words = {}
        for prefix, traces in (("P", positives), ("N", negatives)):
            for i, word in enumerate(traces):
                budget.debit()
                words[prefix + str(i)] = word
        negative = proof["negative_id"]
        need(type(negative) is str and negative.startswith("N") and negative in words,
             "target negative ID")
        events = parse(journal, budget.max_journal_bytes, budget)["events"]
        budget.entries(len(events))
        sources = _Sources(events, budget, max_index_entries)
        for (group, symbols), entry in zip(blocks.items(), entries):
            budget.debit(len(symbols))
            need(type(entry["group"]) is int and entry["group"] == group, "target block order")
            target_word = _project(words[negative], symbols, budget)
            if entry["kind"] == "ZERO_CONTAINMENT":
                region, _, zeros, _ = sources.get(entry["event"], entry["source_group"])
                need(negative in zeros and symbols <= region, "unlicensed zero containment")
                # The replay checked the actual source zero, including anonymous
                # zeros. Independently check the literal target without naming it.
                need(any(_project(word, symbols, budget) == target_word for word in positives),
                     "false raw containment")
            else:
                positive = entry["positive_id"]
                need(type(positive) is str and positive.startswith("P") and positive in words,
                     "target positive ID")
                size = len(symbols)
                paths = entry["paths"]
                need(len(paths) == size * (size + 1) // 2, "atom path coverage")
                ordered = sorted(symbols)
                atoms = chain(((i,) for i in ordered), combinations(ordered, 2))
                for path, atom in zip(paths, atoms):
                    if len(path["edges"]) > budget.max_depth:
                        raise Incomplete("path length cap")
                    _path(path, atom, negative, positive, sources, words, budget)
                need(_project(words[positive], symbols, budget) == target_word,
                     "false raw block match")
        budget.debit(0)
        return dict(status="VERIFIED", result=dict(verdict="STRUCTURAL_NO",
                    owner=list(partition), negative_id=negative))
    except (Incomplete, MemoryError, RecursionError, TimeoutError, InterruptedError) as exc:
        return dict(status="INCOMPLETE", reason=str(exc) or type(exc).__name__)
    except (InvalidProof, ValueError, TypeError, KeyError, IndexError, OverflowError) as exc:
        return dict(status="INVALID", reason=str(exc))
