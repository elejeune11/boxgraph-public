# The barred coefficients of Eq. (63) as the paper defines them from the Eq. (58) coefficients
# (first equalities of Eqs. 64a-64d): built_from coeffs_eq58.
import importlib.util
import pathlib

import mpmath as mp

_path = pathlib.Path(__file__).resolve().parent.parent / "coeffs_eq58" / "model.py"
_spec = importlib.util.spec_from_file_location("haas2021_coeffs_eq58", _path)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)

OUT = ("ab_ss", "ab_sphi", "bb_ss", "bb_sphi")


def run(inputs, settings):
    eta = inputs["eta"]
    if not -1 < eta < 1:
        return {k: None for k in OUT}
    with mp.workdps(60):
        c = _base.coefficients(eta)
        e = mp.mpf(eta)
        return {
            "ab_ss": float(c["a_ss"] - 4 * e * c["b_ss"] + 4 * e**2 * c["g_ss"]),
            "ab_sphi": float(c["a_sphi"] - 2 * e * c["b_phis"]),
            "bb_ss": float(c["b_ss"] - 2 * e * c["g_ss"]),
            "bb_sphi": float(c["b_sphi"] - 2 * e * c["g_sphi"]),
        }
