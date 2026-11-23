"""Traction per site Fc/Nc at a given actin flow v (Eqs. 4, 6, 9, 11), before the force balance.
Units: v nm/s, rates 1/s, xt nm, kT pN*nm, k pN/nm, ly nm -> pN."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "liu2025_steady_linear", Path(__file__).resolve().parent.parent / "steady_linear" / "model.py")
SL = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(SL)


def run(inputs, settings):
    p = dict(inputs)
    return {"fc": SL.traction_per_site(p["v"], p, nl=int(settings.get("n_l", 20000)))}
