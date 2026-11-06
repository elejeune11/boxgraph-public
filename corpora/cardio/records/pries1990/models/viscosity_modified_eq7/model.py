# Eq. 7 exactly as printed: eta_rel' = eta_rel * (D^4 / (D - W)), D and W in um, eta_rel from Eqs. 2 and 3.
import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "pries1990_viscosity_invitro", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "viscosity_invitro", "model.py"))
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)


def run(inputs, settings):
    D, HD, W = inputs["D"], inputs["HD"], inputs["W"]
    return {"eta_rel_mod": _base.eta_rel(D, HD) * (D ** 4 / (D - W))}
