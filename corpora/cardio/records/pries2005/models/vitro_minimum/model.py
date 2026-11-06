# The tube diameter at which Eqs. 5-7 give their smallest relative apparent viscosity, found on a
# logarithmic grid of diameters between the settings D_lo and D_hi (um), refined by a golden-section
# search around the best grid point.
import importlib.util
import math
import os

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    spec = importlib.util.spec_from_file_location(f"pries2005_{name}", os.path.join(_HERE, "..", name, "model.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_vitro = _load("vitro_viscosity")


def argmin(f, lo, hi, n):
    a, b = math.log(lo), math.log(hi)
    xs = [math.exp(a + (b - a) * i / (n - 1)) for i in range(n)]
    vals = [f(x) for x in xs]
    k = min(range(n), key=lambda i: vals[i])
    left, right = xs[max(k - 1, 0)], xs[min(k + 1, n - 1)]
    g = (math.sqrt(5) - 1) / 2
    for _ in range(100):
        c, d = right - g * (right - left), left + g * (right - left)
        if f(c) < f(d):
            right = d
        else:
            left = c
    return (left + right) / 2


def run(inputs, settings):
    HD = inputs["HD"]
    d = argmin(lambda D: _vitro.eta_vitro(D, HD), settings["D_lo"], settings["D_hi"], int(settings["n"]))
    return {"D_min": d}
