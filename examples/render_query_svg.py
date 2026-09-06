from pathlib import Path
from setindex import Q, write_query_svg

query = (((Q("country") == "AU") & (Q("status") == "ACTIVE")) & ~(Q("risk") == "HIGH")) | Q("age").between(60, 80)
output = Path("examples/output/query_expression.svg")
write_query_svg(query, output, title="Set Algebra Query")
print(f"SVG written to: {output}")
