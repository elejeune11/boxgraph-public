# Modified clutch-ensemble ODEs of the Methods (Eqs. 3-12): the substrate is a spring ks along the
# clutch axis and a second spring ks of rest length l orthogonal to it (Eqs. 6-7), held at the
# initial deformation x0 by the external force F0.
#
# State: Pb and xs. <xc> follows from Eq. 8 (Eqs. 4, 5 and 7 combined), <Fc> = (Fs - F0)/nc from
# Eqs. 4-5, vf from Eq. 10 and <k*off> from Eq. 11. Eq. 12 with Eq. 8,
#   d<xc>/dt = (d<xc>/dxs) dxs/dt,  d<xc>/dxs = 1 + (dFs/dxs)/(nc kc),
#   dFs/dxs = ks (2 - l^3/(l^2 + xs^2)^(3/2))   (from Eq. 7),
# gives dxs/dt = Pb vf / (Pb + (dFs/dxs)/(nc kc)). The printed Eq. 13, which the text says is
# Eq. 12 combined with Eqs. 8 and 10, cannot be integrated as printed (q_eq13); this is that
# combination worked out from Eqs. 8, 10 and 12.
# Start: xs = x0 (the substrate at the imposed deformation), which by Eq. 8 gives <xc> = x0 and a
# null clutch force, as Appendix 1 states for the canonical form; Pb(0) = 0 (q_initial_state).
# The cycle ends at the abrupt failure, where r Pb Fb - <Fc> first falls to g_fail after rising.
#
# Numerics: the state is integrated as u = xs - x0, and Fs - F0 is evaluated in a form free of
# cancellation (the same quantity), so a large x0 costs no digits. Units: pN, nm, s.
import math

import numpy as np
from scipy.integrate import LSODA


def _h_diff(a, b, l):
    """a/sqrt(l^2 + a^2) - b/sqrt(l^2 + b^2), without cancellation when a and b are close."""
    A, B = math.sqrt(l * l + a * a), math.sqrt(l * l + b * b)
    den = a * B + b * A
    if a > 0 and b > 0 and den > 0:
        return l * l * (a - b) * (a + b) / (den * A * B)
    return a / A - b / B


def _force(u, x0, ks, l):
    """Fs - F0 (Eqs. 6, 7; the bracket of Eq. 10), at xs = x0 + u."""
    return ks * (2 * u - l * _h_diff(x0 + u, x0, l))


def _cycle(p, settings):
    nm, Fm, vu, nc = p["nm"], p["Fm"], p["vu"], p["nc"]
    kon, koff, Fb, kc, ks, r = p["kon"], p["koff"], p["Fb"], p["kc"], p["ks"], p["r"]
    x0, l = p["x0"], p["l"]

    def rhs(t, s):
        Pb, u, _ = s
        dF = _force(u, x0, ks, l)
        fc = dF / nc                                             # Eqs. 4-5
        vf = vu * (1 - dF / (nm * Fm))                           # Eq. 10
        g = r * Pb * Fb - fc
        if Pb > 0 and g > 0:
            koff_mean = (1 - Pb) * koff + Pb * koff * (r * Pb * Fb / g) ** r     # Eq. 11
        else:
            koff_mean = koff
        xs = x0 + u
        dFs = ks * (2 - l ** 3 / (l * l + xs * xs) ** 1.5)       # dFs/dxs from Eq. 7
        du = Pb * vf / (Pb + dFs / (nc * kc))                    # Eq. 12 with Eq. 8
        return [(1 - Pb) * kon - Pb * koff_mean, du, vf]

    def gap(s):
        return r * s[0] * Fb - _force(s[1], x0, ks, l) / nc

    gfail = float(settings.get("g_fail", 1e-3))
    solver = LSODA(rhs, 0.0, [0.0, 0.0, 0.0], float(settings.get("t_max", 1e5)),
                   rtol=float(settings.get("rtol", 1e-8)), atol=float(settings.get("atol", 1e-12)))
    ts, ys = [0.0], [np.zeros(3)]
    risen = False
    while solver.status == "running":
        solver.step()
        ts.append(solver.t)
        ys.append(solver.y.copy())
        g = gap(solver.y)
        if g > gfail:
            risen = True
        if risen and g <= gfail:
            g0 = gap(ys[-2])
            w = (g0 - gfail) / (g0 - g) if g0 != g else 1.0
            T = ts[-2] + w * (ts[-1] - ts[-2])
            disp = ys[-2][2] + w * (ys[-1][2] - ys[-2][2])
            return T, disp
    return None, None                                            # no failure before t_max


def run(inputs, settings):
    T, disp = _cycle(inputs, settings)
    if T is None:
        return {"t_cycle": None, "v_mean": None}
    return {"t_cycle": float(T), "v_mean": float(disp / T)}
