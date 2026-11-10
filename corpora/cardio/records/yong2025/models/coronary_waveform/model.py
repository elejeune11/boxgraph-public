# Waveforms of the closed-loop circulation (coronary_closed_loop, Eqs. 1-12): the value of each
# flow and pressure at a given phase of the last simulated cycle, for comparison with the
# paper's plotted waveforms (Figs. 3A, 4, 5, 7A-B, Supp. Figs. S1-S2). Loads the printed model's
# code and changes nothing in it. Phase 0 is the start of ventricular contraction (t mod T = 0,
# where e_v of Eq. 4 starts to rise), the origin of the figures' "Cardiac cycle" / "Time (s)"
# axes. Values between the solver's time steps are linearly interpolated.
# Port units: ml/s, mmHg, dimensionless phase.
import importlib.util
import json
from pathlib import Path

import numpy as np

_spec = importlib.util.spec_from_file_location(
    "yong2025_coronary_closed_loop_base_wf",
    Path(__file__).resolve().parent.parent / "coronary_closed_loop" / "model.py")
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)

IX = _base.IX
OUTS = ("q_lad", "q_lcx", "q_rca", "q_gcv", "q_lcx_vein", "p_ao", "p_d_lad", "p_d_lcx", "p_d_rca",
        "p_pa", "q_ao", "q_pa")
_memo = {}  # one simulation serves every phase of a sweep (same inputs and settings)


def _cycle(inputs, settings):
    key = json.dumps([sorted((k, v) for k, v in inputs.items() if k != "phase"), sorted(settings.items())])
    if key in _memo:
        return _memo[key]
    rec = _base.simulate({k: v for k, v in inputs.items() if k != "phase"}, settings)
    if rec is None:
        _memo[key] = None
        return None
    T = inputs["T"]
    t_end = float(settings["t_end"])
    rows = [r for r in rec if r["t"] > t_end - T - 1e-9]
    ph = np.array([((r["t"] % T) / T) for r in rows])
    p = inputs
    ser = {}
    for r in rows:
        x = r["x"]
        vals = {
            "q_lad": r["Q"]["a_lad"], "q_lcx": r["Q"]["a_lcx"], "q_rca": r["Q"]["a_rca"],
            "q_gcv": r["Q"]["v_lad"], "q_lcx_vein": r["Q"]["v_lcx"],
            "p_ao": x[IX["ao"]], "p_d_lad": x[IX["a_lad"]], "p_d_lcx": x[IX["a_lcx"]], "p_d_rca": x[IX["a_rca"]],
            "p_pa": x[IX["pr"]], "q_ao": r["Q"]["av"],
            "q_pa": (x[IX["rv"]] - x[IX["pr"]]) / (p["R_open"] if r["open"]["pv"] else p["R_closed"]),
        }
        for k, v in vals.items():
            ser.setdefault(k, []).append(float(v))
    order = np.argsort(ph)
    ph = ph[order]
    out = (ph, {k: np.array(v)[order] for k, v in ser.items()})
    _memo[key] = out
    return out


def run(inputs, settings):
    c = _cycle(inputs, settings)
    if c is None:
        return {k: float("nan") for k in OUTS}
    ph, ser = c
    x = float(inputs["phase"]) % 1.0
    xp = np.concatenate([ph - 1.0, ph, ph + 1.0])  # periodic
    return {k: float(np.interp(x, xp, np.concatenate([ser[k]] * 3))) for k in OUTS}
