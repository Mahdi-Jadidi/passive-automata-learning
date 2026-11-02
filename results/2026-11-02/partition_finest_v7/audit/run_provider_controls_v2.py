#!/usr/bin/env python3
"""C007 v4 derived controls: invalid inputs/mode, deadline and interruption."""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPL = ROOT / "implementation"
EXPECTED = {
    "provider": "c6c803da1088450d352d56bc1a208d6fa7c0d19416bd702255d866052e454fff",
    "cli": "46642a86c315b95de7b784eb614af4000b52fa96ce55c965f1bbb3de1d15e879",
    "protocol": "74ee1895c49e40abc5cc1c328bc1fad006e06dde397963dc1779c7266a2a06bd",
    "valid_inputs": "906152be7d6830fac80b722da24873195687ca257650b30a02ec8ace2025c39b",
    "invalid_inputs": "481b50913d7ebf30ddeb74c3ec01594c2db18cc673594233bb7d5fce871a99d1",
    "readiness": "cff6e5e5156d1c8abe8069cde7182195742762a387817ea465ccdb66adbe5ef9",
    "c006": "e83c8d13e8eac248415160f6d29fb3309f19b5d447c932e00b69e24e7cb60792",
    "c005": "9f08dd645e7fcccbe8ea8022c758b7cf3277a5f01b6533fb9c1ad0cf08b6c84d",
}


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def api_data(data):
    return {"alphabet": list(data["alphabet"]),
            "positive": ["".join(word) for word in data["positive"]],
            "negative": ["".join(word) for word in data["negative"]]}


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def emit(case_id, control, data, result=None, **extra):
    row = {"record_type": "control_result", "case_id": case_id, "control": control,
           "input_sha256": hashlib.sha256(canonical(data).encode("utf-8")).hexdigest(),
           "result": result}
    row.update(extra)
    print(json.dumps(row, ensure_ascii=False, sort_keys=True), flush=True)


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: run_provider_controls_v2.py VALID_INPUTS INVALID_INPUTS")
    valid_path, invalid_path = (Path(value).resolve(strict=True) for value in sys.argv[1:])
    provider_path = IMPL / "finest_solver_v4.py"
    cli_path = IMPL / "finest_cli_v2.py"
    protocol_path = IMPL / "PROTOCOL_V5.md"
    readiness_path = IMPL / "READINESS_V4.json"
    c006_path = ROOT.parents[1] / "2026-11-01" / "partition_identifiability_v6" / "implementation" / "solver_v5.py"
    c005_path = ROOT.parents[1] / "2026-10-31" / "partition_coverage_v5" / "general" / "known_k_qexact_v2.py"
    checks = {"provider": file_sha(provider_path), "cli": file_sha(cli_path),
              "protocol": file_sha(protocol_path), "valid_inputs": file_sha(valid_path),
              "invalid_inputs": file_sha(invalid_path), "readiness": file_sha(readiness_path),
              "c006": file_sha(c006_path), "c005": file_sha(c005_path)}
    if checks != EXPECTED:
        raise RuntimeError("frozen C007 v4 control inputs or sources changed: " + repr(checks))
    readiness = json.loads(readiness_path.read_text(encoding="utf-8"))
    if readiness.get("provider_sha256") != checks["provider"] or readiness.get("cli_sha256") != checks["cli"]:
        raise RuntimeError("READINESS_V4 anchors do not bind provider/CLI")

    sys.path.insert(0, str(IMPL))
    import finest_solver_v4 as solver  # noqa: E402

    valid_rows = {row["case_id"]: row["input"] for row in read_jsonl(valid_path)}
    invalid_rows = read_jsonl(invalid_path)
    unexpected_errors = 0
    invalid_calls = 0

    # Three frozen invalid inputs in both public modes.
    for row in invalid_rows:
        data = api_data(row["input"])
        for mode in ("adaptive", "reference"):
            invalid_calls += 1
            try:
                result = solver.solve(data, mode=mode)
                emit(row["case_id"], "invalid_input", data, result, mode=mode)
            except BaseException as error:
                unexpected_errors += 1
                emit(row["case_id"], "invalid_input_exception", data, None, mode=mode,
                     exception_type=type(error).__name__, exception=repr(error))

    # Invalid mode must raise ValueError rather than returning a final answer.
    mode_data = api_data(valid_rows["ctrl_unique_finest_3plus"])
    try:
        mode_result = solver.solve(mode_data, mode="unsupported")
        emit("ctrl_invalid_mode", "invalid_mode_returned", mode_data, mode_result, mode="unsupported")
    except ValueError as error:
        emit("ctrl_invalid_mode", "invalid_mode_rejected", mode_data, None, mode="unsupported",
             exception_type=type(error).__name__, exception=str(error))
    except BaseException as error:
        unexpected_errors += 1
        emit("ctrl_invalid_mode", "invalid_mode_exception", mode_data, None, mode="unsupported",
             exception_type=type(error).__name__, exception=repr(error))

    # Expired absolute deadline must be cooperative-incomplete with no final claim.
    expired_data = api_data(valid_rows["ctrl_unique_finest_3plus"])
    expired = solver.solve(expired_data, mode="adaptive", deadline=time.perf_counter() - 1.0)
    emit("ctrl_expired_deadline", "expired_deadline_before_work", expired_data, expired)

    # Inject a cooperative _Stop after swap-stage scanning has started.
    stage_data = {"alphabet": list("abcd"), "positive": ["ab", "cd"], "negative": ["ba", "dc"]}
    original_check = solver._check
    check_calls = 0

    def stop_inside_swap_stage(deadline):
        nonlocal check_calls
        check_calls += 1
        if check_calls == 4:
            raise solver._Stop
        return original_check(deadline)

    solver._check = stop_inside_swap_stage
    try:
        staged = solver.solve(stage_data, mode="adaptive", deadline=time.perf_counter() + 3600.0)
        emit("ctrl_swap_stage_deadline", "injected_stop_during_swap_stage", stage_data, staged,
             injected_check_calls=check_calls)
    except BaseException as error:
        unexpected_errors += 1
        emit("ctrl_swap_stage_deadline", "swap_stage_stop_exception", stage_data, None,
             injected_check_calls=check_calls, exception_type=type(error).__name__, exception=repr(error))
    finally:
        solver._check = original_check

    # On the frozen multiple-maximal fixture, keep one successful separator,
    # then inject either _Stop or KeyboardInterrupt on the next search round.
    partial_data = api_data(valid_rows["ctrl_multiple_maximal_refinements"])
    for control, exception_type in (("ctrl_stop_after_partial_separator", solver._Stop),
                                    ("ctrl_interrupt_after_partial_separator", KeyboardInterrupt)):
        original_masks = solver._canonical_masks
        round_index = 0

        def interrupted_masks(size):
            nonlocal round_index
            round_index += 1
            if round_index == 1:
                yield 1
                yield 3
            else:
                yield 1
                raise exception_type

        solver._canonical_masks = interrupted_masks
        try:
            result = solver.solve(partial_data, mode="adaptive")
            emit("ctrl_partial_separator", control, partial_data, result,
                 injected_mask_rounds=round_index)
        except BaseException as error:
            unexpected_errors += 1
            emit("ctrl_partial_separator", control + "_exception", partial_data, None,
                 injected_mask_rounds=round_index,
                 exception_type=type(error).__name__, exception=repr(error))
        finally:
            solver._canonical_masks = original_masks

    summary = {
        "record_type": "control_summary", "unexpected_errors": unexpected_errors,
        "invalid_input_rows": len(invalid_rows), "invalid_mode_checks": 1,
        "invalid_input_calls": invalid_calls,
        "controls": ["invalid_input_both_modes", "invalid_mode", "expired_deadline",
                     "injected_swap_stage_stop", "post_separator_stop", "post_separator_keyboardinterrupt"],
        "source_hashes": checks,
    }
    print(json.dumps(summary, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
