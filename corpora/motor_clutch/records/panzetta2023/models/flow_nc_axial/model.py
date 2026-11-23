# The modified clutch model under axial residual strain (clutch_axial_ssa) with the number of motors
# equal to the number of clutches, as the paper always sets it (p. 5): one simulation per nc, which
# is how the paper's curves of flow against nc (Figs. 3-5, S2, S3) are made. Outputs as
# clutch_axial_ssa. With ke = 0 it is the canonical model (no orthogonal spring).
import importlib.util
import os

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    spec = importlib.util.spec_from_file_location(f"panzetta2023_{name}", os.path.join(_HERE, "..", name, "model.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_sim = _load("clutch_axial_ssa")


def run(inputs, settings):
    nc = int(round(inputs["nc"]))
    return _sim.simulate({**inputs, "nc": nc, "nm": nc}, settings, _sim.axial_geometry(inputs))
