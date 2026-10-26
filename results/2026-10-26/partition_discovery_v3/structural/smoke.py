"""Small, independently checked branch smoke. Run only through audit.capture.

Persist each raw return or exception before any assertion. This is not the
independent auditor's full recovery/complexity evaluation and is not a benchmark.
"""
import json
import os
from pathlib import Path
import sys
import time
from datetime import datetime, timezone
from uuid import uuid4

from fixed_word_solver import solve


def project(word, block):
    return "".join(a for a in word if a in block)


def canonical(blocks):
    return tuple(sorted(tuple(sorted(block)) for block in blocks))


def small_oracles(data):
    alphabet = sorted(data["alphabet"])
    positive, negative = sorted(set(data["positive"])), sorted(set(data["negative"]))
    fixed, general = set(), set()
    for mask in range(1, 1 << (len(alphabet) - 1)):
        right = {alphabet[i + 1] for i in range(len(alphabet) - 1) if mask >> i & 1}
        left = set(alphabet) - right
        blocks = (left, right)
        languages = [{project(word, block) for word in positive} for block in blocks]
        if all(any(project(n, block) not in languages[i] for i, block in enumerate(blocks))
               for n in negative):
            general.add(canonical(blocks))
        # Without positives choose a local word longer than all negatives.
        if not positive or (all(len(words) == 1 for words in languages)
                            and all(any(project(n, block) not in languages[i]
                                        for i, block in enumerate(blocks)) for n in negative)):
            fixed.add(canonical(blocks))
    return fixed, general


def validate(data, result):
    positive, negative = sorted(set(data["positive"])), sorted(set(data["negative"]))
    alphabet = sorted(data["alphabet"])
    assert result["model_class"] == "fixed_word_product"
    assert "fixed_word" in result["uniqueness_scope"]
    if result["status"] == "found":
        assert result["uniqueness"] == "unique" and result["search_exhausted"]
        assert result["decision_complete"] and len(result["solutions"]) == 1
    elif result["status"] in ("incomplete", "insufficient_coverage"):
        assert not result["search_exhausted"] and result["uniqueness"] == "unknown"
    for solution in result["solutions"]:
        blocks = list(map(set, solution["blocks"]))
        assert len(blocks) == 2 and all(blocks)
        assert not blocks[0].intersection(blocks[1]) and set.union(*blocks) == set(alphabet)
        factors = solution["local_words"]
        assert solution["positive_projection_languages"] == [[w] for w in factors]
        for p in positive:
            assert [project(p, block) for block in blocks] == factors
        assert [w["negative"] for w in solution["negative_witnesses"]] == negative
        for n, witness in zip(negative, solution["negative_witnesses"]):
            images = [project(n, block) for block in blocks]
            unseen = [i for i in (0, 1) if images[i] != factors[i]]
            assert unseen and witness["all_unseen_block_indices"] == unseen
            assert witness["block_index"] in unseen
            assert witness["projection"] == images[witness["block_index"]]
    graph = result["graph"]
    if graph["construction_complete"]:
        expected = set()
        for i, a in enumerate(alphabet):
            for b in alphabet[i + 1:]:
                if len({project(p, {a, b}) for p in positive}) > 1:
                    expected.add((a, b))
        assert set(map(tuple, graph["edges"])) == expected
        for edge, index in zip(graph["edges"], graph["edge_positive_indices"]):
            assert project(positive[0], set(edge)) != project(positive[index], set(edge))
    if (result.get("certificate") or {}).get("kind") == "odd_opposition_cycle":
        cycle = result["certificate"]["symbols"]
        assert cycle[0] == cycle[-1] and (len(cycle) - 1) % 2 == 1
        edges = {frozenset(e) for e in graph["edges"]}
        assert all(frozenset(pair) in edges for pair in zip(cycle, cycle[1:]))


def main():
    folder = Path(__file__).resolve().parent
    payload = json.loads((folder / "smoke_inputs_v1.json").read_text(encoding="utf-8"))
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ") + "_" + uuid4().hex[:8]
    directory = folder / "smoke_runs" / run_id
    directory.mkdir(parents=True, exist_ok=False)
    count, large = 0, 0
    for case in payload["cases"]:
        kwargs = {"max_solutions": case.get("max_solutions", 1)}
        if case.get("expired_deadline"):
            kwargs["deadline"] = time.perf_counter() - 1
        else:
            kwargs["deadline"] = time.perf_counter() + 20
        raw = {"case_id": case["case_id"], "input": case["input"],
               "kwargs": kwargs, "expected_status": case["expected_status"]}
        try:
            raw["result"] = solve(case["input"], **kwargs)
        except Exception as error:
            raw["exception_type"] = type(error).__name__
            raw["exception"] = repr(error)
        # This immutable evidence is durable BEFORE validation, even on failure.
        with (directory / f"{case['case_id']}.json").open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(raw, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        print(json.dumps(raw, ensure_ascii=False), flush=True)
        if case["expected_status"] == "ValueError":
            assert raw.get("exception_type") == "ValueError", case["case_id"]
        else:
            assert "exception" not in raw, case["case_id"]
            result = raw["result"]
            assert result["status"] == case["expected_status"], case["case_id"]
            validate(case["input"], result)
            if len(case["input"]["alphabet"]) <= 6:
                fixed, general = small_oracles(case["input"])
                if result["status"] == "found":
                    assert fixed == {canonical(result["solutions"][0]["blocks"])}, case["case_id"]
                elif result["status"] == "assumption_violation":
                    assert not fixed, case["case_id"]
                for key, value in (("fixed_count", fixed), ("general_count", general)):
                    if key in case:
                        assert len(value) == case[key], case["case_id"]
            else:
                large += 1
            if "target_blocks" in case and result["status"] == "found":
                assert canonical(case["target_blocks"]) == canonical(result["solutions"][0]["blocks"])
        count += 1
    summary = {"run_id": run_id, "status": "branch_smoke_passed", "cases": count,
               "large_constructive_cases": large, "raw_result_directory": str(directory),
               "independent_audit": False, "benchmark": False}
    with (directory / "summary.json").open("x", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
        handle.write("\n")
    print(json.dumps(summary, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
