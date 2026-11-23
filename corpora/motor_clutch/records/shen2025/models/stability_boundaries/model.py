# Phase boundaries of Fig. 2 along v~u at fixed Nc: classify the eigenvalues of the Jacobian (A3, p. 14) at the
# stable fixed point (Eqs. 9-15) by Table II (p. 6), scan v~u downward from vu_max on a grid, and bisect the
# first SS -> US change (the Hopf boundary v~u0(Nc), alpha = 0, p. 11) and the first US -> U change below it.
# CORRECTED = False uses A3 exactly as printed, with J55 = -(Gamma/gamma) nc0 k~c - k~s.
import math

import numpy as np
from scipy.optimize import brentq

CORRECTED = False


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
    return nm0, brentq(g, nstar, Nc, xtol=1e-14), A


def jacobian(p, vu, corrected):
    nm, nc, A = _fixed(p)
    E = math.exp(A / (nc * p["Fb"]))
    Es = math.exp(p["fs"] / p["fd"])
    kc, km, fs, ks, G = p["kc"], p["km"], p["fs"], p["ks"], 1.0 / p["g"]  # G = Gamma/gamma
    a = p["koff"] * nc * kc / p["Fb"] * E
    j55 = -G * (nc * kc + ks) if corrected else -G * nc * kc - ks
    return np.array([
        [-p["w"] - Es, 0, 0, -nm * km / p["fd"] * Es, 0],
        [0, -p["kon"] - p["koff"] * E, -a, 0, a],
        [fs, -A / nc, -nc * kc, nm * km, nc * kc],
        [-fs, A / nc, nc * kc, -vu * km / fs - nm * km, -nc * kc],
        [0, G * A / nc, G * nc * kc, 0, j55],
    ])


def state(p, vu, corrected):
    ev = np.linalg.eigvals(jacobian(p, vu, corrected))
    cplx = np.abs(ev.imag) > 1e-10 * np.maximum(1.0, np.abs(ev))
    if cplx.any():
        return "SS" if ev.real[cplx].max() < 0 else "US"
    return "S" if ev.real.max() < 0 else "U"


def _bisect(p, hi, lo, s_hi, corrected, tol):
    while hi - lo > tol:
        mid = 0.5 * (hi + lo)
        if state(p, mid, corrected) == s_hi:
            hi = mid
        else:
            lo = mid
    return 0.5 * (hi + lo)


def run(inputs, settings):
    corrected = CORRECTED
    grid = np.linspace(float(settings["vu_max"]), float(settings["vu_min"]), int(settings["n_grid"]))
    tol = float(settings["tol"])
    states = [state(inputs, v, corrected) for v in grid]
    hopf = unst = None
    for i in range(1, len(grid)):
        if hopf is None and states[i - 1] == "SS" and states[i] == "US":
            hopf = _bisect(inputs, grid[i - 1], grid[i], "SS", corrected, tol)
        elif hopf is not None and states[i - 1] == "US" and states[i] == "U":
            unst = _bisect(inputs, grid[i - 1], grid[i], "US", corrected, tol)
            break
    if hopf is None or unst is None:
        raise ValueError(f"no SS->US->U sequence on the v~u grid: {sorted(set(states))}")
    return {"vu_hopf": hopf, "vu_unstable": unst}
