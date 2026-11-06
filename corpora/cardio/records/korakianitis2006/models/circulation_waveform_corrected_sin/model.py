# Second reading for the waveforms: as circulation_waveform_corrected (Eqs. 3, 6 and 18
# corrected) but with the vortex term of Eq. 14 as printed (K_v Q sin theta).
import importlib.util
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "_circulation_waveform_corrected", os.path.join(_here, "..", "circulation_waveform_corrected", "model.py"))
_wc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_wc)


def run(inputs, settings):
    return _wc.run(inputs, {**settings, "vortex_angle_factor": 1})
