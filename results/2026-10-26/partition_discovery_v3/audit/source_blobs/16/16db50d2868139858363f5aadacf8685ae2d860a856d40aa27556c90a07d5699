"""Capture only saved-data analysis; NEVER imports providers."""
import importlib.util
import json
from pathlib import Path
import sys
from uuid import uuid4

HERE=Path(__file__).resolve().parent
CYCLE=HERE.parents[1]
AUDIT=CYCLE/'audit'
LEDGER=AUDIT/'performance_adopted/runs/serial_v1/ledger.jsonl'
REPORT=AUDIT/'validation/performance_v4/report.json'
spec=importlib.util.spec_from_file_location('c003_analysis_capture',AUDIT/'capture.py')
capture=importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)
rows=[json.loads(line) for line in LEDGER.read_text(encoding='utf-8').splitlines() if line]
out=HERE/('results_'+uuid4().hex)
sources=[Path(__file__),HERE/'analyze.py',LEDGER,REPORT]
sources.extend(Path(row['attempt_dir'])/'stdout.bin' for row in rows)
record=capture.capture('C003_B_CASE_MEDIAN_POSTPROCESSING',
    [sys.executable,'-B','-X','utf8',str(HERE/'analyze.py'),
     '--ledger',str(LEDGER),'--validator',str(REPORT),'--output',str(out)],
    cwd=CYCLE,timeout_seconds=120,source_paths=sources)
print(json.dumps(dict(output=str(out),capture=record)),flush=True)
sys.exit(0 if record['execution_status']=='success' else 1)
