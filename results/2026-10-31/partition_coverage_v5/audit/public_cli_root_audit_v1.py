"""Independent CLI checks through the C005 workspace root wrapper."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
V5 = HERE.parent
GENERAL = V5 / "general"
WRAPPER = V5 / "solver.py"
EXACT = GENERAL / "known_k_qexact_v2.py"
SPARSE = V5 / "structural" / "sparse_certificate_v2.py"
CLI = GENERAL / "public_cli_v1.py"
EXPECTED = {
    "solver.py": "a977a7d869a5ee61bcc8997d79618a95945e0117201ad33d017a2a9eda7e43b1",
    "public_cli_v1.py": "964185568bbad53b54bb78769232dd828d3e980ed02038110675bf382d1bd2d7",
    "known_k_qexact_v2.py": "9f08dd645e7fcccbe8ea8022c758b7cf3277a5f01b6533fb9c1ad0cf08b6c84d",
    "sparse_certificate_v2.py": "1ff16263322f2009d68cd2b4ecc3b6587fa9ef80695fa9489fb199c9e13d6705",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_partition(blocks):
    return tuple(sorted(tuple(sorted(block)) for block in blocks))


def partitions(alphabet, k):
    symbols = sorted(alphabet)
    owners = [0] * len(symbols)

    def visit(pos, maximum):
        if pos == len(symbols):
            if maximum + 1 == k:
                yield canonical_partition([
                    [s for s, owner in zip(symbols, owners) if owner == color]
                    for color in range(k)
                ])
            return
        for color in range(min(maximum + 1, k - 1) + 1):
            owners[pos] = color
            yield from visit(pos + 1, max(maximum, color))

    if symbols:
        yield from visit(1, 0)


def project(word, block):
    members = set(block)
    return "".join(symbol for symbol in word if symbol in members)


def oracle(data, q):
    positives = sorted(set(data["positive"]))
    negatives = sorted(set(data["negative"]))
    feasible = set()
    for blocks in partitions(data["alphabet"], data["k"]):
        languages = [{project(word, block) for word in positives} for block in blocks]
        if q is not None and any(len(language) > q for language in languages):
            continue
        if any(all(project(word, block) in languages[i] for i, block in enumerate(blocks))
               for word in negatives):
            continue
        feasible.add(blocks)
    return feasible


def result_partitions(result):
    return {canonical_partition(row["blocks"]) for row in result.get("solutions", [])}


def check_solutions(data, result, expected, q):
    errors = []
    actual = result_partitions(result)
    if actual != expected:
        errors.append("partition_set_differs_from_direct_oracle")
    positives = sorted(set(data["positive"]))
    negatives = sorted(set(data["negative"]))
    for solution in result.get("solutions", []):
        blocks = solution["blocks"]
        languages = [{project(word, block) for word in positives} for block in blocks]
        if solution.get("positive_projection_languages") != [sorted(language) for language in languages]:
            errors.append("positive_projection_language_mismatch")
        if q is not None and any(len(language) > q for language in languages):
            errors.append("full_block_cap_violation")
        witnesses = {row.get("negative"): row for row in solution.get("negative_witnesses", [])}
        if set(witnesses) != set(negatives):
            errors.append("negative_witness_coverage_mismatch")
        for word in negatives:
            images = [project(word, block) for block in blocks]
            unseen = [i for i, image in enumerate(images) if image not in languages[i]]
            row = witnesses.get(word)
            if not unseen:
                errors.append("negative_accepted")
            elif (row is None or row.get("block_index") != unseen[0]
                  or row.get("projection") != images[unseen[0]]
                  or sorted(row.get("all_unseen_block_indices", [])) != unseen):
                errors.append("negative_witness_invalid")
    return errors


def invoke(path, *args):
    process = subprocess.run(
        [sys.executable, "-B", "-X", "utf8", str(WRAPPER), str(path), *args],
        cwd=REPO, capture_output=True, text=True, encoding="utf-8", timeout=30,
    )
    try:
        payload = json.loads(process.stdout)
    except Exception as exc:
        raise AssertionError({"argv": args, "returncode": process.returncode,
                              "stdout": process.stdout, "stderr": process.stderr,
                              "decode_error": repr(exc)}) from exc
    return process.returncode, payload


def main():
    for path in (WRAPPER, CLI, EXACT, SPARSE):
        name = path.name
        if digest(path) != EXPECTED[name]:
            raise AssertionError(f"source hash mismatch: {name}")
    sample_path = GENERAL / "sanity_inputs_v1.json"
    certificate_path = GENERAL / "public_cli_certificate_input_v1.json"
    invalid_path = GENERAL / "sanity_invalid_v1.json"
    sample = json.loads(sample_path.read_text(encoding="utf-8"))
    cert_data = json.loads(certificate_path.read_text(encoding="utf-8"))
    expected_unrestricted = oracle(sample, None)
    expected_q2 = oracle(sample, 2)
    expected_cert_q2 = oracle(cert_data, 2)
    errors = []
    rows = {}

    code, result = invoke(sample_path, "--max-solutions", "all")
    row_errors = check_solutions(sample, result, expected_unrestricted, None)
    if code != 0 or not result.get("complete") or not result.get("search_exhausted"):
        row_errors.append("exact_all_incomplete_or_wrong_exit")
    rows["exact_all_unrestricted"] = {"exit_code": code, "status": result.get("status"),
                                       "solution_count": len(result.get("solutions", [])),
                                       "oracle_count": len(expected_unrestricted), "errors": row_errors,
                                       "result": result}
    errors.extend({"case": "exact_all_unrestricted", "check": error} for error in row_errors)

    code, result = invoke(certificate_path, "--mode", "certificate", "--q", "2")
    row_errors = check_solutions(cert_data, result, expected_cert_q2, 2)
    if code != 0 or result.get("status") != "found" or result.get("uniqueness") != "unique":
        row_errors.append("certificate_success_missing")
    rows["certificate_success"] = {"exit_code": code, "status": result.get("status"),
                                   "solution_count": len(result.get("solutions", [])),
                                   "oracle_count": len(expected_cert_q2), "errors": row_errors,
                                   "result": result}
    errors.extend({"case": "certificate_success", "check": error} for error in row_errors)

    code, result = invoke(sample_path, "--mode", "certificate", "--q", "2")
    if code != 4 or result.get("status") != "insufficient_coverage":
        errors.append({"case": "certificate_abstention", "check": "abstention_or_exit_code_mismatch"})
    rows["certificate_abstention"] = {"exit_code": code, "status": result.get("status"), "result": result}

    code, result = invoke(sample_path, "--mode", "hybrid", "--q", "2")
    row_errors = check_solutions(sample, result, expected_q2, 2)
    if (code != 0 or result.get("fallback_trigger") != "insufficient_coverage"
            or result.get("status") != "found"):
        row_errors.append("hybrid_fallback_missing")
    rows["hybrid_fallback"] = {"exit_code": code, "status": result.get("status"),
                               "fallback_trigger": result.get("fallback_trigger"),
                               "solution_count": len(result.get("solutions", [])),
                               "oracle_count": len(expected_q2), "errors": row_errors,
                               "result": result}
    errors.extend({"case": "hybrid_fallback", "check": error} for error in row_errors)

    code, result = invoke(sample_path, "--mode", "hybrid", "--q", "2", "--timeout-seconds", "0")
    if code != 3 or result.get("status") != "incomplete" or "fallback_trigger" in result:
        errors.append({"case": "hybrid_deadline", "check": "deadline_status_or_fallback_mismatch"})
    rows["hybrid_deadline"] = {"exit_code": code, "status": result.get("status"), "result": result}

    code, result = invoke(sample_path, "--q", "0")
    if code != 2 or result.get("status") != "invalid_input":
        errors.append({"case": "invalid_q", "check": "invalid_q_not_rejected"})
    rows["invalid_q"] = {"exit_code": code, "status": result.get("status"), "result": result}

    code, result = invoke(invalid_path)
    if code != 2 or result.get("status") != "invalid_input":
        errors.append({"case": "contradictory_labels", "check": "invalid_data_not_rejected"})
    rows["contradictory_labels"] = {"exit_code": code, "status": result.get("status"), "result": result}

    output = {
        "schema": "C005-independent-root-cli-audit-v1",
        "source_sha256": {path.name: digest(path) for path in (WRAPPER, CLI, EXACT, SPARSE)},
        "counts": {"cli_cases": len(rows), "oracle_unrestricted": len(expected_unrestricted),
                   "oracle_q2_sample": len(expected_q2), "oracle_q2_certificate_input": len(expected_cert_q2),
                   "errors": len(errors)},
        "cases": rows,
        "errors": errors,
    }
    print(json.dumps(output, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
