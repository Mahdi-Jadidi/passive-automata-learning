"""Independent O(T) block-routing per witness and DFA-world replay, no gate imports."""
import hashlib,json
from pathlib import Path
from certificate_replay_c015_v1 import canonical
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
class Replay:
    def __init__(self):self.data={};self.partitions={};self.worlds={}
    def input(self,cell):
        p=cell['input']
        if p not in self.data:
            assert sha(p)==cell['input_sha256'];self.data[p]=json.loads(Path(p).read_text(encoding='utf8'))
        return self.data[p]
    def witness(self,cell,w):
        d=self.input(cell);key=canonical(w['blocks'],sorted(d['alphabet']));ck=(cell['input_sha256'],key)
        if ck not in self.partitions:
            owner={a:i for i,g in enumerate(w['blocks']) for a in g};size=len(w['blocks'])
            def project(word):
                out=[[] for _ in range(size)]
                for ch in word:out[owner[ch]].append(ch)
                return [''.join(v) for v in out]
            languages=[set() for _ in range(size)]
            for p in d['positive']:
                for i,value in enumerate(project(p)):languages[i].add(value)
            rejected=[]
            for n in d['negative']:rejected.append(frozenset(i for i,value in enumerate(project(n)) if value not in languages[i]))
            assert all(rejected);self.partitions[ck]=rejected
        assert w['local_language_rule']=='positive_projections_from_input';refs=w['negative_rejections'];assert len(refs)==len(d['negative']) and {r['negative_index'] for r in refs}==set(range(len(d['negative'])))
        for r in refs:
            ni,bi=r['negative_index'],r['rejected_by_block'];assert type(ni)is int and type(bi)is int and 0<=ni<len(d['negative']) and bi in self.partitions[ck][ni]
        return key
    def graph(self,d,certificate):
        parent={a:a for a in d['alphabet']}
        def root(a):
            while parent[a]!=a:a=parent[a]
            return a
        for e in certificate.get('swap_forest',[]):
            pi,ni=e['positive_index'],e['negative_index'];assert type(pi)is int and type(ni)is int and 0<=pi<len(d['positive']) and 0<=ni<len(d['negative'])
            p,n=d['positive'][pi],d['negative'][ni];i,j=e['positions'];assert type(i)is int and type(j)is int and j==i+1 and 0<=i<j<len(p) and len(p)==len(n)
            chars=list(p);chars[i],chars[j]=chars[j],chars[i];assert p[i]!=p[j] and ''.join(chars)==n and e['symbols']==[p[i],p[j]]
            a,b=root(p[i]),root(p[j]);assert a!=b;parent[b]=a
        groups={}
        for a in sorted(parent):groups.setdefault(root(a),[]).append(a)
        atoms=sorted(groups.values())
        if 'forced_atoms' in certificate:assert certificate['forced_atoms']==atoms
        return atoms
    def result(self,cell,result):
        d=self.input(cell);status=result['status'];assert result['known_k'] is None and result['physical_truth_read'] is False
        assert ('partition' in result)==(status=='certified_unique')
        if status=='unresolved':
            assert result['findings']==dict(data_insufficient=None,computation_incomplete=True) and 'alternatives' not in result;return status
        assert status in ['ambiguous','certified_unique'] and result['findings']==dict(data_insufficient=status=='ambiguous',computation_incomplete=False)
        cert=result['certificate'];route=cert['route']
        if status=='ambiguous':assert len(result['alternatives'])==2 and len({self.witness(cell,w) for w in result['alternatives']})==2
        else:
            key=self.witness(cell,cert['witness']);assert result['partition']==cert['witness']['blocks'] and max(key)==0
        if route=='unary_all_partitions':
            assert status=='ambiguous' and cert['family']=='all_set_partitions';refs=cert['negative_count_certificates'];assert len(refs)==len(d['negative']) and {r['negative_index'] for r in refs}==set(range(len(d['negative'])))
            for r in refs:
                a=r['symbol'];ni=r['negative_index'];assert a in d['alphabet'] and d['negative'][ni].count(a)==r['negative_count'] and r['negative_count'] not in {p.count(a) for p in d['positive']}
        else:
            atoms=self.graph(d,cert)
            if status=='certified_unique':assert len(atoms)==1,'unsupported large unique proof'
            else:assert route in ['compatible_forced_atoms','two_exact_search_witnesses']
        return status
    def world(self,cell):
        ck=(cell['input_sha256'],cell['world_sha256'])
        if ck in self.worlds:return self.worlds[ck]
        d=self.input(cell);assert sha(cell['world'])==cell['world_sha256'];world=json.loads(Path(cell['world']).read_text(encoding='utf8'));devices=world['devices'];owner=world['ownership'];assert set(owner)==set(d['alphabet']) and len(d['alphabet'])==40
        seen=set();tables=[];starts=[];accepts=[]
        for i,dev in enumerate(devices):
            assert dev['id']==i and dev['states']==list(range(len(dev['states']))) and dev['start'] in dev['states'];starts.append(dev['start']);accepts.append(set(dev['accepting']));assert accepts[-1]<=set(dev['states'])
            assert dev['alphabet'] and not seen.intersection(dev['alphabet']);seen.update(dev['alphabet'])
            assert all(owner[a]==i for a in dev['alphabet']);assert len(dev['transitions'])==len(dev['states'])
            for row in dev['transitions']:assert set(row)==set(dev['alphabet']) and all(type(q)is int and q in dev['states'] for q in row.values())
            tables.append(dev['transitions'])
        assert seen==set(d['alphabet']);assert len(d['positive'])==len(d['negative'])==cell['samples_per_label']
        refs=[]
        for label,name in [(True,'positive'),(False,'negative')]:
            for wi,word in enumerate(d[name]):
                assert len(word)<=cell['max_length'];states=starts.copy()
                for ch in word:
                    i=owner[ch];states[i]=tables[i][states[i]][ch]
                rejecting=[i for i,q in enumerate(states) if q not in accepts[i]];assert (not rejecting)==label
                if not label:refs.append(dict(negative_index=wi,rejected_by_device=rejecting[0]))
        # Each positive projection reaches an accepting state in every local
        # DFA; the recorded negative projection reaches a rejecting state.
        # Determinism proves it differs from every positive projection. Thus
        # saved-world truth compatibility follows without a second O(K*T) scan.
        report=dict(case_id=cell['case_id'],status='independent_DFA_labels_and_truth_compatibility_proved',negative_device_rejections=refs,T=sum(map(len,d['positive']+d['negative'])),actual_lengths=list(map(len,d['positive']+d['negative'])),world_sha256=cell['world_sha256'])
        self.worlds[ck]=report;return report
