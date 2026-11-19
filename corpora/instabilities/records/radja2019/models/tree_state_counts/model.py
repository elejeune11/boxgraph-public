# Groups the state dots of the circular family tree into terminal taxa by angle and counts them.
# Adjacent families on the tree are about 1.8 degrees apart; the dots of one family lie on one
# radius. angle_tol_deg (an added choice, 0.7) joins dots whose angles differ by less than it;
# the grouping is the same for any tolerance from 0.4 to 0.9 degrees.


def run(inputs, settings):
    tol = float(settings["angle_tol_deg"])
    dots = []
    for k in ("O", "P", "G", "B"):
        for a in inputs[k]["x"]:
            dots.append((float(a) % 360.0, k))
    dots.sort()
    groups = []
    for a, k in dots:
        if groups and a - groups[-1][-1][0] <= tol:
            groups[-1].append((a, k))
        else:
            groups.append([(a, k)])
    # the circle closes: join the last and first groups if they are within tol across 360
    if len(groups) > 1 and groups[0][0][0] + 360.0 - groups[-1][-1][0] <= tol:
        groups[0] = groups.pop() + groups[0]
    kinds = [set(k for _, k in g) for g in groups]
    return {
        "n_eq": float(sum("O" in s for s in kinds)),
        "n_eq_only": float(sum(s == {"O"} for s in kinds)),
        "n_eq_mixed": float(sum("O" in s and len(s) > 1 for s in kinds)),
        "n_tips": float(len(kinds)),
        "n_noneq": float(sum("O" not in s for s in kinds)),
        "n_pink": float(sum("P" in s for s in kinds)),
        "n_green": float(sum("G" in s for s in kinds)),
        "n_blue": float(sum("B" in s for s in kinds)),
    }
