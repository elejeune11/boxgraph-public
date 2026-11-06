# Optimal substrate stiffness of the code's model: the stiffness at which the mean retrograde flow
# (retro, motorclutch2_3.m line 144) is least. The code sweeps stiffness=logspace(-2,2,10) (line 27)
# and plots retro against it (line 159) but does not locate the minimum; locating it is ours: the
# least grid point and a parabola in log10(stiffness) through it and its two neighbours.
import importlib.util
import math
import os

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    spec = importlib.util.spec_from_file_location(f"odde_code_{name}", os.path.join(_HERE, "..", name, "model.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_mc = _load("mc_event_port")


def grid(settings):
    lo, hi = math.log10(settings["ksub_min"]), math.log10(settings["ksub_max"])
    n = int(settings["n_points"])
    return [10 ** (lo + (hi - lo) * j / (n - 1)) for j in range(n)]   # MATLAB logspace(lo, hi, n)


def run(inputs, settings):
    ks = grid(settings)
    sim = {"events": settings["events"], "seed": settings["seed"]}
    v = [_mc.run({**inputs, "Ksub": k}, sim)["v_retro"] for k in ks]
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
