# Eq. 11 written in the shell normalization (kappa-hat = alpha kappa-bar, p-hat = alpha^2 p-bar, Eqs. 3-4):
# kappa-bar_w = kappa-hat_w / alpha. For p-hat = 0 it is the paper's cubic
# kappa-bar^3 - 6 kappa-bar^2 - 12 kappa-bar + 24 = 0 for any alpha.
import importlib.util
import pathlib

_path = pathlib.Path(__file__).resolve().parent.parent / "wrinkling_eq11" / "model.py"
_spec = importlib.util.spec_from_file_location("qiu2022_wrinkling_eq11", _path)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)


def run(inputs, settings):
    a = inputs["alpha"]
    return {"kbar_w": _base.smallest_positive_root(a, a**2 * inputs["pbar"]) / a}
