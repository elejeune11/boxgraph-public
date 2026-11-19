# Variant of mode_wavelength_h: the relaxed thickness is h = gz a (gz = 1/g), so a/h = g.
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "tallinen2015_first_unstable_mode", Path(__file__).resolve().parent.parent / "first_unstable_mode" / "model.py")
_fm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_fm)


def run(inputs, settings):
    g, la = _fm.first_mode(inputs["eta"], settings)
    gz = 1.0 / g
    a_over_h = 1.0 / gz  # h = gz a
    return {"l_over_h": la * a_over_h}
