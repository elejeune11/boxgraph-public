import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "wan2002_profile_eq3_5", Path(__file__).resolve().parent.parent / "profile_terms_eq3_5" / "model.py")
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)


def run(inputs, settings):
    n, nu = inputs["n"], inputs["nu"]
    return {"delta": base.delta_eq3(n), "N": nu * base.wall_integral_eq4(n)}
