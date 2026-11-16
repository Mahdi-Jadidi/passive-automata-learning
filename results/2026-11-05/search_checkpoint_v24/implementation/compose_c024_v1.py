"""Mechanical composition of frozen, disjoint A/B changes; no public edits."""
import hashlib
from pathlib import Path
here=Path(__file__).resolve().parent
a=(here/'candidate_c024a_v1/gate_v1.py').read_bytes()
b=(here/'candidate_c024b_v1/gate_v1.py').read_bytes()
assert hashlib.sha256(a).hexdigest()=='9725a263266f4e131019936e771b5df1cb100cd5715ec85c7dae90040f7e33f4'
assert hashlib.sha256(b).hexdigest()=='4e5a8e39528efadf3d2eeaab2dfa02a0d77711d7028005737fe78a42b38cb9a3'
at=a.decode().replace('\r\n','\n');bt=b.decode().replace('\r\n','\n')
prefix=at[:at.index('        solutions = []\n')]
suffix=bt[bt.index('        solutions = []\n'):]
combined=prefix+suffix
combined=combined.replace("METHOD = 'C024-A-forced-atom-bipartition-gate-v1'", "METHOD = 'C024-integrated-exact-search'")
out=here/'integrated_c024_v1';out.mkdir(exist_ok=False)
(out/'gate_v1.py').write_text(combined,encoding='utf-8')
(out/'partition_gate_v1.py').write_bytes((here/'baseline_c020_v1/partition_gate_v1.py').read_bytes())
print(hashlib.sha256((out/'gate_v1.py').read_bytes()).hexdigest())
