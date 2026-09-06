# python-algebraic-inverted-index

Python set algebra over inverted indexes, with dynamic SVG visualisation and a Model 204-inspired mapping of `FIND`-style retrieval to generic domain expressions.

`python-algebraic-inverted-index` is a small, dependency-free Python research package for expressing application-domain queries as set algebra over inverted indexes, independent of any specific database engine.

The package does **not** model a domain as interacting objects. It models a domain as sets of records characterised by facts, with computation expressed through algebra over those sets.

## Core idea

Represent an application domain as:

```text
field/value -> set of record IDs
```

and compose selections using set algebra.

For example:

```python
from setindex import InvertedIndex, Q

idx = InvertedIndex(["country", "status", "risk"])

idx.add({"name": "Asha", "country": "AU", "status": "ACTIVE", "risk": "LOW"})
idx.add({"name": "Ben",  "country": "AU", "status": "ACTIVE", "risk": "HIGH"})

eligible = (
    (Q("country") == "AU")
    & (Q("status") == "ACTIVE")
    & ~(Q("risk") == "HIGH")
)

rids = idx.evaluate(eligible)
records = idx.fetch(rids)
```

The expression is evaluated over record-ID sets first. Full records are materialised only when required.

## Set operators

```text
A & B     intersection
A | B     union
~A        complement relative to the indexed universe
A - B     difference
A ^ B     symmetric difference

Q(field) == value
Q(field).one_of(v1, v2, ...)
Q(field).between(low, high)
```

A derived similarity measure is also provided:

```python
from setindex import jaccard
score = jaccard(set_a, set_b)
```

with:

```text
J(A,B) = |A ∩ B| / |A ∪ B|
```

## Architecture

```text
DOMAIN
   ↓
algebraic expression
   ├── evaluate → RID found set
   ├── render   → SVG explanation
   └── compile  → future backend query
```

The important separation is between:

```text
domain expression
      ↓
set algebra
      ↓
physical retrieval engine
```

That makes it possible to experiment with the same domain expression over Python sets today and other retrieval backends later.

## Dynamic SVG visualisation

The package renders the same algebraic query in two complementary ways.

### 1. Expression-tree view

This view shows logical structure and operator precedence.

```python
from setindex import write_query_svg

write_query_svg(
    eligible,
    "query_expression.svg",
    title="Set Algebra Query",
)
```

A query such as:

```python
(Q("country") == "AU") \
& (Q("status") == "ACTIVE") \
& ~(Q("risk") == "HIGH")
```

is rendered as an operator tree containing `AND`, `NOT`, and the predicate leaves.

This view is useful for:

- explaining the algebra;
- checking operator grouping;
- mapping expressions to backend query syntax;
- comparing the same logical query across storage engines.

### 2. Set-distribution view

This view shows how actual indexed records are distributed across the predicate sets and which records satisfy the final expression.

```python
from setindex import write_set_diagram_svg

write_set_diagram_svg(
    eligible,
    idx,
    "eligible_set_diagram.svg",
    title="Eligible Records",
    label_field="name",
)
```

For two or three predicates, the package renders a coloured Venn/Euler-style SVG. For the example above, it visualises:

```text
(country = AU) ∩ (status = ACTIVE) - (risk = HIGH)
```

and highlights the records satisfying the full expression.

For four or five predicates, a conventional Venn diagram becomes difficult to read, so the renderer automatically switches to a colourful predicate-membership matrix. Each row is a record, each predicate is a set-membership column, and the final result is shown explicitly.

```text
2–3 predicates  → Venn/Euler-style set diagram
4–5 predicates  → predicate-membership matrix
```

This keeps the visualisation useful without pretending that high-dimensional set relationships remain readable as overlapping circles.

## Same expression, multiple projections

The same query object can now support three different concerns:

```text
algebraic expression
      ├── execute  → found set
      ├── visualise→ SVG
      └── translate→ backend query
```

That means the diagram is not manually maintained documentation. It is generated from the same expression that drives execution.

## Example outputs

Running:

```bash
PYTHONPATH=. python examples/render_query_svg.py
PYTHONPATH=. python examples/render_set_diagram_svg.py
```

generates:

```text
examples/output/query_expression.svg
examples/output/eligible_set_diagram.svg
examples/output/five_predicates_set_diagram.svg
```

