# eta_vivo = eta_vitro(Dph, HD) (D/Deff)^4 (p. 3), with Eqs. 5-7 and 8-11 from the sibling models.
import importlib.util
import os

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    spec = importlib.util.spec_from_file_location(f"pries2005_{name}", os.path.join(_HERE, "..", name, "model.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_vitro = _load("vitro_viscosity")
_esl = _load("esl_thickness")


def eta_vivo(p):
    w = _esl.thickness(p)
    D = p["D"]
    d_eff = D - 2.0 * w["Weff"]
    d_ph = D - 2.0 * w["Wph"]
    return _vitro.eta_vitro(d_ph, p["HD"]) * (D / d_eff) ** 4


def run(inputs, settings):
    return {"eta_vivo": eta_vivo(inputs)}
