# Generic algebra mapped to Model 204 concepts

This is an architectural mapping, not a claim of implementation equivalence.

| Generic algebra | Model 204-style form |
|---|---|
| equality | `FIND RECORDS WITH STATUS = 'ACTIVE'` |
| intersection | `... STATUS = 'ACTIVE' AND REGION = 'VIC'` |
| union | `... STATUS = 'ACTIVE' OR STATUS = 'PENDING'` |
| complement | negative criterion using `NOT` |
| range | range criterion / `IN RANGE` |
| found set | result of `FIND` |

Derived operators:

```text
A - B = A AND NOT B
A XOR B = (A AND NOT B) OR (B AND NOT A)
```
