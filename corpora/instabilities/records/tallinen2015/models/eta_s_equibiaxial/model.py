# Equibiaxial growth (p. 4): plane-strain results carry over with eta -> gy eta and
# g -> gx sqrt(gy). With g = gx = gy the effective growth is g^(3/2); the sulcification threshold
# is met at g^(3/2) = gs, i.e. g = gs^(2/3), and the crossing with the linear threshold is where
# the effective modulus ratio gy eta equals the uniaxial eta_s(gs). So eta_s,biax = eta_s(gs)/gs^(2/3).
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "tallinen2015_eta_s_uniaxial", Path(__file__).resolve().parent.parent / "eta_s_uniaxial" / "model.py")
_es = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_es)


def run(inputs, settings):
    gs = inputs["gs"]
    gy = gs ** (2.0 / 3.0)
    return {"eta_s": _es.eta_s(gs, settings) / gy}
