# One open-loop synthetic tree grown by the released svVascularize (svv 0.0.57) with the paper's
# constants, then (our own code, below) the statistics the record compares, and the paper's tree
# equations (Eqs. S3, S6, S8, S9, S10) recomputed on the grown tree's own topology, lengths and flows.
#
# The tree is grown by grow.py, run in a subprocess under the separate environment that holds svv
# (corpus/cardio/envs/sim, `python -I`, SVV_TELEMETRY_DISABLED=1); it returns plain numbers. svv's
# randomness (Python's random, numpy's global generator and the domain's own PCG64) is seeded with the
# `seed` setting.
#
# Statistics (diameters in um):
#   bifurcations = vessels with two children; dM = mother diameter, dL >= dS the daughters
#   A = (dL^2 + dS^2) / dM^2 (area growth, schwarz2020 Eq. 2); S = dS / dL (daughter symmetry, Eq. 1)
#   medians over all bifurcations, and over mothers with dM > d_A_large_um (A) and dM > d_S_large_um (S)
#   (settings: schwarz2020's thresholds, p. 5 "larger than 400 um" and p. 9 ">500 um"), with svv's
#   stored radii (column 21, what svv exports), and again with radii propagated from svv's root radius
#   by svv's own stored ratios (outputs *_beta), because the two differ (radius_dev_stored)
#   Eq. S5 on the stored radii: (r_L^gamma + r_R^gamma) / r_parent^gamma at each bifurcation
#   Murray identity at each bifurcation: beta_L^gamma + beta_R^gamma, with svv's stored ratios (cols 23-24)
#   Horton ratios: Kassab's diameter-defined Strahler ordering (kassab1993 Eq. 1, 'pair' rule; conventional
#   Strahler first, then the Eq. 1b bounds from the element diameters, repeated until no order changes),
#   elements = segments of one order in series, least squares of log10(mean element diameter), log10(mean
#   element length) and log10(element count) on order over orders 1..top; ratios 10^b, 10^b and 10^-b.
# Equations recomputed bottom-up on the grown tree (mu = the `mu` input; flows Q from svv, which sums the
# terminal flows, Eq. S3):
#   ratio of daughter radii, equal pressure drops (Eq. S9): r_R / r_L = (R*_R Q_R / (R*_L Q_L))^(1/4)
#   beta_L = (1 + (r_R/r_L)^gamma)^(-1/gamma), beta_R = (1 + (r_L/r_R)^gamma)^(-1/gamma)   (Eq. S6)
#   printed Eq. S10: R*_i = 8 mu l_i / pi + (beta_L / R*_L + beta_R / R*_R)^-1   (terminal: 8 mu l_i / pi)
#   with beta^4 in place of beta (the form svv's code uses, svv/tree/utils/c_update.py lines 32-37)
#   root radius (Eq. S8): r_root = (R*_root Q_root / dP_tree)^(1/4); radii down the tree r_child = beta r_parent
import json
import os
import subprocess

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
MMHG = 1333.22387415          # dyn/cm^2 per mmHg
_CACHE = {}


def _sim_python():
    d = _HERE
    for _ in range(10):
        cand = os.path.join(d, "corpus", "cardio", "envs", "sim", "bin", "python")
        if os.path.exists(cand):
            return cand
        d = os.path.dirname(d)
    raise FileNotFoundError("the svv environment corpus/cardio/envs/sim was not found")


def grow(req):
    key = json.dumps(req, sort_keys=True)
    if key in _CACHE:
        return _CACHE[key]
    env = dict(os.environ)
    env["SVV_TELEMETRY_DISABLED"] = "1"
    proc = subprocess.run([_sim_python(), "-I", os.path.join(_HERE, "grow.py")], input=key,
                          capture_output=True, text=True, env=env, cwd=_HERE, timeout=3600)
    if proc.returncode != 0:
        raise RuntimeError(f"svv growth failed: {proc.stderr[-3000:]}")
    res = json.loads(proc.stdout)
    _CACHE[key] = res
    return res


def _arr(res, k):
    return np.array([np.nan if x is None else x for x in res[k]], dtype=float)


def _depth(left, right, parent):
    """Generation of every vessel counted from the root (the row without a parent), by traversal: svv's
    own depth column (26) does not equal it in the trees grown here, so it is not used."""
    n = len(left)
    depth = np.full(n, -1.0)
    stack = [int(np.where(np.isnan(parent))[0][0])]
    depth[stack[0]] = 0
    while stack:
        i = stack.pop()
        for c in (left[i], right[i]):
            if not np.isnan(c):
                depth[int(c)] = depth[i] + 1
                stack.append(int(c))
    return depth


