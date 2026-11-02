#!/usr/bin/env python3
"""Captured provider control cases: invalid data, stop, and interruption."""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION = ROOT / "implementation"
sys.path.insert(0, str(IMPLEMENTATION))
import finest_solver_v3  # noqa: E402


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def api_data(data):
    return {"alphabet": list(data["alphabet"]),
            "positive": ["".join(word) for word in data["positive"]],
            "negative": ["".join(word) for word in data["negative"]]}


def load_payload(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line]


def record(case_id, control, data, result, **extra):
    value = {"record_type": "control_result", "case_id": case_id,
             "control": control,
             "input_sha256": hashlib.sha256(canonical(data).encode("utf-8")).hexdigest(),
             "result": result}
    value.update(extra)
    print(json.dumps(value, ensure_ascii=False, sort_keys=True), flush=True)


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: run_provider_controls_v1.py VALID_INPUTS INVALID_INPUTS")
    valid_rows = {row["case_id"]: row["input"] for row in load_payload(sys.argv[1])}
    invalid_rows = load_payload(sys.argv[2])
    errors = 0

    for row in invalid_rows:
        data = api_data(row["input"])
        for mode in ("adaptive", "reference"):
            try:
                result = finest_solver_v3.solve(data, mode=mode)
                record(row["case_id"], "invalid_input", data, result, mode=mode)
            except BaseException as error:
                errors += 1
                record(row["case_id"], "invalid_input_exception", data, None,
                       mode=mode, exception_type=type(error).__name__, exception=repr(error))

    expired_data = api_data(valid_rows["ctrl_unique_finest_3plus"])
    try:
        expired = finest_solver_v3.solve(expired_data, mode="adaptive",
                                         deadline=time.perf_counter() - 1.0)
        record("ctrl_expired_deadline", "absolute_deadline_before_work", expired_data, expired)
    except BaseException as error:
        errors += 1
        record("ctrl_expired_deadline", "absolute_deadline_exception", expired_data, None,
               exception_type=type(error).__name__, exception=repr(error))

    # Stop inside the cheap must-link-component direct test. The provider's
    # cooperative check is patched only in this captured child process.
    cheap_data = api_data(valid_rows["ctrl_no_negatives"])
    old_check = finest_solver_v3._check
    check_calls = 0

    def stop_inside_cheap(deadline):
        nonlocal check_calls
        check_calls += 1
        if check_calls == 2:
            raise finest_solver_v3._Stop
        return old_check(deadline)

    finest_solver_v3._check = stop_inside_cheap
    try:
        cheap = finest_solver_v3.solve(cheap_data, mode="adaptive",
                                       deadline=time.perf_counter() + 3600.0)
        record("ctrl_cheap_path_cooperative_stop", "injected_stop_during_cheap_oracle",
               cheap_data, cheap, injected_check_calls=check_calls)
    except BaseException as error:
        errors += 1
        record("ctrl_cheap_path_cooperative_stop", "injected_stop_exception", cheap_data, None,
               injected_check_calls=check_calls, exception_type=type(error).__name__, exception=repr(error))
    finally:
        finest_solver_v3._check = old_check

    # On this frozen fixture the fourth direct-oracle return is the post-check
    # after the first successful separator. Inject _Stop and KeyboardInterrupt
    # there to require a partial meet/history with incomplete finality.
    ambiguity_data = api_data(valid_rows["ctrl_partial_meet_ambiguity"])
    for control, exception_type in (("ctrl_post_separator_stop", finest_solver_v3._Stop),
                                    ("ctrl_interrupt_after_partial_separator", KeyboardInterrupt)):
        old_direct = finest_solver_v3._direct
        direct_calls = 0

        def stop_after_one_separator(*args, **kwargs):
            nonlocal direct_calls
            value = old_direct(*args, **kwargs)
            direct_calls += 1
            if direct_calls == 4:
                raise exception_type
            return value

        finest_solver_v3._direct = stop_after_one_separator
        try:
            result = finest_solver_v3.solve(ambiguity_data, mode="adaptive")
            record("ctrl_partial_meet_ambiguity", control, ambiguity_data, result,
                   injected_direct_calls=direct_calls)
        except BaseException as error:
            errors += 1
            record("ctrl_partial_meet_ambiguity", control + "_exception", ambiguity_data, None,
                   injected_direct_calls=direct_calls, exception_type=type(error).__name__, exception=repr(error))
        finally:
            finest_solver_v3._direct = old_direct

    print(json.dumps({"record_type": "control_summary", "errors": errors,
                      "invalid_inputs": len(invalid_rows),
                      "controls": ["absolute_deadline_before_work", "injected_stop_during_cheap_oracle",
                                   "injected_post_separator_stop", "injected_post_separator_keyboardinterrupt"]},
                     sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
