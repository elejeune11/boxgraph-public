"""Python port (our code) of the linear KD / linear WT steady state of Linear_KD_WT_model.m.

Ported, in the order of the MATLAB file:
  lines 32-35, 54   the substrate spring k's = E (4 pi / 9) a_1 1e-9 1000   [pN/nm from Pa, nm]
  lines 49-50       Nm = pi a_2^2 / 1e6 sigma_m, Nc = pi a_2^2 / 1e6 sigma_c
  line 52           k = k's kc / (k's + kc)
  lines 56-57       Fm = Fst Nm (1 - v / v0), floored at -1000 pN
  lines 164-188     per (E, v): C = kon / (kon int_0^inf exp(-I(x)/v) dx + v),
                    Fc = Nc int_0^inf F(x) C exp(-I(x)/v) dx
  force_with_yield_point.m       F(x) = k x for |x| <= l_yield, k l_yield sign(x) beyond
  k_off_integral_catch_bond_v4c.m I(x) = a1 (e^{k x/Fd1} - 1) + a2 (e^{k x/Fd2} - 1) for x <= l_yield,
                    a_i = k_off_i Fd_i / k, continued linearly with slope k_off(l_yield) beyond
  line 296 (contour) the zero contour of Fc - Fm on the code's (log10 v, log10 E) grid
  lines 309-312     traction P = Fm(v*) 1e-12 / pi / (a_2 1e-9)^2 at the contour flow v*, floored at 0
  lines 357-381, 402-403  mean tension of an engaged clutch and density of engaged clutches at v*

Two departures, both needed to evaluate the code's curves at the E of a printed figure reading:
  * the contour is taken along v at the requested E itself (the code's 100-point v grid,
    linear interpolation in log10 v as MATLAB's contour does on a grid edge), not on the code's
    100-point E grid; an E outside the code's range [Young_modulus_min, Young_modulus_max] gives NaN;
  * MATLAB's adaptive integral(f, 0, Inf) is replaced by scipy quad on [0, l_yield] plus the exact
    tail beyond l_yield (where I(x) is linear), at a relative tolerance of 1e-10.
"""
import math

import numpy as np
from scipy.integrate import quad


def k_off_integral(x, l_yield, k, k_off_1, k_off_2, F_d_1, F_d_2):
    # k_off_integral_catch_bond_v4c.m lines 5-15
    a_1 = k_off_1 * F_d_1 / k
    a_2 = k_off_2 * F_d_2 / k
    if x <= l_yield:
        return a_1 * (math.exp(k * x / F_d_1) - 1) + a_2 * (math.exp(k * x / F_d_2) - 1)
    k_off_y = k_off_1 * math.exp(k * l_yield / F_d_1) + k_off_2 * math.exp(k * l_yield / F_d_2)
    return (a_1 * (math.exp(k * l_yield / F_d_1) - 1) + a_2 * (math.exp(k * l_yield / F_d_2) - 1)
            + k_off_y * (x - l_yield))


def force_with_yield_point(x, l_yield, k):
    # force_with_yield_point.m lines 5-11
    return k * x if abs(x) <= l_yield else k * l_yield * math.copysign(1.0, x)


def clutch_integrals(v, k, p):
    """int exp(-I/v) dx and int F exp(-I/v) dx over [0, inf)."""
    ly = p["l_yield"]
    args = (ly, k, p["k_off_1"], p["k_off_2"], p["F_d_1"], p["F_d_2"])

    def s(x):
        return math.exp(-k_off_integral(x, *args) / v)

    # break [0, ly] where exp(-I/v) changes fastest: near 0 its scale is v / k_off(0)
    k0 = p["k_off_1"] + p["k_off_2"]
    pts = sorted({min(ly, v / k0 * m) for m in (1, 10, 100)} - {ly})
    edges = [0.0] + pts + [ly]
    Z = M = 0.0
    for a, b in zip(edges[:-1], edges[1:]):
        Z += quad(s, a, b, epsabs=0.0, epsrel=1e-10, limit=500)[0]
        M += quad(lambda x: force_with_yield_point(x, ly, k) * s(x), a, b, epsabs=0.0, epsrel=1e-10, limit=500)[0]
    # beyond ly: I(x) = I(ly) + k_off_y (x - ly), F = k ly
    k_off_y = p["k_off_1"] * math.exp(k * ly / p["F_d_1"]) + p["k_off_2"] * math.exp(k * ly / p["F_d_2"])
    tail = s(ly) * v / k_off_y
    return Z + tail, M + k * ly * tail


