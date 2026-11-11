# The paper's symmetric bifurcation (Fig. 2, p. 6) run with the released svOneDSolver: an inlet
# branch of n_in elements and two equal daughter branches of n_br elements each, all elements of
# length h; uniform radii r_in and r_br; Olufsen's law (Eq. 11 with Eq. 14); the inflow waveform at
# the inlet (Eq. 7); equal resistances R at the two outlets (Eq. 8); pressure continuity and mass
# conservation at the junction (Eq. 41). Returns features of the last computed cycle.
import importlib.util
import math
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "wan2002_oned", Path(__file__).resolve().parent.parent / "single_segment_svoned" / "oned.py")
oned = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(oned)


def simulate(inputs, settings):
    sub = int(settings["subdivide"])
    h = inputs["h"]
    n_in, n_br = int(round(inputs["n_in"])), int(round(inputs["n_br"]))
    L_in, L_br = n_in * h, n_br * h
    S_in, S_br = math.pi * inputs["r_in"] ** 2, math.pi * inputs["r_br"] ** 2
    q0 = float(settings["q_init"])
    segs = [
        {"name": "inlet", "length": L_in, "n_el": n_in * sub, "node_in": 0, "node_out": 1, "z_in": 0.0, "z_out": -L_in,
         "area_in": S_in, "area_out": S_in, "q0": q0, "bc": "NOBOUND", "table": None},
        {"name": "right", "length": L_br, "n_el": n_br * sub, "node_in": 1, "node_out": 2, "z_in": -L_in, "z_out": -L_in - L_br,
         "area_in": S_br, "area_out": S_br, "q0": q0 / 2, "bc": "RESISTANCE", "table": "RR", "R": inputs["R"]},
        {"name": "left", "length": L_br, "n_el": n_br * sub, "node_in": 1, "node_out": 3, "z_in": -L_in, "z_out": -L_in - L_br,
         "area_in": S_br, "area_out": S_br, "q0": q0 / 2, "bc": "RESISTANCE", "table": "RL", "R": inputs["R"]},
    ]
    mat = {"rho": inputs["rho"], "mu": inputs["nu"] * inputs["rho"], "p_ref": inputs["p_ref"] * oned.MMHG,
           "n": inputs["n"], "k1": inputs["k1"], "k2": inputs["k2"], "k3": inputs["k3"]}
    inflow = oned.read_table(settings["inflow_file"], settings["inflow_table"])
    res, dt, T, spc, _ = oned.solve(segs, [(1, [0], [1, 2])], mat, inflow, settings)

    def lc(seg, f, node, scale=1.0):
        return [v / scale for v in oned.last_cycle(res[seg][f][node], spc)]
    return {
        "Q_in": lc("inlet", "flow", 0), "p_in": lc("inlet", "pressure", 0, oned.MMHG),
        "Q_j": lc("inlet", "flow", -1), "p_j": lc("inlet", "pressure", -1, oned.MMHG),
        "Q_r0": lc("right", "flow", 0), "p_r0": lc("right", "pressure", 0, oned.MMHG),
        "Q_l0": lc("left", "flow", 0), "p_l0": lc("left", "pressure", 0, oned.MMHG),
        "Q_r": lc("right", "flow", -1), "p_r": lc("right", "pressure", -1, oned.MMHG),
        "Q_l": lc("left", "flow", -1), "p_l": lc("left", "pressure", -1, oned.MMHG),
        "dt": dt, "T": T,
    }


def run(inputs, settings):
    c = simulate(inputs, settings)
    return {
        "p_in_max": max(c["p_in"]), "p_in_min": min(c["p_in"]),
        "Q_r_max": max(c["Q_r"]), "Q_r_min": min(c["Q_r"]), "Q_r_mean": oned.cycle_mean(c["Q_r"]),
        "p_r_max": max(c["p_r"]), "p_r_min": min(c["p_r"]),
        "flow_asym": max(abs(a - b) for a, b in zip(c["Q_r"], c["Q_l"])),
        "p_jump": max(max(abs(a - b), abs(a - d)) for a, b, d in zip(c["p_j"], c["p_r0"], c["p_l0"])),
        "mass_res": max(abs(a - b - d) for a, b, d in zip(c["Q_j"], c["Q_r0"], c["Q_l0"])),
    }
