# The other fields of the steady state of Eqs. (5)-(9), from the solver of clutch_profile (built_from):
# myosin density M~, its gradient dM~/dx~, adhesion density N~adh, myosin force F dM~/dx~, and the
# internal viscous force lambda d2V~/dx~2, which Eq. (5) sets equal to T~ - F~myo (used at every node).
# Values between grid nodes are linear interpolations, as MATLAB draws the curves.
import importlib.util
from pathlib import Path

import numpy as np

_spec = importlib.util.spec_from_file_location(
    "craig2015_clutch_profile_f", Path(__file__).resolve().parent.parent / "clutch_profile" / "model.py")
_prof = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_prof)


def run(inputs, settings):
    p = _prof._params(inputs)
    x, V, M, N, T = _prof.solve(p, settings)
    _, dM, _ = _prof._fields(V, p, settings)
    Fmyo = inputs["F"] * dM
    xi = inputs["x"]
    f = lambda a: float(np.interp(xi, x, a))  # noqa: E731
    return {"M": f(M), "dM": f(dM), "N": f(N), "Fmyo": f(Fmyo), "Fvisc": f(T - Fmyo)}
