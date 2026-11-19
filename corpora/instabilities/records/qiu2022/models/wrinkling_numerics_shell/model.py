# wrinkling_numerics_balloon in the shell normalization: kappa-bar_w = kappa-hat_w / alpha, p-hat = alpha^2 p-bar.
import importlib.util
import pathlib

_path = pathlib.Path(__file__).resolve().parent.parent / "wrinkling_numerics_balloon" / "model.py"
_spec = importlib.util.spec_from_file_location("qiu2022_wrinkling_numerics_balloon", _path)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)


def run(inputs, settings):
    a = inputs["alpha"]
    return {"kbar_w": float(_base.onset(a**2 * inputs["pbar"], a, settings)) / a}
