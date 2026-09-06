from setindex import InvertedIndex, Q, write_set_diagram_svg

records = [
    {"name": "Asha", "country": "AU", "status": "ACTIVE", "risk": "LOW",  "age": 68, "segment": "GOLD",   "channel": "WEB"},
    {"name": "Ben",  "country": "AU", "status": "ACTIVE", "risk": "HIGH", "age": 61, "segment": "SILVER", "channel": "WEB"},
    {"name": "Chen", "country": "NZ", "status": "ACTIVE", "risk": "LOW",  "age": 73, "segment": "GOLD",   "channel": "MOBILE"},
    {"name": "Devi", "country": "AU", "status": "CLOSED", "risk": "LOW",  "age": 70, "segment": "BRONZE", "channel": "BRANCH"},
    {"name": "Eli",  "country": "AU", "status": "ACTIVE", "risk": "LOW",  "age": 55, "segment": "SILVER", "channel": "MOBILE"},
]

idx = InvertedIndex(["country", "status", "risk", "age", "segment", "channel"])
for record in records:
    idx.add(record)

eligible = ((Q("country") == "AU") & (Q("status") == "ACTIVE") & ~(Q("risk") == "HIGH"))
write_set_diagram_svg(eligible, idx, "examples/output/eligible_set_diagram.svg", title="Eligible Records — Set Diagram")

five_predicates = ((Q("country") == "AU") & (Q("status") == "ACTIVE") & Q("age").between(50, 80) & Q("segment").one_of("GOLD", "SILVER") & ~(Q("risk") == "HIGH"))
write_set_diagram_svg(five_predicates, idx, "examples/output/five_predicates_set_diagram.svg", title="Five-Predicate Membership Diagram")
print("SVG written to: examples/output/eligible_set_diagram.svg")
print("SVG written to: examples/output/five_predicates_set_diagram.svg")
