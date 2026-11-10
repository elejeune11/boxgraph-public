# Our code (software: true only to read the released network from $BOXGRAPH_SOURCE): Kassab et al.'s
# (1993) diameter-defined Strahler ordering (kassab1993 Eq. 1, p. 4) and their per-order statistics and
# Horton fits (Eqs. 2-5, p. 9; connectivity matrix, p. 13) applied to 'Human Left Coronary graph.mat'.
#
# Direction: the flow of our Poiseuille-Kirchhoff solution of the network (network_solution's _solve,
# on the same inputs as run_net_release); a segment's daughters are the segments flowing out of its
# downstream node. The graph is a DAG under flow (loops are crossed one way), so orders are assigned
# from the downstream end: a segment is processed after every segment downstream of it (sorted by the
# pressure at its upstream end).
#   Conventional Strahler (Kassab Fig. 4A, the version "when a vessel of order 2 meets a vessel of
#   order 1, the order number remains unchanged"): a segment without daughters is order 1; otherwise
#   m = the largest daughter order, and the order is m + 1 if two or more daughters have order m, else m.
#   Diameter-defined (Eq. 1): with D_n, SD_n the mean and SD of the element diameters of order n, the
#   upper bound of order n is [(D_n + SD_n) + (D_(n+1) - SD_(n+1))]/2 (Eq. 1b). A segment's order is
#   m (largest daughter order, 1 without daughters), increased by one by the rule below. D_n, SD_n are
#   recomputed and the rule reapplied until no order changes (at most max_iter cycles).
#   Elements: segments of the same order in series (p. 8). A segment joins the daughter of its own order
#   (the widest, if several) and a daughter joins at most one parent (the widest); the chains are the
#   elements. Element length = sum of the segment lengths; element diameter = the mean of the segment
#   diameters, or the length-weighted mean (setting element_diameter).
#   Connectivity C(n, m) (p. 13): the number of elements of order n springing directly from elements of
#   order m, divided by the number of elements of order m.
#   Horton fits (Eqs. 2, 4, 5): least squares of log10 of the element mean diameter (um), mean length
#   (um) and element count on order, over orders fit_lo..top; ratio = 10^b (Eq. 3) for diameter and
#   length, 10^-b (N_(n-1)/N_n) for number, as kassab1993's Table 4 and its record's fit models.
#   Setting rule: 'pair' (default) raises the order only where two daughters of the largest order meet
#   AND the diameter exceeds Eq. 1b, kassab1993 p. 4 ("when two vessels of a given order meet, the order
#   number of the offspring is increased by one if and only if its diameter is larger ..."); 'one_step'
#   drops the meeting condition (any segment whose diameter exceeds Eq. 1b of its largest daughter's
#   order is raised by one). At the highest order Eq. 1b is undefined and the conventional rule applies.
import importlib.util
import os

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(_HERE, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


T = _load("schwarz_tree", os.path.join("..", "tree_table1", "_tree.py"))
NS = _load("schwarz_network_solution", os.path.join("..", "network_solution", "model.py"))
_CACHE = {}


def _graph(t, inputs):
    """Segments (IE then SE) with their upstream and downstream node, daughters and processing order."""
    net = {k: t[k] for k in ("ie_nodes", "ie_d", "ie_l", "se_node", "se_d", "se_l", "se_inlet", "se_Gdist")}
    net["n_in"] = t["n_in"]
    sol = NS._solve(net, inputs["P_in"], inputs["P_cap"], inputs["Hd"], inputs["mu_p"])
    P, q_ie, q_se = sol["P_nodes"], sol["q_ie"], sol["q_se"]
    n_in = t["n_in"]
    a, b = t["ie_nodes"][:, 0], t["ie_nodes"][:, 1]
    up_ie, dn_ie = np.where(q_ie >= 0, a, b), np.where(q_ie >= 0, b, a)
    # source/sink nodes get ids n_in.. so that they are nobody's upstream node except their own segment
    ext = n_in + np.arange(len(q_se))
    up_se = np.where(q_se >= 0, ext, t["se_node"])
    dn_se = np.where(q_se >= 0, t["se_node"], ext)
    up, dn = np.r_[up_ie, up_se], np.r_[dn_ie, dn_se]
    d = np.r_[t["ie_d"], t["se_d"]] * 1e6          # um
    ln = np.r_[t["ie_l"], t["se_l"]] * 1e3         # mm
    n_nodes = n_in + len(q_se)
    Pn = np.r_[P, np.full(len(q_se), -np.inf)]
    Pn[up_se[q_se >= 0]] = np.inf                  # sources: most upstream
    # daughters of s: segments whose upstream node is dn[s] (CSR by node)
    order_up = np.argsort(up, kind="stable")
    start = np.searchsorted(up[order_up], np.arange(n_nodes + 1))
    proc = np.argsort(Pn[up], kind="stable")       # downstream first
    return {"up": up, "dn": dn, "d": d, "l": ln, "by_up": order_up, "start": start, "proc": proc}


def _daughters(g, s):
    node = g["dn"][s]
    return g["by_up"][g["start"][node]:g["start"][node + 1]]


def _assign(g, ub, rule):
    """One pass from the downstream end. ub None: conventional Strahler; else Eq. 1 with upper bounds ub[n].
    The highest order has no Eq. 1b bound (there is no D_(n+1)); there the conventional rule applies."""
    o = np.zeros(len(g["d"]), dtype=np.int64)
    for s in g["proc"]:
        ch = _daughters(g, s)
        if len(ch) == 0:
            o[s] = 1
            continue
        co = o[ch]
        m = int(co.max())
        pair = np.sum(co == m) >= 2
        if ub is None or m not in ub:
            o[s] = m + 1 if pair else m
        elif rule == "pair":
            o[s] = m + 1 if (pair and g["d"][s] > ub[m]) else m
        elif rule == "one_step":
            o[s] = m + 1 if g["d"][s] > ub[m] else m
        else:
            raise ValueError(f"unknown rule {rule}")
    return o


def _elements(g, o, how):
    nseg = len(o)
    cand = np.full(nseg, -1)
    for s in range(nseg):
        ch = _daughters(g, s)
        same = ch[o[ch] == o[s]]
        if len(same):
            cand[s] = same[np.argmax(g["d"][same])]
    # a daughter claimed by several parents (a merge) continues the widest; the others end there
    par = np.full(nseg, -1)
    for s in np.argsort(-g["d"], kind="stable"):
        c = cand[s]
        if c >= 0 and par[c] < 0:
            par[c] = s
    nxt = np.full(nseg, -1)
    for c in np.where(par >= 0)[0]:
        nxt[par[c]] = c
    elem = np.full(nseg, -1)
    k = 0
    for s in range(nseg):
        if par[s] >= 0:
            continue
        x = s
        while x >= 0:
            elem[x] = k
            x = nxt[x]
        k += 1
    w = g["l"] if how == "length_weighted" else np.ones(nseg)
    L = np.bincount(elem, weights=g["l"], minlength=k)
    D = np.bincount(elem, weights=g["d"] * w, minlength=k) / np.bincount(elem, weights=w, minlength=k)
    eo = np.zeros(k, dtype=np.int64)
    eo[elem] = o
    nseg_e = np.bincount(elem, minlength=k)
    return elem, eo, D, L, nseg_e


def _bounds(eo, D):
    orders = sorted(set(eo.tolist()))
    mean = {n: float(D[eo == n].mean()) for n in orders}
    sd = {n: float(D[eo == n].std(ddof=1)) if np.sum(eo == n) > 1 else 0.0 for n in orders}
    ub = {}
    for n in orders:
        if n + 1 in mean:
            ub[n] = ((mean[n] + sd[n]) + (mean[n + 1] - sd[n + 1])) / 2
    return ub


def _order(t, inputs, settings):
    key = (inputs["P_in"], inputs["P_cap"], inputs["Hd"], inputs["mu_p"],
           settings["element_diameter"], settings["max_iter"], settings["rule"])
    if key in _CACHE:
        return _CACHE[key]
    g = _graph(t, inputs)
    how = settings["element_diameter"]
    o = _assign(g, None, None)
    it, changed = 0, -1
    while it < settings["max_iter"]:
        elem, eo, D, L, ns = _elements(g, o, how)
        o2 = _assign(g, _bounds(eo, D), settings["rule"])
        changed = int(np.sum(o2 != o))
        o = o2
        it += 1
        if changed == 0:
            break
    elem, eo, D, L, ns = _elements(g, o, how)
    # connectivity: elements of order n springing directly from each element (daughters outside it)
    k = len(eo)
    pairs = set()
    for s in range(len(o)):
        for c in _daughters(g, s):
            if elem[c] != elem[s]:
                pairs.add((elem[s], elem[c]))
    pa = np.array(sorted(pairs), dtype=np.int64).reshape(-1, 2)
    res = {"g": g, "o": o, "elem": elem, "eo": eo, "D": D, "L": L, "ns": ns, "pairs": pa,
           "iterations": it, "converged": changed == 0, "k": k}
    _CACHE[key] = res
    return res


def _fit(xs, ys):
    xs, ys = np.asarray(xs, float), np.asarray(ys, float)
    mx, my = xs.mean(), ys.mean()
    sxx, syy, sxy = np.sum((xs - mx) ** 2), np.sum((ys - my) ** 2), np.sum((xs - mx) * (ys - my))
    b = sxy / sxx
    return float(my - b * mx), float(b), float(sxy * sxy / (sxx * syy)), float(10 ** b)


def run_order(inputs, settings):
    """Per-order statistics of order n (used by tree_strahler_order)."""
    t = T.load(settings["file"])
    r = _order(t, inputs, settings)
    g, o, eo, D, L = r["g"], r["o"], r["eo"], r["D"], r["L"]
    n = int(round(inputs["n"]))
    sel_e, sel_s = eo == n, o == n
    nan = float("nan")
    out = {"N_elem": float(sel_e.sum()), "N_seg": float(sel_s.sum())}
    out["D_elem"] = float(D[sel_e].mean()) if sel_e.any() else nan
    out["D_elem_sd"] = float(D[sel_e].std(ddof=1)) if sel_e.sum() > 1 else nan
    out["L_elem"] = float(L[sel_e].mean()) if sel_e.any() else nan
    out["D_seg"] = float(g["d"][sel_s].mean()) if sel_s.any() else nan
    out["L_seg"] = float(g["l"][sel_s].mean()) if sel_s.any() else nan
    out["SE"] = out["N_seg"] / out["N_elem"] if out["N_elem"] else nan
    pa = r["pairs"]
    for name, m in (("C_same", n), ("C_next", n + 1)):
        nm = float(np.sum(eo == m))
        out[name] = float(np.sum((eo[pa[:, 0]] == m) & (eo[pa[:, 1]] == n))) / nm if nm else nan
    return out


def run(inputs, settings):
    t = T.load(settings["file"])
    r = _order(t, inputs, settings)
    o, eo, D, L = r["o"], r["eo"], r["D"], r["L"]
    top = int(eo.max())
    out = {"n_orders": float(top), "iterations": float(r["iterations"]), "converged": float(r["converged"]),
           "n_segments": float(len(o)), "n_elements": float(r["k"])}
    orders = [k for k in range(int(settings["fit_lo"]), top + 1) if np.any(eo == k)]
    Dm = [D[eo == k].mean() for k in orders]
    Lm = [L[eo == k].mean() * 1e3 for k in orders]        # um, as kassab1993's Horton length fits
    Nm = [np.sum(eo == k) for k in orders]
    for name, ys in (("D", Dm), ("L", Lm), ("N", Nm)):
        a, b, r2, ratio = _fit(orders, np.log10(ys))
        out[f"a_{name}"], out[f"b_{name}"], out[f"R2_{name}"], out[f"ratio_{name}"] = a, b, r2, ratio
    out["ratio_N"] = 10 ** (-out["b_N"])                   # N_(n-1)/N_n, as kassab1993's number ratio
    return out
