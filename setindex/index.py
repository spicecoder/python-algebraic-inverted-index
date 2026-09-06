from collections import defaultdict

class InvertedIndex:
    def __init__(self, indexed_fields):
        self.indexed_fields = tuple(indexed_fields)
        self._index = {f: defaultdict(set) for f in self.indexed_fields}
        self._records = {}
        self._universe = set()
        self._next_rid = 1

    @property
    def universe(self):
        return set(self._universe)

    def add(self, record, rid=None):
        if rid is None:
            rid = self._next_rid
            self._next_rid += 1
        elif rid >= self._next_rid:
            self._next_rid = rid + 1
        if rid in self._records:
            raise ValueError(f"RID {rid} already exists")
        stored = dict(record)
        self._records[rid] = stored
        self._universe.add(rid)
        for field in self.indexed_fields:
            if field not in stored:
                continue
            value = stored[field]
            if isinstance(value, (list, tuple, set, frozenset)):
                for item in value:
                    self._index[field][item].add(rid)
            else:
                self._index[field][value].add(rid)
        return rid

    def eq(self, field, value):
        return set(self._index[field].get(value, set()))

    def in_values(self, field, values):
        result = set()
        for value in values:
            result.update(self._index[field].get(value, set()))
        return result

    def between(self, field, low, high):
        result = set()
        for value, rids in self._index[field].items():
            if low <= value <= high:
                result.update(rids)
        return result

    def evaluate(self, query):
        return query.evaluate(self)

    def fetch(self, rids):
        return [self._records[rid] for rid in rids]

    def items(self):
        return list(self._records.items())

    def get(self, rid):
        return self._records[rid]
