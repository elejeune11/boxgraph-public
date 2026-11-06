# Eq. 10 (printed root) then Eq. 7: D in um, hematocrits and output dimensionless.
import importlib.util
from pathlib import Path

_HERE = Path(__file__).resolve().parent.parent


def _load(name):
    spec = importlib.util.spec_from_file_location(f"pries1992_{name}", _HERE / name / "model.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_eq10 = _load("eq10_discharge_hct")
_eq7 = _load("eq7_eta_combined")


def run(inputs, settings):
    D = inputs["D"]
    HD = _eq10.run({"HctT": inputs["HctT"], "D": D}, {})["HctD"]
    return {"eta": _eq7.run({"D": D, "HctD": HD}, {})["eta"]}
