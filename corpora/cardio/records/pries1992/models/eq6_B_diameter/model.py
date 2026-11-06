# Eq. 6 of the paper with eta_rel0.45 from Eq. 2 and C from Eq. 4: D in um, output dimensionless.
import importlib.util
from pathlib import Path

_HERE = Path(__file__).resolve().parent.parent


def _load(name):
    spec = importlib.util.spec_from_file_location(f"pries1992_{name}", _HERE / name / "model.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_eq2 = _load("eq2_eta045")
_eq4 = _load("eq4_C")


def run(inputs, settings):
    D = inputs["D"]
    eta045 = _eq2.run({"D": D}, {})["eta045"]
    C = _eq4.run({"D": D}, {})["C"]
    return {"B": (eta045 - 1.0) / ((1.0 - 0.45) ** C - 1.0)}
