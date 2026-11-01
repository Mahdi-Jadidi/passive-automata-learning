"""Promote the reviewed root-ready README without changing its worker source."""
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
source=ROOT/'implementation/ROOT_README_CANDIDATE_FA_v1.md'
raw=source.read_bytes()
with (ROOT/'README_FA.md').open('xb') as f:f.write(raw)
with (ROOT/'coordination/readme_promotion.json').open('x',encoding='utf-8') as f:
    json.dump(dict(source=str(source.relative_to(ROOT)),target='README_FA.md',sha256=sha256(raw).hexdigest()),f,indent=2)
print('README promoted')
