#!/usr/bin/env python3
"""Independent replay of C007 adaptive/reference batches against all-k truth."""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest_bytes(data):
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line]


def normalized_partition(partition):
    return tuple(sorted((tuple(sorted(block)) for block in partition), key=lambda block: block[0]))


def normalized_set(partitions):
    return {normalized_partition(partition) for partition in partitions}


def api_data(data):
    return {"alphabet": list(data["alphabet"]),
            "positive": ["".join(word) for word in data["positive"]],
            "negative": ["".join(word) for word in data["negative"]]}


def sorted_labels(data):
    return sorted(set(data["positive"])), sorted(set(data["negative"]))


def projection(word, block):
    symbols = set(block)
    return "".join(symbol for symbol in word if symbol in symbols)


def direct_witness(data, partition):
    positive, negative = sorted_labels(data)
    blocks = [list(block) for block in partition]
    languages = [{projection(word, block) for word in positive} for block in blocks]
    for word in negative:
        projections = [projection(word, block) for block in blocks]
        if all(value in languages[index] for index, value in enumerate(projections)):
            matches = [next(candidate for candidate in positive
                            if projection(candidate, block) == projections[index])
                       for index, block in enumerate(blocks)]
            return None, {"negative": word, "projections": projections,
                          "matching_positive_by_block": matches}
    witness = {
        "partition": [sorted(block) for block in blocks],
        "positive_projection_languages": [sorted(language) for language in languages],
        "positive_witnesses": [
            {"word": word, "projections": [projection(word, block) for block in blocks]}
            for word in positive],
        "negative_witnesses": [
            {"word": word,
             "projections": [projection(word, block) for block in blocks],
             "rejected_by_blocks": [index for index, block in enumerate(blocks)
                                    if projection(word, block) not in languages[index]]}
            for word in negative],
    }
    return witness, None


def is_valid_partition(partition, alphabet, exact_blocks=None):
    if not isinstance(partition, list) or not partition:
        return False
    if exact_blocks is not None and len(partition) != exact_blocks:
        return False
    if any(not isinstance(block, list) or not block for block in partition):
        return False
    if any(any(not isinstance(symbol, str) for symbol in block) for block in partition):
        return False
    flat = [symbol for block in partition for symbol in block]
    return len(flat) == len(set(flat)) and set(flat) == set(alphabet)


def refines(fine, coarse):
    coarse_sets = [set(block) for block in coarse]
    return all(any(set(block) <= target for target in coarse_sets) for block in fine)


def coarsening_meet(current, cut):
    result = []
    for block in current:
        for side in cut:
            intersection = sorted(set(block) & set(side))
            if intersection:
                result.append(intersection)
    return sorted(result, key=lambda block: block[0])


def cut_splits_partition(partition, cut):
    owner = {symbol: side_index for side_index, side in enumerate(cut) for symbol in side}
    return any(len({owner[symbol] for symbol in block}) > 1 for block in partition)


def cut_from_mask(atoms, mask):
    sides = [[], []]
    for index, atom in enumerate(atoms):
        sides[0 if mask & (1 << index) else 1].extend(atom)
    return [sorted(sides[0]), sorted(sides[1])]


def canonical_masks(count):
    total = (1 << (count - 1)) - 1
    return [(tail << 1) | 1 for tail in range(total)]


def dsu_components(alphabet, edges):
    parent = {symbol: symbol for symbol in alphabet}

    def find(item):
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    for edge in edges:
        a, b = edge["symbols"]
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra
    groups = {}
    for symbol in alphabet:
        groups.setdefault(find(symbol), []).append(symbol)
    return sorted((sorted(group) for group in groups.values()), key=lambda group: group[0])


