# Fig. 7 middle left (p. 8): heart period change in open loop, T(Pcs) - T(P_ref), from the static
# steady state of Eqs. 31-42 (reflex_static). Ports: mmHg, s.
import importlib.util
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("_reflex_static", os.path.join(_here, "..", "reflex_static", "model.py"))
_rs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_rs)


def run(inputs, settings):
    p = inputs
    return {"dT": _rs.steady(p, p["Pcs"])["T"] - _rs.steady(p, p["P_ref"])["T"]}
