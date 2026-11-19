# Wavelength of linear instability against the equibiaxial threshold growth g (thick black curves,
# Figs. 4(d), 4(e)). With g = gx = gy the effective plane-strain growth is g^(3/2) (p. 4); the
# first unstable mode with that threshold has wavelength l_c/a (wavelength_at_threshold.mode_at).
# The relaxed thickness is h = a/gz as printed (p. 1), with gz = 1/(gx gy) = 1/g^2.
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
    gz = 1.0 / (g * g)
    return {"l_over_h": la * gz}  # h = a/gz, a/h = gz
