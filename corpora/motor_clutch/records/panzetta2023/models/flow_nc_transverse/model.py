# The modified clutch model under transverse residual strain (clutch_transverse_ssa) with the
# number of motors equal to the number of clutches (p. 5): the curves of flow against nc of Fig. 7A.
import importlib.util
import os

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    spec = importlib.util.spec_from_file_location(f"panzetta2023_{name}", os.path.join(_HERE, "..", name, "model.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_sim = _load("clutch_axial_ssa")
_tr = _load("clutch_transverse_ssa")


def run(inputs, settings):
    nc = int(round(inputs["nc"]))
    return _sim.simulate({**inputs, "nc": nc, "nm": nc}, settings, _tr.transverse_geometry(inputs))
