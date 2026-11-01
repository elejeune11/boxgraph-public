# Optimal substrate stiffness ks,opt: the substrate spring constant at which the time-averaged
# F-actin retrograde flow of the motor-clutch model is minimal (equivalently, traction maximal).
# Built from motor_clutch_ssa: the same simulation on a log-spaced grid of substrate stiffness;
# the minimum is located by a parabola in log10(ksub) through the lowest grid point and its
# two neighbours.
import importlib.util
import math
import os

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    spec = importlib.util.spec_from_file_location(f"bangasser2013_{name}", os.path.join(_HERE, "..", name, "model.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_mc = _load("motor_clutch_ssa")


def grid(settings):
    lo, hi = math.log10(settings["ksub_min"]), math.log10(settings["ksub_max"])
    n = int(round((hi - lo) * settings["per_decade"])) + 1
    return [10 ** (lo + (hi - lo) * j / (n - 1)) for j in range(n)]


def run(inputs, settings):
    ks = grid(settings)
    sim = {"t_total": settings["t_total"], "seed": settings["seed"]}
    v = [_mc.simulate({**inputs, "ksub": k}, sim)["v_retro"] for k in ks]
    j = min(range(len(v)), key=lambda i: v[i])
    lx = [math.log10(k) for k in ks]
    if 0 < j < len(v) - 1:
        y0, y1, y2 = v[j - 1], v[j], v[j + 1]
        den = y0 - 2 * y1 + y2
        h = lx[j + 1] - lx[j]
        shift = 0.5 * (y0 - y2) / den * h if den > 0 else 0.0
        x = lx[j] + max(-h, min(h, shift))
    else:
        x = lx[j]
    return {"ks_opt": 10 ** x, "v_min": float(v[j])}
