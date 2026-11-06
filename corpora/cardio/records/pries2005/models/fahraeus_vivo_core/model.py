# Eq. 13 with the factor inverted: (HT/HD)vivo = (HT/HD)vitro(Dph) * (Dph/D)^2.
import importlib.util
import os

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    spec = importlib.util.spec_from_file_location(f"pries2005_{name}", os.path.join(_HERE, "..", name, "model.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_fv = _load("fahraeus_vitro")
_esl = _load("esl_thickness")


def run(inputs, settings):
    D = inputs["D"]
    d_ph = D - 2.0 * _esl.thickness(inputs)["Wph"]
    return {"ratio": _fv.ratio(d_ph, inputs["HD"]) * (d_ph / D) ** 2}
