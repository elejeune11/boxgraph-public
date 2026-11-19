# Variant of wavelength_at_threshold: the relaxed thickness is h = gz a (gz = 1/g), so a/h = g.
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "tallinen2015_wavelength_at_threshold",
    Path(__file__).resolve().parent.parent / "wavelength_at_threshold" / "model.py")
_wt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_wt)


def run(inputs, settings):
    g = inputs["g"]
    la, _ = _wt.mode_at(g, settings)
    return {"l_over_h": la * g}  # h = gz a, so a/h = 1/gz = g
