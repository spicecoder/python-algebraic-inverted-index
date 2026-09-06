RIDSet = set[int]

def intersect(*sets_: RIDSet) -> RIDSet:
    if not sets_:
        return set()
    ordered = sorted(sets_, key=len)
    result = set(ordered[0])
    for s in ordered[1:]:
        result.intersection_update(s)
        if not result:
            break
    return result

def union(*sets_: RIDSet) -> RIDSet:
    result: RIDSet = set()
    for s in sets_:
        result.update(s)
    return result

def difference(left: RIDSet, right: RIDSet) -> RIDSet:
    return left - right

def xor(left: RIDSet, right: RIDSet) -> RIDSet:
    return left ^ right

def complement(universe: RIDSet, operand: RIDSet) -> RIDSet:
    return universe - operand

def jaccard(left, right) -> float:
    u = left | right
    return 1.0 if not u else len(left & right) / len(u)
