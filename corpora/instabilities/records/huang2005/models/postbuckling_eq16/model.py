# Eq. 16 as a function of the membrane force: A_eq/h = (2/(k_eq h)) sqrt(|N|/(E_bar h) - f_min)
# = amp_coeff * sqrt(|N|/N_c - 1), with k_eq and f_min from model sinusoidal_finite_substrate
# (Eqs. 10 and 13). The wavelength 2 pi / k_eq does not depend on the force (p. 7).
import importlib.util
import math
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "huang2005_sinusoidal_finite_substrate",
    Path(__file__).resolve().parent.parent / "sinusoidal_finite_substrate" / "model.py",
)
_BASE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_BASE)


def run(inputs, settings):
    base = _BASE.run({k: inputs[k] for k in ("Ebar_over_Esbar", "H_over_h", "nu_s")}, settings)
    r = inputs["N_over_Nc"]
    if r < 1:
        raise ValueError("below the critical membrane force the film is flat (A = 0)")
    return {"A_over_h": base["amp_coeff"] * math.sqrt(r - 1), "lam_over_h": base["lam_over_h"]}