def valid_edge(edge, data):
    alphabet = set(data["alphabet"])
    positive, negative = sorted_labels(data)
    if not isinstance(edge, dict):
        return False
    pair = edge.get("symbols")
    witness = edge.get("witness")
    if (not isinstance(pair, list) or len(pair) != 2 or pair[0] == pair[1]
            or any(not isinstance(symbol, str) or symbol not in alphabet for symbol in pair)
            or not isinstance(witness, dict) or not isinstance(witness.get("negative"), str)):
        return False
    a, b = pair
    negative_word = witness["negative"]
    if negative_word not in negative:
        return False
    if witness.get("rule") == "adjacent_swap":
        p = witness.get("positive")
        i = witness.get("position")
        return (p in positive and isinstance(i, int) and not isinstance(i, bool)
                and 0 <= i < len(p) - 1 and p[i:i + 2] in (a + b, b + a)
                and p[:i] + p[i + 1] + p[i] + p[i + 2:] == negative_word)
    if witness.get("rule") != "insertion_rescue":
        return False
    pair_words = witness.get("positive")
    i = witness.get("position")
    if (not isinstance(pair_words, list) or len(pair_words) != 2
            or any(word not in positive for word in pair_words)
            or isinstance(i, bool) or not isinstance(i, int) or not 0 <= i < len(negative_word)):
        return False
    base, rescue = pair_words
    deleted = negative_word[i]
    if deleted not in pair or negative_word[:i] + negative_word[i + 1:] != base:
        return False
    inserted = pair[1] if deleted == pair[0] else pair[0]
    return rescue in (negative_word[:i] + inserted + negative_word[i:],
                      negative_word[:i + 1] + inserted + negative_word[i + 1:])


def verified_forced_atoms(atoms, all_compatible):
    for block in atoms:
        for i, left in enumerate(block):
            for right in block[i + 1:]:
                if any(not any(left in candidate and right in candidate for candidate in partition)
                       for partition in all_compatible):
                    return False
    return True


def verify_edge_set(data, certificate, oracle):
    edges = certificate.get("must_link_edges")
    if not isinstance(edges, list) or any(not valid_edge(edge, data) for edge in edges):
        return None, "bad_must_link_edge"
    atoms = dsu_components(data["alphabet"], edges)
    if normalized_partition(certificate.get("components", [])) != normalized_partition(atoms):
        return None, "must_link_components_mismatch"
    all_compatible = oracle["compatible_partitions"]
    if not verified_forced_atoms(atoms, all_compatible):
        return None, "must_link_edge_not_forced_by_all_k_oracle"
    return atoms, None


def verify_collision(data, partition, collision):
    if not isinstance(collision, dict):
        return False
    positive, negative = sorted_labels(data)
    word = collision.get("negative")
    matches = collision.get("matching_positive_by_block")
    if word not in negative or not isinstance(matches, list) or len(matches) != len(partition):
        return False
    projections = [projection(word, block) for block in partition]
    if collision.get("projections") != projections:
        return False
    return all(matches[index] in positive
               and projection(matches[index], block) == projections[index]
               for index, block in enumerate(partition))


