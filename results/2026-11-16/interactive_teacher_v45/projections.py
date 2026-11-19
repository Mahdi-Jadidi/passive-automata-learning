"""Exact, reusable projections of a fixed labelled sample."""


class ProjectionStore:
    """Cache projections using a hash-consed prefix DAG.

    Masks index the supplied alphabet. A cache miss is derived from the cached
    superset with the fewest symbols, breaking ties by numeric mask.
    """

    def __init__(self, Sigma, positive, negative, tick):
        self.Sigma = tuple(Sigma)
        self.positive = tuple(tuple(w) for w in positive)
        self.negative = tuple(tuple(w) for w in negative)
        self.tick = tick
        self._bits = {symbol: 1 << i for i, symbol in enumerate(self.Sigma)}
        self._parents = [-1]
        self._symbols = [None]
        self._intern = {}
        self._cache = {}
        self.stats = {"dag_nodes": 0, "cache_hits": 0, "cache_misses": 0,
                      "transformed_nodes": 0, "materialized_words": 0}
        self._full_mask = (1 << len(self.Sigma)) - 1
        terminals = []
        for word in self.positive + self.negative:
            node = 0
            for symbol in word:
                self.tick()
                # Validate the declared alphabet even if the word is never queried.
                self._bits[symbol]
                node = self._node(node, symbol)
            terminals.append(node)
        self._initial_terminals = tuple(terminals)
        self.entry(self._full_mask)

    def _node(self, parent, symbol):
        key = (parent, symbol)
        node = self._intern.get(key)
        if node is None:
            node = len(self._parents)
            self._intern[key] = node
            self._parents.append(parent)
            self._symbols.append(symbol)
            self.stats["dag_nodes"] += 1
        return node

    def _word(self, node):
        symbols = []
        while node:
            self.tick()
            symbols.append(self._symbols[node])
            node = self._parents[node]
        symbols.reverse()
        self.stats["materialized_words"] += 1
        return tuple(symbols)

    def entry(self, symbol_mask):
        if not isinstance(symbol_mask, int) or symbol_mask < 0 or symbol_mask & ~self._full_mask:
            raise ValueError("symbol mask must be a subset of Sigma")
        if symbol_mask in self._cache:
            self.stats["cache_hits"] += 1
            return self._cache[symbol_mask][1]
        self.stats["cache_misses"] += 1
        self.tick()
        if symbol_mask == self._full_mask and not self._cache:
            terminals = self._initial_terminals
        else:
            candidates = (m for m in self._cache if m & symbol_mask == symbol_mask)
            source = min(candidates, key=lambda m: (m.bit_count(), m))
            source_terminals = self._cache[source][0]
            memo = {0: 0}
            transformed = []
            for terminal in source_terminals:
                path = []
                node = terminal
                while node not in memo:
                    self.tick()
                    path.append(node)
                    node = self._parents[node]
                while path:
                    self.tick()
                    old = path.pop()
                    parent = memo[self._parents[old]]
                    symbol = self._symbols[old]
                    memo[old] = self._node(parent, symbol) if self._bits[symbol] & symbol_mask else parent
                    self.stats["transformed_nodes"] += 1
                transformed.append(memo[terminal])
            terminals = tuple(transformed)
        split = len(self.positive)
        positive_ids, negative_ids = terminals[:split], terminals[split:]
        # Reuse materialized values for repeated terminal IDs in this entry.
        words = {}
        for node in terminals:
            self.tick()
            if node not in words:
                words[node] = self._word(node)
        positives = [words[node] for node in positive_ids]
        negatives = [words[node] for node in negative_ids]
        first_ids = {}
        for i, node in enumerate(positive_ids):
            self.tick()
            first_ids.setdefault(node, i)
        witness = {words[node]: i for node, i in first_ids.items()}
        rejection_mask = 0
        for i, node in enumerate(negative_ids):
            self.tick()
            if node not in first_ids:
                rejection_mask |= 1 << i
        result = {"positive": positives, "negative": negatives,
                  "rejection_mask": rejection_mask, "positive_witness": witness}
        self._cache[symbol_mask] = (terminals, result)
        return result

