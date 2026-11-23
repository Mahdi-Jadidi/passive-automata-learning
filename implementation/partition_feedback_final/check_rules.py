"""Verify the specific targets indexed by the English decision reference."""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

from audit import sample, triples
from experiments import fixtures
from sample import read_sample
from verify import Replay, at, elements, partition, require, verify

HERE = Path(__file__).resolve().parent
OUT = HERE / "evidence"


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def event_check(D, result, event):
    _, positives, negatives = read_sample(D, lambda: None)
    full = (1 << len(D["alphabet"])) - 1
    replay = Replay(positives, negatives, full, lambda: None)
    replay.logs = result["transcript"]["queries"]
    rule = event["rule"]
    proof = result.get("certificate", {})
    active = full ^ sum(proof.get("unused", []))
    if rule in ("A01", "A02"):
        require(result["status"] == "INFEASIBLE" and proof["kind"] == rule and event["i"] == proof["i"],
                "infeasibility event does not name its witness")
        if rule == "A01":
            require(event["j"] == proof["j"], "different positive witness")
    elif rule == "A03":
        require(event["blocks"] == proof["unused"], "unused symbols differ from certificate")
    elif rule == "A04":
        require(len(set(positives)) < len(positives) or len(set(negatives)) < len(negatives), "no duplicate")
        require([positives[i] for i in event["positive_ids"]] == list(dict.fromkeys(positives)),
                "deduplication loses a positive")
    elif rule == "A05":
        require(() in positives or () in negatives, "missing empty word")
    elif rule == "A06":
        require(not negatives or (not positives and full), "nontrivial obligations")
    elif rule == "A07":
        require(event in proof["contractions"], "unverified contraction target")
    elif rule in ("A08", "A09"):
        region = replay.fact(event, event["i"])
        x, y = at(positives, event["j"]), at(negatives, event["i"])
        cx, cy = Counter(x), Counter(y)
        different = sum(1 << a for a in cx.keys() | cy.keys() if cx[a] != cy[a])
        require((region == (active & ~different)) == (rule == "A08"), "incorrect witness source")
    elif rule == "A10":
        require(event["initial_answer"] == [active], "different initial block")
        replay.answer(partition([active, *proof.get("unused", [])], full))
    elif rule == "A11":
        require(len(replay.singleton_coverage()) == len(negatives), "singleton coverage is incomplete")
        if "blocks" in event:
            require(proof["kind"] == "singleton", "wrong singleton certificate")
            partition(event["blocks"], full)
            require(event["blocks"] == sorted(1 << a for a in elements(full)), "wrong singleton target")
    elif rule == "A12":
        known = replay.singleton_coverage()
        require(dict(event["coverage"]) == known and len(event["coverage"]) == len(known), "false singleton witness")
        require(event["unresolved"] == sorted(set(range(len(negatives))) - known.keys()), "wrong residual IDs")
    elif rule in ("A13", "A14", "A15"):
        target = partition(event["blocks"], full)
        replay.answer(target)
        if rule != "A15":
            expected = tuple(
                sum(1 << D["alphabet"].index(a) for a in block) for block in result["blocks"]
            )
            allowed = ("pair", "two-pairs") if rule == "A13" else ("rank",)
            require(target == partition(expected, full) and proof["kind"] in allowed
                    and event["certificate_kind"] == proof["kind"], "wrong target or certificate type")
    elif rule in ("S01", "S03", "S06", "S07", "S10"):
        query = at(replay.logs, event["query"])
        if rule == "S01":
            require(query["status"] == "NO" and query["failed"] == event["negative"], "wrong failed column")
        elif rule == "S03":
            require(query["status"] == "NO" and any(
                i != query["failed"] for table in query["tables"] for i, _ in table["zeros"]
            ), "missing reusable second column")
        elif rule == "S06":
            require(query["purpose"] == "diagnostic" and event["estimated_children"] >= 2,
                    "missing paid diagnostic")
            parent = partition(event["parent"], active)
            target = query["blocks"]
            require(all(any(b & a == a for b in target) for a in parent), "probe splits parent")
            at(negatives, event["negative"])
        elif rule == "S07":
            require(query["purpose"] == "incumbent", "missing incumbent proposal")
        else:
            require(any(len(g) > 1 for t in query["tables"] for g in t["free"]), "missing tied free columns")
    elif rule in ("S02", "S04", "S05", "S08", "S09", "S12"):
        target = partition(event["blocks"], active)
        if rule in ("S02", "S05"):
            region = replay.region(event["region"], target, active)
            if rule == "S05":
                count = sum(any((a | b) & group == a | b for group in region)
                            for a, b in combinations(target, 2))
                require(count == event["hidden_edges"] and any(
                    r["kind"] == "branch" and r["blocks"] == event["blocks"] and r["region"] == event["region"]
                    for r in proof["records"]
                ), "wrong waived edges or branch target")
        elif rule == "S04":
            replay.answer(partition([*target, *proof.get("unused", [])], full))
            require(all(any(i in g and t["block"] & b == t["block"]
                            for q in replay.logs for t in q["tables"] for g in t["free"] for b in target)
                        for i in range(len(negatives))), "missing inherited rejecting region")
        else:
            record = next((r for r in proof["records"] if r["blocks"] == event["blocks"]), None)
            require(record is not None, "no verified cutoff at cited target")
            if rule == "S08":
                require(record["kind"] == "unit" and event["lower"] == 1, "wrong unit cutoff")
            else:
                require(record["kind"] in ("overlap", "disjoint") and record["facts"] == event["facts"],
                        "wrong bound proof")
                require(event["lower"] == replay.lower(event["facts"], target, record["kind"] == "overlap"),
                        "incorrect bound value")
    else:
        require(rule == "S11" and result["status"] == "INCOMPLETE"
                and not replay.logs and not proof, "unknown event makes a claim")


