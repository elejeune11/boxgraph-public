"""Single fold of a confined inextensible ring: delta/R -> alpha, gamma, P_B R^3/K (solver in elastica.py)."""
import importlib.util
import math
import pathlib

_spec = importlib.util.spec_from_file_location(
    "trushko2020_elastica", pathlib.Path(__file__).resolve().parent / "elastica.py")
E = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E)


def run(inputs, settings):
    tab = E.table(1.0, 80.0, float(settings.get("step_deg", 0.5)))
    d = inputs["delta_over_R"]
    a = E.interp(tab, 1, 0, d)
    if a is None:
        return {"alpha": None, "gamma": None, "PBR3_over_K": None}
    return {"alpha": math.degrees(a),
            "gamma": math.degrees(E.interp(tab, 1, 2, d)),
            "PBR3_over_K": E.interp(tab, 1, 4, d)}
