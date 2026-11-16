"""Explain work units; not a substitute for end-to-end timing."""
import importlib.util,json,time
from pathlib import Path
import encoding as E
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def main():
    path=ROOT/'results/2026-11-15/exact_optimizer_v42/encoding.py'
    spec=importlib.util.spec_from_file_location('v42_encoding',path);old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    original=old.reject;calls=[]
    def counted(Sigma,S_plus,S_minus,indices):
        calls.append(sum(1<<i for i in indices));return original(Sigma,S_plus,S_minus,indices)
    old.reject=counted
    corpus=ROOT/'results/2026-11-13/exact_candidates_v33/audit/timing_cases.jsonl'
    with (HERE/'extraction_diagnostics.jsonl').open('x',encoding='utf8') as stream:
        for row in map(json.loads,corpus.read_text().splitlines()):
            Sigma,S_plus,S_minus=E.normalize(row['input']);calls.clear()
            prior=old.build(Sigma,S_plus,S_minus,old.budget(None))
            prepared=E.Prepared(Sigma,S_plus,S_minus,E.budget(None))
            revised=E.build(Sigma,S_plus,S_minus,prepared.tick,prepared)
            assert all(set(x)==set(y) for x,y in zip(prior['edges'],revised['edges']))
            rec={'case':row['case'],'context':'full extraction only, not early optimizer routes','v42_projection_calls':len(calls),'v42_distinct_masks':len(set(calls)),'v42_subset_loop_candidates':2**prior['q']-1,'v43':prepared.stats,'minimal_sets':sum(map(len,revised['edges']))}
            stream.write(json.dumps(rec)+'\n');stream.flush();print(rec)
if __name__=='__main__':main()
