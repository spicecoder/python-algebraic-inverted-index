from setindex import InvertedIndex, Q

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
print("eligible RIDs:", sorted(idx.evaluate(eligible)))
print("records:", idx.fetch(sorted(idx.evaluate(eligible))))

senior_eligible = eligible & Q("age").between(60, 120)
print("senior eligible:", idx.fetch(sorted(idx.evaluate(senior_eligible))))
