# Dynamic SVG rendering

The package supports two diagram styles generated programmatically from the same query expression.

## 1. Expression tree

```python
from setindex import write_query_svg
write_query_svg(query, "query.svg", title="Set Algebra Query")
```

## 2. Set diagram

```python
from setindex import write_set_diagram_svg
write_set_diagram_svg(query, index, "set-diagram.svg", title="Eligible Records")
```

Behaviour:
- 2–3 predicates → Venn/Euler-style coloured set diagram
- 4–5 predicates → colourful predicate-membership matrix
