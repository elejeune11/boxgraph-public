# The anatomic diameter, between the settings D_lo and D_hi (um), at which the ESL-based in vivo
# law gives its smallest effective relative viscosity. D_lo above Dcrit excludes the small-diameter
# branch below the ESL peak (Fig. 4, top).
import importlib.util
import os

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    spec = importlib.util.spec_from_file_location(f"pries2005_{name}", os.path.join(_HERE, "..", name, "model.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_vivo = _load("vivo_viscosity")
_min = _load("vitro_minimum")


def run(inputs, settings):
    p = dict(inputs)

    def f(D):
        p["D"] = D
        return _vivo.eta_vivo(p)

    return {"D_min": _min.argmin(f, settings["D_lo"], settings["D_hi"], int(settings["n"]))}
