# Variant of energy_eq70: the correction terms of Eqs. (70a) and (70b) multiplied by the prefactors of
# the energies they correct, (C h/2) eps^3 for the stretching energy (Eq. 66a) and (C h^3/2) eps^3 for
# the bending energy (Eq. 66c).
import importlib.util
import pathlib

_p = pathlib.Path(__file__).resolve().parent.parent / "energy_eq70" / "model.py"
_spec = importlib.util.spec_from_file_location("haas2021_energy_eq70", _p)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)


def run(inputs, settings):
    if not -1 < inputs["eta"] < 1:
        return {"e_stretch": None, "e_bend": None}
    e0, add_st, add_bd = _base.terms(inputs)
    C, eps, h = inputs["C"], inputs["eps"], inputs["h"]
    return {"e_stretch": e0["e0_stretch"] + C * h / 2 * eps**3 * add_st,
            "e_bend": e0["e0_bend"] + C * h**3 / 2 * eps**3 * add_bd}
