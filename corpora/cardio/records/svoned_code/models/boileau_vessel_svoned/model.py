# A single uniform vessel of the Boileau et al. benchmarks (Benchmarks 2 and 3: common carotid, upper
# thoracic aorta) run with the released svOneDSolver: inflow at the inlet, a three-element Windkessel
# (the release's RCR outlet) at the outlet. The benchmark's tube law P = Pd + beta/Ad (sqrt(A) - sqrt(Ad)),
# beta = (4/3) sqrt(pi) E h, is the release's LINEAR material p = p_ref + EHR (sqrt(S/S0) - 1)
# (Code/Source/cvOneDMaterialLinear.cxx, line 184) with p_ref = Pd, S0 = Ad = pi rd^2 and
# EHR = beta / sqrt(Ad) = (4/3) E h / rd. The velocity profile order zeta of the benchmark is the
# release's profile exponent n: delta = 1/(1 + n), N = -2 pi nu (n + 2) (cvOneDMaterial.h, lines 99-103),
# the same 1 + delta = (zeta + 2)/(zeta + 1) and friction -2 (zeta + 2) pi nu as the benchmark's profile.
# Returns, at time t on the reference's clock (1D phase = t_ini + lag + t, modulo the period), the
# pressure, flow and change in radius from diastole at the midpoint and the inlet-minus-outlet pressure.
import functools
import importlib.util
import math
import os

_spec = importlib.util.spec_from_file_location("svoned_helper", os.path.join(os.path.dirname(os.path.abspath(__file__)), "svoned.py"))
svoned = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(svoned)


@functools.lru_cache(maxsize=8)
def _simulate(L, rd, h, E, rho, mu, Pd, Pout, R1, C, R2, zeta, T, n_el, spc, n_cycles, quad, tol, form, stab, q0, inflow_file):
    q, T_file, _ = svoned.fourier_inflow(inflow_file)
    dt = T / spc
    table = [(k * dt, q(k * dt)) for k in range(spc + 1)]
    if q0 is None:   # setting q_init 'inflow': start from the inflow at t = 0
        q0 = q(0.0)
    Ad = math.pi * rd ** 2
    EHR = 4.0 / 3.0 * E * h / rd
    seg = {"name": "v", "length": L, "n_el": n_el, "node_in": 0, "node_out": 1, "z_in": 0.0, "z_out": L,
           "area_in": Ad, "area_out": Ad, "q0": q0, "mat": "MAT1", "bc": "RCR", "table": "WK",
           "table_rows": [(0.0, R1), (0.0, C), (0.0, R2), (0.0, Pout)]}
    mat = {"name": "MAT1", "kind": "LINEAR", "rho": rho, "mu": mu, "p_ref": Pd, "n": zeta, "params": [EHR]}
    n_steps = spc * n_cycles
    res = svoned.solve([seg], [], [mat], table, dt, n_steps, quad, tol, form, stab)["v"]
    return res, dt, n_steps, T_file


def _q0(v):
    return None if v == "inflow" else float(v)


def run(inputs, settings):
    x = inputs
    res, dt, n_steps, _ = _simulate(x["L"], x["rd"], x["h"], x["E"], x["rho"], x["mu"], x["Pd"], x["Pout"], x["R1"],
                                    x["C"], x["R2"], x["zeta"], x["T"], int(settings["n_elements"]),
                                    int(settings["steps_per_cycle"]), int(settings["n_cycles"]), int(settings["quad_points"]),
                                    float(settings["tolerance"]), int(settings["formulation"]), int(settings["stabilization"]),
                                    _q0(settings["q_init"]), settings["inflow_file"])
    T = x["T"]
    phase = x["t_ini"] + x["lag"] + x["t"]
    mid = int(settings["n_elements"]) // 2
    p_mid = svoned.at_phase(res["pressure"][mid], dt, n_steps, T, phase)
    p_in = svoned.at_phase(res["pressure"][0], dt, n_steps, T, phase)
    p_out = svoned.at_phase(res["pressure"][-1], dt, n_steps, T, phase)
    q_mid = svoned.at_phase(res["flow"][mid], dt, n_steps, T, phase)
    s_mid = svoned.at_phase(res["area"][mid], dt, n_steps, T, phase)
    return {"P": p_mid, "dP": p_in - p_out, "Q": q_mid, "dr": math.sqrt(s_mid / math.pi) - x["rd"]}
