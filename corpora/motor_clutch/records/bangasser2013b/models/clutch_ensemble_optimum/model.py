# Optimum stiffness of the clutch-ensemble ODEs (Eqs. 8-12, 19): the substrate stiffness at which
# the actin flow averaged over one load-and-fail cycle is smallest (Fig. 4 legend).
# A log-spaced scan over [ks_min, ks_max] at points_per_decade, then a bounded scalar minimisation
# in log10(ks) between the scan neighbours of the smallest value.
# The cycle integration is the same as in clutch_ensemble_cycle (copied, so this file stands alone).
import numpy as np
from scipy.integrate import LSODA
from scipy.optimize import minimize_scalar


def _mean_flow(p, ks, settings):
    nm, Fm, vu, nc = p["nm"], p["Fm"], p["vu"], p["nc"]
    kon, koff, Fb, kc, r = p["kon"], p["koff"], p["Fb"], p["kc"], p["r"]
    a = kc * nc / (ks + nc * kc)

    def rhs(t, y):
        Pb, xc, _ = y
        Fc = kc * (1 - a) * xc
        vf = vu * (1 - ks * a * xc / (nm * Fm))
        g = r * Pb * Fb - Fc
        if Pb > 0 and g > 0:
            koff_mean = (1 - Pb) * koff + Pb * koff * (r * Pb * Fb / g) ** r
        else:
            koff_mean = koff
        return [(1 - Pb) * kon - Pb * koff_mean, Pb * vf / (1 - (1 - Pb) * a), vf]

    gfail = float(settings.get("g_fail", 1e-3))
    solver = LSODA(rhs, 0.0, [0.0, 0.0, 0.0], float(settings.get("t_max", 1e5)),
                   rtol=float(settings.get("rtol", 1e-8)), atol=float(settings.get("atol", 1e-12)))
    ts, ys = [0.0], [np.zeros(3)]
    risen = False
    while solver.status == "running":
        solver.step()
        ts.append(solver.t)
        ys.append(solver.y.copy())
        g = r * solver.y[0] * Fb - kc * (1 - a) * solver.y[1]
        if g > gfail:
            risen = True
        if risen and g <= gfail:
            g0 = r * ys[-2][0] * Fb - kc * (1 - a) * ys[-2][1]
            w = (g0 - gfail) / (g0 - g) if g0 != g else 1.0
            T = ts[-2] + w * (ts[-1] - ts[-2])
            disp = ys[-2][2] + w * (ys[-1][2] - ys[-2][2])
            return disp / T
    raise RuntimeError("no failure before t_max")


def run(inputs, settings):
    lo = np.log10(float(settings.get("ks_min", 0.01)))
    hi = np.log10(float(settings.get("ks_max", 1e4)))
    ppd = float(settings.get("points_per_decade", 8))
    n = int(round((hi - lo) * ppd)) + 1
    grid = np.linspace(lo, hi, n)
    v = np.array([_mean_flow(inputs, 10 ** g, settings) for g in grid])
    i = int(np.argmin(v))
    a, b = grid[max(i - 1, 0)], grid[min(i + 1, n - 1)]
    res = minimize_scalar(lambda g: _mean_flow(inputs, 10 ** g, settings), bounds=(a, b),
                          method="bounded", options={"xatol": float(settings.get("log10_xtol", 1e-4))})
    best = res.x if res.fun <= v[i] else grid[i]
    return {"ks_opt": float(10 ** best)}
