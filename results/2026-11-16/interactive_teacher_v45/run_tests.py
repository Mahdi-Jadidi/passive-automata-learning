"""Save auditable subprocess test reports without overwriting previous evidence."""
import json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
def main():
    with (HERE/'test_runs.jsonl').open('x',encoding='utf-8') as out:
        for filename in ['projection_tests.py','teacher_tests.py','master_tests.py','cut_certificate_tests.py']:
            run=subprocess.run([sys.executable,str(HERE/filename)],capture_output=True,text=True,timeout=180)
            row={'test':filename,'exit_code':run.returncode,'stdout':run.stdout,'stderr':run.stderr}
            out.write(json.dumps(row)+'\n');out.flush()
            print(json.dumps(row),flush=True)
            assert run.returncode==0
if __name__=='__main__':main()