def _strahler(left, right, depth, d_um, l_um, max_iter=50):
    n = len(d_um)
    kids = [[int(c) for c in (left[i], right[i]) if not np.isnan(c)] for i in range(n)]
    proc = np.argsort(-depth, kind="stable")          # deepest first: daughters before mothers

    def assign(ub):
        o = np.zeros(n, dtype=np.int64)
        for s in proc:
            ch = kids[s]
            if not ch:
                o[s] = 1
                continue
            co = o[ch]
            m = int(co.max())
            pair = int(np.sum(co == m)) >= 2
            if ub is None or m not in ub:
                o[s] = m + 1 if pair else m
            else:
                o[s] = m + 1 if (pair and d_um[s] > ub[m]) else m
        return o

    def elements(o):
        nxt = np.full(n, -1)
        has_par = np.zeros(n, bool)
        for s in range(n):
            same = [c for c in kids[s] if o[c] == o[s]]
            if same:
                c = max(same, key=lambda x: d_um[x])
                nxt[s] = c
                has_par[c] = True
        elem = np.full(n, -1)
        k = 0
        for s in range(n):
            if has_par[s]:
                continue
            x = s
            while x >= 0:
                elem[x] = k
                x = nxt[x]
            k += 1
        L = np.bincount(elem, weights=l_um, minlength=k)
        D = np.bincount(elem, weights=d_um, minlength=k) / np.bincount(elem, minlength=k)
        eo = np.zeros(k, dtype=np.int64)
        eo[elem] = o
        return eo, D, L

    def bounds(eo, D):
        orders = sorted(set(eo.tolist()))
        mean = {m: float(D[eo == m].mean()) for m in orders}
        sd = {m: float(D[eo == m].std(ddof=1)) if np.sum(eo == m) > 1 else 0.0 for m in orders}
        return {m: ((mean[m] + sd[m]) + (mean[m + 1] - sd[m + 1])) / 2 for m in orders if m + 1 in mean}

    o = assign(None)
    for _ in range(max_iter):
        eo, D, L = elements(o)
        o2 = assign(bounds(eo, D))
        changed = int(np.sum(o2 != o))
        o = o2
        if changed == 0:
            break
    eo, D, L = elements(o)
    top = int(eo.max())
    orders = [m for m in range(1, top + 1) if np.any(eo == m)]
    out = {"n_orders": float(top)}
    for name, ys in (("D", [D[eo == m].mean() for m in orders]), ("L", [L[eo == m].mean() for m in orders]),
                     ("N", [float(np.sum(eo == m)) for m in orders])):
        if len(orders) < 2:
            out[f"ratio_{name}"] = float("nan")
            continue
        b = np.polyfit(np.array(orders, float), np.log10(np.array(ys, float)), 1)[0]
        out[f"ratio_{name}"] = float(10 ** (-b) if name == "N" else 10 ** b)
    return out


def _recompute(left, right, length, flow, depth, mu, gamma, dP, power):
    n = len(length)
    rstar = np.zeros(n)
    bl = np.full(n, np.nan)
    br = np.full(n, np.nan)
    for i in np.argsort(-depth, kind="stable"):
        own = 8.0 * mu * length[i] / np.pi
        if np.isnan(left[i]) and np.isnan(right[i]):
            rstar[i] = own
            continue
        a, b = int(left[i]), int(right[i])
        lr = (rstar[b] * flow[b] / (rstar[a] * flow[a])) ** 0.25          # r_R / r_L, Eq. S9
        bl[i] = (1.0 + lr ** gamma) ** (-1.0 / gamma)
        br[i] = (1.0 + lr ** (-gamma)) ** (-1.0 / gamma)
        rstar[i] = own + 1.0 / (bl[i] ** power / rstar[a] + br[i] ** power / rstar[b])
    r = np.zeros(n)
    r[0] = (rstar[0] * flow[0] / dP) ** 0.25                                # Eq. S8
    for i in np.argsort(depth, kind="stable"):
        if not np.isnan(left[i]):
            r[int(left[i])] = bl[i] * r[i]
            r[int(right[i])] = br[i] * r[i]
    return rstar[0], r


