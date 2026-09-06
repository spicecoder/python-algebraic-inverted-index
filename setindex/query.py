from dataclasses import dataclass
from typing import Any, Protocol

class Evaluator(Protocol):
    def eq(self, field: str, value: Any) -> set[int]: ...
    def in_values(self, field: str, values: tuple[Any, ...]) -> set[int]: ...
    def between(self, field: str, low: Any, high: Any) -> set[int]: ...
    @property
    def universe(self) -> set[int]: ...

class Query:
    def evaluate(self, index: Evaluator) -> set[int]:
        raise NotImplementedError
    def __and__(self, other): return And(self, other)
    def __or__(self, other): return Or(self, other)
    def __invert__(self): return Not(self)
    def __sub__(self, other): return Difference(self, other)
    def __xor__(self, other): return Xor(self, other)
    def to_tree(self):
        raise NotImplementedError

@dataclass(frozen=True)
class Eq(Query):
    field: str
    value: Any
    def evaluate(self, index): return index.eq(self.field, self.value)
    def to_tree(self): return {"type": "predicate", "label": f"{self.field} = {self.value}"}

@dataclass(frozen=True)
class InSet(Query):
    field: str
    values: tuple[Any, ...]
    def evaluate(self, index): return index.in_values(self.field, self.values)
    def to_tree(self):
        joined = ", ".join(str(v) for v in self.values)
        return {"type": "predicate", "label": f"{self.field} IN {{{joined}}}"}

@dataclass(frozen=True)
class Between(Query):
    field: str
    low: Any
    high: Any
    def evaluate(self, index): return index.between(self.field, self.low, self.high)
    def to_tree(self): return {"type": "predicate", "label": f"{self.low} <= {self.field} <= {self.high}"}

@dataclass(frozen=True)
class And(Query):
    left: Query
    right: Query
    def evaluate(self, index): return self.left.evaluate(index) & self.right.evaluate(index)
    def to_tree(self): return {"type": "operator", "label": "AND", "children": [self.left.to_tree(), self.right.to_tree()]}

@dataclass(frozen=True)
class Or(Query):
    left: Query
    right: Query
    def evaluate(self, index): return self.left.evaluate(index) | self.right.evaluate(index)
    def to_tree(self): return {"type": "operator", "label": "OR", "children": [self.left.to_tree(), self.right.to_tree()]}

@dataclass(frozen=True)
class Not(Query):
    operand: Query
    def evaluate(self, index): return index.universe - self.operand.evaluate(index)
    def to_tree(self): return {"type": "operator", "label": "NOT", "children": [self.operand.to_tree()]}

@dataclass(frozen=True)
class Difference(Query):
    left: Query
    right: Query
    def evaluate(self, index): return self.left.evaluate(index) - self.right.evaluate(index)
    def to_tree(self): return {"type": "operator", "label": "DIFF", "children": [self.left.to_tree(), self.right.to_tree()]}

@dataclass(frozen=True)
class Xor(Query):
    left: Query
    right: Query
    def evaluate(self, index): return self.left.evaluate(index) ^ self.right.evaluate(index)
    def to_tree(self): return {"type": "operator", "label": "XOR", "children": [self.left.to_tree(), self.right.to_tree()]}

@dataclass(frozen=True)
class Field:
    name: str
    def __eq__(self, value: object):
        return Eq(self.name, value)
    def one_of(self, *values: Any): return InSet(self.name, tuple(values))
    def between(self, low: Any, high: Any): return Between(self.name, low, high)

def Q(field: str) -> Field:
    return Field(field)
