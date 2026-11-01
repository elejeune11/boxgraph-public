"""Mean-field motor-clutch model on a purely elastic substrate of stiffness ks
(Fig. 1B; SI Fig. S1A, S7): the logic of mean_field_sls with no Maxwell element
(ka = 0), so the substrate is the spring ks alone."""
import importlib.util
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("gong2018_mean_field_sls", os.path.join(_HERE, "..", "mean_field_sls", "model.py"))
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)


def run(inputs, settings):
    p = {k: inputs[k] for k in _base.PARAMS}
    out = _base.mean_speed(p, [], [], inputs["ks"], settings)
    return {"Vs": out["Vs"]}
