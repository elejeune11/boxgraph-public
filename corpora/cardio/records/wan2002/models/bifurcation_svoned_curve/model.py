# The symmetric bifurcation of Fig. 2 run with the released svOneDSolver (model bifurcation_svoned),
# returning the inlet and the two outlet flows and pressures of the last computed cycle at time t of
# the cycle, for a sweep over the time axis of Fig. 2.
import importlib.util
from pathlib import Path

_d = Path(__file__).resolve().parent.parent / "bifurcation_svoned"
_spec = importlib.util.spec_from_file_location("wan2002_bifurcation", _d / "model.py")
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)

KEYS = ("Q_in", "p_in", "Q_r", "p_r", "Q_l", "p_l")


def run(inputs, settings):
    c = base.simulate({k: v for k, v in inputs.items() if k != "t"}, settings)
    t = inputs["t"]
    if not (0.0 <= t <= c["T"] + 1e-12):
        return {k: float("nan") for k in KEYS}
    return {k: base.oned.at_phase(c[k], c["dt"], t) for k in KEYS}
