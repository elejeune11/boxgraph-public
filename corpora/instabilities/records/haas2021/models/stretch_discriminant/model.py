# Discriminant of the stretching quadratic form of Eq. (66a), (alphabar_sphi + alphabar_phis)^2
# - 4 alphabar_ss alpha_phiphi, from the coefficients of Eqs. (58c), (64a), (64b).
import importlib.util
import pathlib


def _load(name):
    p = pathlib.Path(__file__).resolve().parent.parent / name / "model.py"
    spec = importlib.util.spec_from_file_location("haas2021_" + name, p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_c58 = _load("coeffs_eq58")
_c64 = _load("coeffs_bar_eq64")


def run(inputs, settings):
    eta = inputs["eta"]
    if not -1 < eta < 1:
        return {"D": None}
    a = _c58.run({"eta": eta}, {})
    b = _c64.run({"eta": eta}, {})
    return {"D": (2 * b["ab_sphi"]) ** 2 - 4 * b["ab_ss"] * a["a_phiphi"]}
