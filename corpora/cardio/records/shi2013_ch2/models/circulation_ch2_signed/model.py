# Corrected variant of circulation_ch2: everything as printed except Eq. 2-13, whose reverse
# branch (P_lv < P_sas) gets a minus sign, so a valve can carry reverse (regurgitant) flow.
# The printed model's code is loaded from its own file and run with that one change.
import importlib.util
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "circulation_ch2_printed", os.path.join(_here, "..", "circulation_ch2", "model.py"))
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)


def run(inputs, settings):
    return _base.summarise(_base.simulate(inputs, settings, signed=True), inputs)
