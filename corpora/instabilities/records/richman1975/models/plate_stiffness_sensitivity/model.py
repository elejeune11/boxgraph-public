import importlib.util
import os

_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "plate_on_foundation", "model.py")
_spec = importlib.util.spec_from_file_location("richman1975_plate_on_foundation", _path)
_plate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_plate)


def run(inputs, settings):
    base = {k: inputs[k] for k in ("t1", "t2", "E2_over_E1", "Ecore_over_E1", "stress_ratio")}
    softer = dict(base, Ecore_over_E1=inputs["Ecore_over_E1"] / inputs["F"])
    l0 = _plate.run(base, settings)["l_over_t"]
    l1 = _plate.run(softer, settings)["l_over_t"]
    return {"factor": l1 / l0}
