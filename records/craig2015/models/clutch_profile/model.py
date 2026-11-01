# Steady state of the dimensionless adhesion-clutch model, Eqs. (5)-(9) of Craig et al. 2015,
# on a grid of n_segments equal segments over [0, L] (x in um, L0 = 1 um so x~ = x/um):
#   lambda V'' = T - Fmyo,   Fmyo = F dM/dx,   M = 1 - gamma d(VM)/dx,
#   Nadh = (1 + b F dM/dx) exp(-V/v*),   T = Nadh V,
# with V(0) = 1, dV/dx(L) = 0, M(0) = 0, Nadh(0) = 0 (boundary conditions, p. 5).
# Advection of myosin by the first-order upwind scheme (p. 8). The paper time-steps the PDEs to
# steady state; here the steady equations of the same discretisation are solved directly.
# Choices the paper does not state are settings: the difference used for dM/dx ("central"),
# how dV/dx(L) = 0 is discretised ("first_order": V_N = V_{N-1}; or "ghost"),
# and how the traction peak is located on the grid ("node": the grid node of largest T).
import math

import numpy as np
from scipy.optimize import root


def _fields(V, p, s):
    n = len(V) - 1
    dx = s["L"] / n
    lam, F, b, vs, g = p
    M = np.zeros(n + 1)
    for i in range(1, n + 1):  # steady upwind: 0 = 1 - M_i - g (V_i M_i - V_{i-1} M_{i-1}) / dx
        M[i] = (1.0 + g * V[i - 1] * M[i - 1] / dx) / (1.0 + g * V[i] / dx)
    dM = np.empty(n + 1)
    if s.get("dM_scheme", "central") == "central":
        dM[1:-1] = (M[2:] - M[:-2]) / (2 * dx)
        dM[0] = (M[1] - M[0]) / dx
        dM[-1] = (M[-1] - M[-2]) / dx
    else:  # backward (upwind) difference
        dM[1:] = (M[1:] - M[:-1]) / dx
        dM[0] = (M[1] - M[0]) / dx
    N = (1.0 + b * F * dM) * np.exp(-V / vs)
    N[0] = 0.0
    return M, dM, N


def _full(Vin, s):
    """Unknowns -> all nodes. neumann = "first_order": V_N = V_{N-1} (dV/dx(L) = 0 to first order);
    "ghost": V_N is unknown and a ghost node V_{N+1} = V_{N-1} closes the second difference at N."""
    if s.get("neumann", "first_order") == "first_order":
        return np.concatenate([[1.0], Vin, [Vin[-1]]])
    return np.concatenate([[1.0], Vin])


def _residual(Vin, p, s):
    V = _full(Vin, s)
    n = len(V) - 1
    dx = s["L"] / n
    lam, F = p[0], p[1]
    M, dM, N = _fields(V, p, s)
    if s.get("neumann", "first_order") == "first_order":
        lap = (V[2:] - 2 * V[1:-1] + V[:-2]) / dx ** 2
        return lam * lap - (N[1:-1] * V[1:-1] - F * dM[1:-1])
    Vp = np.concatenate([V, [V[-2]]])  # ghost node
    lap = (Vp[2:] - 2 * Vp[1:-1] + Vp[:-2]) / dx ** 2
    return lam * lap - (N[1:] * V[1:] - F * dM[1:])


def solve(p, s):
    n = int(s["n_segments"])
    x = np.linspace(0.0, s["L"], n + 1)
    lam = p[0]
    k = n - 1 if s.get("neumann", "first_order") == "first_order" else n
    guess = np.exp(-x[1:k + 1] / max(0.5, math.sqrt(lam)))
    sol = None
    tries = [(g0, m) for m in ("hybr", "lm") for g0 in (guess, np.ones(k), 0.5 * np.ones(k), 0.2 * np.ones(k))]
    for g0, method in tries:
        opts = {"xtol": 1e-12, "maxfev": 200000} if method == "hybr" else {"xtol": 1e-12, "ftol": 1e-12, "maxiter": 200000}
        sol = root(_residual, g0, args=(p, s), method=method, options=opts)
        if sol.success and np.max(np.abs(_residual(sol.x, p, s))) < 1e-8:
            break
    if sol is None or not sol.success:
        raise RuntimeError("steady state not found: " + (sol.message if sol else ""))
    V = _full(sol.x, s)
    M, dM, N = _fields(V, p, s)
    return x, V, M, N, N * V


def _params(inputs):
    return (inputs["lam"], inputs["F"], inputs["b"], inputs["vstar"], inputs["gamma"])


def run(inputs, settings):
    x, V, M, N, T = solve(_params(inputs), settings)
    xi = inputs["x"]
    return {"V": float(np.interp(xi, x, V)), "T": float(np.interp(xi, x, T))}