def sources():
    d = fixtures()
    return {
        "example": sample("abcd", ["ab", "cd"], [""]),
        "example_full": sample("abcd", ["ab", "cd"], [""]),
        "unknown": sample("abcd", ["ab", "cd"], [""]),
        "empty_alphabet": sample("", [], [""]),
        "opposite_labels": sample("ab", ["a"], ["a"]),
        "unused_and_contraction": sample("abz", ["ab"], ["ba"]),
        "duplicate": sample("abc", ["a", "a"], ["", ""]),
        "no_positive": sample("ab", [], [""]),
        "held_together": sample("abc", ["ab"], ["ba", "baa", "aba"]),
        "order_triples": triples(3, "order"),
        "sunflower": triples(3, "sunflower"),
        "unit": sample("ab", ["ab"], ["ba"]),
        "singleton_stage": d["hdfs_holdout_512"],
    }


def main():
    path = OUT / "rule_index.json"
    base = json.loads((HERE.parent / "partition_feedback_paper/evidence/rule_index.json").read_text())
    base["A11"]["event_indices"] = [1]
    base.update({
        "A12": {"file": "exam_multi.json", "event_indices": [0]},
        "A13": {"file": "hdfs_1024.json", "event_indices": [1]},
        "A14": {"file": "rank_triple.json", "event_indices": [1]},
        "A15": {"file": "cover_path_8.json", "event_indices": [33]},
        "S12": {"file": "cover_path_8.json", "event_indices": [34]},
    })
    raw = sources()
    validated = {}
    for rule, ref in base.items():
        name = Path(ref["file"]).stem
        source = json.loads((OUT / ref["file"]).read_text())
        D = source["input"] if "input" in source else raw[name]
        result = source.get("result", source)
        verdict = verify(D, result)["status"]
        require(verdict == ("INCOMPLETE" if rule == "S11" else "VERIFIED"), "invalid replay")
        if rule in ("A15", "S12"):
            ref["event_indices"] = [i for i, e in enumerate(result["transcript"]["events"]) if e["rule"] == rule]
        events = [result["transcript"]["events"][i] for i in ref["event_indices"]]
        require(events and all(event["rule"] == rule for event in events), "wrong rule citation")
        for event in events:
            event_check(D, result, event)
        validated[rule] = dict(ref, input_sha256=digest(D), event_sha256=[digest(e) for e in events],
                               target=[{k: e[k] for k in ("i", "j", "region", "query", "blocks",
                                        "parent", "unresolved", "initial_answer", "negative", "lower")
                                        if k in e} for e in events], verdict=verdict, event_check="VERIFIED")
    source = json.loads((OUT / "cover_path_8.json").read_text())
    proof_event = next(e for e in source["result"]["transcript"]["events"] if e["rule"] == "S12")
    bad = deepcopy(proof_event)
    bad["blocks"] = [65535]
    try:
        event_check(source["input"], source["result"], bad)
    except ValueError:
        pass
    else:
        raise AssertionError("changed event target was accepted")
    path.write_text(json.dumps(validated, indent=2) + "\n", encoding="utf-8")
    print(f"{len(validated)} rules verified")


if __name__ == "__main__":
    main()

