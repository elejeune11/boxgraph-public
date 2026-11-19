# Fig. 4: lambda* - lambda_W = c* lambda_W sqrt(xibar_1) = c* sqrt(lambda_W^2 xibar_1), with c* the
# N-mode coefficient of criterion (i) from nmode_cstar_eq46 (built_from).
import importlib.util
import math
import pathlib

_path = pathlib.Path(__file__).resolve().parent.parent / "nmode_cstar_eq46" / "model.py"
_spec = importlib.util.spec_from_file_location("cao2011_nmode_cstar_eq46_curve", _path)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)


def run(inputs, settings):
    cstar = _base.cstar_max_strain(inputs, settings)
    return {"dl": cstar * math.sqrt(inputs["s"])}
