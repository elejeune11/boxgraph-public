# Eqs. 2, 3 and 5 exactly as printed, using circulation_valves' own activation functions.
import importlib.util
import math
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "_circulation_valves", os.path.join(_here, "..", "circulation_valves", "model.py"))
_cv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_cv)


def run(inputs, settings):
    tc = math.fmod(inputs["t"], inputs["T"])
    ev = _cv._e_ventricle(tc, inputs["Ts1"], inputs["Ts2"])
    ea = _cv._e_atrium(tc, inputs["Tpwb"], inputs["Tpww"])
    return {"Elv": inputs["Elvd"] + (inputs["Elvs"] - inputs["Elvd"]) / 2.0 * ev,
            "Ela": inputs["Ela_min"] + (inputs["Ela_max"] - inputs["Ela_min"]) / 2.0 * ea}
