"""Collect final checkpoint provenance without executing experiments."""
import hashlib
import json
from pathlib import Path

here = Path(__file__).resolve().parent
root = here.parents[2]
audit = json.loads((here / 'audit/FINAL_SUMMARY_V2.json').read_text(encoding='utf-8'))
coordination = json.loads((here / 'COORDINATION_FINAL_V1.json').read_text(encoding='utf-8-sig'))
evidence = ['PLAN_FA_V1.md', 'COORDINATION_FINAL_V1.json', 'MASTER_DECISION_FA.md',
            'MANAGER_REVIEW_A_V1.md', 'MANAGER_REVIEW_B_V1.md', 'RESEARCH_REPORT_FA.md',
            'theory/PAPER_CHECKPOINT_EN_V1.md', 'audit/FINAL_SUMMARY_V2.json',
            'PUBLIC_VERIFICATION_V1.json']
ledger = {
    'id': 'C024-checkpoint-final-v1', 'date': '2026-11-05', 'timezone': 'Asia/Tehran',
    'execution_status': 'successful_checkpoint_complete',
    'public_status': 'promoted_integrated_C024',
    'public_entry_sha256': hashlib.sha256((root / 'partition.py').read_bytes()).hexdigest(),
    'integrated_solver_sha256': '0aded302c5f9b0a364e3428a8319eab15b1d96be67fd98a64d117faa1b3a1d61',
    'coordination': coordination,
    'ideas': [
        {'id': 'C024-A', 'basis': 'C006-T3', 'status': 'exact; target benefit with retained regressions',
         'source_sha256': '9725a263266f4e131019936e771b5df1cb100cd5715ec85c7dae90040f7e33f4',
         'decision': 'promote unknown-K route'},
        {'id': 'C024-B', 'basis': 'C020-envelope-proposal', 'status': 'exact; target benefit on frozen suite',
         'source_sha256': '4e5a8e39528efadf3d2eeaab2dfa02a0d77711d7028005737fe78a42b38cb9a3',
         'decision': 'promote known-K route'}],
    'official_timing_attempts': audit['official_attempts'],
    'correctness': audit['correctness'], 'integrated': audit['integrated'],
    'disclosures': audit['disclosures'] + ['Manager final-ledger shell parse failure preserved separately; no command executed'],
    'measurement_limits': ['Integrated official timing unmeasured', 'Memory unmeasured',
                           'RPNI benefit unmeasured', 'Natural-log recovery accuracy unmeasured',
                           'External novelty review pending'],
    'evidence': [{'path': path, 'sha256': hashlib.sha256((here / path).read_bytes()).hexdigest()}
                 for path in evidence],
    'traceability': 'Full commands, environment, source/input hashes, stdout/stderr and errors in audit captures and profile metadata',
}
(here / 'RESEARCH_LEDGER_V1.json').write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'checkpoint_complete': True, 'evidence_files': len(evidence), 'public_status': ledger['public_status']}))
