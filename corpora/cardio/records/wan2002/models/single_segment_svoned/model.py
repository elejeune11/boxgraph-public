# The paper's single segment (Fig. 1, p. 6) run with the released svOneDSolver: a straight elastic
# tube of radius r0 and length L, Olufsen's law (Eq. 11 with Eq. 14) for the wall, the profile
# exponent n (Eqs. 5-6), the inflow waveform prescribed at the inlet (Eq. 7) and a resistance at the
# outlet (Eq. 8, p = QR). Returns features of the last computed cycle at the inlet and outlet nodes.
import importlib.util
import math
from pathlib import Path

_spec = importlib.util.spec_from_file_location("wan2002_oned", Path(__file__).resolve().parent / "oned.py")
oned = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(oned)


def simulate(inputs, settings):
    S0 = math.pi * inputs["r0"] ** 2
    inflow = oned.read_table(settings["inflow_file"], settings["inflow_table"])
    seg = {"name": "seg", "length": inputs["L"], "n_el": int(settings["n_elements"]), "node_in": 0, "node_out": 1,
           "z_in": 0.0, "z_out": -inputs["L"], "area_in": S0, "area_out": S0, "q0": float(settings["q_init"]),
           "bc": "RESISTANCE", "table": "RT", "R": inputs["R"]}
    mat = {"rho": inputs["rho"], "mu": inputs["nu"] * inputs["rho"], "p_ref": inputs["p_ref"] * oned.MMHG,
           "n": inputs["n"], "k1": inputs["k1"], "k2": inputs["k2"], "k3": inputs["k3"]}
    res, dt, T, spc, _ = oned.solve([seg], [], mat, inflow, settings)
    r = res["seg"]
    return {"Q_in": oned.last_cycle(r["flow"][0], spc), "Q_out": oned.last_cycle(r["flow"][-1], spc),
            "p_in": [p / oned.MMHG for p in oned.last_cycle(r["pressure"][0], spc)],
            "p_out": [p / oned.MMHG for p in oned.last_cycle(r["pressure"][-1], spc)], "dt": dt, "T": T}


def run(inputs, settings):
    c = simulate(inputs, settings)
    return {
        "Q_in_max": max(c["Q_in"]), "Q_in_min": min(c["Q_in"]),
        "Q_out_max": max(c["Q_out"]), "Q_out_min": min(c["Q_out"]), "Q_out_mean": oned.cycle_mean(c["Q_out"]),
        "p_in_max": max(c["p_in"]), "p_in_min": min(c["p_in"]), "p_in_mean": oned.cycle_mean(c["p_in"]),
        "p_out_max": max(c["p_out"]), "p_out_min": min(c["p_out"]),
        "delay": oned.peak_time(c["Q_out"], c["dt"]) - oned.peak_time(c["Q_in"], c["dt"]),
    }
