# Our solver (software: true only so that it may read the released network from $BOXGRAPH_SOURCE):
# the paper's steady Poiseuille-Kirchhoff hemodynamics (schwarz2020 Eqs. 3-6, pp. 4-5) on the released
# graph 'Human Left Coronary graph.mat' (struct TreeQ, explanation_of_data.txt sections 3.1-3.7).
# Nothing of the authors' analysis code is used (it is not released); only the graph's fields are read:
#   TreeQ.IE.nodes, .d, .l                 internal elements (two internal nodes each)
#   TreeQ.SE.node, .d, .l, .isinlet, .Gdist source/sink elements; Gdist the imputed distal conductance
#   TreeQ.SE.VVoronoi, .PerfBranchID        Voronoi volumes and perfusion branches (for perfusion)
# Conductance of each segment: Eq. 5, G = pi d^4 / (128 mu l), with mu = mu_p * mu_rel(d in um, Hd) by
# Eq. 3 (Pries et al. 1994 in vivo). A sink element drains through its segment and its distal tree in
# series, 1/G = 1/Gseg + 1/Gdist (TreeQ.SE.G, line 145 of the guide), to P_cap; the two inlets
# (isinlet) are held at P_in through their own segment. Kirchhoff at every internal node gives a sparse
# linear system in the internal node pressures, solved with scipy.sparse.linalg.spsolve.
# Derived per segment, as the release's fields define them (checked against them in this record):
#   P   mid-segment pressure, (P_up + P_down)/2;  Q  |flow|;  v = 8 Q / (pi d^2) centerline velocity;
#   tau = |P_up - P_down| d / (4 l) (Eq. 6);  distal conductance Q / (P_down - P_cap).
# Class statistics: medians over the segments of the diameter class containing d. Classes are 20 um
# wide from 50 um (settings class_width_um, class_first_edge_um), all segments below 50 um in one;
# this is our reading of the released tables' classes, not a stated rule.
# Power laws y = a d^b (d in m): non-linear least squares in linear space (scipy curve_fit), started
# from the log-log line; r2 = 1 - SSres/SStot in linear space.
# Perfusion per perfusion branch: the outflow of its sink elements over the weight of its territory,
# W * f_tree * V_branch / sum(V) (guide line 163; W the heart weight, f_tree the tree's share of all
# Voronoi volumes).
# Not a port: the authors' hemodynamics code is not released (guide line 34). The release's own
# solution fields (TreeQ.IN.P, SE.Q, SE.Gseg, IE.G, IE.WSS) are not read here; a few are data of the
# record that the runs are compared with. Pressures go to mmHg (class tables, pressure law) with
# 133.32 Pa/mmHg, the factor of the release's workbooks. Loading the file takes about 20 s.
import math
import os
import pathlib

import numpy as np

_CACHE = {}  # the network read once per process, and solutions by their inputs


def _scal(x):
    return float(x) if np.ndim(x) == 0 else float("nan")


def _network(name):
    key = ("net", name)
    if key not in _CACHE:
        import scipy.io

        m = scipy.io.loadmat(str(pathlib.Path(os.environ["BOXGRAPH_SOURCE"]) / name), squeeze_me=True, struct_as_record=False)
        T = m["TreeQ"]
        ie, se = T.IE, T.SE
        net = {
            "n_in": len(T.IN),
            "ie_nodes": np.array([np.asarray(e.nodes, dtype=np.int64) for e in ie]) - 1,
            "ie_d": np.array([_scal(e.d) for e in ie]),
            "ie_l": np.array([_scal(e.l) for e in ie]),
            "se_node": np.array([int(e.node) for e in se], dtype=np.int64) - 1,
            "se_d": np.array([_scal(e.d) for e in se]),
            "se_l": np.array([_scal(e.l) for e in se]),
            "se_inlet": np.array([bool(e.isinlet) for e in se]),
            "se_Gdist": np.array([_scal(e.Gdist) for e in se]),
            "se_V": np.array([_scal(e.VVoronoi) for e in se]),
            "se_branch": np.array([_scal(e.PerfBranchID) for e in se]),
        }
        _CACHE[key] = net
    return _CACHE[key]


def mu_rel(d_um, hd):
    """Eq. 3 (Pries et al. 1994, in vivo), d in um."""
    mu045 = 6 * np.exp(-0.085 * d_um) + 3.2 - 2.44 * np.exp(-0.06 * d_um ** 0.645)
    s = 1 / (1 + 1e-11 * d_um ** 12)
    c = (0.8 + np.exp(-0.075 * d_um)) * (-1 + s) + s
    r = (d_um / (d_um - 1.1)) ** 2
    return (1 + (mu045 - 1) * ((1 - hd) ** c - 1) / ((1 - 0.45) ** c - 1) * r) * r


