"""Exercise capture.py success, program-error, timeout and snapshot handling."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


CAPTURE_PATH = Path(__file__).with_name("capture.py")
SPEC = importlib.util.spec_from_file_location("c002_capture_selftest_module", CAPTURE_PATH)
CAPTURE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(CAPTURE)


def run(label: str, code: str, timeout: float = 5.0):
    return CAPTURE.capture(
        label,
        [sys.executable, "-B", "-X", "utf8", "-c", code],
        cwd=Path(__file__).parent,
        timeout_seconds=timeout,
        source_paths=[Path(__file__)],
    )


def main() -> int:
    passed = run("capture-selftest-success",
                 "import sys; print('out-ok'); print('err-ok', file=sys.stderr)")
    failed = run("capture-selftest-program-error",
                 "import sys; print('failure-out'); print('failure-err', file=sys.stderr); sys.exit(7)")
    timed = run("capture-selftest-timeout",
                "import time; print('before-timeout', flush=True); time.sleep(3)", 0.25)

    assert passed["execution_status"] == "success" and passed["exit_code"] == 0
    assert failed["execution_status"] == "program_error" and failed["exit_code"] == 7
    assert timed["execution_status"] == "timed_out" and timed["exit_code"] is None
    for record, expected in ((passed, b"out-ok"), (failed, b"failure-out"),
                             (timed, b"before-timeout")):
        attempt = Path(record["attempt_dir"])
        assert (attempt / "manifest.json").is_file()
        assert (attempt / "result.json").is_file()
        assert (attempt / "stderr.bin").is_file()
        assert expected in (attempt / "stdout.bin").read_bytes()
        import json
        manifest = json.loads((attempt / "manifest.json").read_text(encoding="utf-8"))
        assert manifest["sources"]
        for source in manifest["sources"]:
            blob = CAPTURE.AUDIT_DIR / source["snapshot"]
            assert blob.is_file()
            assert CAPTURE._sha256(blob.read_bytes()) == source["sha256"]

    print("capture self-test passed: success, program_error, timed_out, raw output, source hashes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