def verify_no_separator(data, certificate, claimed_meet, oracle):
    alphabet = data["alphabet"]
    atoms, error = verify_edge_set(data, certificate, oracle)
    if error:
        return False, error, None
    if not is_valid_partition(claimed_meet, alphabet):
        return False, "invalid_claimed_meet", None
    records = certificate.get("cut_records")
    if not isinstance(records, list):
        return False, "missing_cut_records", None
    expected_masks = canonical_masks(len(atoms))
    by_mask = {}
    for record in records:
        if not isinstance(record, dict):
            return False, "malformed_cut_record", None
        mask = record.get("mask")
        if isinstance(mask, bool) or not isinstance(mask, int) or mask in by_mask:
            return False, "duplicate_or_invalid_cut_mask", None
        by_mask[mask] = record
    if set(by_mask) != set(expected_masks):
        return False, "incomplete_cut_cover", None

    feasible_cuts = []
    for mask in expected_masks:
        cut = cut_from_mask(atoms, mask)
        record = by_mask[mask]
        if record.get("kind") == "incompatible":
            if not verify_collision(data, cut, record.get("collision")):
                return False, f"invalid_collision_cut_{mask}", None
        elif record.get("kind") == "compatible_nonseparator":
            expected_witness, collision = direct_witness(data, cut)
            if expected_witness is None or record.get("witness") != expected_witness:
                return False, f"invalid_compatible_cut_witness_{mask}", None
            if cut_splits_partition(claimed_meet, cut):
                return False, f"nonseparator_cut_splits_meet_{mask}", None
            feasible_cuts.append(cut)
        else:
            return False, f"unknown_cut_record_kind_{mask}", None

    current = [list(alphabet)]
    history = certificate.get("successful_separators", [])
    if not isinstance(history, list):
        return False, "malformed_successful_separator_history", None
    for step in history:
        if not isinstance(step, dict):
            return False, "malformed_successful_separator", None
        cut = step.get("cut")
        if not is_valid_partition(cut, alphabet, exact_blocks=2):
            return False, "invalid_successful_separator", None
        witness, collision = direct_witness(data, cut)
        if witness is None or step.get("witness") != witness:
            return False, "separator_not_independently_compatible", None
        if not cut_splits_partition(current, cut):
            return False, "separator_does_not_refine_current_meet", None
        if any(cut_splits_partition([atom], cut) for atom in atoms):
            return False, "separator_splits_forced_atom", None
        mask = step.get("mask")
        if mask is not None:
            if isinstance(mask, bool) or not isinstance(mask, int) or mask not in expected_masks:
                return False, "invalid_separator_mask", None
            if normalized_partition(cut_from_mask(atoms, mask)) != normalized_partition(cut):
                return False, "separator_mask_mismatch", None
        current = coarsening_meet(current, cut)

    for cut in feasible_cuts:
        current = coarsening_meet(current, cut)
    if normalized_partition(current) != normalized_partition(claimed_meet):
        return False, "meet_reconstruction_mismatch", current
    return True, "complete_separator_cover", atoms


def verify_early_ambiguity(data, result, certificate, oracle):
    if result.get("meet_is_final") is not False:
        return False, "early_meet_must_be_marked_nonfinal"
    atoms, error = verify_edge_set(data, certificate, oracle)
    if error:
        return False, error
    history = certificate.get("successful_separators")
    if not isinstance(history, list) or len(history) < 2:
        return False, "early_ambiguity_needs_two_feasible_cuts"
    current = [list(data["alphabet"])]
    for step in history:
        cut = step.get("cut") if isinstance(step, dict) else None
        if not is_valid_partition(cut, data["alphabet"], exact_blocks=2):
            return False, "malformed_early_separator"
        witness, collision = direct_witness(data, cut)
        if witness is None or witness != step.get("witness"):
            return False, "early_separator_not_compatible"
        if not cut_splits_partition(current, cut):
            return False, "early_separator_does_not_split_previous_meet"
        if any(cut_splits_partition([atom], cut) for atom in atoms):
            return False, "early_separator_splits_forced_atom"
        mask = step.get("mask")
        if mask is not None:
            if isinstance(mask, bool) or not isinstance(mask, int) or mask not in canonical_masks(len(atoms)):
                return False, "bad_early_separator_mask"
            if normalized_partition(cut_from_mask(atoms, mask)) != normalized_partition(cut):
                return False, "early_separator_mask_mismatch"
        current = coarsening_meet(current, cut)
    partial = result.get("partial_meet")
    if normalized_partition(current) != normalized_partition(partial):
        return False, "partial_meet_reconstruction_mismatch"
    witness, collision = direct_witness(data, partial)
    if witness is not None or not verify_collision(data, partial, result.get("meet_collision")):
        return False, "partial_meet_not_proved_infeasible"
    # This directly confirms that every full compatible answer respects every
    # found feasible separator, rather than treating the partial meet as final.
    if any(not refines(partition, partial) for partition in oracle["compatible_partitions"]):
        return False, "oracle_partition_violates_partial_meet"
    return True, "early_infeasible_meet_decision_only"


