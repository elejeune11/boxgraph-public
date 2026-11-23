# Stiffness of the flow minimum and of the traction maximum of one module, from module_ssa on a
# log-spaced κs grid; each extremum located by a parabola in log10 κs through the extreme grid
# point and its neighbours (clipped to one grid step).
import importlib.util
import math
import os

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    spec = importlib.util.spec_from_file_location(f"bangasser2017_{name}", os.path.join(_HERE, "..", name, "model.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_mod = _load("module_ssa")


def grid(settings):
    lo, hi = math.log10(settings["ks_min"]), math.log10(settings["ks_max"])
    n = int(round((hi - lo) * settings["per_decade"])) + 1
    return [10 ** (lo + (hi - lo) * j / (n - 1)) for j in range(n)]


def _extremum(lx, y, sign):
    """sign=+1: minimum; sign=-1: maximum. Returns log10 location."""
    z = [sign * v for v in y]
    j = min(range(len(z)), key=lambda i: z[i])
    if 0 < j < len(z) - 1:
        y0, y1, y2 = z[j - 1], z[j], z[j + 1]
        den = y0 - 2 * y1 + y2
        h = lx[j + 1] - lx[j]
        shift = 0.5 * (y0 - y2) / den * h if den > 0 else 0.0
        return lx[j] + max(-h, min(h, shift)), j
    return lx[j], j


def run(inputs, settings):
    ks = grid(settings)
    sim = {"t_total": settings["t_total"], "seed": settings["seed"]}
    out = [_mod.simulate({**inputs, "ks": k}, sim) for k in ks]
    v = [o["v_flow"] for o in out]
    F = [o["F_trac"] for o in out]
    lx = [math.log10(k) for k in ks]
    xv, jv = _extremum(lx, v, +1)
    xf, jf = _extremum(lx, F, -1)
    return {"ks_flow_min": 10 ** xv, "ks_trac_max": 10 ** xf, "v_min": float(v[jv]), "F_max": float(F[jf])}
