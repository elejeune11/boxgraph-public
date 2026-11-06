# Artificial heart pacing (p. 7): the loop from carotid sinus pressure to heart period is cut
# and heart period is imposed; every other baroreflex mechanism works in closed loop. This
# model runs circulation_baroreflex (Eqs. 1-42) at two imposed heart rates, HR and
# HR * (1 + dHR/100), and returns the percent change in mean cardiac output between them.
import importlib.util
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "_circulation_baroreflex", os.path.join(_here, "..", "circulation_baroreflex", "model.py"))
_cb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_cb)


def run(inputs, settings):
    p = dict(inputs)
    hr = p.pop("HR")              # beats/min
    dhr = p.pop("dHR")            # percent
    hr2 = hr * (1.0 + dhr / 100.0)
    co1 = _cb.simulate(p, settings, fixed_T=60.0 / hr)["CO"]
    co2 = _cb.simulate(p, settings, fixed_T=60.0 / hr2)["CO"]
    return {"dCO": 100.0 * (co2 - co1) / co1, "CO_low": co1, "CO_high": co2}
