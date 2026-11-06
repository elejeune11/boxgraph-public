# Fig. 6 (p. 7): artificial pacing. circulation_baroreflex (Eqs. 1-42) is run with the heart period
# imposed at 60/HR, every other mechanism in closed loop; SV is mean cardiac output times the period.
import importlib.util
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "_circulation_baroreflex", os.path.join(_here, "..", "circulation_baroreflex", "model.py"))
_cb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_cb)


def run(inputs, settings):
    p = dict(inputs)
    T = 60.0 / p.pop("HR")
    co = _cb.simulate(p, settings, fixed_T=T)["CO"]
    return {"CO": co, "SV": co * T}
