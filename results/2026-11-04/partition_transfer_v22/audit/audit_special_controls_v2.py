"""Check named C020 controls and C022 proof counterexamples independently."""
import json,sys
from pathlib import Path
from oracle_data_v1 import feasible,blocks
A=Path(__file__).resolve().parent

def main():
    run=A/'small_runs/C022-IND-20261104-01';ledger=list(map(json.loads,(run/'ledger.jsonl').read_text().splitlines()));required={
      'c020_duplicate_edge_unknown':('certified_unique',False),
      'c018_graph_empty_unique_noK':('certified_unique',True),
      'graph_failure_unique_K4':('incompatible',True),
      'empty_P_noK':('ambiguous',None),
      'empty_N_noK':('ambiguous',None),
      'empty_both_noK':('ambiguous',None),
      'c020_unicode_exact_unknown':('ambiguous',None),
    };rows=[]
    for entry in ledger:
      records={r['job_id']:r['result'] for r in map(json.loads,(A/'attempts'/entry['attempt_id']/'stdout.bin').read_bytes().splitlines())}
      for jid,(want,empty_graph) in required.items():
        r=records[jid];c=r.get('certificate',{});got=(r['status'],len(c.get('swap_forest',[])))
        assert got[0]==want,(entry['provider'],jid,got,want)
        if empty_graph is True:assert got[1]==0,(entry['provider'],jid,got)
        rows.append({'provider':entry['provider'],'job_id':jid,'status':r['status'],'route':c.get('route'),'swap_edges':got[1]})
    data={'alphabet':list('abcd'),'positive':['abcd'],'negative':['bacd','abdc']}; atoms=[['a','b'],['c','d']]; split=[['a'],['b'],['c'],['d']]
    assert feasible(data,(0,0,1,1));assert not feasible(data,(0,1,2,3))
    invalid_transfer=[]
    owner={ch:i for i,g in enumerate(split) for ch in g}; langs=[set() for _ in split]
    for p in data['positive']:
      out=['' for _ in split]
      for ch in p:out[owner[ch]]+=ch
      for i,v in enumerate(out):langs[i].add(v)
    for ni,n in enumerate(data['negative']):
      out=['' for _ in split]
      for ch in n:out[owner[ch]]+=ch
      reject=[i for i,v in enumerate(out) if v not in langs[i]]
      assert not reject
      invalid_transfer.append({'negative_index':ni,'split_partition_rejecting_blocks':reject,'reason':'candidate transfer is invalid if it splits the source rejecting atom'})
    incompatible_atoms={'alphabet':list('abcd'),'positive':['bacd','abdc'],'negative':['abcd']};forced=[['a','b'],['c','d']];whole=[list('abcd')]
    assert not feasible(incompatible_atoms,(0,0,1,1));assert feasible(incompatible_atoms,(0,0,0,0))
    report={'status':'accepted','small_gate_special_controls':rows,'split_atom_counterexample':{'compatible_forced_atoms':atoms,'atom_partition_compatible':True,'split_partition':split,'split_partition_compatible':False,'invalid_transfer_attempts':invalid_transfer},'no_compatible_atom_witness_counterexample':{'forced_atoms':forced,'forced_atom_partition_compatible':False,'coarsening':whole,'coarsening_compatible':True,'conclusion':'transfer must remain gated on the successfully validated atom_witness; the exact search fallback remains necessary'}}
    out=A/'SPECIAL_CONTROLS_AND_COUNTEREXAMPLES_V1.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':report['status'],'special_rows':len(rows),'split_rejecting_blocks':[x['split_partition_rejecting_blocks'] for x in invalid_transfer],'unvalidated_atoms_partition_compatible':False,'merged_partition_compatible':True},ensure_ascii=False))
if __name__=='__main__':main()

