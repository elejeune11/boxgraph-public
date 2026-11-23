"""Python port (our code) of the steady state of the talin WT model, talin_WT_model.m.

Ported, in the order of the MATLAB files:
  talin_WT_model.m lines 21-24     v grid: 100 points, 1 to 300 nm/s, geometric
                   lines 48-52     k's = E (4 pi / 9) a_1 1e-9 1000
                   lines 54-58     Nm, Nc; Fm = Fst Nm (1 - v/v0), floored at -0.5 pN
                   lines 69-73     two states: row 1 = bitget(1,1) = 1 (R3 unfolded), row 2 = folded
                   lines 75-81     kT = 1.38e-23 * 310 / 1e-21; Fu = kT / x_u; dG0 = kT ln(kf0 / ku0)
                   lines 254-258   extension grid 0 : v/200 : min(1000, 150 + sqrt(1e4 / k's), 20 v)
                   lines 263-265   p_on(0) = Boltzmann weights exp(-G(0)/kT), normalised
                   lines 267-340   the Runge-Kutta march in l (step 2h on the grid of step h),
                                   rates capped at 100 /s, stop when sum(p_on) < 1e-6
                   lines 345-357   C = kon / (kon sum(p) 2h + v); Nc_total = Nc / max(1 - alpha I_C, 0.01);
                                   Fc = Nc_total sum(F p) 2h
                   line 471        zero contour of Fc - Fm (here along v at the requested E)
                   lines 483-486   P = Fm(v*) / (pi a_2^2), floored at 0
                   lines 537-648   at v*: engaged clutches and mean tension per state
  tabulate_clutch_force_and_energy.m lines 7-19   force tables per state, csaps smoothing (p = 0.1),
                                   capped at 100 pN from the first point above 100; G = cumsum(F) h + state dG0
  force_vs_extension_clutch_v2.m lines 19-44      FJC of (Ng + 3 state + 0) rigid domains of size b in series
                                   with a WLC linker of contour L and the substrate spring k's; force
                                   100 pN beyond 0.9999 (L + N b) + 100 / k's; otherwise the grid force
                                   (1e-6 : 0.001 : 300 pN) minimising |zero_delta_force_function|
  zero_delta_force_function.m lines 12-21

Departures (needed to run here, none changes the model):
  * the grid force is found by bisection on the (monotonic) error function and then the nearer of
    the two neighbouring grid forces is taken by the same |error| criterion: the same grid point as
    MATLAB's brute-force min over 300000 forces, except at exact ties;
  * MATLAB's csaps(x, y, p) is scipy's make_smoothing_spline(x, y, lam = (1 - p) / p), the same
    objective p sum (y - f)^2 + (1 - p) int f''^2 up to the factor 1/p;
  * the contour is taken along v at the requested E (no E grid); an E outside [E_min, E_max] gives NaN;
  * in lines 537-648 MATLAB's parfor reuses p_0_on from the last pass of the main loop; here it is
    computed for v* itself (it differs only through F(0) h, which is below 1e-3 pN nm).
"""
import math

import numpy as np
from scipy.interpolate import make_smoothing_spline

F_GRID_START, F_GRID_STEP, F_GRID_END = 1e-6, 0.001, 300.0
N_F_GRID = int(math.floor((F_GRID_END - F_GRID_START) / F_GRID_STEP + 1e-9)) + 1


def delta_force(F, x, ks, n_rigid, b, L, kT, Lp):
    """zero_delta_force_function.m, vectorised over F (and x of the same shape)."""
    z = b * F / kT
    ext_fjc = n_rigid * b * (1.0 / np.tanh(z) - 1.0 / z)
    delta = x - ext_fjc - F / ks
    r = np.abs(delta) / L
    with np.errstate(divide="ignore", invalid="ignore"):
        f_wlc = kT / Lp * np.sign(delta) * (r + 0.25 / (1 - r) ** 2 - 0.25)
    err = np.where(r < 0.9999, F - f_wlc, 10000.0)
    return err, delta, r


