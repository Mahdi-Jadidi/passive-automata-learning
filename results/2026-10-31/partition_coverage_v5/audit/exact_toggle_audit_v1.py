"""Compare exact q-opposition-disabled results against oracle and captured on results."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
V5 = HERE.parent
ROOT = HERE / "frozen_corpus_v2"
MANIFEST = ROOT / "manifest_v1.json"
EXACT_PATH = V5 / "general" / "known_k_qexact_v2.py"
ON_GATE = V5 / "evidence" / "attempts" / "20261101T053324.043566Z_c9b3c6ee88" / "stdout.bin"
EXPECTED_EXACT_SHA256 = "9f08dd645e7fcccbe8ea8022c758b7cf3277a5f01b6533fb9c1ad0cf08b6c84d"
EXPECTED_ON_GATE_SHA256 = "c1e88726875c73ab02122063681a0c61c841b2e4ab76b2965a44f2c9ce5084ad"
AUDIT_DRIVER = HERE / "small_gate_driver_v2.py"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    if digest(EXACT_PATH) != EXPECTED_EXACT_SHA256:
        raise AssertionError("exact provider source hash mismatch")
    if digest(ON_GATE) != EXPECTED_ON_GATE_SHA256:
        raise AssertionError("captured on-mode output hash mismatch")
    audit = load_module("audit_reused_independent_oracle", AUDIT_DRIVER)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    on_output = json.loads(ON_GATE.read_text(encoding="utf-8"))
    exact = load_module("audit_exact_toggle_v2", EXACT_PATH)
    on_rows = {(row["id"], row["q"]): row for row in on_output["exact_full_set_rows"]}
    if len(on_rows) != 870:
        raise AssertionError(f"expected 870 captured on rows, got {len(on_rows)}")
    rows = []
    errors = []
    valid_rows = [row for row in manifest["small"]["cases"]
                  if row["family"] != "invalid_input_control"]
    if len(valid_rows) != 174:
        raise AssertionError(f"expected 174 valid inputs, got {len(valid_rows)}")
    for row in valid_rows:
        data = json.loads((ROOT / row["input"]).read_text(encoding="utf-8"))
        for q in (1, 2, 3, 4, None):
            key = (row["id"], q)
            on_row = on_rows.get(key)
            if on_row is None:
                errors.append({"id": row["id"], "q": q, "check": "captured_on_row_missing"})
                continue
            expected = audit.oracle(data, q)
            try:
                result = exact.solve(data, k=data["k"], local_word_cap=q,
                                     deadline=None, max_solutions=None,
                                     use_q_opposition=False)
                actual = audit.partition_set(result)
                on_actual = audit.partition_set(on_row["result"])
                witness_errors = [error for solution in result.get("solutions", [])
                                  for error in audit.verify_partition_and_witnesses(data, solution, q)]
                row_errors = []
                if actual != expected:
                    row_errors.append("disabled_full_set_differs_from_oracle")
                if actual != on_actual:
                    row_errors.append("enabled_disabled_full_set_mismatch")
                if (not result.get("search_exhausted") or not result.get("decision_complete")
                        or witness_errors):
                    row_errors.append("disabled_search_or_witness_incomplete")
                row_errors.extend(witness_errors)
                errors.extend({"id": row["id"], "q": q, "check": error}
                              for error in row_errors)
                rows.append({"id": row["id"], "q": q,
                             "expected_count": len(expected),
                             "on_count": len(on_actual), "off_count": len(actual),
                             "status": result.get("status"),
                             "search_exhausted": result.get("search_exhausted"),
                             "decision_complete": result.get("decision_complete"),
                             "errors": row_errors, "result": result})
            except Exception as exc:
                errors.append({"id": row["id"], "q": q,
                               "check": "disabled_provider_exception", "exception": repr(exc)})
    output = {
        "schema": "C005-independent-exact-toggle-audit-results-v1",
        "corpus_manifest_sha256": digest(MANIFEST),
        "provider_sha256": digest(EXACT_PATH),
        "captured_on_stdout_sha256": digest(ON_GATE),
        "counts": {"valid_payloads": len(valid_rows), "q_modes": 5,
                   "disabled_full_set_comparisons": len(rows), "errors": len(errors)},
        "errors": errors,
        "rows": rows,
    }
    print(json.dumps(output, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