def run(inputs, settings):
    req = {"seed": int(settings["seed"]), "n_terminals": int(round(inputs["n_terminals"])),
           "cube_edge": inputs["cube_edge"], "gamma": inputs["gamma"],
           "radius_exponent": inputs["alpha_r"], "length_exponent": inputs["alpha_l"],
           "kinematic_viscosity": inputs["mu"] / 100.0 / inputs["rho"], "density": inputs["rho"],   # cP -> P
           "terminal_flow": inputs["Q_term"], "root_pressure": inputs["P_root"],
           "terminal_pressure": inputs["P_term"]}
    res = grow(req)
    left, right = _arr(res, "left"), _arr(res, "right")
    depth = _depth(left, right, _arr(res, "parent"))
    length, radius, flow = _arr(res, "length"), _arr(res, "radius"), _arr(res, "flow")
    lbif, rbif = _arr(res, "lbif"), _arr(res, "rbif")
    gamma = inputs["gamma"]
    d_um = 2.0 * radius * 1e4
    l_um = length * 1e4
    bif = np.where(~np.isnan(left) & ~np.isnan(right))[0]
    dM = d_um[bif]
    d1, d2 = d_um[left[bif].astype(int)], d_um[right[bif].astype(int)]
    dL, dS = np.maximum(d1, d2), np.minimum(d1, d2)
    A = (dL ** 2 + dS ** 2) / dM ** 2
    S = dS / dL
    nan = float("nan")
    d_A, d_S = float(settings["d_A_large_um"]), float(settings["d_S_large_um"])
    bigA, bigS = dM > d_A, dM > d_S
    msum = lbif[bif] ** gamma + rbif[bif] ** gamma                     # svv's stored ratios, Eq. S6 identity
    rsum = (d1 ** gamma + d2 ** gamma) / dM ** gamma                    # Eq. S5 on svv's stored radii
    # radii propagated from the root radius by svv's own stored ratios (Eq. S6, p. 4 "propagate radii")
    rb = np.zeros(len(radius))
    rb[0] = radius[0]
    for i in np.argsort(depth, kind="stable"):
        if not np.isnan(left[i]):
            rb[int(left[i])] = lbif[i] * rb[i]
            rb[int(right[i])] = rbif[i] * rb[i]
    dev = np.abs(radius / rb - 1.0)
    db_um = 2.0 * rb * 1e4
    dMb = db_um[bif]
    e1, e2 = db_um[left[bif].astype(int)], db_um[right[bif].astype(int)]
    eL, eS = np.maximum(e1, e2), np.minimum(e1, e2)
    Ab, Sb = (eL ** 2 + eS ** 2) / dMb ** 2, eS / eL
    bigAb, bigSb = dMb > d_A, dMb > d_S
    out = {"n_terminals_grown": float(res["n_terminals"]), "n_segments": float(len(length)),
           "root_diameter": float(d_um[0]), "min_diameter": float(np.min(d_um)),
           "A_median_all": float(np.median(A)), "S_median_all": float(np.median(S)),
           "A_median_large": float(np.median(A[bigA])) if bigA.any() else nan,
           "S_median_large": float(np.median(S[bigS])) if bigS.any() else nan,
           "n_bif_A_large": float(bigA.sum()), "n_bif_S_large": float(bigS.sum()),
           "murray_sum_max": float(np.max(msum)), "murray_sum_min": float(np.min(msum)),
           "murray_radius_sum_max": float(np.max(rsum)), "murray_radius_sum_min": float(np.min(rsum)),
           "murray_radius_sum_median": float(np.median(rsum)),
           "radius_dev_stored": float(np.max(dev)), "frac_radius_dev_1pct": float(np.mean(dev > 0.01)),
           "A_median_all_beta": float(np.median(Ab)), "S_median_all_beta": float(np.median(Sb)),
           "A_median_large_beta": float(np.median(Ab[bigAb])) if bigAb.any() else nan,
           "S_median_large_beta": float(np.median(Sb[bigSb])) if bigSb.any() else nan,
           "t_grow": float(res["t_grow"])}
    out.update(_strahler(left, right, depth, d_um, l_um))
    mu_P = inputs["mu"] / 100.0                                         # cP -> poise (dyn s/cm^2)
    dP = (inputs["P_root"] - inputs["P_term"]) * MMHG
    rs_p, r_p = _recompute(left, right, length, flow, depth, mu_P, gamma, dP, 1.0)
    rs_4, r_4 = _recompute(left, right, length, flow, depth, mu_P, gamma, dP, 4.0)
    out["rstar_root_svv"] = float(_arr(res, "rstar")[0])
    out["rstar_root_s10"] = float(rs_p)
    out["rstar_root_s10_beta4"] = float(rs_4)
    out["root_diameter_s10"] = float(2e4 * r_p[0])
    out["root_diameter_s10_beta4"] = float(2e4 * r_4[0])
    return out