def code_grid(p, settings):
    n = int(settings.get("n_steps", 100))
    index = np.arange(n)
    v_actin = settings.get("v_min", 0.1) * np.exp(index * math.log(settings.get("v_span", 3000.0)) / (n - 1))
    return v_actin


def steady_curve(p, settings, E):
    """Fc - Fm on the code's v grid at Young's modulus E, and the clutch integrals there."""
    geo = 4 * math.pi / 9 * p["a_1"] * 1e-9 * 1000  # lines 32-33, 54
    ks = E * geo
    k = ks * p["kc"] / (ks + p["kc"])  # line 52
    Nm = math.pi * p["a_2"] ** 2 / 1e6 * p["sigma_m"]  # line 49
    Nc = math.pi * p["a_2"] ** 2 / 1e6 * p["sigma_c"]  # line 50
    v_actin = code_grid(p, settings)
    Fm = p["Fst"] * Nm * (1 - v_actin / p["v0"])  # line 56
    Fm = np.maximum(Fm, -1000.0)  # line 57
    Fc = np.empty_like(v_actin)
    for j, v in enumerate(v_actin):  # lines 170-187
        Z, M = clutch_integrals(v, k, p)
        C = p["kon"] / (p["kon"] * Z + v)
        Fc[j] = Nc * C * M
    return v_actin, Fc, Fm, k, Nm, Nc


def roots(v_actin, g):
    """Zero crossings of g along the grid, linear in log10 v (MATLAB contour on one grid line).
    Stable when g rises through zero (the clutches outpull the motors above the root)."""
    out = []
    x = np.log10(v_actin)
    for i in range(len(g) - 1):
        if g[i] == 0.0:
            out.append({"v": float(v_actin[i]), "stable": bool(g[i + 1] > 0)})
        elif g[i] * g[i + 1] < 0:
            t = g[i] / (g[i] - g[i + 1])
            out.append({"v": float(10 ** (x[i] + t * (x[i + 1] - x[i]))), "stable": bool(g[i + 1] > g[i])})
    return out


def pick(rs, branch):
    if branch == "unstable":
        un = [r for r in rs if not r["stable"]]
        return un[0] if len(rs) == 3 and un else None
    st = [r for r in rs if r["stable"]]
    if not st:
        return None
    return min(st, key=lambda r: r["v"]) if branch == "strong" else max(st, key=lambda r: r["v"])


def run(inputs, settings):
    p = dict(inputs)
    E = p["E"]
    nan = float("nan")
    empty = {"P": nan, "v": nan, "F1": nan, "n_on": nan}
    if not (settings.get("E_min", 1e2) <= E <= settings.get("E_max", 1e10)):
        return empty
    v_actin, Fc, Fm, k, Nm, Nc = steady_curve(p, settings, E)
    r = pick(roots(v_actin, Fc - Fm), settings.get("branch", "strong"))
    if r is None:
        return empty
    v = r["v"]
    z = (1 - v / p["v0"]) * p["Fst"] * Nm  # line 309
    P = max(z, 0.0) * 1e-12 / math.pi / (p["a_2"] * 1e-9) ** 2  # lines 311-312
    Z, M = clutch_integrals(v, k, p)  # lines 363-381
    C = p["kon"] / (p["kon"] * Z + v)
    p_on = C * Z
    F1 = C * M / p_on
    n_on = Nc * p_on / (math.pi * p["a_2"] ** 2) * 1e6  # lines 402-403
    return {"P": float(P), "v": float(v), "F1": float(F1), "n_on": float(n_on)}
