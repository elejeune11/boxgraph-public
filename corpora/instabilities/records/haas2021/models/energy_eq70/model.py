# Eqs. (70a) and (70b) as printed: the large-bending stretching and bending energies written as the
# classical ones (Eqs. 69a, 69b) plus correction terms. As printed, the correction terms carry no
# prefactor (no C, h or eps^3). built_from energy_eq67_classical and k_eq71.
import importlib.util
import pathlib


def _load(name):
    p = pathlib.Path(__file__).resolve().parent.parent / name / "model.py"
    spec = importlib.util.spec_from_file_location("haas2021_" + name, p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_classical = _load("energy_eq67_classical")
_k = _load("k_eq71")


def terms(inputs):
    eta = inputs["eta"]
    q = 1 - eta**2
    e0 = _classical.run(inputs, {})
    k = float(_k.k_of(eta))
    Es, Ep, Ks, Kp = inputs["Es"], inputs["Ephi"], inputs["Ks"], inputs["Kphi"]
    add_st = eta**2 * (2 - eta**2) / q**2 * (2 * Es + Ep) ** 2
    add_bd = eta**2 * (3 - 2 * eta**2) / (36 * q**2) * (3 * Ks + Kp) * (k * Ks + Kp)
    return e0, add_st, add_bd


def run(inputs, settings):
    if not -1 < inputs["eta"] < 1:
        return {"e_stretch": None, "e_bend": None}
    e0, add_st, add_bd = terms(inputs)
    return {"e_stretch": e0["e0_stretch"] + add_st, "e_bend": e0["e0_bend"] + add_bd}
