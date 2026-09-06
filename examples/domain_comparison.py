from setindex import jaccard

a = {"identity_verified", "request_accepted", "payment_authorised", "audit_recorded"}
b = {"identity_verified", "request_accepted", "risk_checked", "audit_recorded"}

print("shared:", sorted(a & b))
print("A only:", sorted(a - b))
print("B only:", sorted(b - a))
print("Jaccard:", round(jaccard(a, b), 3))
