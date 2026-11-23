"""Check a certified weighted prune after actual merges, and corrupt its proof."""
from copy import deepcopy
import evaluate
from search import solve
from verify import verify


def run():
    data = evaluate.sample("abcde", ["cabaeba", "aca", "adbd", "eaeee", "ecad", "cbcaa"],
                           ["bebcacd", "ab", "ca"])
    result = solve(data, mode="maximal", shortcuts=False)
    assert result["max_devices"] == evaluate.exhaustive_optimum(data) == 2
    assert verify(data, result)["status"] == "VERIFIED"
    rows = result["certificate"]["rejections"]
    node = next(row for row in rows if row["reason"] == "weighted" and len(row["partition"]) < 5)
    broken = deepcopy(result)
    broken["certificate"]["rejections"].remove(node)
    assert verify(data, broken)["status"] == "INVALID"
    print("Verified and tampered with a weighted prune below the root.")


if __name__ == "__main__":
    run()
