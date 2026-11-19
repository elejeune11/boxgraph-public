# Fig. 5, the asymptotic line: eps* = 1 - lambda*, lambda* = lambda_W (1 + c* sqrt(xibar_1)),
# lambda_W = coef/sqrt(lambda_3) (Eq. 1.1), c* the N-mode coefficient of criterion (i) from
# nmode_cstar_eq46 (built_from).
import importlib.util
import math
import pathlib

_path = pathlib.Path(__file__).resolve().parent.parent / "nmode_cstar_eq46" / "model.py"
_spec = importlib.util.spec_from_file_location("cao2011_nmode_cstar_eq46_strain", _path)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)


def run(inputs, settings):
    cstar = _base.cstar_max_strain(inputs, settings)
    lam_w = inputs["coef"] / math.sqrt(inputs["lam3"])
    return {"eps": 1.0 - lam_w * (1.0 + cstar * math.sqrt(inputs["xi1"]))}
