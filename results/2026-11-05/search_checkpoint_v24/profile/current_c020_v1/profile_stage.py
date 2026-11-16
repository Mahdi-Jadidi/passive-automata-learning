"""Bounded diagnostic profile; never an ordinary timing benchmark."""
import cProfile, hashlib, importlib.util, io, json, platform, pstats, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
BASE = ROOT / 'results/2026-11-05/search_checkpoint_v24/implementation/baseline_c020_v1/gate_v1.py'
spec = importlib.util.spec_from_file_location('baseline', BASE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
case = sys.argv[1]
if case == 'obstruction_m8':
    n = 'abcdefgh'
    source = HERE / 'obstruction_m8.json'
    source.write_text(json.dumps(dict(alphabet=list(n), positive=[n[:i]+n[i+1:] for i in range(8)], negative=[n])), encoding='utf-8')
    k = None
else:
    source = ROOT / f'results/2026-11-04/scaling_v20/audit/fixtures_v1/{case}/solver_input.json'
    k = 4
started = time.perf_counter()
raw = source.read_bytes()
data = json.loads(raw.decode('utf-8-sig'))
read_seconds = time.perf_counter() - started
prof = cProfile.Profile()
solve_start = time.perf_counter()
result = prof.runcall(gate.solve, data, known_k=k, deadline=solve_start+19)
solve_seconds = time.perf_counter()-solve_start
output_start = time.perf_counter()
out = json.dumps(result, ensure_ascii=False, sort_keys=True)
(HERE / f'{case}.stdout.json').write_text(out, encoding='utf-8')
output_seconds = time.perf_counter()-output_start
prof.dump_stats(str(HERE / f'{case}.prof'))
buf = io.StringIO()
pstats.Stats(prof, stream=buf).strip_dirs().sort_stats('cumulative').print_stats()
(HERE / f'{case}.pstats.txt').write_text(buf.getvalue(), encoding='utf-8')
meta = dict(case=case, known_k=k, command=f'py -3.14 {__file__} {case}', python=sys.version, executable=sys.executable,
            platform=platform.platform(), input_path=str(source), input_sha256=hashlib.sha256(raw).hexdigest(),
            gate_sha256=hashlib.sha256(BASE.read_bytes()).hexdigest(), read_json_seconds=read_seconds,
            profiled_solve_seconds=solve_seconds, serialize_write_seconds=output_seconds, output_bytes=len(out.encode()),
            status=result['status'], certificate=result.get('certificate'), metrics=result['metrics'], completed=result['status']!='unresolved')
(HERE / f'{case}.metadata.json').write_text(json.dumps(meta, indent=2), encoding='utf-8')
print(json.dumps(dict(case=case, status=result['status'], seconds=solve_seconds)))
