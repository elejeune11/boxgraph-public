# The bioreactor model of bioreactor_eqs5_1_15 (Eqs. 5-1 to 5-15, as printed), evaluated at an
# instant t, so that the waveforms of Figs. 5-3 to 5-6 can be compared with figure readings point
# by point. The integration is bioreactor_eqs5_1_15's own; this file only interpolates its last
# simulated cycle. The plotted times (35-38 s) lie in the converged periodic solution, so t is
# taken at its phase in the last simulated cycle: the value at t0 + ((t - t0) mod T).
# One simulation per set of inputs is kept in memory, so a sweep over t costs one simulation.
import importlib.util
import math
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "_bioreactor_eqs5_1_15", os.path.join(_here, "..", "bioreactor_eqs5_1_15", "model.py"))
_b = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_b)

OUT = ("Pct", "Qct", "l", "u", "Pcl", "Pcu", "Ps", "Qci", "Qs")


def run(inputs, settings):
    base = {k: v for k, v in inputs.items() if k != "t"}
    res = _b.last_cycle(base, settings)
    if res is None:
        return {k: float("nan") for k in OUT}
    t0, h, rows = res
    T = base["T"]
    t = float(inputs["t"])
    s = (t - t0) % T
    x = s / h
    i = min(int(math.floor(x)), len(rows) - 2)
    w = x - i
    j = {nm: k for k, nm in enumerate(_b.NAMES)}
    return {k: (1.0 - w) * rows[i][j[k]] + w * rows[i + 1][j[k]] for k in OUT}
