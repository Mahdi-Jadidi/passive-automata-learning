"""Create or check hashes of the V46 source, evidence, page renders and PDF."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PDF = ROOT/'output/pdf/Certified_Maximum_Alphabet_Partitioning_Interactive_Teacher_V46_EN.pdf'
MANIFEST = HERE/'manifest.json'


def collect():
    paths = [p for p in HERE.rglob('*') if p.is_file() and p != MANIFEST
             and '__pycache__' not in p.parts]
    paths.extend((PDF,ROOT/'README.md',ROOT/'START_HERE_FA.md'))
    return {
        p.relative_to(ROOT).as_posix(): {'bytes':p.stat().st_size,
                                       'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
        for p in sorted(paths)
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write',action='store_true')
    args = ap.parse_args()
    actual = collect()
    if args.write:
        with MANIFEST.open('x',encoding='utf-8') as stream:
            json.dump(actual,stream,indent=2)
            stream.write('\n')
    else:
        saved = json.loads(MANIFEST.read_text(encoding='utf-8'))
        differences = [p for p in sorted(set(saved)|set(actual)) if saved.get(p)!=actual.get(p)]
        if differences:
            raise SystemExit('\n'.join(differences))
    print(f'{len(actual)} files verified')


if __name__ == '__main__':
    main()
