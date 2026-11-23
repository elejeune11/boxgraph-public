# Optimal number of clutches with the residual strain applied transversally (Fig. 7): the same
# search as optimal_nc_axial (nc log-spaced, nm = nc, cubic spline minimum) on clutch_transverse_ssa.
import importlib.util
import os

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    spec = importlib.util.spec_from_file_location(f"panzetta2023_{name}", os.path.join(_HERE, "..", name, "model.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_opt = _load("optimal_nc_axial")
_tr = _load("clutch_transverse_ssa")


def run(inputs, settings):
    return _opt.optimum(inputs, settings, _tr.transverse_geometry(inputs))
