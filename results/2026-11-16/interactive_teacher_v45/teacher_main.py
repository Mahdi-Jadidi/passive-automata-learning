"""Literal implementation of the fixed-partition procedure in main.pdf §5."""
from itertools import product


class MainTeacher:
    def __init__(self, tick):
        self.tick = tick
        self.cache = {}
        self.stats = None
        self.completed_checks = 0

    def _local(self, block, pos, neg, bound, metrics):
        key = (block, pos, neg, bound)
        self.tick()
        if key in self.cache:
            metrics['cache_hits'] += 1
            return self.cache[key]
        rows = {}
        index = {a: i for i, a in enumerate(block)}
        for q in range(1, bound + 1):
            self.tick()
            for transitions in product(range(q), repeat=q * len(block)):
                self.tick()
                for accepting in product((0, 1), repeat=q):
                    self.tick()
                    metrics['dfa_representations'] += 1
                    def accepts(word):
                        state = 0
                        for symbol in word:
                            self.tick()
                            state = transitions[state * len(block) + index[symbol]]
                        self.tick()
                        return accepting[state]
                    if not all(accepts(w) for w in pos):
                        continue
                    bits = tuple(1 - accepts(w) for w in neg)
                    if bits not in rows:
                        rows[bits] = {'states': q, 'initial': 0,
                                      'alphabet': block, 'transitions': transitions,
                                      'accepting': tuple(i for i, x in enumerate(accepting) if x)}
        # Publish only a fully enumerated table: interrupted builds cannot poison cache.
        self.cache[key] = rows
        return rows

    def check(self, blocks, images):
        tick = self.tick
        blocks = tuple(tuple(b) for b in blocks)
        metrics = {'dfa_representations': 0, 'cache_hits': 0, 'branches': 0,
                   'semijoin_checks': 0, 'local_rows': [], 'q_rows': [],
                   'vertices': 0, 'edges': 0, 'cycle_bits': 0, 'bounds': [],
                   'completed_checks': self.completed_checks}
        self.stats = metrics
        local = []
        all_pos, all_neg = [], []
        for block in blocks:
            tick()
            pos = tuple(tuple(w) for w in images[block]['positive'])
            neg = tuple(tuple(w) for w in images[block]['negative'])
            if all_neg and len(neg) != len(all_neg[0]):
                raise ValueError('negative projection lists must have equal length')
            prefixes = {()}
            for word in pos:
                for j in range(len(word) + 1):
                    tick()
                    prefixes.add(word[:j])
            bound = len(prefixes) + 1 if pos else 1
            metrics['bounds'].append(bound)
            local.append(self._local(block, pos, neg, bound, metrics))
            metrics['local_rows'].append(len(local[-1]))
            all_pos.append(pos)
            all_neg.append(neg)
        n = len(all_neg[0]) if blocks else 0
        k = len(blocks)
        # Columns are (component index, negative index), with distinct names
        # even when two negative projections coincide.
        forced = set()
        for b in range(k):
            for i in range(n):
                tick()
                if all_neg[b][i] in all_pos[b]:
                    forced.add((b, i))
        schemas, tables = [], []
        for b in range(k):
            schema = tuple((b, i) for i in range(n) if (b, i) not in forced)
            schemas.append(schema)
            # Each entry retains its original full row for witness recovery.
            table = []
            for bits in local[b]:
                tick()
                if all(bits[i] == 0 for bb, i in forced if bb == b):
                    table.append((tuple(bits[i] for _, i in schema), bits))
            tables.append(table)
        for i in range(n):
            schema = tuple((b, i) for b in range(k) if (b, i) not in forced)
            schemas.append(schema)
            table = []
            for bits in product((0, 1), repeat=len(schema)):
                tick()
                if any(bits):
                    table.append((bits, None))
            tables.append(table)
            metrics['q_rows'].append(len(table))
        vcount = len(tables)
        edges = [(b, k + i, (b, i)) for b in range(k) for i in range(n)
                 if (b, i) not in forced]
        metrics['vertices'], metrics['edges'] = vcount, len(edges)
        parent = list(range(vcount))
        def root(v):
            while parent[v] != v:
                tick()
                v = parent[v]
            return v
        forest, feedback = [], []
        for a, b, col in edges:
            tick()
            ra, rb = root(a), root(b)
            if ra == rb:
                feedback.append(col)
            else:
                parent[ra] = rb
                forest.append((a, b, col))
        metrics['cycle_bits'] = len(feedback)
        adjacency = [[] for _ in tables]
        for a, b, col in forest:
            adjacency[a].append((b, col))
            adjacency[b].append((a, col))
        for assignment in product((0, 1), repeat=len(feedback)):
            tick()
            metrics['branches'] += 1
            fixed = dict(zip(feedback, assignment))
            reduced, reduced_schemas = [], []
            for schema, table in zip(schemas, tables):
                tick()
                keep = [j for j, c in enumerate(schema) if c not in fixed]
                conditioned = []
                seen = set()
                for values, original in table:
                    tick()
                    if any(values[j] != fixed[c] for j, c in enumerate(schema) if c in fixed):
                        continue
                    row = tuple(values[j] for j in keep)
                    if row not in seen:
                        conditioned.append((row, original))
                        seen.add(row)
                reduced.append(conditioned)
                reduced_schemas.append(tuple(schema[j] for j in keep))
            if any(not t for t in reduced):
                continue
            # Root every connected component, retaining isolated vertices.
            parents, order, roots = {}, [], []
            for start in range(vcount):
                tick()
                if start in parents:
                    continue
                roots.append(start)
                parents[start] = None
                stack = [start]
                while stack:
                    tick()
                    v = stack.pop()
                    order.append(v)
                    for w, col in adjacency[v]:
                        tick()
                        if w not in parents:
                            parents[w] = (v, col)
                            stack.append(w)
            def semijoin(a, b, col):
                ia, ib = reduced_schemas[a].index(col), reduced_schemas[b].index(col)
                retained = []
                for row in reduced[a]:
                    supported = False
                    for other in reduced[b]:
                        tick()
                        metrics['semijoin_checks'] += 1
                        if row[0][ia] == other[0][ib]:
                            supported = True
                            break
                    if supported:
                        retained.append(row)
                reduced[a] = retained
            for v in reversed(order):
                tick()
                if parents[v] is not None:
                    p, col = parents[v]
                    semijoin(p, v, col)
            if any(not reduced[r] for r in roots):
                continue
            for v in order:
                tick()
                if parents[v] is not None:
                    p, col = parents[v]
                    semijoin(v, p, col)
            chosen = {}
            for v in order:
                tick()
                if parents[v] is None:
                    chosen[v] = reduced[v][0]
                else:
                    p, col = parents[v]
                    pv = chosen[p][0][reduced_schemas[p].index(col)]
                    for row in reduced[v]:
                        tick()
                        if row[0][reduced_schemas[v].index(col)] == pv:
                            chosen[v] = row
                            break
            rows = {blocks[b]: chosen[b][1] for b in range(k)}
            witnesses = {blocks[b]: local[b][rows[blocks[b]]] for b in range(k)}
            self.completed_checks += 1
            metrics['completed_checks'] = self.completed_checks
            return {'status': 'ACCEPT', 'metrics': metrics, 'rows': rows, 'witness': witnesses}
        self.completed_checks += 1
        metrics['completed_checks'] = self.completed_checks
        return {'status': 'REJECT', 'metrics': metrics}
