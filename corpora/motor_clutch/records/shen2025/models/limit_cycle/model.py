# Limit cycle of the dimensionless system Eq. 6 (p. 4) in the US region (Sec. III E, Fig. 11).
# Start at the stable-branch fixed point (Eqs. 9-15) with nc raised by the fraction `perturb`, integrate with
# LSODA to t_transient + t_window (dimensionless time), and on the window [t_transient, end], sampled at
# n_samples points of the dense output:
#   period: mean spacing of the upward crossings of y~ through its fixed-point value y~0;
#   frequency in Hz = 1/(period * tau), tau the characteristic time in s;
#   amplitude of y~ = (max - min)/2 over the window (the paper does not define its amplitude: q_amplitude_def).
import math

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq


def _fixed(p):
    nm0 = p["w"] * p["Nm"] / (p["w"] + math.exp(p["fs"] / p["fd"]))
    A = nm0 * p["fs"] - p["F"]
    if A <= 0:
        raise ValueError("nm0 fs - F <= 0: only the trivial fixed point")
    a, r, Nc = A / p["Fb"], p["koff"] / p["kon"], p["Nc"]
    nstar = brentq(lambda n: 1 + r * math.exp(min(a / n, 700.0)) * (1 - a / n), a / 700.0, a, xtol=1e-14)
    g = lambda n: n + r * n * math.exp(min(a / n, 700.0)) - Nc  # noqa: E731
    if g(nstar) > 0:
        raise ValueError("Nc < Nc,min: no fixed point (region N)")
    nc0 = brentq(g, nstar, Nc, xtol=1e-14)
    xs0 = A / p["ks"]
    return [nm0, nc0, xs0 + A / (nc0 * p["kc"]), p["fs"] / p["km"], xs0]


def run(inputs, settings):
    p = inputs

    def rhs(t, s):
        nm, nc, xo, y, xs = s
        xc = xo - xs
        f3 = nm * p["km"] * y - nc * p["kc"] * xc - p["F"]
        return [p["w"] * (p["Nm"] - nm) - nm * math.exp(min(p["km"] * y / p["fd"], 700.0)),
                p["kon"] * (p["Nc"] - nc) - p["koff"] * nc * math.exp(min(p["kc"] * xc / p["Fb"], 700.0)),
                f3,
                p["vu"] * (1 - p["km"] * y / p["fs"]) - f3,
                (nc * p["kc"] * xc - p["ks"] * xs) / p["g"]]

    s0 = _fixed(p)
    y0 = s0[3]
    s0[1] *= 1.0 + float(settings["perturb"])
    t1, tw = float(settings["t_transient"]), float(settings["t_window"])
    sol = solve_ivp(rhs, (0.0, t1 + tw), s0, method="LSODA", rtol=float(settings["rtol"]),
                    atol=float(settings["atol"]), dense_output=True)
    if not sol.success:
        raise RuntimeError(sol.message)
    t = np.linspace(t1, t1 + tw, int(settings["n_samples"]))
    y = sol.sol(t)[3]
    up = np.where((y[:-1] < y0) & (y[1:] >= y0))[0]
    if len(up) < 3:
        raise ValueError("no sustained oscillation in the window (not in the US region?)")
    # linear interpolation of the crossing times
    tc = t[up] + (y0 - y[up]) / (y[up + 1] - y[up]) * (t[up + 1] - t[up])
    period = float(np.mean(np.diff(tc)))
    return {"freq": 1.0 / (period * p["tau"]), "amp": float(y.max() - y.min()) / 2.0}
