# The anatomic diameter, on a logarithmic grid between the settings D_lo and D_hi (um), at which
# Eqs. 8-11 give their largest effective layer thickness (the grid point itself: the peak of Eq. 9
# is a corner, so no smooth refinement is used).
import importlib.util
import math
import os

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    spec = importlib.util.spec_from_file_location(f"pries2005_{name}", os.path.join(_HERE, "..", name, "model.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_esl = _load("esl_thickness")


def run(inputs, settings):
    p = dict(inputs)
    lo, hi, n = math.log(settings["D_lo"]), math.log(settings["D_hi"]), int(settings["n"])
    best = None
    for i in range(n):
        p["D"] = math.exp(lo + (hi - lo) * i / (n - 1))
        w = _esl.thickness(p)["Weff"]
        if best is None or w > best[0]:
            best = (w, p["D"])
    return {"D_peak": best[1]}
