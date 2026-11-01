"""Freeze theory-lead examples as an audit-only input/grammar extension."""
import argparse
import hashlib
import json
from pathlib import Path


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--manager-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    rows = []
    for source_name, source_path in (("theory_examples_v1", args.source),
                                     ("manager_examples_v1", args.manager_source)):
        original = json.loads(source_path.read_text(encoding="utf-8"))
        for name, raw in original.items():
            if not isinstance(raw, dict) or "alphabet" not in raw:
                continue
            data = dict(alphabet=raw["alphabet"], positive=raw["positive"],
                        negative=raw["negative"])
            words = data["positive"] + data["negative"]
            case_id = f"{source_name}_{name}"
            if name == "infinite_irreducible_target_sample" or name == "irreducible_target_insufficient_sample":
                grammar = dict(kind="repeated_token_word_star", unit="ab")
                true_target = "(ab)*"
            else:
                tail_symbol = data["alphabet"][0]
                grammar = dict(kind="finite_words_plus_unary_tail",
                               finite_words=sorted(set(data["positive"])),
                               tail_symbol=tail_symbol,
                               tail_min_length=max(map(len, words), default=0) + 1)
                true_target = "one-factor-infinite-regular-completion"
            rows.append(dict(case_id=case_id, input=data,
                             source_file=source_path.name,
                             original_example_id=name,
                             true_target_description=true_target,
                             grammar=grammar))
    files = {"inputs.jsonl": b"".join(canonical({"case_id": r["case_id"], "input": r["input"]})
                                      for r in rows),
             "truth_sidecars.jsonl": b"".join(canonical(r) for r in rows)}
    entries = {}
    for name, raw in files.items():
        (args.output / name).write_bytes(raw)
        entries[name] = dict(sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
    manifest = dict(extension="C006_THEORY_EXAMPLES_V1", cases=len(rows),
                    source_hashes={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                   for p in (args.source, args.manager_source)},
                    protocol="PROTOCOL_V3.md", files=entries,
                    status="frozen_before_candidate_comparison")
    (args.output / "manifest.json").write_bytes(canonical(manifest))
    print(json.dumps(manifest, ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
