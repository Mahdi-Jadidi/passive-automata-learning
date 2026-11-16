"""Check source integrity, record a regression, and hash the delivery artifacts."""
from pathlib import Path
import hashlib,json
from spec import budget
from verify import check_drup
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    frozen=HERE.parent/'exact_optimizer_v43'
    expected={'encoding.py':'38da943c28419cb02c7b2aecff56c9ce189ed57ec51e39d2e19b74afab50727e',
              'optimizer.py':'a4dcb3f1dfa6a84d5743276a9d8d584ab6e17d79fda1da95d3aa0ba976d8da63',
              'verify.py':'e42c85a2cddb61797856114292f3577a2356c6bebcdf6bb7933ba6ca71af0dad'}
    for name,value in expected.items():assert digest(frozen/name)==value
    assert digest(HERE/'sources/main.pdf')==digest(Path('C:/Users/Mahdi/Downloads/main.pdf'))
    class DuplicateFixture:
        variables=1
        def threshold(self,t):return [[1,1],[-1]]
    assert check_drup(DuplicateFixture(),1,[],budget(None))
    checks={'frozen_v43_sources':'UNCHANGED','user_main_pdf':'UNCHANGED',
            'duplicate_literal_regression':'PASS','teacher_fast_substitute':'NOT_IMPLEMENTED',
            'pdf_pages_visually_inspected':6,'and_model_field_trials':0}
    (HERE/'release_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    output=ROOT/'output/pdf/Interactive_Partition_Learning_Unchanged_Teacher_V45_EN.pdf'
    paths=[p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and 'rendered' not in p.parts and p.name!='manifest.json']+[output]
    manifest={p.relative_to(ROOT).as_posix():{'sha256':digest(p),'bytes':p.stat().st_size} for p in sorted(paths)}
    (HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'files':len(manifest),'checks':checks}))
if __name__=='__main__':main()
