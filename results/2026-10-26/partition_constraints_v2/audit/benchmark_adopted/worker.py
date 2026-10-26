"""One fresh-process invocation of the unchanged C002 driver; stdout is untouched.

Positional arguments: ROOT INPUT METHOD timing|memory SIDECAR SOFT_SECONDS.
Bootstrap imports sys/time are outside the measured pipeline. All driver imports,
input reading, preprocessing, search, JSON serialization and stdout flushing are
inside. runpy infrastructure is also included, identically for all methods.
"""
import sys
import time


def main():
    root, input_path, method, mode, sidecar, soft_seconds = sys.argv[1:]
    if mode not in ("timing", "memory"):
        raise ValueError("mode must be timing or memory")
    memory = None
    if mode == "memory":
        import tracemalloc
        memory = tracemalloc
        memory.start()
    started = time.perf_counter()
    code = 1
    error = None
    try:
        import runpy
        from pathlib import Path
        sys.path.insert(0, root)
        sys.argv = [str(Path(root) / "solver.py"), input_path,
                    "--method", method, "--timeout-seconds", soft_seconds]
        try:
            runpy.run_path(sys.argv[0], run_name="__main__")
            code = 0
        except SystemExit as exit_request:
            if exit_request.code is None:
                code = 0
            elif isinstance(exit_request.code, int):
                code = exit_request.code
            else:
                print(exit_request.code, file=sys.stderr)
                code = 1
    except BaseException as exception:
        import traceback
        error = repr(exception)
        traceback.print_exc()
    finally:
        sys.stdout.flush()
        sys.stderr.flush()
        pipeline_seconds = time.perf_counter() - started
        allocation = memory.get_traced_memory() if memory is not None else None
        if memory is not None:
            memory.stop()
        # Metadata writing, including this import, is outside measured time/peak.
        import json
        from pathlib import Path
        record = {
            "schema_version": 1, "mode": mode, "method": method,
            "exit_code": code, "pipeline_seconds": pipeline_seconds,
            "pipeline_scope": "runpy import through unchanged driver and output flush",
            "python_traced_current_bytes": allocation[0] if allocation else None,
            "python_traced_peak_bytes": allocation[1] if allocation else None,
            "worker_error": error,
            "memory_scope": "Python tracemalloc allocations since start; excludes bootstrap, RSS and untraced native allocations",
        }
        with Path(sidecar).open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(record, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
