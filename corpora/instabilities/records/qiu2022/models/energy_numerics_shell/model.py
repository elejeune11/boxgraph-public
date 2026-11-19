# The numerical minimum of Eq. 2 (energy_numerics_balloon) in the shell normalization of Eq. 3:
# kappa-hat = alpha kappa-bar, p-hat = alpha^2 p-bar, M-bar = M-hat / alpha.
import importlib.util
import pathlib

_path = pathlib.Path(__file__).resolve().parent.parent / "energy_numerics_balloon" / "model.py"
_spec = importlib.util.spec_from_file_location("qiu2022_energy_numerics_balloon", _path)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)


def run(inputs, settings):
    a = inputs["alpha"]
    out = _base.run({"khat": a * inputs["kbar"], "phat": a**2 * inputs["pbar"], "alpha": a}, settings)
    return {"Mbar": out["Mhat"] / a}
