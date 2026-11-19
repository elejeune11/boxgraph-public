"""Shared solver: the buckled segment of an inextensible confined ring (Methods S1, Section 4, Eqs. S28-S30).

Units: R = 1, K = 1 (lengths in R, forces per length in K/R^2).
The fold axis is the y axis; the contact points sit at (+-sin a, cos a) on the unit circle and the
deepest point of the fold at (0, 1 - delta), where the tangent is horizontal (phi = 0, Eq. S29).
K phi'' = -F_B sin phi (Eq. S28), with F_B along x. At the contact point the ring joins the circle
with continuous tangent and curvature (curvature 1/R) and position (sin a, cos a) (the
self-consistency conditions stated after Eq. S30).
With the first integral (1/2) phi'^2 - F cos phi = const, the curvature at the apex follows from
F and a; F is then the root of x(S*) = sin a, S* being the first point after the inflection where
phi reaches the circle's tangent angle -a (the paper's phi(S*) = alpha, with phi measured the
other way round). The equation is integrated in the scaled arc length t = s sqrt(F).
Of the roots, the one with the largest force is taken: the single fold without loops.
"""
import functools
import math

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

RTOL = 1e-10


def _shoot(a, F):
    k0 = math.sqrt(1.0 + 2.0 * F * (1.0 - math.cos(a)))
    q = math.sqrt(F)

    def rhs(t, u):
        phi, w, x, y = u
        return [w, -math.sin(phi), math.cos(phi) / q, math.sin(phi) / q]

    def ev_end(t, u):
        return u[0] + a
    ev_end.terminal = True
    ev_end.direction = -1

    def ev_infl(t, u):
        return u[1]
    ev_infl.terminal = False
    ev_infl.direction = -1

    sol = solve_ivp(rhs, [0.0, 40.0], [0.0, k0 / q, 0.0, 0.0], events=[ev_end, ev_infl],
                    rtol=RTOL, atol=1e-12, max_step=0.02)
    if not sol.t_events[0].size:
        return None
    S = sol.t_events[0][0] / q
    xe, ye = sol.y_events[0][0][2], sol.y_events[0][0][3]
    infl = sol.y_events[1][0] if sol.y_events[1].size else None
    return S, xe, ye, infl, k0


def solve(a):
    """Opening (half) angle a in radians -> dict with F (= F_B R^2/K), delta/R, gamma, S*/R."""
    def g(F):
        r = _shoot(a, F)
        return None if r is None else r[1] - math.sin(a)

    F0 = 66.0 / a ** 2
    Fs = np.geomspace(30 * F0, F0 / 30, 60)
    prev = None
    root = None
    for F in Fs:
        v = g(F)
        if v is None:
            prev = None
            continue
        if prev is not None and np.sign(v) != np.sign(prev[1]):
            root = brentq(lambda f: g(f), F, prev[0], xtol=1e-13, rtol=1e-12)
            break
        prev = (F, v)
    if root is None:
        return None
    S, xe, ye, infl, k0 = _shoot(a, root)
    y0 = math.cos(a) - ye        # height of the apex above the centre
    delta = 1.0 - y0
    gamma = math.atan2(infl[2], y0 + infl[3]) if infl is not None else None
    return {"F": root, "delta": delta, "gamma": gamma, "S": S, "k0": k0}


def _solve_near(a, Fguess):
    """As solve, with the root bracketed near a known force (marching along a)."""
    def g(F):
        r = _shoot(a, F)
        return None if r is None else r[1] - math.sin(a)

    lo, hi = Fguess / 1.3, Fguess * 1.3
    glo, ghi = g(lo), g(hi)
    if glo is None or ghi is None or np.sign(glo) == np.sign(ghi):
        return solve(a)
    root = brentq(g, lo, hi, xtol=1e-13, rtol=1e-12)
    S, xe, ye, infl, k0 = _shoot(a, root)
    y0 = math.cos(a) - ye
    gamma = math.atan2(infl[2], y0 + infl[3]) if infl is not None else None
    return {"F": root, "delta": 1.0 - y0, "gamma": gamma, "S": S, "k0": k0}


@functools.lru_cache(maxsize=4)
def table(a_min_deg=1.0, a_max_deg=80.0, step_deg=0.5):
    """The solution along a grid of opening angles, marching from small angles (deterministic; cached
    so that the points of one sweep share it)."""
    rows = []
    F = None
    for deg in np.arange(a_min_deg, a_max_deg + 1e-9, step_deg):
        a = math.radians(deg)
        r = solve(a) if F is None else _solve_near(a, F * (deg - step_deg) ** 2 / deg ** 2)
        if r is None:
            break
        F = r["F"]
        rows.append((a, r["delta"], r["gamma"], r["F"], r["F"] * math.cos(a)))
    return np.array(rows)   # columns: a, delta/R, gamma, F_B R^2/K, P_B R^3/K


def interp(tab, xcol, ycol, x):
    """Linear interpolation of column ycol at x of column xcol (monotone in the table's range)."""
    xs, ys = tab[:, xcol], tab[:, ycol]
    if xs[0] > xs[-1]:
        xs, ys = xs[::-1], ys[::-1]
    if not (xs[0] <= x <= xs[-1]):
        return None
    return float(np.interp(x, xs, ys))
