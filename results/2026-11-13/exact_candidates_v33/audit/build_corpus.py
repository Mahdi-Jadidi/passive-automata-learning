"""Deterministically generate frozen synthetic correctness and timing cases."""
import json
import random
from pathlib import Path
import insertion_oracle as oracle

HERE = Path(__file__).resolve().parent
def record(a, p, n):
    return {'alphabet': a, 'positive': p, 'negative': n}

def main():
    prior = [json.loads(x) for x in (HERE / 'prior_fixed_cases.jsonl').read_text(encoding='utf-8-sig').splitlines() if x]
    cases = [{'case': 'exhaustive_%04d' % i, 'input': x} for i, x in enumerate(oracle.exhaustive_binary_cases())]
    cases += [{'case': 'seeded_%02d' % i, 'input': x} for i, x in enumerate(oracle.seeded_cases())]
    cases += [{'case': 'prior_' + x['case'], 'input': x['input']} for x in prior]
    # Both originals and transformations are fixed and named for explicit metamorphic comparisons.
    a = ['a', 'bc', 'ab', 'c']
    base = record(a, [[], ['a','bc'], ['ab','c']], [['a'], ['c','a']])
    renamed = {'a':'α','bc':'x y','ab':'☃','c':'x|y'}
    ren = lambda words: [[renamed[x] for x in w] for w in words]
    cases += [
        {'case':'meta_original','input':base},
        {'case':'meta_duplicate','input':record(a, base['positive'] + [base['positive'][1]], base['negative'] + [base['negative'][0]])},
        {'case':'meta_renamed','input':record([renamed[x] for x in a], ren(base['positive']), ren(base['negative']))},
        {'case':'meta_unused','input':record(a + ['unused|⊥'], base['positive'], base['negative'])},
    ]
    (HERE / 'correctness_cases.jsonl').write_text(''.join(json.dumps(x, ensure_ascii=False, separators=(',',':'))+'\n' for x in cases), encoding='utf-8', newline='\n')
    s = lambda m: [f's{i}' for i in range(m)]
    def rev_pair(m):
        a=s(m); return record(a,[a],[list(reversed(a))])
    a=s(8); b=s(9); c=s(10)
    rng=random.Random(331337)
    long_a=s(4)
    long_words=[[rng.choice(long_a) for _ in range(180)] for _ in range(8)]
    many_a=s(3)
    many_words=[]
    for _ in range(120):
        w=[rng.choice(many_a) for _ in range(rng.randrange(2,15))]
        if w not in many_words: many_words.append(w)
    timing=[
        ('empty_all_8','singleton/all-compatible, no observations',record(a,[],[])),
        ('all_compatible_10','Bell-heavy and unused IDs',record(c,[],[])),
        ('oneblock_8','only whole block rejects each adjacent swap',record(a,[a],[a[:i]+[a[i+1],a[i]]+a[i+2:] for i in range(7)])),
        ('ties_8','alternative rejecting blocks, unused IDs',record(a,[[],a],[['s0']])),
        ('reverse_9','many order constraints, nontrivial coverage',rev_pair(9)),
        ('reverse_10','Bell-heavy order constraint',rev_pair(10)),
        ('overlap_8','multiple negative coverage alternatives',record(a,[[],a],[['s0'],['s1'],['s2'],['s3']])),
        ('repeated_projections_9','shared masks and projections',record(b,[b, list(reversed(b))],[[b[0],b[2]],[b[1],b[3]],[b[0],b[4]], [b[2],b[5]]])),
        ('long_words_4','long words, small alphabet',record(long_a,long_words[:4],long_words[4:])),
        ('many_words_3','many traces, small alphabet',record(many_a,many_words[:len(many_words)//2],many_words[len(many_words)//2:])),
    ]
    (HERE / 'timing_cases.jsonl').write_text(''.join(json.dumps({'case':name,'purpose':why,'input':data},ensure_ascii=False,separators=(',',':'))+'\n' for name,why,data in timing),encoding='utf-8',newline='\n')
    print(json.dumps({'correctness':len(cases),'prior':len(prior),'timing':len(timing)},sort_keys=True))

if __name__ == '__main__': main()