def replay_result(data, result, oracle):
    alphabet = data["alphabet"]
    status = result.get("status")
    if result.get("complete") is not True or result.get("decision_complete") is not True:
        return False, "provider_result_not_decision_complete"
    expected_unique = oracle["meet_compatible"]
    expected_meet = normalized_partition(oracle["meet"])
    frontier = oracle["maximal_refinement_frontier"]
    if expected_unique:
        expected_status = "one_block_only" if len(oracle["meet"]) == 1 else "finest_unique"
    else:
        expected_status = "multiple_maximal_exist"
    if status != expected_status:
        return False, f"status_mismatch_expected_{expected_status}_got_{status}"

    certificate = result.get("finality_certificate")
    if not isinstance(certificate, dict):
        return False, "missing_finality_certificate"
    kind = certificate.get("kind")
    if kind == "must_link_components_compatible":
        atoms, error = verify_edge_set(data, certificate, oracle)
        if error:
            return False, error
        if status == "multiple_maximal_exist":
            return False, "shortcut_cannot_prove_ambiguity"
        if normalized_partition(atoms) != expected_meet:
            return False, "shortcut_atoms_not_exact_sample_meet"
        witness, collision = direct_witness(data, atoms)
        if witness is None:
            return False, "shortcut_partition_incompatible"
        if result.get("finest_witness") != witness:
            return False, "shortcut_witness_replay_mismatch"
        if status == "one_block_only" and (len(atoms) != 1 or oracle["compatible_binary_partitions"]):
            return False, "shortcut_one_block_only_mismatch"
        if status == "one_block_only" and result.get("meet_partition") != atoms:
            return False, "shortcut_one_block_partition_mismatch"
        return True, "must_link_components_compatible"

    if kind == "early_infeasible_meet":
        if status != "multiple_maximal_exist":
            return False, "early_infeasible_meet_wrong_status"
        valid, why = verify_early_ambiguity(data, result, certificate, oracle)
        return valid, why

    if kind != "complete_separator_cover":
        return False, "unsupported_finality_certificate"
    claimed_meet = certificate.get("meet_partition")
    valid, why, details = verify_no_separator(data, certificate, claimed_meet, oracle)
    if not valid:
        return False, why
    if normalized_partition(claimed_meet) != expected_meet:
        return False, "complete_cover_meet_differs_from_all_k_oracle"
    if status == "finest_unique":
        witness, collision = direct_witness(data, result.get("finest_witness", {}).get("partition", []))
        if witness is None or witness != result.get("finest_witness"):
            return False, "final_finest_witness_replay_mismatch"
        if normalized_partition(result["finest_witness"]["partition"]) != expected_meet:
            return False, "final_finest_witness_not_oracle_meet"
    elif status == "multiple_maximal_exist":
        witness, collision = direct_witness(data, claimed_meet)
        if witness is not None or not verify_collision(data, claimed_meet, result.get("meet_collision")):
            return False, "final_meet_incompatibility_not_replayed"
        if len(frontier) < 2:
            return False, "oracle_does_not_have_multiple_maxima"
    elif status == "one_block_only":
        if normalized_partition(claimed_meet) != expected_meet or oracle["compatible_binary_partitions"]:
            return False, "complete_cover_one_block_only_mismatch"
        witness, collision = direct_witness(data, [list(alphabet)])
        if witness is None:
            return False, "universal_partition_incompatible"
        if result.get("finest_witness") is not None and result["finest_witness"] != witness:
            return False, "one_block_witness_replay_mismatch"
    return True, "complete_separator_cover"


def parse_batch(path, expected_mode):
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    records = [json.loads(line) for line in lines]
    if not records or records[-1].get("record_type") != "batch_summary":
        raise AssertionError(f"missing batch summary: {path}")
    summary = records[-1]
    if summary.get("mode") != expected_mode:
        raise AssertionError(f"mode mismatch in capture: {path}")
    cases = records[:-1]
    if any(record.get("record_type") != "case_result" for record in cases):
        raise AssertionError(f"provider batch contains case errors: {path}")
    return {record["case_id"]: record for record in cases}, summary, len(Path(path).read_bytes())


