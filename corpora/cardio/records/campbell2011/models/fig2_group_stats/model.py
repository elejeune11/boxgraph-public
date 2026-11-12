# Group statistics of Fig. 2's per-patient points (one point per patient, one group per run).
# Units: widths and radii in um, length density in mm/mm^3, BSA in m^2.
# Percentiles: linear interpolation between order statistics (numpy's default); the paper does
# not say which definition it used (question q_fig2_percentile_method).
# Spearman: Pearson correlation of the ranks, ties given their average rank. The points are read
# from the plot, so two patients with the same printed BSA land a fraction of a pixel apart; x
# values closer than the tie setting are treated as equal (question q_fig2_ties).


def _pct(v, p):
    s = sorted(v)
    h = (len(s) - 1) * p / 100.0
    i = int(h)
    return s[i] if i + 1 >= len(s) else s[i] + (h - i) * (s[i + 1] - s[i])


def _merge_ties(v, tol):
    """Values closer than tol to their neighbour in sorted order share one value (the group mean)."""
    order = sorted(range(len(v)), key=lambda i: v[i])
    out = list(v)
    group = [order[0]]
    for a, b in zip(order, order[1:]):
        if v[b] - v[a] <= tol:
            group.append(b)
        else:
            m = sum(v[i] for i in group) / len(group)
            for i in group:
                out[i] = m
            group = [b]
    m = sum(v[i] for i in group) / len(group)
    for i in group:
        out[i] = m
    return out


def _ranks(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2.0 + 1
        i = j + 1
    return r


def _spearman(x, y):
    rx, ry = _ranks(x), _ranks(y)
    n = len(x)
    mx, my = sum(rx) / n, sum(ry) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    sxx = sum((a - mx) ** 2 for a in rx)
    syy = sum((b - my) ** 2 for b in ry)
    return sxy / (sxx * syy) ** 0.5


def run(inputs, settings):
    if settings.get("percentile_method", "linear") != "linear":
        raise ValueError("only linear percentiles are implemented")
    tb, tw = float(settings["bsa_tie_m2"]), float(settings["width_tie_um"])
    W, R, L, D = inputs["W"], inputs["R"], inputs["L"], inputs["D"]
    out = {}
    for name, c in (("w", W), ("R", R), ("Lv", L), ("RD", D)):
        out[name + "_q25"] = _pct(c["y"], 25)
        out[name + "_med"] = _pct(c["y"], 50)
        out[name + "_q75"] = _pct(c["y"], 75)
    out["bsa_med"] = _pct(W["x"], 50)
    out["wB_med"] = _pct([y / x for x, y in zip(W["x"], W["y"])], 50)
    out["RB_med"] = _pct([y / x for x, y in zip(R["x"], R["y"])], 50)
    out["Rw_med"] = _pct([y / x for x, y in zip(D["x"], D["y"])], 50)
    out["rho_wB"] = _spearman(_merge_ties(W["x"], tb), W["y"])
    out["rho_RB"] = _spearman(_merge_ties(R["x"], tb), R["y"])
    out["rho_LB"] = _spearman(_merge_ties(L["x"], tb), L["y"])
    out["rho_Rw"] = _spearman(_merge_ties(D["x"], tw), D["y"])
    for k, c in (("n_W", W), ("n_R", R), ("n_L", L), ("n_D", D)):
        out[k] = float(len(c["y"]))
    return out
