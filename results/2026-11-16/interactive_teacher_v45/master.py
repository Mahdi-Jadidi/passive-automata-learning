"""Exact partition master: pair equivalence, class count, and lazy cover cuts."""


class Master:
    def __init__(self, q, tick=None):
        if type(q) is not int or q < 0:
            raise ValueError("q must be a nonnegative integer")
        self.q, self.tick = q, tick
        self.clauses = []
        self.variables = 0
        self.pairs = {(i, j): self._var() for i in range(q) for j in range(i + 1, q)}
        # The three implications per triple make the symmetric pair relation transitive.
        for i in range(q):
            for j in range(i + 1, q):
                for k in range(j + 1, q):
                    a, b, c = self.pairs[i, j], self.pairs[i, k], self.pairs[j, k]
                    self.clauses.extend([[-a, -b, c], [-a, -c, b], [-b, -c, a]])
                    self._tick()
        # Exactly one representative (the least index) exists in each class.
        reps = [self._and([-self.pairs[j, i] for j in range(i)]) for i in range(q)]
        # Dynamic programming: dp[t] iff at least t representatives have appeared.
        dp = [True] + [False] * q
        for rep in reps:
            dp = [True] + [self._or([dp[t], self._and([dp[t - 1], rep])])
                           for t in range(1, q + 1)]
        self.thresholds = dp

    def _tick(self):
        if self.tick is not None:
            self.tick()

    def _var(self):
        self.variables += 1
        return self.variables

    def _and(self, terms):
        terms = list(terms)
        if any(x is False for x in terms):
            return False
        terms = [x for x in terms if x is not True]
        if not terms:
            return True
        if len(terms) == 1:
            return terms[0]
        v = self._var()
        self.clauses.extend([[-v, x] for x in terms])
        self.clauses.append([v] + [-x for x in terms])
        return v

    def _or(self, terms):
        terms = list(terms)
        if any(x is True for x in terms):
            return True
        terms = [x for x in terms if x is not False]
        if not terms:
            return False
        if len(terms) == 1:
            return terms[0]
        v = self._var()
        self.clauses.extend([[v, -x] for x in terms])
        self.clauses.append([-v] + terms)
        return v

    def add_cover(self, cover):
        full = (1 << self.q) - 1
        cover = list(cover)
        if any(type(u) is not int or u <= 0 or u >= full for u in cover):
            raise ValueError("cover masks must be nonempty proper subsets of the atoms")
        cover = sorted(set(cover))
        start = len(self.clauses)
        anchors = []
        # An anchor witnesses its entire equivalence class. For each U, its
        # class escapes U iff anchor is outside U or is equivalent to someone
        # outside U. Thus the disjunction is exactly the requested class cut.
        for a in range(self.q):
            escapes = []
            for u in cover:
                if not (u & (1 << a)):
                    escapes.append(True)
                else:
                    escapes.append(self._or([self.pairs[min(a, b), max(a, b)]
                                             for b in range(self.q) if not (u & (1 << b))]))
            anchors.append(self._and(escapes))
            self._tick()
        cut = self._or(anchors)
        if cut is False:
            self.clauses.append([])
        elif cut is not True:
            self.clauses.append([cut])
        return self.clauses[start:]

    def threshold(self, t):
        if type(t) is not int or t < 0:
            raise ValueError("threshold must be a nonnegative integer")
        if t > self.q:
            return self.clauses + [[]]
        lit = self.thresholds[t]
        if lit is True:
            return self.clauses[:]
        if lit is False:
            return self.clauses + [[]]
        return self.clauses + [[lit]]

    def decode(self, model):
        positive = {x for x in model if x > 0}
        blocks = []
        for i in range(self.q):
            for block in blocks:
                if self.pairs[block[0], i] in positive:
                    block.append(i)
                    break
            else:
                blocks.append([i])
        return blocks