def force_vs_extension(ks, x, state, p):
    """force_vs_extension_clutch_v2.m for one state, x a 1-d array of extensions."""
    L = p["L"]
    n_rigid = p["Ng"] + 3 * state + p["N_integrin"]
    kT, Lp, b = p["kT"], p["Lp"], p["b"]
    force = np.empty_like(x)
    big = x > 0.9999 * (L + n_rigid * b) + 100.0 / ks
    force[big] = 100.0
    xs = x[~big]
    if xs.size:
        # monotone surrogate of the error: -inf where delta > 0.9999 L, +inf where delta < -0.9999 L
        def g(F):
            err, delta, r = delta_force(F, xs, ks, n_rigid, b, L, kT, Lp)
            return np.where(r < 0.9999, err, np.where(delta > 0, -np.inf, np.inf))
        lo = np.full(xs.shape, F_GRID_START)
        hi = np.full(xs.shape, F_GRID_START + (N_F_GRID - 1) * F_GRID_STEP)
        for _ in range(70):
            mid = 0.5 * (lo + hi)
            pos = g(mid) > 0
            hi = np.where(pos, mid, hi)
            lo = np.where(pos, lo, mid)
        n0 = np.clip(np.floor((lo - F_GRID_START) / F_GRID_STEP).astype(int), 0, N_F_GRID - 1)
        best_n = n0.copy()
        best_e = np.full(xs.shape, np.inf)
        for dn in (-1, 0, 1, 2):  # neighbours of the root on the grid; first minimum wins, as MATLAB's min
            n = np.clip(n0 + dn, 0, N_F_GRID - 1)
            e = np.abs(delta_force(F_GRID_START + n * F_GRID_STEP, xs, ks, n_rigid, b, L, kT, Lp)[0])
            better = (e < best_e) | ((e == best_e) & (n < best_n))
            best_n = np.where(better, n, best_n)
            best_e = np.where(better, e, best_e)
        force[~big] = F_GRID_START + best_n * F_GRID_STEP
    return force


def tabulate(ks, x, p):
    """tabulate_clutch_force_and_energy.m: rows 0 (state 1, unfolded) and 1 (state 0, folded)."""
    states = [1, 0]  # bitget(i, 1) for i = 1, 2
    forces = np.empty((2, x.size))
    for i, st in enumerate(states):
        raw = force_vs_extension(ks, x, st, p)
        lam = (1 - p["csaps_p"]) / p["csaps_p"]
        sm = make_smoothing_spline(x, raw, lam=lam)(x)
        above = np.nonzero(sm > 100)[0]
        if above.size:
            sm[above[0]:] = 100.0
        forces[i] = sm
    h = x[1] - x[0]
    G = np.cumsum(forces, axis=1) * h + np.array([[st * p["dG0"]] for st in states])
    return forces, G


def clutch_state(E, v, p, settings):
    """Lines 254-357 for one (E, v): returns Fc, engaged numbers and mean forces per state."""
    ks = E * (4 * math.pi / 9 * p["a_1"] * 1e-9 * 1000)
    lmax = min(1000.0, 150.0 + math.sqrt(10000.0 / ks), 20.0 * v)
    h = v / settings.get("ext_per_v", 200)
    n = int(math.floor(lmax / h * (1 + 1e-12))) + 1
    x = np.arange(n) * h
    F, G = tabulate(ks, x, p)
    p0 = np.exp(-G[:, 0] / p["kT"])
    p0 = p0 / p0.sum()
    kT = p["kT"]
    koff = p["k_off_1"] * np.exp(F / p["F_d_1"]) + p["k_off_2"] * np.exp(F / p["F_d_2"])
    koff = np.minimum(koff, 100.0)
    kun = np.minimum(p["ku0"] * np.exp(F[1] / p["Fu"]), 100.0)
    kre = kun * np.exp((G[0] - G[1]) / kT)
    N = (n - 1) // 2
    pu = np.zeros(N + 1)
    pf = np.zeros(N + 1)
    pu[0], pf[0] = p0
    a11 = (-koff[0] - kre) / v  # unfolded leaves by refolding
    a22 = (-koff[1] - kun) / v
    a12 = kun / v
    a21 = kre / v
    for k in range(N):  # k here is MATLAB's k - 1
        i0, i1, i2 = 2 * k, 2 * k + 1, 2 * k + 2
        u, f = pu[k], pf[k]
        k1u = a11[i0] * u + a12[i0] * f
        k1f = a21[i0] * u + a22[i0] * f
        uu, ff = u + h * k1u, f + h * k1f
        k2u = a11[i1] * uu + a12[i1] * ff
        k2f = a21[i1] * uu + a22[i1] * ff
        uu, ff = u + h * k2u, f + h * k2f
        k3u = a11[i1] * uu + a12[i1] * ff
        k3f = a21[i1] * uu + a22[i1] * ff
        uu, ff = u + 2 * h * k3u, f + 2 * h * k3f
        k4u = a11[i2] * uu + a12[i2] * ff
        k4f = a21[i2] * uu + a22[i2] * ff
        pu[k + 1] = u + h / 3 * (k1u + 2 * k2u + 2 * k3u + k4u)
        pf[k + 1] = f + h / 3 * (k1f + 2 * k2f + 2 * k3f + k4f)
        if pu[k + 1] + pf[k + 1] < 1e-6:
            break
    I = p["kon"] * (pu[:N].sum() + pf[:N].sum()) * 2 * h + v
    C = p["kon"] / I
    pu, pf = C * pu, C * pf
    I_C = pu[:N].sum() * 2 * h
    denom = 1 - p["alpha"] * I_C
    if denom < 0.01:
        denom = 0.01
    Nc = math.pi * p["a_2"] ** 2 / 1e6 * p["sigma_c"]
    Nct = Nc / denom
    Fo = F[:, 0:2 * N - 1:2]
    Mu = (Fo[0] * pu[:N]).sum() * 2 * h
    Mf = (Fo[1] * pf[:N]).sum() * 2 * h
    Fc = Nct * (Mu + Mf)
    Non_u = Nct * pu[:N].sum() * 2 * h
    Non_f = Nct * pf[:N].sum() * 2 * h
    return {"Fc": Fc, "Non_u": Non_u, "Non_f": Non_f,
            "F_u": Nct * Mu / Non_u if Non_u > 0 else float("nan"),
            "F_f": Nct * Mf / Non_f if Non_f > 0 else float("nan"),
            "denominator": denom}


