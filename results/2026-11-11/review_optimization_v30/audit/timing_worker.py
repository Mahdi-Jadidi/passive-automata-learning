"""One fresh process for a single frozen timing observation."""
import argparse
import importlib.util
import json
import sys

parser = argparse.ArgumentParser()
parser.add_argument("module")
parser.add_argument("function")
args = parser.parse_args()
spec = importlib.util.spec_from_file_location("timedsolver", args.module)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
record = json.load(sys.stdin)
print(json.dumps(getattr(module, args.function)(record), ensure_ascii=False, sort_keys=True,
                 separators=(",", ":")))
