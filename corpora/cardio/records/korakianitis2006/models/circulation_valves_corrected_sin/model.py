# Second reading of the corrections to circulation_valves: Eqs. 3, 6 and 18 corrected as in
# circulation_valves_corrected, but the vortex term of Eq. 14 kept as printed (K_v Q sin theta).
# Uses circulation_valves_corrected's code with the vortex angle factor fixed at 1.
import importlib.util
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "_circulation_valves_corrected", os.path.join(_here, "..", "circulation_valves_corrected", "model.py"))
_cvc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_cvc)


def run(inputs, settings):
    return _cvc.run(inputs, {**settings, "vortex_angle_factor": 1})
