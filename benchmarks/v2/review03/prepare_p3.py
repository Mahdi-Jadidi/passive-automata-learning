"""Extract the seven original P3 fixtures, with references in a separate directory."""
import argparse, hashlib, json
from pathlib import Path
CASES={
 'tiny_choice':('planted','1c064aa4c7ce111ec8c403e8b6a05b64de5acdec2ef564861f06c2e2e2e42f23',0,2),
 'small_choice':('planted','10b0c3534ddf42369db003bca6b323c9fdaa33cd36aa15031360c3428949931b',0,4),
 'medium_choice':('planted','abdce6ec6d39f21d845dabe409e6978f38f4bcb4871854cf82e55507ccb9862f',1,300),
 'huge_choice_active':('planted','0be60da81326bcd8974da1df07e018e60dcd62714123b884c873ed3be782beba',1,9000),
 'hdfs_1024':('pinned','7d076991e9ba118b98226a64d9551cd5c6df5d0797183d2e8a95ed896b057075',0,2),
 'hdfs_holdout_1024_uncapped':('pinned','238d37c4588f1a8506275859ede5cf6a5225630bb3454c016568ff7e2ae5ff6c',0,2),
 'cover_path_8':('pinned','948f306e7509babd3d054a02e8df4b1232a30147305183edb8f7937e3ccc6fc7',0,4),
}
def sha(b): return hashlib.sha256(b).hexdigest()
def prepare(root,out):
    staged=[]
    for name,(origin,digest,floor,cost) in CASES.items():
        b=(root/(origin+'-inputs')/(name+'.json')).read_bytes(); d=json.loads(b)
        if sha(b)!=digest or set(d)!={'alphabet','positive','negative'}: raise ValueError('input mismatch: '+name)
        r=(root/(origin+'-refs')/(name+'.json')).read_bytes(); ref=json.loads(r)
        observed=len(d['alphabet'])-(len(ref['blocks']) if origin=='planted' else ref['result']['max_devices'])
        if observed!=cost: raise ValueError('reference mismatch: '+name)
        m=dict(case=name,provenance=origin,input_sha256=digest,alphabet=len(d['alphabet']),positives=len(d['positive']),negatives=len(d['negative']),occurrences=sum(map(len,d['positive']+d['negative'])),max_word_length=max(map(len,d['positive']+d['negative']),default=0))
        evaluation=dict(case=name,reference_sha256=sha(r),archived_reference_cost=cost,review02_verified_p1_floor=floor,review02_verified_p1_optimum=None,operational_status='INCOMPLETE')
        staged.append((name,b,r,m,evaluation))
    out.mkdir(parents=True,exist_ok=False); (out/'inputs').mkdir(); (out/'evaluation').mkdir()
    for name,b,r,m,e in staged:
        (out/'inputs'/(name+'.json')).write_bytes(b);(out/'evaluation'/(name+'.json')).write_bytes(r)
    (out/'input-manifest.json').write_text(json.dumps([x[3] for x in staged],indent=2)+'\n')
    (out/'evaluation'/'index.json').write_text(json.dumps([x[4] for x in staged],indent=2)+'\n')
    print('prepared',len(staged),'original inputs; input manifest sha256',sha((out/'input-manifest.json').read_bytes()))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('recovery_root',type=Path);p.add_argument('output',type=Path);a=p.parse_args();prepare(a.recovery_root,a.output)
