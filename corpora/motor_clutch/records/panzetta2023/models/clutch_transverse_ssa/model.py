# Modified motor-clutch model with the residual strain applied transversally (Fig. 1C; Eqs. 2-4,
# 7-12): P1 is moved to P1' by x0, with eps0 = sqrt(l^2 + x0^2)/l - 1 (Eq. 9), and the force
# balance is F0 + sum Fc_i = Fs (Eq. 7) with F0 = ke eps0 l + ks x0 as printed (Eq. 8).
# Reader's reading (q_transverse_fs, q_transverse_load): Fs is the force of the two springs at the
# total displacement x0 + x_s (Eq. 6 with the vertical distance l, the spring's rest length, since
# P2 does not move), and the load on the motors in Eq. 10 is the sum of the clutch forces.
# The simulation itself is shared with clutch_axial_ssa.
import importlib.util
import math
import os

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    spec = importlib.util.spec_from_file_location(f"panzetta2023_{name}", os.path.join(_HERE, "..", name, "model.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_sim = _load("clutch_axial_ssa")


def transverse_geometry(inputs):
    l, eps0, ke, ks = inputs["l"], inputs["eps0"], inputs["ke"], inputs["ks"]
    x0 = l * math.sqrt((1.0 + eps0) ** 2 - 1.0)       # Eq. 9 solved for x0
    F0 = ke * eps0 * l + ks * x0                       # Eq. 8 as printed
    return {"L": l, "x_off": x0, "F0": F0}


def run(inputs, settings):
    return _sim.simulate(inputs, settings, transverse_geometry(inputs))
