# The dashed vertical line 'Linear instability' of Fig. 3: on axes (g, A/h) it is the line
# g = g_c(eta) for every amplitude, g_c the first-unstable-mode threshold of Eq. 1. The amplitude
# input only says where on the line the value is read; it does not enter the result.
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "tallinen2015_first_unstable_mode", Path(__file__).resolve().parent.parent / "first_unstable_mode" / "model.py")
_fm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_fm)


def run(inputs, settings):
    return {"g": _fm.first_mode(inputs["eta"], settings)[0]}
