"""All antichains on four atoms: test exactness of region pruning itself."""
import encoding as E
def main():
    q=4;subsets=list(range(1,1<<q));checked=0
    for pattern in range(1<<len(subsets)):
        edges=[s for j,s in enumerate(subsets) if pattern>>j&1]
        if any(x!=y and x&y==x for x in edges for y in edges):continue
        prepared=object.__new__(E.Prepared)
        prepared.groups=[[i] for i in range(q)];prepared.tick=lambda:None
        prepared.stats={'regions':0,'false_regions':0}
        prepared.atom_rejects=lambda mask,j:any(mask&e==e for e in edges)
        found=prepared.minimal_witnesses(0)
        assert set(found)==set(edges),(edges,found)
        checked+=1
    print({'antichains_checked':checked})
if __name__=='__main__':main()
