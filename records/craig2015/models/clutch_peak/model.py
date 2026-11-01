# Traction peak of the steady state of Eqs. (5)-(9): its distance from the leading edge and the
# actin flow speed there in units of v*. Uses the solver of the clutch_profile model (built_from).
import importlib.util
from pathlib import Path

import numpy as np

_spec = importlib.util.spec_from_file_location(
    "craig2015_clutch_profile", Path(__file__).resolve().parent.parent / "clutch_profile" / "model.py")
_prof = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_prof)


def run(inputs, settings):
    x, V, M, N, T = _prof.solve(_prof._params(inputs), settings)
    i = int(np.argmax(T))
    if settings.get("peak", "node") == "parabola" and 0 < i < len(T) - 1:
        a, c, e = T[i - 1], T[i], T[i + 1]
        den = a - 2 * c + e
        off = 0.5 * (a - e) / den if den != 0 else 0.0
        dx = x[1] - x[0]
        xp = x[i] + off * dx
        vp = float(np.interp(xp, x, V))
    else:
        xp, vp = float(x[i]), float(V[i])
    return {"x_peak": float(xp), "v_peak": vp / inputs["vstar"]}
