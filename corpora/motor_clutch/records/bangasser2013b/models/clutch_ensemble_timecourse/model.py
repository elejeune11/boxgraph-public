# The clutch-ensemble ODEs (Eqs. 8-12, 19) of clutch_ensemble_cycle, evaluated at a time t of the
# cycle. After the failure all quantities return to their initial values (p. 5: 'all quantities
# return to their initial values'), as the ODE lines of Figs. 2B-F and S2E are drawn.
# The integration is the same as in clutch_ensemble_cycle (copied, so this file stands alone).
import numpy as np
from scipy.integrate import LSODA


def _cycle(p, settings):
    nm, Fm, vu, nc = p["nm"], p["Fm"], p["vu"], p["nc"]
    kon, koff, Fb, kc, ks, r = p["kon"], p["koff"], p["Fb"], p["kc"], p["ks"], p["r"]
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
            return T, solver, a
    raise RuntimeError("no failure before t_max")


def run(inputs, settings):
    p = inputs
    T, _, a = _cycle(p, settings)
    t = float(p["t"])
    if t >= T:
        return {"Pb": 0.0, "xs": 0.0, "Fc": 0.0, "vf": p["vu"], "koff_mean": p["koff"]}
    # integrate again to exactly t (dense output of a fresh solve, same tolerances)
    from scipy.integrate import solve_ivp
    nm, Fm, vu, nc = p["nm"], p["Fm"], p["vu"], p["nc"]
    kon, koff, Fb, kc, ks, r = p["kon"], p["koff"], p["Fb"], p["kc"], p["ks"], p["r"]

    def koff_mean_of(Pb, xc):
        g = r * Pb * Fb - kc * (1 - a) * xc
        if Pb > 0 and g > 0:
            return (1 - Pb) * koff + Pb * koff * (r * Pb * Fb / g) ** r
        return koff

    def rhs(tt, y):
        Pb, xc = y
        vf = vu * (1 - ks * a * xc / (nm * Fm))
        return [(1 - Pb) * kon - Pb * koff_mean_of(Pb, xc), Pb * vf / (1 - (1 - Pb) * a)]

    if t <= 0:
        Pb, xc = 0.0, 0.0
    else:
        sol = solve_ivp(rhs, [0.0, t], [0.0, 0.0], method="LSODA",
                        rtol=float(settings.get("rtol", 1e-8)), atol=float(settings.get("atol", 1e-12)))
        Pb, xc = sol.y[0, -1], sol.y[1, -1]
    return {"Pb": Pb, "xs": a * xc, "Fc": kc * (1 - a) * xc,
            "vf": vu * (1 - ks * a * xc / (nm * Fm)), "koff_mean": koff_mean_of(Pb, xc)}
