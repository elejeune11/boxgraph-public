# The coefficients of Eq. (63) divided by alphabar_ss, the scaling of Fig. 3: the unbarred ones from
# coeffs_eq58 (Eqs. 58), the barred ones from the printed closed forms of coeffs_bar_eq64 (Eqs. 64).
# Evaluated in 60-digit arithmetic like the models they are built from.
import importlib.util
import pathlib

import mpmath as mp

_here = pathlib.Path(__file__).resolve().parent.parent


def _load(name):
    spec = importlib.util.spec_from_file_location("haas2021_" + name, _here / name / "model.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_c58 = _load("coeffs_eq58")
_c64 = _load("coeffs_bar_eq64")

OUT = ("r_asphi", "r_aphiphi", "r_bss", "r_bsphi", "r_bphis", "r_bphiphi", "r_gss", "r_gsphi", "r_gphiphi")


def run(inputs, settings):
    eta = inputs["eta"]
    if not -1 < eta < 1:
        return {k: None for k in OUT}
    c = _c58.coefficients(eta)
    b = _c64.run({"eta": eta}, {})
    with mp.workdps(60):
        abar = mp.mpf(4) / (1 - mp.mpf(eta) ** 2) ** 2
        return {
            "r_asphi": b["ab_sphi"] / float(abar),
            "r_aphiphi": float(c["a_phiphi"] / abar),
            "r_bss": b["bb_ss"] / float(abar),
            "r_bsphi": b["bb_sphi"] / float(abar),
            "r_bphis": float(c["b_phis"] / abar),
            "r_bphiphi": float(c["b_phiphi"] / abar),
            "r_gss": float(c["g_ss"] / abar),
            "r_gsphi": float(c["g_sphi"] / abar),
            "r_gphiphi": float(c["g_phiphi"] / abar),
        }
