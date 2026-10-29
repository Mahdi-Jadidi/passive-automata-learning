"""Boundary API audit; k=1 is recorded as a structural-only extension."""
from __future__ import annotations
import importlib.util
import json
import sys
import time
from pathlib import Path

MANIFEST = Path(sys.argv[1]).resolve()
ROOT = MANIFEST.parent
HERE = Path(__file__).resolve().parent
G_PATH = HERE.parent / "general" / "known_k_v3.py"
S_PATH = HERE.parent / "structural" / "singleton_solver_v1.py"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def invoke(module, data, **kwargs):
    try:
        return {"returned": module.solve(data, **kwargs)}
    except Exception as exc:
        return {"raised": type(exc).__name__, "message": str(exc)}


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    g, s = load("boundary_general_v3", G_PATH), load("boundary_s001", S_PATH)
    rows = [x for x in manifest["cases"] if x["family"] == "invalid"]
    records, problems = [], []
    for row in rows:
        data = json.loads((ROOT / row["input"]).read_text(encoding="utf-8"))
        grec, srec = invoke(g, data, max_solutions=None), invoke(s, data, max_solutions=None)
        rec = {"id": row["id"], "general": grec, "structural": srec}
        sys.stdout.write(json.dumps({"type": "raw_invalid_case", **rec}, ensure_ascii=False,
                                    separators=(",", ":")) + "\n")
        sys.stdout.flush()
        if row["id"] == "invalid_k_one":
            if grec.get("raised") != "ValueError":
                problems.append({"id": row["id"], "kind": "general_should_reject_common_k1"})
            # Structural v1's k=1 acceptance is explicitly outside common scope.
            if srec.get("raised") is not None:
                problems.append({"id": row["id"], "kind": "structural_k1_extension_unexpectedly_rejected"})
        elif grec.get("raised") != "ValueError" or srec.get("raised") != "ValueError":
            problems.append({"id": row["id"], "kind": "invalid_input_not_rejected"})
        records.append({"id": row["id"], "general_error": grec.get("raised"),
                        "structural_error": srec.get("raised"),
                        "structural_k1_extension": row["id"] == "invalid_k_one"})
    # Omitted k must use the common default k=2.
    default_data = json.loads((ROOT / "inputs/absent_symbols.json").read_text(encoding="utf-8"))
    default_data.pop("k")
    default_g = g.solve(default_data, deadline=time.perf_counter()+10, max_solutions=None)
    default_s = s.solve(default_data, deadline=time.perf_counter()+10, max_solutions=None)
    sys.stdout.write(json.dumps({"type": "raw_default_k", "input": default_data,
                                 "general": default_g, "structural": default_s},
                                ensure_ascii=False, separators=(",", ":")) + "\n")
    sys.stdout.flush()
    if default_g.get("k") != 2 or default_s.get("k") != 2:
        problems.append({"kind": "omitted_k_default_not_two"})
    # Expired deadlines must not turn incomplete into infeasible.
    expired_g = g.solve(default_data, deadline=time.perf_counter()-1, max_solutions=None)
    expired_s = s.solve(default_data, deadline=time.perf_counter()-1, max_solutions=None)
    if expired_g.get("status") != "incomplete" or expired_s.get("status") != "incomplete":
        problems.append({"kind": "expired_deadline_not_incomplete",
                         "general": expired_g.get("status"), "structural": expired_s.get("status")})
    option_errors = {}
    for label, kwargs in (("max_zero", {"max_solutions": 0}),
                          ("max_bool", {"max_solutions": True}),
                          ("q_zero", {"max_solutions": None, "local_word_cap": 0}),
                          ("q_bool", {"max_solutions": None, "local_word_cap": True})):
        if label.startswith("q_"):
            value = invoke(g, default_data, **kwargs)
            option_errors[label] = value
            if value.get("raised") != "ValueError":
                problems.append({"kind": "invalid_option_not_rejected", "option": label})
        else:
            value_g = invoke(g, default_data, **kwargs)
            value_s = invoke(s, default_data, **kwargs)
            option_errors[label] = {"general": value_g, "structural": value_s}
            if value_g.get("raised") != "ValueError" or value_s.get("raised") != "ValueError":
                problems.append({"kind": "invalid_option_not_rejected", "option": label})
    result = {"audit": "C004 boundary API audit v1", "case_count": len(records),
              "records": records, "omitted_k_default": {"general_k": default_g.get("k"),
              "structural_k": default_s.get("k")}, "expired_deadline": {
              "general": expired_g.get("status"), "structural": expired_s.get("status")},
              "invalid_options": option_errors, "k1_policy": "General provider rejects; structural v1 accepts as provider-only extension outside common k>=2 scope.",
              "problems": problems}
    sys.stdout.write(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    sys.stdout.flush()
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
