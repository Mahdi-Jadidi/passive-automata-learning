"""Compare indexed RUP with prior scanning RUP on seeded arbitrary CNFs."""
import random
from verify import RupDatabase,rup
def main():
    rng=random.Random(20261116);checks=0
    for _ in range(1000):
        clauses=[[rng.choice([-1,1])*rng.randrange(1,6) for _ in range(rng.randrange(5))] for _ in range(rng.randrange(12))]
        database=RupDatabase(clauses,lambda:None)
        for __ in range(4):
            trial=list(set(rng.choice([-1,1])*rng.randrange(1,6) for ___ in range(rng.randrange(5))))
            # Scanning comparator uses deduplicated clauses as the original
            # scan algorithm assumes clauses do not contain duplicate literals.
            canonical=[list(set(c)) for c in clauses]
            assert database.check(trial)==rup(canonical,trial,lambda:None),(clauses,trial)
            checks+=1
    print({'indexed_rup_comparisons':checks})
if __name__=='__main__':main()
