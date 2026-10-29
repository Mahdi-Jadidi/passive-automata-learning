"""Independent integrity, label, and long-family proof audit for frozen inputs."""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

FREEZE = Path(sys.argv[1]).resolve()
ROOT = FREEZE.parent
MANIFEST = ROOT / "manifest.json"


def project(word, block):
    members = set(block)
    return "".join(ch for ch in word if ch in members)


def run_dfa(dfa, word):
    state = dfa["start"]
    for ch in word:
        state = dfa["transitions"][str(state)][ch]
    return state in dfa["accepting"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    problems, records, grid = [], [], {}
    actual_hashes = {entry["path"]: entry["sha256"] for entry in freeze["files"]}
    for entry in freeze["files"]:
        path = ROOT / entry["path"]
        if not path.is_file() or sha(path) != entry["sha256"] or path.stat().st_size != entry["bytes"]:
            problems.append({"kind": "frozen_file_hash_mismatch", "path": entry["path"]})
    for row in manifest["cases"]:
        ipath = ROOT / row["input"]
        data = json.loads(ipath.read_text(encoding="utf-8"))
        cid, family = row["id"], row["family"]
        if set(data) - {"alphabet", "k", "positive", "negative"}:
            problems.append({"id": cid, "kind": "truth_or_metadata_leaked_into_solver_input"})
        alphabet = data.get("alphabet")
        positives, negatives = data.get("positive"), data.get("negative")
        valid_k = (isinstance(data.get("k"), int) and not isinstance(data.get("k"), bool)
                   and 2 <= data["k"] <= len(alphabet or []))
        invalid_expected = family == "invalid"
        if not invalid_expected:
            if (not isinstance(alphabet, list) or len(alphabet) < 2 or
                    any(not isinstance(ch, str) or len(ch) != 1 for ch in alphabet) or
                    len(set(alphabet)) != len(alphabet) or not valid_k):
                problems.append({"id": cid, "kind": "unexpected_invalid_schema"})
            if not isinstance(positives, list) or not isinstance(negatives, list):
                problems.append({"id": cid, "kind": "samples_not_lists"})
            elif any(not isinstance(w, str) or set(w)-set(alphabet) for w in positives+negatives):
                problems.append({"id": cid, "kind": "sample_outside_declared_alphabet"})
            elif set(positives) & set(negatives):
                problems.append({"id": cid, "kind": "contradictory_labels_unexpected"})
        if row.get("truth"):
            tpath = ROOT / row["truth"]
            truth = json.loads(tpath.read_text(encoding="utf-8"))
            blocks = truth.get("blocks")
            if not isinstance(blocks, list) or len(blocks) != data["k"]:
                problems.append({"id": cid, "kind": "truth_block_count_mismatch"})
                continue
            flat = [ch for block in blocks for ch in block]
            if sorted(flat) != sorted(alphabet) or len(flat) != len(set(flat)):
                problems.append({"id": cid, "kind": "truth_does_not_partition_alphabet"})
            if "dfas" in truth:
                dfas = truth["dfas"]
                if len(dfas) != len(blocks):
                    problems.append({"id": cid, "kind": "dfa_count_mismatch"})
                for word in positives:
                    images = [project(word, block) for block in blocks]
                    if not all(run_dfa(dfa, image) for dfa, image in zip(dfas, images)):
                        problems.append({"id": cid, "kind": "planted_positive_rejected_by_truth_dfa"})
                        break
                for word in negatives:
                    images = [project(word, block) for block in blocks]
                    if all(run_dfa(dfa, image) for dfa, image in zip(dfas, images)):
                        problems.append({"id": cid, "kind": "planted_negative_accepted_by_all_truth_dfas"})
                        break
            elif "local_languages" in truth:
                langs = truth["local_languages"]
                if len(langs) != len(blocks):
                    problems.append({"id": cid, "kind": "local_language_count_mismatch"})
                else:
                    for word in positives:
                        images = [project(word, block) for block in blocks]
                        if not all(image in set(lang) for image, lang in zip(images, langs)):
                            problems.append({"id": cid, "kind": "planted_positive_outside_finite_local_language"})
                            break
                    for word in negatives:
                        images = [project(word, block) for block in blocks]
                        if all(image in set(lang) for image, lang in zip(images, langs)):
                            problems.append({"id": cid, "kind": "planted_negative_accepted_by_all_finite_local_languages"})
                            break
                    if family in ("small_singleton", "long_singleton"):
                        if any(len(set(lang)) != 1 for lang in langs):
                            problems.append({"id": cid, "kind": "singleton_truth_has_non_singleton_language"})
                        else:
                            singleton = [next(iter(set(lang))) for lang in langs]
                            for word in positives:
                                if [project(word, block) for block in blocks] != singleton:
                                    problems.append({"id": cid, "kind": "singleton_projection_not_fixed"})
                                    break
            if family in ("long_singleton", "stress_16384"):
                local_words = [lang[0] for lang in truth["local_languages"]]
                forward = "".join(local_words)
                reverse = "".join(reversed(local_words))
                if forward not in positives or reverse not in positives:
                    problems.append({"id": cid, "kind": "opposite_block_order_anchors_missing"})
                # Forward/reverse concatenations prove every cross-block pair
                # reverses order; fixed local projections prove no within-block edge.
                if any(project(w, block) != local for w in positives
                       for block, local in zip(blocks, local_words)):
                    problems.append({"id": cid, "kind": "long_singleton_truth_projection_mismatch"})
                if row.get("length") != len(forward) or len(forward) not in (128, 1024, 4096, 16384):
                    problems.append({"id": cid, "kind": "long_singleton_length_mismatch"})
            if family in ("random_dfa", "context_regular", "long_singleton", "stress_16384"):
                target = row.get("length")
                if any(len(w) != target for w in positives + negatives):
                    problems.append({"id": cid, "kind": "long_trace_length_not_exact"})
        else:
            truth = None
        if family in ("long_singleton", "random_dfa", "context_regular", "stress_16384"):
            key = (family, row["alphabet_size"], row["k"], row.get("length"))
            grid[str(key)] = grid.get(str(key), 0) + 1
        records.append({"id": cid, "family": family, "alphabet_size": row["alphabet_size"],
                        "k": row["k"], "positive_count": row["positive_count"],
                        "negative_count": row["negative_count"],
                        "positive_lengths": row["positive_lengths"],
                        "negative_lengths": row["negative_lengths"],
                        "truth_checked": truth is not None})
    small = [r for r in manifest["cases"] if r["alphabet_size"] <= 7 and r["family"] != "invalid"]
    summary = {"audit": "C004 corpus/truth integrity v1", "case_count": len(records),
               "frozen_file_count": len(freeze["files"]), "manifest_sha256": sha(MANIFEST),
               "small_alpha_full_set_case_count": len(small),
               "grid_cell_count": len(grid), "grid": grid,
               "truth_sidecar_count": sum(bool(r.get("truth")) for r in manifest["cases"]),
               "problems": problems, "case_records": records}
    sys.stdout.write(json.dumps(summary, ensure_ascii=False, separators=(",", ":")))
    sys.stdout.flush()
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
