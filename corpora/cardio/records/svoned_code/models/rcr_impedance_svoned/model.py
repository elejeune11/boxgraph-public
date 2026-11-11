# The release's RCR outlet (cvOneDSubdomain.cxx, SetBoundRCRValues, lines 300-315; cvOneDMthModelBase.cxx,
# the conservative outlet flux) under a sinusoidal flow, run with the released svOneDSolver: a short,
# nearly rigid tube (the release's own static test material, OLUFSEN with k1 = 1e15, k2 = -20, k3 = 1e9,
# as in Tests/SystemTests/cases/tube_rcr.in) carrying Q(t) = Q0 + Q1 sin(2 pi f t) into the RCR outlet.
# The input impedance of the outlet is the ratio of the first Fourier coefficients of the pressure and
# the flow at the outlet node over the last period, so the tube itself does not enter it.
import cmath
import functools
import importlib.util
import math
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("svoned_helper", os.path.join(_here, "..", "boileau_vessel_svoned", "svoned.py"))
svoned = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(svoned)


@functools.lru_cache(maxsize=16)
def _simulate(Rc, Rd, C, f, n_pts, n_tau, Q0, Q1, n_el, L, area, tol):
    T = 1.0 / f
    dt = T / n_pts
    tau = Rd * C
    n_cycles = int(math.ceil(n_tau * tau / T)) + 2
    table = [(k * dt, Q0 + Q1 * math.sin(2 * math.pi * k * dt / T)) for k in range(n_pts + 1)]
    seg = {"name": "t", "length": L, "n_el": n_el, "node_in": 0, "node_out": 1, "z_in": 0.0, "z_out": L,
           "area_in": area, "area_out": area, "q0": Q0, "mat": "MAT1", "bc": "RCR", "table": "WK",
           "table_rows": [(0.0, Rc), (0.0, C), (0.0, Rd), (0.0, 0.0)]}
    mat = {"name": "MAT1", "kind": "OLUFSEN", "rho": 1.06, "mu": 0.04, "p_ref": 0.0, "n": 2.0, "params": [1.0e15, -20.0, 1.0e9]}
    n_steps = n_pts * n_cycles
    res = svoned.solve([seg], [], [mat], table, dt, n_steps, 2, tol, 1, 1)["t"]
    p = res["pressure"][-1][-n_pts:]
    q = res["flow"][-1][-n_pts:]
    # first Fourier coefficients over the last period (samples at k dt, k = n_steps - n_pts + 1 .. n_steps)
    k0 = n_steps - n_pts + 1
    P1 = sum(v * cmath.exp(-2j * math.pi * (k0 + i) / n_pts) for i, v in enumerate(p))
    Q1c = sum(v * cmath.exp(-2j * math.pi * (k0 + i) / n_pts) for i, v in enumerate(q))
    Z = P1 / Q1c
    return abs(Z), math.degrees(cmath.phase(Z))


def run(inputs, settings):
    mod, ph = _simulate(inputs["Rc"], inputs["Rd"], inputs["C"], inputs["f"], int(settings["n_pts"]), float(settings["n_tau"]),
                        float(settings["Q0"]), float(settings["Q1"]), int(settings["n_elements"]), float(settings["length"]),
                        float(settings["area"]), float(settings["tolerance"]))
    return {"modulus": mod, "phase": ph}