def main():
    if len(sys.argv) != 7:
        raise SystemExit("usage: validate_provider_gate_v1.py ADAPTIVE_STDOUT REFERENCE_STDOUT INPUTS PRIMARY INDEPENDENT REPORT")
    adaptive_path, reference_path, inputs_path, primary_path, independent_path, report_path = map(Path, sys.argv[1:])
    input_rows = read_jsonl(inputs_path)
    primary_rows = read_jsonl(primary_path)
    independent_rows = read_jsonl(independent_path)
    expected_ids = [row["case_id"] for row in input_rows]
    oracle_by_id = {row["case_id"]: row for row in primary_rows}
    independent_by_id = {row["case_id"]: row for row in independent_rows}
    adaptive, adaptive_summary, adaptive_bytes = parse_batch(adaptive_path, "adaptive")
    reference, reference_summary, reference_bytes = parse_batch(reference_path, "reference")
    if (len(expected_ids) != len(set(expected_ids)) or set(adaptive) != set(expected_ids)
            or set(reference) != set(expected_ids) or set(oracle_by_id) != set(expected_ids)
            or set(independent_by_id) != set(expected_ids)):
        raise AssertionError("input/provider/oracle case ID sets differ")

    failures = []
    status_hist = {"adaptive": Counter(), "reference": Counter()}
    certificate_hist = Counter()
    cut_count = 0
    early_count = 0
    for row in input_rows:
        case_id = row["case_id"]
        data = api_data(row["input"])
        oracle = oracle_by_id[case_id]
        # Independent direct-poset definition must agree with the primary meet.
        direct = independent_by_id[case_id]
        if direct["unique_finest_by_direct_poset"] != oracle["meet_compatible"]:
            failures.append({"case_id": case_id, "scope": "oracle", "reason": "direct_poset_vs_meet"})
        if direct["direct_finest_candidates"]:
            if normalized_partition(direct["direct_finest_candidates"][0]) != normalized_partition(oracle["meet"]):
                failures.append({"case_id": case_id, "scope": "oracle", "reason": "direct_finest_not_meet"})
        for mode, batch in (("adaptive", adaptive), ("reference", reference)):
            record = batch[case_id]
            if record.get("payload_sha256") != oracle["payload_sha256"] or record.get("mode") != mode:
                failures.append({"case_id": case_id, "mode": mode, "scope": "binding", "reason": "payload_or_mode_mismatch"})
                continue
            result = record["result"]
            status_hist[mode][result.get("status", "missing")] += 1
            valid, reason = replay_result(data, result, oracle)
            if not valid:
                failures.append({"case_id": case_id, "mode": mode, "scope": "certificate", "reason": reason})
            else:
                certificate_hist[result["finality_certificate"]["kind"]] += 1
                if result["finality_certificate"]["kind"] == "early_infeasible_meet":
                    early_count += 1
                if result["finality_certificate"]["kind"] == "complete_separator_cover":
                    cut_count += len(result["finality_certificate"].get("cut_records", []))
            if mode == "reference":
                observed = normalized_set(result.get("reference_bipartitions", []))
                expected = normalized_set(oracle["compatible_binary_partitions"])
                if observed != expected:
                    failures.append({"case_id": case_id, "mode": mode, "scope": "all_binary", "reason": "binary_reference_set_mismatch"})

    # Explicitly require all registered edge cases to hit their intended class.
    required = {
        "ctrl_unique_finest_3plus": ("finest_unique", 3),
        "ctrl_multiple_maximal_refinements": ("multiple_maximal_exist", 2),
        "ctrl_partial_meet_ambiguity": ("multiple_maximal_exist", 2),
        "ctrl_one_block_only": ("one_block_only", 1),
        "ctrl_no_positives": ("finest_unique", 3),
        "ctrl_no_negatives": ("finest_unique", 3),
        "ctrl_unused_symbol": ("finest_unique", 3),
    }
    for case_id, (expected_status, minimum_frontier) in required.items():
        for mode, batch in (("adaptive", adaptive), ("reference", reference)):
            result = batch[case_id]["result"]
            oracle = oracle_by_id[case_id]
            if (result.get("status") != expected_status
                    or len(oracle["maximal_refinement_frontier"]) < minimum_frontier):
                failures.append({"case_id": case_id, "mode": mode, "scope": "target_control", "reason": "target_control_not_hit"})
    epsilon_row = next(row for row in input_rows if row["case_id"] == "ctrl_epsilon_positive")
    if [] not in epsilon_row["input"]["positive"]:
        failures.append({"case_id": "ctrl_epsilon_positive", "scope": "target_control", "reason": "epsilon_missing"})

    # Mutation controls prove the independent replay rejects missing/forged
    # finality claims rather than only accepting the provider's outputs.
    mutation_results = {}
    base_complete = next((record["result"] for record in adaptive.values()
                          if record["result"].get("finality_certificate", {}).get("kind") == "complete_separator_cover"
                          and record["result"]["finality_certificate"].get("cut_records")), None)
    base_id = next((case_id for case_id, record in adaptive.items()
                    if record["result"].get("finality_certificate", {}).get("kind") == "complete_separator_cover"
                    and record["result"]["finality_certificate"].get("cut_records")), None)
    if base_complete is None:
        failures.append({"scope": "mutation", "reason": "no_complete_cover_fixture"})
    else:
        base_row = next(row for row in input_rows if row["case_id"] == base_id)
        base_data = api_data(base_row["input"])
        base_oracle = oracle_by_id[base_id]
        missing = json.loads(json.dumps(base_complete))
        missing["finality_certificate"]["cut_records"].pop()
        mutation_results["missing_cut_branch_rejected"] = not replay_result(base_data, missing, base_oracle)[0]
        forged = json.loads(json.dumps(base_complete))
        record = next((r for r in forged["finality_certificate"]["cut_records"] if r.get("kind") == "incompatible"), None)
        if record is None:
            mutation_results["forged_collision_rejected"] = False
        else:
            record["collision"]["matching_positive_by_block"][0] += "#"
            mutation_results["forged_collision_rejected"] = not replay_result(base_data, forged, base_oracle)[0]
    early_id = "ctrl_partial_meet_ambiguity"
    early_result = adaptive[early_id]["result"]
    early_row = next(row for row in input_rows if row["case_id"] == early_id)
    early_data = api_data(early_row["input"])
    early_oracle = oracle_by_id[early_id]
    partial_mutant = json.loads(json.dumps(early_result))
    partial_mutant["finality_certificate"]["successful_separators"].pop()
    mutation_results["partial_meet_missing_separator_rejected"] = not replay_result(early_data, partial_mutant, early_oracle)[0]
    finality_mutant = json.loads(json.dumps(early_result))
    finality_mutant["meet_is_final"] = True
    mutation_results["partial_meet_as_final_rejected"] = not replay_result(early_data, finality_mutant, early_oracle)[0]
    if not all(mutation_results.values()):
        failures.append({"scope": "mutation", "reason": "one_or_more_mutants_accepted", "details": mutation_results})

    report = {
        "schema_version": 1,
        "status": "accepted" if not failures else "rejected",
        "valid_rows": len(input_rows),
        "adaptive_rows": len(adaptive),
        "reference_rows": len(reference),
        "adaptive_status_counts": dict(sorted(status_hist["adaptive"].items())),
        "reference_status_counts": dict(sorted(status_hist["reference"].items())),
        "independent_certificate_replays": sum(sum(status_hist[mode].values())
                                                for mode in ("adaptive", "reference")),
        "complete_cover_cut_records_replayed": cut_count,
        "early_ambiguity_certificates_replayed": early_count,
        "mutations_rejected": mutation_results,
        "batch_capture_bytes": {"adaptive": adaptive_bytes, "reference": reference_bytes},
        "batch_attempt_ids": {"adaptive": adaptive_path.parent.name, "reference": reference_path.parent.name},
        "input_sha256": digest_bytes(inputs_path.read_bytes()),
        "all_k_primary_sha256": digest_bytes(primary_path.read_bytes()),
        "all_k_independent_sha256": digest_bytes(independent_path.read_bytes()),
        "failures": failures,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                           encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