The repository includes these generated files as examples.

## Model 204 connection

Model 204 is relevant here as an architectural reference because its retrieval model centres on indexed field values, Boolean `FIND` criteria, and found sets.

This package is **not** an M204 emulator.

The relationship is conceptual:

| Generic set algebra | Model 204-style retrieval |
|---|---|
| `status == ACTIVE` | `FIND ... STATUS = 'ACTIVE'` |
| `A & B` | `A AND B` |
| `A | B` | `A OR B` |
| `~A` | negative criterion using `NOT` |
| `A - B` | `A AND NOT B` |
| range predicate | range criterion / `IN RANGE` |
| RID result set | found set produced by `FIND` |

For example, this Python expression:

```python
(
    (Q("STATUS") == "ACTIVE")
    & (Q("REGION") == "VIC")
    & ~(Q("RISK") == "HIGH")
)
```

maps conceptually to:

```text
FIND ALL RECORDS FOR WHICH
       STATUS = 'ACTIVE'
   AND REGION = 'VIC'
   AND NOT RISK = 'HIGH'
```

See `docs/m204-mapping.md` for the architectural mapping.

## Why inverted indexes?

A key-value lookup typically answers:

```text
Given this key, what is its value?
```

An inverted index answers a different class of question:

```text
Which records have this property?
```

For example:

```text
country = AU      -> {1, 2, 4, 7}
status = ACTIVE   -> {1, 2, 3, 7}
risk = HIGH       -> {2, 8}
```

The query:

```text
AU ∩ ACTIVE - HIGH
```

can be resolved by set operations over record identifiers before the underlying records need to be fetched.

This makes inverted access especially interesting for questions involving:

- membership;
- overlap;
- difference;
- common occurrence;
- comparison between domains;
- similarity between sets;
- result counting without materialisation.

## Database independence

The current implementation uses Python's built-in `set` and `dict` types and has no external runtime dependencies.

The algebra is deliberately separated from the physical store so that future adapters can experiment with:

```text
Python sets
compressed / Roaring bitmaps
PostgreSQL
MongoDB
Lucene-style posting lists
Model 204
```

The goal is not to hide database capabilities behind an ORM. It is to preserve a **set-theoretic domain expression** while allowing different retrieval engines to execute it.

## Repository structure

```text
python-algebraic-inverted-index/
├── README.md
├── pyproject.toml
├── sample-output.txt
├── setindex/
│   ├── __init__.py
│   ├── algebra.py
│   ├── index.py
│   ├── query.py
│   ├── render_svg.py
│   └── render_venn.py
├── examples/
│   ├── customers.py
│   ├── domain_comparison.py
│   ├── render_query_svg.py
│   ├── render_set_diagram_svg.py
│   └── output/
│       ├── query_expression.svg
│       ├── eligible_set_diagram.svg
│       └── five_predicates_set_diagram.svg
└── docs/
    ├── algebra.md
    ├── m204-mapping.md
    └── svg.md
```

## Run

Python 3.11+ is recommended.

No third-party packages are required.

```bash
PYTHONPATH=. python examples/customers.py
PYTHONPATH=. python examples/domain_comparison.py
PYTHONPATH=. python examples/render_query_svg.py
PYTHONPATH=. python examples/render_set_diagram_svg.py
```

## Current scope

This is a research package, not a production database engine.

The current implementation deliberately keeps the storage and rendering logic simple so that the algebra is easy to inspect, test, and compare.

Important limitations include:

- Python sets are the reference backend, not a persistence engine;
- range evaluation is intentionally simple;
- the Venn/Euler layout is illustrative rather than mathematically area-proportional;
- diagrams currently support up to five predicates;
- backend compilation is an architectural extension point rather than a completed feature.

## Possible next steps

```text
SetBackend
   ↓
BitmapBackend
   ↓
PostgreSQL compiler
   ↓
MongoDB compiler
   ↓
Model 204 FIND compiler
```

A particularly useful experiment will be to preserve exactly the same query expression while measuring how different physical retrieval engines perform set selection, result counting, and record materialisation.

## Research direction

The broader question behind this repository is simple:

> What becomes possible when an application domain is expressed directly as sets and relations between sets, instead of making object structure the primary computational abstraction?

The package is intended as a small executable place to explore that question.
