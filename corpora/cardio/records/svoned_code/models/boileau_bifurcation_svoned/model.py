# The aortic bifurcation of the Boileau et al. benchmarks (Benchmark 4) run with the released
# svOneDSolver: a uniform aorta (segment 0) branching at one joint into two identical uniform iliac
# arteries (segments 1, 2), inflow at the aortic inlet and the release's RCR outlet at each iliac end.
# Tube law, profile and clock as in boileau_vessel_svoned (whose helper svoned.py this model loads):
# LINEAR material per vessel with p_ref = Pd, S0 = pi rd^2, EHR = (4/3) E h / rd, exponent n = zeta.
# The release's joint enforces one pressure and conservation of mass (theory.rst, Remark 2: Lagrange
# multipliers); the benchmark's junction keeps the total pressure P + rho U^2 / 2 continuous instead.
# Returns, at time t on the reference's clock, pressure, flow and change in radius from diastole at the
# aortic midpoint, the aortic end (the joint) and the midpoint of the first iliac artery.
import functools
import importlib.util
import math
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("svoned_helper", os.path.join(_here, "..", "boileau_vessel_svoned", "svoned.py"))
svoned = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(svoned)


@functools.lru_cache(maxsize=8)
def _simulate(La, rda, ha, Ea, Li, rdi, hi, Ei, rho, mu, Pd, Pout, R1, C, R2, zeta, T,
              n_a, n_i, spc, n_cycles, quad, tol, form, stab, q0, inflow_file):
    q, _, _ = svoned.fourier_inflow(inflow_file)
    dt = T / spc
    table = [(k * dt, q(k * dt)) for k in range(spc + 1)]
    if q0 is None:   # setting q_init 'inflow': start from the inflow at t = 0
        q0 = q(0.0)
    Aa, Ai = math.pi * rda ** 2, math.pi * rdi ** 2
    wk = [(0.0, R1), (0.0, C), (0.0, R2), (0.0, Pout)]
    segs = [
        {"name": "ao", "length": La, "n_el": n_a, "node_in": 0, "node_out": 1, "z_in": 0.0, "z_out": La,
         "area_in": Aa, "area_out": Aa, "q0": q0, "mat": "MATA", "bc": "NOBOUND", "table": None},
        {"name": "il1", "length": Li, "n_el": n_i, "node_in": 1, "node_out": 2, "z_in": La, "z_out": La + Li,
         "area_in": Ai, "area_out": Ai, "q0": q0 / 2, "mat": "MATI", "bc": "RCR", "table": "WK1", "table_rows": wk},
        {"name": "il2", "length": Li, "n_el": n_i, "node_in": 1, "node_out": 3, "z_in": La, "z_out": La + Li,
         "area_in": Ai, "area_out": Ai, "q0": q0 / 2, "mat": "MATI", "bc": "RCR", "table": "WK2", "table_rows": wk},
    ]
    mats = [{"name": "MATA", "kind": "LINEAR", "rho": rho, "mu": mu, "p_ref": Pd, "n": zeta, "params": [4.0 / 3.0 * Ea * ha / rda]},
            {"name": "MATI", "kind": "LINEAR", "rho": rho, "mu": mu, "p_ref": Pd, "n": zeta, "params": [4.0 / 3.0 * Ei * hi / rdi]}]
    n_steps = spc * n_cycles
    res = svoned.solve(segs, [(1, [0], [1, 2])], mats, table, dt, n_steps, quad, tol, form, stab)
    return res, dt, n_steps


def run(inputs, settings):
    x = inputs
    n_a, n_i = int(settings["n_elements_aorta"]), int(settings["n_elements_iliac"])
    res, dt, n_steps = _simulate(x["La"], x["rda"], x["ha"], x["Ea"], x["Li"], x["rdi"], x["hi"], x["Ei"], x["rho"], x["mu"],
                                 x["Pd"], x["Pout"], x["R1"], x["C"], x["R2"], x["zeta"], x["T"], n_a, n_i,
                                 int(settings["steps_per_cycle"]), int(settings["n_cycles"]), int(settings["quad_points"]),
                                 float(settings["tolerance"]), int(settings["formulation"]), int(settings["stabilization"]),
                                 None if settings["q_init"] == "inflow" else float(settings["q_init"]), settings["inflow_file"])
    T = x["T"]
    ph = x["t_ini"] + x["lag"] + x["t"]

    def at(seg, field, node):
        return svoned.at_phase(res[seg][field][node], dt, n_steps, T, ph)

    def dr(seg, node, rd):
        return math.sqrt(at(seg, "area", node) / math.pi) - rd
    out = {}
    for tag, seg, node, rd in (("mid", "ao", n_a // 2, x["rda"]), ("end", "ao", -1, x["rda"]), ("il", "il1", n_i // 2, x["rdi"])):
        out["P_" + tag] = at(seg, "pressure", node)
        out["Q_" + tag] = at(seg, "flow", node)
        out["dr_" + tag] = dr(seg, node, rd)
    out["Q_asym"] = at("il1", "flow", -1) - at("il2", "flow", -1)
    return out
