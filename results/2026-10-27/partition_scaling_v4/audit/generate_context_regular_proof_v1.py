"""Record and independently check regular target-language interpretations."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpora" / "stage2_v1"
OUTPUT = HERE / "context_regular_target_proof_v1.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def project(word, block):
    members = set(block)
    return "".join(ch for ch in word if ch in members)


def in_tile_star(word, prefix, tiles):
    if not word.startswith(prefix):
        return False
    suffix = word[len(prefix):]
    if len(suffix) % 2:
        return False
    return all(suffix[i:i+2] in tiles for i in range(0, len(suffix), 2))


def main():
    manifest_path = CORPUS / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    proofs, failures = [], []
    for case_id in manifest["contextual_case_ids"]:
        row = next(item for item in manifest["cases"] if item["id"] == case_id)
        input_path = CORPUS / row["input"]
        truth_path = CORPUS / row["truth"]
        data = json.loads(input_path.read_text(encoding="utf-8"))
        truth = json.loads(truth_path.read_text(encoding="utf-8"))
        base = truth["base"]
        blocks = truth["target_blocks"]
        block_languages = []
        for block in blocks:
            tiles = sorted("".join(edge) for edge in truth["tree_edges"]
                           if edge[0] in block and edge[1] in block)
            prefix = project(base, block)
            block_languages.append({"block": block, "mandatory_prefix": prefix,
                                    "tiles": tiles, "regular_expression_schema":
                                    "mandatory_prefix followed by zero or more complete listed 2-symbol tiles"})
        positives_ok = True
        positive_checks = []
        for word in data["positive"]:
            projections = [project(word, block) for block in blocks]
            accepted = [in_tile_star(projection, spec["mandatory_prefix"], spec["tiles"])
                        for projection, spec in zip(projections, block_languages)]
            positive_checks.append({"word_sha256": hashlib.sha256(word.encode("utf-8")).hexdigest(),
                                    "length": len(word), "projection_lengths": list(map(len, projections)),
                                    "all_factors_accept": all(accepted)})
            positives_ok = positives_ok and all(accepted)
        negative_checks = []
        negatives_ok = True
        for word in data["negative"]:
            projections = [project(word, block) for block in blocks]
            accepted = [in_tile_star(projection, spec["mandatory_prefix"], spec["tiles"])
                        for projection, spec in zip(projections, block_languages)]
            rejected_blocks = [i for i, bit in enumerate(accepted) if not bit]
            negative_checks.append({"word_sha256": hashlib.sha256(word.encode("utf-8")).hexdigest(),
                                    "length": len(word), "projection_lengths": list(map(len, projections)),
                                    "accepted_by_factors": accepted, "rejected_factor_indices": rejected_blocks})
            negatives_ok = negatives_ok and bool(rejected_blocks)
        edges_forced = True
        expected = {tuple(sorted(edge)) for edge in truth["tree_edges"]}
        if len(expected) != len(data["alphabet"]) - data["k"]:
            edges_forced = False
        owner = {symbol: i for i, block in enumerate(blocks) for symbol in block}
        if any(owner[a] != owner[b] for a, b in expected):
            edges_forced = False
        parent = {symbol: symbol for symbol in data["alphabet"]}

        def find(symbol):
            while parent[symbol] != symbol:
                parent[symbol] = parent[parent[symbol]]
                symbol = parent[symbol]
            return symbol

        for a, b in expected:
            parent[find(b)] = find(a)
        component_map = {}
        for symbol in data["alphabet"]:
            component_map.setdefault(find(symbol), []).append(symbol)
        forced_components = {tuple(sorted(block)) for block in component_map.values()}
        target_components = {tuple(sorted(block)) for block in blocks}
        if forced_components != target_components or len(target_components) != data["k"] or any(len(block) < 2 for block in blocks):
            edges_forced = False
        okay = positives_ok and negatives_ok and edges_forced
        if not okay:
            failures.append(case_id)
        proofs.append({"case": case_id, "input_sha256": sha(input_path),
                       "truth_sidecar_sha256": sha(truth_path),
                       "alphabet_size": len(data["alphabet"]), "k": data["k"],
                       "base_sha256": hashlib.sha256(base.encode("utf-8")).hexdigest(),
                       "base_length": len(base), "target_blocks": blocks,
                       "block_languages": block_languages,
                       "positive_membership_checks": positive_checks,
                       "negative_nonmembership_checks": negative_checks,
                       "tree_must_link_edges": [list(edge) for edge in sorted(expected)],
                       "forced_tree_components": [list(block) for block in sorted(forced_components)],
                       "tree_components_equal_exact_k_blocks": edges_forced,
                       "unique_partition_reason": "Each tree edge is forced together: if its endpoints were separated, C+a would have the same local projection as positive C+ab on the a-side and as positive C on every other side, so the negative would be accepted. The tree edges force the listed k components, and exactly k nonempty blocks therefore give one partition.",
                       "regular_target_language": "L_i = u_i E_i*; u_i is the projection of C on block i; E_i contains the declared center+leaf 2-symbol tree tiles.",
                       "positive_membership_all_pass": positives_ok,
                       "negative_nonmembership_all_pass": negatives_ok,
                       "accepted": okay})
    record = {"schema": "C004-contextual-regular-target-proof-v1",
              "corpus_manifest_sha256": sha(manifest_path),
              "proof_generator_sha256": sha(Path(__file__)),
              "case_count": len(proofs), "accepted": not failures,
              "failures": failures, "proofs": proofs}
    if OUTPUT.exists():
        raise FileExistsError(f"refusing to overwrite proof record: {OUTPUT}")
    OUTPUT.write_text(json.dumps(record, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"accepted": record["accepted"], "case_count": len(proofs),
                      "failures": failures, "proof_sha256": sha(OUTPUT)},
                     ensure_ascii=False, separators=(",", ":")))
    if failures:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
