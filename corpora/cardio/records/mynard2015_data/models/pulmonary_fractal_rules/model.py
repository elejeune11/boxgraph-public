# Adapter (software: true): the fractal rules of the paper's Eq. 2 as the released pulmonary networks follow
# them (Supplemental File 1, MOESM1_1D_segments.xlsx, read from $BOXGRAPH_SOURCE). Our own code:
#   the tree: settings.direction 'outlet' (arteries): the segments of settings.block downstream of
#     settings.roots, daughters named in column H; 'inlet' (veins): every segment of the block, daughters (the
#     upstream veins) named in column G. Only segments of the tree count as daughters ('VB:' beds do not).
#   per bifurcation (a tree segment with two daughters), from inlet A0 (column E), r = sqrt(A0/pi):
#     gamma = r_d2^2 / r_d1^2 with d1 the larger daughter (Eq. 2, right);
#     xi solving D_p^xi = D_d1^xi + D_d2^xi (Eq. 2, left), by bisection on [1, 10];
#   per tree segment: L/r, length (column D) over inlet radius.
# Outputs: the smallest and largest of each over the tree, and the number of bifurcations.
import importlib.util
import math
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("mynard2015_data_sheets", os.path.join(_HERE, "..", "network_counts", "_sheets.py"))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)


def _xi(Dp, D1, D2):
    f = lambda x: D1 ** x + D2 ** x - Dp ** x
    lo, hi = 1.0, 10.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if (f(lo) > 0) == (f(mid) > 0):
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def run(inputs, settings):
    block = [s for s in S.segments() if s["block"] == settings["block"]]
    by = {s["C"]: s for s in block}
    col = "H" if settings["direction"] == "outlet" else "G"
    if settings["direction"] == "outlet":
        tree, stack = set(), [n for r in settings["roots"] for n in S.names(by[r]["H"]) if n in by]
        while stack:
            n = stack.pop()
            if n not in tree:
                tree.add(n)
                stack += [m for m in S.names(by[n]["H"]) if m in by]
    else:
        tree = set(by)
    gam, xis, lr = [], [], []
    for n in sorted(tree):
        s = by[n]
        lr.append(s["D"] / math.sqrt(s["E"] / math.pi))
        kids = [k for k in S.names(s[col]) if k in tree]
        if len(kids) == 2:
            a1, a2 = sorted((by[k]["E"] for k in kids), reverse=True)
            gam.append(a2 / a1)
            xis.append(_xi(S.diameter(s["E"]), S.diameter(a1), S.diameter(a2)))
        elif kids:
            raise ValueError(f"{n}: {len(kids)} daughters")
    return {"gamma_min": min(gam), "gamma_max": max(gam), "xi_min": min(xis), "xi_max": max(xis),
            "L_over_r_min": min(lr), "L_over_r_max": max(lr), "n_bifurcations": float(len(gam))}
