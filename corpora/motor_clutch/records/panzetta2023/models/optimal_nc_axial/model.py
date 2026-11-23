# Optimal number of clutches: the nc at which the mean retrograde flow of the modified clutch model
# is lowest (Sec. 3.2-3.3). As the paper does it (p. 3, p. 6): the simulation is run for nc values
# logarithmically spaced between nc_min and nc_max, with the number of motors equal to the number of
# clutches (p. 5), and the minimum is located on a cubic spline through the points.
# Built from clutch_axial_ssa; the geometry is chosen by the `geometry` setting of each model.
import importlib.util
import math
import os

import numpy as np
from scipy.interpolate import CubicSpline

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    spec = importlib.util.spec_from_file_location(f"panzetta2023_{name}", os.path.join(_HERE, "..", name, "model.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_sim = _load("clutch_axial_ssa")


def nc_grid(settings):
    lo, hi, m = math.log10(settings["nc_min"]), math.log10(settings["nc_max"]), int(settings["n_nc"])
    return [int(round(10 ** (lo + (hi - lo) * j / (m - 1)))) for j in range(m)]


def optimum(inputs, settings, geometry):
    grid = sorted(set(nc_grid(settings)))
    sim = {"n_events": settings["n_events"], "seed": settings["seed"]}
    v = [_sim.simulate({**inputs, "nc": nc, "nm": nc}, sim, geometry)["v_retro"] for nc in grid]
    lx = np.log10(grid)
    spline = CubicSpline(lx, v)
    fine = np.linspace(lx[0], lx[-1], 4001)
    vf = spline(fine)
    j = int(np.argmin(vf))
    return {"nc_opt": float(10 ** fine[j]), "v_min": float(vf[j])}


def run(inputs, settings):
    return optimum(inputs, settings, _sim.axial_geometry(inputs))
