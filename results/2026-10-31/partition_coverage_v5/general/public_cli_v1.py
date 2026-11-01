"""Combined user-facing CLI for exact, certificate, and hybrid search.

The CLI defaults to exact search. Certificate mode may abstain when its sparse
unique-color certificate is unavailable. Hybrid mode falls through to exact
search only on that abstention, using the same absolute deadline.
"""
import argparse
import importlib.util
import json
import math
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parent.parent
GENERAL = Path(__file__).resolve().parent


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load provider: " + str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _normalize_certificate(result, mode):
    result = dict(result)
    result["mode"] = mode
    result["complete"] = bool(result.get("search_exhausted")) and result.get("status") != "incomplete"
    result["enumeration_complete"] = bool(result.get("search_exhausted"))
    result["decision_complete"] = bool(result.get("decision_complete"))
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="JSON data with alphabet, positive, negative, and optional k")
    parser.add_argument("--mode", choices=("exact", "certificate", "hybrid"), default="exact")
    parser.add_argument("--k", type=int, help="known number of nonempty blocks; defaults to input k or 2")
    parser.add_argument("--q", type=int, default=None,
                        help="finite local-word cap; omit for unrestricted regular factors (exact only)")
    parser.add_argument("--max-solutions", default="2",
                        help="positive count or 'all'; exact enumeration defaults to 2")
    parser.add_argument("--timeout-seconds", type=float, default=None,
                        help="finite nonnegative cooperative timeout shared across providers")
    parser.add_argument("--no-q-opposition", action="store_true",
                        help="disable q-opposition pruning in exact mode for matched baselines")
    args = parser.parse_args(argv)

    try:
        if args.timeout_seconds is not None and (not math.isfinite(args.timeout_seconds)
                or args.timeout_seconds < 0):
            raise ValueError("timeout-seconds must be finite and nonnegative")
        if args.q is not None and args.q < 1:
            raise ValueError("q must be a positive integer")
        if args.k is not None and args.k < 2:
            raise ValueError("k must be at least 2")
        if args.mode in ("certificate", "hybrid") and args.q is None:
            raise ValueError("certificate and hybrid modes require --q")
        if args.mode != "exact" and args.no_q_opposition:
            raise ValueError("--no-q-opposition is available only in exact mode")
        if args.max_solutions.lower() == "all":
            max_solutions = None
        else:
            try:
                max_solutions = int(args.max_solutions)
            except ValueError as exc:
                raise ValueError("max-solutions must be a positive integer or 'all'") from exc
            if max_solutions < 1:
                raise ValueError("max-solutions must be a positive integer or 'all'")

        start = time.perf_counter()
        deadline = (None if args.timeout_seconds is None
                    else start + args.timeout_seconds)
        with open(args.input, "r", encoding="utf-8-sig") as stream:
            data = json.load(stream)
        if not isinstance(data, dict):
            raise ValueError("input must be an object")
        k = args.k if args.k is not None else data.get("k", 2)
        if isinstance(k, bool) or not isinstance(k, int) or k < 2:
            raise ValueError("k must be an integer of at least 2")
        data = dict(data)
        data["k"] = k

        exact = _load("c005_exact_v2", GENERAL / "known_k_qexact_v2.py")
        if args.mode == "exact":
            result = exact.solve(data, k=k, local_word_cap=args.q, deadline=deadline,
                                 max_solutions=max_solutions,
                                 use_q_opposition=not args.no_q_opposition)
            result["mode"] = "exact"
            result["selected_provider"] = "known_k_qexact_v2"
        else:
            structural = _load("c005_sparse_certificate_v2",
                               ROOT / "structural" / "sparse_certificate_v2.py")
            certificate = structural.solve(data, k=k, local_word_cap=args.q,
                                           deadline=deadline, max_solutions=max_solutions)
            certificate = _normalize_certificate(certificate, args.mode)
            certificate["selected_provider"] = "sparse_certificate_v2"
            if args.mode == "certificate" or certificate.get("status") != "insufficient_coverage":
                result = certificate
            else:
                # Insufficient coverage is abstention, not infeasibility. The
                # exact provider gets the original absolute deadline and q.
                result = exact.solve(data, k=k, local_word_cap=args.q, deadline=deadline,
                                     max_solutions=max_solutions)
                result["mode"] = "hybrid"
                result["selected_provider"] = "known_k_qexact_v2"
                result["certificate_attempt"] = {
                    "method": certificate.get("method"),
                    "status": certificate.get("status"),
                    "reason": certificate.get("reason"),
                    "search_exhausted": certificate.get("search_exhausted")}
                result["fallback_trigger"] = "insufficient_coverage"

        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        status = result.get("status")
        if status == "incomplete":
            return 3
        if status == "insufficient_coverage":
            return 4
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "invalid_input", "error": str(exc)},
                         ensure_ascii=False, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
