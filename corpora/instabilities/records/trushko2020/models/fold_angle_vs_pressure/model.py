"""alpha from P_B R^3 and K, through the fold_elastica table."""
import importlib.util
import math
import pathlib

_spec = importlib.util.spec_from_file_location(
    "trushko2020_elastica", pathlib.Path(__file__).resolve().parent.parent / "fold_elastica" / "elastica.py")
E = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E)


def run(inputs, settings):
    tab = E.table(1.0, 80.0, float(settings.get("step_deg", 0.5)))
    p = inputs["PBR3"] / inputs["K"]          # both in uN*um: P_B R^3 / K
    a = E.interp(tab, 4, 0, p)
    return {"alpha": None if a is None else math.degrees(a)}
