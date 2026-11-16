"""Create the fixed C030 adversarial and bounded-timing inputs."""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent


def rec(alphabet, positive=(), negative=()):
    return {"alphabet": list(alphabet), "positive": [list(w) for w in positive],
            "negative": [list(w) for w in negative]}


fixed = [
    ("empty_alphabet_epsilon_positive", rec([], [()], [])),
    ("empty_alphabet_negative_epsilon", rec([], [], [()])),
    ("one_symbol_all_compatible", rec(["only"])),
    ("empty_observations", rec(["a", "b", "c"])),
    ("empty_positive", rec(["a", "b", "c"], [], [("a",), ("b", "c")])),
    ("empty_negative", rec(["a", "b", "c"], [(), ("a",), ("b", "c")], [])),
    ("all_compatible_no_negative", rec(["a", "b", "c"], [(), ("a", "b")], [])),
    ("contradictory_label", rec(["a", "b"], [("a",)], [("a",)])),
    ("unused_ids", rec(["a", "unused-1", "unused-2", "b"], [("a",)], [("b",)])),
    ("duplicate_order_refs", rec(["z", "a", "μ"], [("z",), ("a",), ("z",), ()],
                                   [("a",), ("z",), ("a",), ("μ",)])),
    ("nonadjacent_forced_pair", rec(["left", "gap", "right", "tail"],
                                     [("left", "right")], [("left",), ("right",)])),
    ("tied_nontrivial_optimum", rec(["a", "b", "c"], [(), ("a", "b", "c")], [("a",)])),
    ("different_C_and_O", rec(["a", "b"], [("a",), ("b",)], [("a", "b")])),
    ("unicode_punctuation_space_ids", rec(["x y", "☃", "!", "prefix-long", "prefix"],
                                           [("x y", "☃"), ("!",)], [("prefix", "prefix-long")])),
    ("raw_join_collision", rec(["a", "bc", "ab", "c"], [("a", "bc")], [("ab", "c")])),
    ("long_small_alphabet", rec(["0", "1", "2", "3"],
                                 [tuple("0" if i % 2 == 0 else "1" for i in range(2048))],
                                 [tuple("2" if i % 3 == 0 else "3" for i in range(2048))])),
    ("many_words_small_alphabet", rec(["a", "b", "c", "d"],
                                       [tuple(w) for w in [("a",)*i + ("b",) for i in range(80)]],
                                       [tuple(w) for w in [("c",)*i + ("d",) for i in range(80)]])),
    # C026 CE1, CE2 initial, canonical-changing extension, CE3 meet, CE7.
    ("C026_CE1", rec(["a", "b"], [()], [("a",)])),
    ("C026_CE2_initial", rec(["a", "b", "c"], [(), ("a", "b", "c")], [("a",)])),
    ("C026_CE2_add_b", rec(["a", "b", "c"], [(), ("a", "b", "c")], [("a",), ("b",)])),
    ("C026_CE2_add_c", rec(["a", "b", "c"], [(), ("a", "b", "c")], [("a",), ("c",)])),
    ("C026_CE3_meet", rec(["a", "b", "c"], [(), ("a", "b", "c")], [("a",)])),
    ("C026_CE7_expansion", rec(["a", "b"], [("a", "b")], [("b", "a")])),
    ("quantifier_counterexample", rec(["a", "b"], [("a",), ("b",)], [("a", "b")])),
]

# Timing corpus: fixed before candidate measurements; <= 8 input records.
timing = [
    ("singleton_no_observations_m8", rec([f"s{i}" for i in range(8)])),
    ("singleton_compatible_m5", rec([f"b{i}" for i in range(5)])),
    ("forced_nonadjacent", rec(["a", "gap1", "b", "gap2", "c", "d"],
                                [("a", "b")], [("a",), ("b",)])),
    ("tied_nontrivial_optimum", rec(["a", "b", "c"], [(), ("a", "b", "c")], [("a",)])),
    ("memo_repeated_masks", rec([f"q{i}" for i in range(7)],
                                 [("q0", "q2", "q4"), ("q1", "q3", "q5")],
                                 [(f"q{i}",) for i in range(7)])),
    ("memo_early_failure", rec([f"e{i}" for i in range(7)],
                                [("e0",)], [("e1",), ("e0", "e2"), ("e0", "e3"), ("e0", "e4")])),
    ("long_many_words", next(value for key, value in fixed if key == "many_words_small_alphabet")),
    ("general_no_shortcut_m7", rec([f"g{i}" for i in range(7)],
                                    [("g0", "g1"), ("g2", "g3"), ("g4",)],
                                    [("g0",), ("g2", "g4"), ("g6",)])),
]


def write(name, rows):
    (OUT / name).write_text("".join(json.dumps({"case": key, "input": value}, ensure_ascii=False,
                                                separators=(",", ":")) + "\n"
                                for key, value in rows), encoding="utf-8")


if __name__ == "__main__":
    write("fixed_cases.jsonl", fixed)
    write("timing_cases.jsonl", timing)
    print(json.dumps({"fixed_cases": len(fixed), "timing_cases": len(timing)}, sort_keys=True))
