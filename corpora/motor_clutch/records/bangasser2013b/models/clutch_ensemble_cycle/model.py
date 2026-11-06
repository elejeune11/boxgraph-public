# Clutch-ensemble ODEs of Bangasser and Odde 2013 (Eqs. 8-12 with the mean off-rate of Eq. 19),
# integrated over one load-and-fail cycle from the unloaded, unbound state.
#
# State: Pb (fraction bound) and <xc> (mean clutch end position, nm). <xs> follows from Eq. 10,
# <Fc> from Eq. 9 and <vf> from Eq. 11. Eq. 12 with d<xs>/dt = a d<xc>/dt, a = kc nc/(ks + nc kc),
# gives d<xc>/dt = Pb <vf> / (1 - (1 - Pb) a).
# Eq. 19: <k*off> = (1 - Pb) koff + Pb koff (1 - <Fc>/(r Pb Fb))^(-r), written here as
# Pb koff (r Pb Fb / g)^r with g = r Pb Fb - <Fc>.
# The cycle fails when g reaches zero (<k*off> diverges and Pb collapses, Figs. 2B, 2F); the
# failure time is taken where g first falls to the setting g_fail (pN) after it has risen above it.
# Units: forces pN, lengths nm, times s, stiffnesses pN/nm, velocities nm/s.
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
            disp = ys[-2][2] + w * (ys[-1][2] - ys[-2][2])
            return T, disp, np.array(ts[:-1] + [T]), np.array(ys[:-1] + [ys[-2] + w * (ys[-1] - ys[-2])]), a
    raise RuntimeError("no failure before t_max")


def run(inputs, settings):
    T, disp, _, _, _ = _cycle(inputs, settings)
    return {"t_cycle": T, "v_mean": disp / T}
