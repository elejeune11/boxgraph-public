# Eq. 13 gives κsub from E, then the motor-clutch model (Eqs. 1-5) runs on it.
import importlib.util
import os

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    spec = importlib.util.spec_from_file_location(f"chan2008_{name}", os.path.join(_HERE, "..", name, "model.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_eq13 = _load("ksub_eq13")
_mc = _load("motor_clutch")


def run(inputs, settings):
    i = inputs
    ksub = _eq13.run({"E": i["E"], "L": i["L"], "nu": i["nu"]}, {})["ksub"]
    out = _mc.simulate(i["nm"], i["Fm"], i["vu"], i["nc"], i["kon"], i["koff"], i["Fb"], i["kc"], ksub, settings)
    out["ksub"] = ksub
    return out
