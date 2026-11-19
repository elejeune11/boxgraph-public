# The first unstable mode (p. 2, Appendix B): Eq. 1's threshold g(eta, l/a) minimized over the
# wavelength. A log-spaced grid over [la_min, la_max] locates the minimum, which is then refined
# by a bounded scalar minimization between the neighbouring grid points. When the minimum sits at
# la_min, the mode is the zero-wavelength (Biot) mode and its threshold is the l/a -> 0 limit.
# The search range and grid are the reader's numerical choices (the paper states none).
import importlib.util
import math
from pathlib import Path

import numpy as np
from scipy.optimize import minimize_scalar

_spec = importlib.util.spec_from_file_location(
    "tallinen2015_eq1_threshold", Path(__file__).resolve().parent.parent / "eq1_threshold" / "model.py")
_eq1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_eq1)


def first_mode(eta, settings):
    la_min = settings.get("la_min", 0.05)
    la_max = settings.get("la_max", 15.0)
    n = int(settings.get("n_grid", 80))
    g_max = settings.get("g_max", 4.0)
    n_scan = settings.get("n_scan", 200)

    def f(la):
        g = _eq1.threshold(eta, la, g_max, n_scan)
        return math.inf if g is None else g

    las = np.exp(np.linspace(math.log(la_min), math.log(la_max), n))
    gv = [f(la) for la in las]
    i = int(np.argmin(gv))
    if i == 0:
        return gv[0], float(las[0])
    lo, hi = float(las[i - 1]), float(las[min(i + 1, n - 1)])
    r = minimize_scalar(f, bounds=(lo, hi), method="bounded", options={"xatol": 1e-10})
    if r.fun <= gv[i]:
        return float(r.fun), float(r.x)
    return gv[i], float(las[i])


def run(inputs, settings):
    g, la = first_mode(inputs["eta"], settings)
    return {"g": g, "l_over_a": la}
