# Effective two-dimensional energy density of the large-bending shell theory, Eq. (63), split into
# stretching, coupling and bending parts as in Eqs. (65)-(66). Coefficients from Eqs. (58) and the
# closed forms (64) (built_from coeffs_eq58, coeffs_bar_eq64). All quantities nondimensional
# (lengths scaled by the embryo radius R, energies by C R^2 per unit area).
import importlib.util
import pathlib

import mpmath as mp


def _load(name):
    p = pathlib.Path(__file__).resolve().parent.parent / name / "model.py"
    spec = importlib.util.spec_from_file_location("haas2021_" + name, p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_c58 = _load("coeffs_eq58")
_c64 = _load("coeffs_bar_eq64")

OUT = ("e_stretch", "e_couple", "e_bend", "e")


def run(inputs, settings):
    eta = inputs["eta"]
    if not -1 < eta < 1:
        return {k: None for k in OUT}
    with mp.workdps(60):
        c = _c58.coefficients(eta)
        b = _c64.run({"eta": eta}, {})
        C, eps, h = (mp.mpf(inputs[k]) for k in ("C", "eps", "h"))
        Es, Ep, Ks, Kp = (mp.mpf(inputs[k]) for k in ("Es", "Ephi", "Ks", "Kphi"))
        ab_ss, ab_sp = mp.mpf(b["ab_ss"]), mp.mpf(b["ab_sphi"])
        bb_ss, bb_sp = mp.mpf(b["bb_ss"]), mp.mpf(b["bb_sphi"])
        st = C * h / 2 * eps**3 * (ab_ss * Es**2 + 2 * ab_sp * Es * Ep + c["a_phiphi"] * Ep**2)
        cp = C * h**2 * eps**3 * (bb_ss * Es * Ks + bb_sp * Es * Kp + c["b_phis"] * Ep * Ks
                                   + c["b_phiphi"] * Ep * Kp)
        bd = C * h**3 / 2 * eps**3 * (c["g_ss"] * Ks**2 + 2 * c["g_sphi"] * Ks * Kp + c["g_phiphi"] * Kp**2)
        return {"e_stretch": float(st), "e_couple": float(cp), "e_bend": float(bd), "e": float(st + cp + bd)}
