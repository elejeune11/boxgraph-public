# The paper says (p. 9) that the average (DC) root impedance Z(0, 0) of a structured tree is
# "approximately inversely proportional to the root radius to the third power". This gives the
# power p of a two-point log-log slope of Z(0, 0) between two root radii, with Z(0, 0) from the
# tree of structured_tree_impedance at omega = 0 (Eq. 18 per vessel, Eq. 17 at bifurcations).
import importlib.util
import math
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "_structured_tree_impedance", os.path.join(_here, "..", "structured_tree_impedance", "model.py"))
_t = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_t)


def run(inputs, settings):
    common = {k: inputs[k] for k in ("r_min", "lrr", "xi", "gamma", "k1", "k2", "k3", "nu", "rho")}
    z_lo = _t.run(dict(common, r_root=inputs["r_lo"], omega=0.0), {})["Zmod"]
    z_hi = _t.run(dict(common, r_root=inputs["r_hi"], omega=0.0), {})["Zmod"]
    return {"p": math.log(z_lo / z_hi) / math.log(inputs["r_hi"] / inputs["r_lo"])}