def _solve(net, P_in, P_cap, Hd, mu_p):
    key = ("sol", id(net), P_in, P_cap, Hd, mu_p)
    if key in _CACHE:
        return _CACHE[key]
    import scipy.sparse as sp
    import scipy.sparse.linalg as spl

    g_ie = math.pi * net["ie_d"] ** 4 / (128 * mu_p * mu_rel(net["ie_d"] * 1e6, Hd) * net["ie_l"])
    g_seg = math.pi * net["se_d"] ** 4 / (128 * mu_p * mu_rel(net["se_d"] * 1e6, Hd) * net["se_l"])
    inlet = net["se_inlet"]
    g_se = np.where(inlet, g_seg, 1 / (1 / g_seg + 1 / np.where(inlet, 1.0, net["se_Gdist"])))
    p_src = np.where(inlet, P_in, P_cap)
    a, b = net["ie_nodes"][:, 0], net["ie_nodes"][:, 1]
    ns, n = net["se_node"], net["n_in"]
    rows = np.concatenate([a, b, a, b, ns])
    cols = np.concatenate([a, b, b, a, ns])
    vals = np.concatenate([g_ie, g_ie, -g_ie, -g_ie, g_se])
    K = sp.csc_matrix((vals, (rows, cols)), shape=(n, n))
    rhs = np.bincount(ns, weights=g_se * p_src, minlength=n)
    P = spl.spsolve(K, rhs)
    q_ie = g_ie * (P[a] - P[b])                 # from nodes[0] to nodes[1]
    q_se = g_se * (p_src - P[ns])               # into the network: > 0 at the inlets, < 0 at sinks
    p_end = P[ns] + q_se / g_seg                # pressure at the source/sink node of the segment
    # per segment: internal elements first, then source/sink elements
    up_ie, dn_ie = np.where(q_ie >= 0, P[a], P[b]), np.where(q_ie >= 0, P[b], P[a])
    up_se, dn_se = np.where(q_se >= 0, p_end, P[ns]), np.where(q_se >= 0, P[ns], p_end)
    d = np.concatenate([net["ie_d"], net["se_d"]])
    l = np.concatenate([net["ie_l"], net["se_l"]])
    Q = np.abs(np.concatenate([q_ie, q_se]))
    up, dn = np.concatenate([up_ie, up_se]), np.concatenate([dn_ie, dn_se])
    sol = {
        "P_nodes": P, "q_ie": q_ie, "q_se": q_se, "g_ie": g_ie, "g_seg": g_seg,
        "d": d, "internal": np.r_[np.ones(len(q_ie), bool), np.zeros(len(q_se), bool)],
        "P": (up + dn) / 2, "Q": Q, "v": 8 * Q / (math.pi * d ** 2), "wss": np.abs(up - dn) * d / (4 * l),
        "G_dist": Q / (dn - P_cap),
    }
    _CACHE[key] = sol
    return sol


def _class(d_um, d, width, first):
    if d_um < first:
        return d * 1e6 < first
    lo = first + width * math.floor((d_um - first) / width)
    return (d * 1e6 >= lo) & (d * 1e6 < lo + width)


def _power_fit(x, y):
    from scipy.optimize import curve_fit

    b0, la0 = np.polyfit(np.log(x), np.log(y), 1)
    p, _ = curve_fit(lambda t, a, b: a * t ** b, x, y, p0=[math.exp(la0), b0], maxfev=20000)
    r2 = 1 - np.sum((y - p[0] * x ** p[1]) ** 2) / np.sum((y - y.mean()) ** 2)
    return float(p[0]), float(p[1]), float(r2)


def _fits(net, sol, key, d_lo, d_hi):
    fk = ("fits", key, d_lo, d_hi)
    if fk in _CACHE:
        return _CACHE[fk]
    d, mmHg = sol["d"], 133.32
    out = {}
    out["G_a"], out["G_b"], out["G_r2"] = _power_fit(d, sol["G_dist"])
    i = sol["internal"]
    _, out["G_b_internal"], _ = _power_fit(d[i], sol["G_dist"][i])
    out["Q_a"], out["Q_b"], out["Q_r2"] = _power_fit(d, sol["Q"] * 6e7)
    out["v_a"], out["v_b"], out["v_r2"] = _power_fit(d, sol["v"] * 100)
    s = (d >= d_lo) & (d <= d_hi)
    out["P_a"], out["P_b"], out["P_r2"] = _power_fit(d[s], sol["P"][s] / mmHg)
    ok = np.isfinite(net["se_Gdist"]) & ~net["se_inlet"]
    out["Gdist_a"], out["Gdist_b"], _ = _power_fit(net["se_d"][ok], net["se_Gdist"][ok])
    _CACHE[fk] = out
    return out


