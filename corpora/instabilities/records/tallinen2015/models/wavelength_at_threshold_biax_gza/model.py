# Variant of wavelength_at_threshold_biax: relaxed thickness h = gz a, gz = 1/g^2, so a/h = g^2.
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "tallinen2015_wavelength_at_threshold",
    Path(__file__).resolve().parent.parent / "wavelength_at_threshold" / "model.py")
_wt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_wt)


def run(inputs, settings):
    g = inputs["g"]
    la, _ = _wt.mode_at(g ** 1.5, settings)
    return {"l_over_h": la * g * g}
