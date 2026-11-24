"""Run against byte-verified actual stream modules, never vendored substitutes."""
import argparse
from hashlib import sha1, sha256
from pathlib import Path
import os
import sys
import unittest

CORE_HEAD = '539af04bb0b097de5704c28f2b82f23cea5ef783'
INTERFACE_HEAD = 'c6487af8f234cf183ed6febce1e1263de0a57e15'
PROOF_HEAD = 'db8fb33a5726c779e385544219e39db662a6cb5b'
CORE = dict(zip(('component_closure.py','core.py','evidence_store.py','schema.py','sparse_analysis.py',
                 'tests/test_evidence_store.py','tests/test_schema_closure.py','tests/test_sparse_analysis.py'),
                ('97844bc266556cc04cd54a75c0d57dc00d6709ea','997304c3adce9d3148d454b079639575f419ba0e',
                 '42e38c8ee590267b292ebc0d678e9d4f3a56849b','65a7522a8442a184c14f7a0fa74fc307ce60229f',
                 'f773cc1c6b1a852193ba2afb75aa2fce4941a5c2','56ffa92c8bb75606a0ffc70e20e57cda8f905bbe',
                 'ad959bcd10615d951f4207a7b0e0cf8098c753db','965abe7e10fecf35b441fefa844aebf75e549646')))
INTERFACE = {'adapter.py':'c38e441c7327a44adad8a0fe1125d45c93e8ef69',
             'strict_ledger.py':'a66975de137e3ec556b8c7aacd108cf975c46344'}
PROOF = {'independent_replay.py':'aa09243fa7ccc941c37609e959aefb419075df32',
         'production_replay.py':'f0bfa1785b49aab010f2af69e0e14c0af46d577c',
         'ledger_replay.py':'c2ae28e42a71aab91f329cf728ab7a95538cbf4e'}


def verify_files(root, entries):
    for name, expected in entries.items():
        content = (root/name).read_bytes()
        actual = sha1(b'blob '+str(len(content)).encode()+b'\0'+content).hexdigest()
        if actual != expected:
            raise SystemExit(f'blob mismatch: {root/name}: {actual} != {expected}')
        print(f'blob OK {name} {actual}',flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--interface-dir',required=True,type=Path)
    parser.add_argument('--proof-dir',required=True,type=Path)
    parser.add_argument('--artifact',required=True,type=Path)
    parser.add_argument('--full',action='store_true')
    args=parser.parse_args()
    module=Path(__file__).resolve().parents[1]
    interface=args.interface_dir.resolve(); proof=args.proof_dir.resolve()
    print('Pinned predecessors:', CORE_HEAD, INTERFACE_HEAD, PROOF_HEAD,flush=True)
    verify_files(module,CORE); verify_files(interface,INTERFACE); verify_files(proof,PROOF)
    sys.path[:0]=[str(module.parent),str(interface),str(proof)]
    os.environ['P2_ARTIFACT']=str(args.artifact.resolve())
    # Remove stale output so a failed run cannot be mistaken for a new artifact.
    args.artifact.unlink(missing_ok=True)
    loader=unittest.TestLoader(); suite=unittest.TestSuite()
    if args.full:
        suite.addTests(loader.discover(str(module/'tests')))
    suite.addTests(loader.loadTestsFromName('selector_v2.integration.test_roundtrip'))
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful() or not args.artifact.is_file():
        return 1
    b=args.artifact.read_bytes()
    print('artifact bytes',len(b),'sha256',sha256(b).hexdigest(),flush=True)
    return 0


if __name__=='__main__': raise SystemExit(main())
