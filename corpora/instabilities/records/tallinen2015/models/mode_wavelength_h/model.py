# Wavelength of the first unstable mode over the relaxed layer thickness h, using the relation
# printed on p. 1: h = a/gz, with gz = 1/g for uniaxial growth, so a/h = gz = 1/g.
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "tallinen2015_first_unstable_mode", Path(__file__).resolve().parent.parent / "first_unstable_mode" / "model.py")
_fm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_fm)


def run(inputs, settings):
    g, la = _fm.first_mode(inputs["eta"], settings)
    gz = 1.0 / g
    a_over_h = gz  # h = a/gz
    return {"l_over_h": la * a_over_h}