def params(inputs):
    p = dict(inputs)
    p["kT"] = p["kB"] * p["T"] / 1e-21  # line 75: pN nm
    p["Fu"] = p["kT"] / p["x_u"]  # line 79
    p["dG0"] = p["kT"] * math.log(p["kf0"] / p["ku0"])  # line 81
    return p


def v_grid(settings):
    n = int(settings.get("n_steps", 100))
    return settings.get("v_min", 1.0) * np.exp(np.arange(n) * math.log(settings.get("v_span", 300.0)) / (n - 1))


def roots(v_actin, g):
    out = []
    x = np.log10(v_actin)
    for i in range(len(g) - 1):
        if g[i] * g[i + 1] < 0:
            t = g[i] / (g[i] - g[i + 1])
            out.append({"v": float(10 ** (x[i] + t * (x[i + 1] - x[i]))), "stable": bool(g[i + 1] > g[i])})
    return out


def run(inputs, settings):
    p = params(inputs)
    settings = dict(settings)
    settings.setdefault("csaps_p", 0.1)
    p["csaps_p"] = settings["csaps_p"]
    E = p["E"]
    nan = float("nan")
    empty = {k: nan for k in ("P", "v", "F_f", "F_u", "n_f", "n_u", "unfolded_pct")}
    if not (settings.get("E_min", 1e2) <= E <= settings.get("E_max", 1e6)):
        return empty
    va = v_grid(settings)
    Nm = math.pi * p["a_2"] ** 2 / 1e6 * p["sigma_m"]
    Fm = np.maximum(p["Fst"] * Nm * (1 - va / p["v0"]), -0.5)
    Fc = np.array([clutch_state(E, v, p, settings)["Fc"] for v in va])
    rs = [r for r in roots(va, Fc - Fm) if r["stable"]]
    if not rs:
        return empty
    v = min(rs, key=lambda r: r["v"])["v"] if settings.get("branch", "strong") == "strong" else max(rs, key=lambda r: r["v"])["v"]
    P = max((1 - v / p["v0"]) * p["Fst"] * Nm, 0.0) * 1e-12 / math.pi / (p["a_2"] * 1e-9) ** 2
    s = clutch_state(E, v, p, settings)
    area = math.pi * p["a_2"] ** 2 / 1e6
    return {"P": float(P), "v": float(v), "F_f": float(s["F_f"]), "F_u": float(s["F_u"]),
            "n_f": float(s["Non_f"] / area), "n_u": float(s["Non_u"] / area),
            "unfolded_pct": float(100 * s["Non_u"] / (s["Non_u"] + s["Non_f"]))}