def _quartiles(v, method):
    v = np.sort(v)
    if method == "linear":
        return [float(np.percentile(v, p)) for p in (25, 50, 75)]
    pos = np.arange(1, len(v) + 1) - 0.5   # Matlab prctile
    return [float(np.interp(p / 100.0 * len(v), pos, v)) for p in (25, 50, 75)]


def run(inputs, settings):
    net = _network(settings["file"])
    P_in, P_cap, Hd, mu_p = inputs["P_in"], inputs["P_cap"], inputs["Hd"], inputs["mu_p"]
    sol = _solve(net, P_in, P_cap, Hd, mu_p)
    width, first = settings["class_width_um"], settings["class_first_edge_um"]
    d = sol["d"]
    c = _class(inputs["d"], d, width, first)
    out = {
        "d_class": float(np.median(d[c]) * 1e6),
        "n_class": float(c.sum()),
        "P_class": float(np.median(sol["P"][c])),
        "Q_class": float(np.median(sol["Q"][c])),
        "G_class": float(np.median(sol["G_dist"][c])),
        "wss_class": float(np.median(sol["wss"][c])),
        "v_class": float(np.median(sol["v"][c])),
    }
    out.update(_fits(net, sol, (P_in, P_cap, Hd, mu_p), inputs["d_fit_lo"] * 1e-6, inputs["d_fit_hi"] * 1e-6))
    inl = np.where(net["se_inlet"])[0]            # SE 100960 (LCX) and 100961 (LAD), guide line 142
    out["Q_total"] = float(sol["q_se"][inl].sum())
    out["Q_LCX"], out["Q_LAD"] = float(sol["q_se"][inl[0]]), float(sol["q_se"][inl[1]])
    out["G_LCX"], out["G_LAD"] = float(sol["g_seg"][inl[0]]), float(sol["g_seg"][inl[1]])
    out["G_SE1"], out["G_IE1"] = float(sol["g_seg"][0]), float(sol["g_ie"][0])
    out["P_IN1"] = float(sol["P_nodes"][0])
    # signed from TreeQ.IE(1).nodes(1) to nodes(2), as the release stores it
    out["wss_IE1"] = float((sol["P_nodes"][net["ie_nodes"][0, 0]] - sol["P_nodes"][net["ie_nodes"][0, 1]])
                           * net["ie_d"][0] / (4 * net["ie_l"][0]))
    out["Q_large_median"] = float(np.median(sol["Q"][d > inputs["d_large"] * 1e-6]))
    out["wss_small_median"] = float(np.median(sol["wss"][d < inputs["d_cut"] * 1e-6]))
    # the class with the largest median shear stress, among classes of at least min_class_n segments
    lo = np.where(d * 1e6 < first, 0, np.floor((d * 1e6 - first) / width) + 1).astype(int)
    best, best_d = -1.0, float("nan")
    for k in np.unique(lo):
        s = lo == k
        if s.sum() >= settings["min_class_n"]:
            w = float(np.median(sol["wss"][s]))
            if w > best:
                best, best_d = w, float(np.median(d[s]) * 1e6)
    out["d_wss_peak"] = best_d
    # perfusion (guide lines 98-101, 163-168)
    br, V, qs = net["se_branch"], net["se_V"], sol["q_se"]
    okv = np.isfinite(V)
    ids = np.unique(br[np.isfinite(br)])
    order = np.argsort(br[np.isfinite(br)], kind="stable")
    brs, Vs, qss = br[np.isfinite(br)][order], np.nan_to_num(V[np.isfinite(br)][order]), qs[np.isfinite(br)][order]
    starts = np.searchsorted(brs, ids)
    Vb = np.add.reduceat(Vs, starts)
    Qb = -np.add.reduceat(qss, starts)
    Vsum = float(np.sum(V[okv]))
    weight = inputs["W"] * inputs["f_tree"] * Vb / Vsum          # kg
    perf = Qb / weight * 6e7 / 1000                               # m^3/s/kg -> ml/min/g
    p25, p50, p75 = _quartiles(perf, settings.get("percentile_method", "linear"))
    out.update({"perf_median": p50, "perf_p25": p25, "perf_p75": p75, "n_perf": float(len(ids)),
                "V_perfused": Vsum, "V_territory_median": float(np.median(Vb))})
    return out
