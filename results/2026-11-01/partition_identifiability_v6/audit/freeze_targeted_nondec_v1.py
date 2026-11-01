"""Freeze the manager-supplied four-symbol non-decomposition candidate."""
import argparse
import hashlib
import json
from pathlib import Path


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    visible = dict(case_id="manager_candidate_four_symbol_cycles",
                   input=dict(alphabet=list("abcd"),
                              positive=["acdb", "cabd", "bcda", "dabc"],
                              negative=["abcd"]))
    truth = dict(case_id=visible["case_id"], original_candidate_preserved=True,
                 generator_kind="one_factor_infinite_regular_control",
                 blocks=[list("abcd")],
                 grammars=[dict(kind="finite_words_plus_unary_tail",
                                finite_words=visible["input"]["positive"],
                                tail_symbol="a", tail_min_length=5)])
    files = {"input.jsonl": canonical(visible), "truth.jsonl": canonical(truth)}
    entries = {}
    for name, raw in files.items():
        (args.output / name).write_bytes(raw)
        entries[name] = dict(sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
    manifest = dict(extension="C006_TARGETED_NONDECOMPOSITION_V1",
                    protocol="PROTOCOL_V2.md", cases=1, files=entries,
                    generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    solver_input_policy="Only input.jsonl is provider-visible; no k/q/truth.",
                    status="frozen_before_oracle_evaluation")
    (args.output / "manifest.json").write_bytes(canonical(manifest))
    print(json.dumps(manifest, ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
