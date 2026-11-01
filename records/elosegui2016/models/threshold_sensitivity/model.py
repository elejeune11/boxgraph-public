# Threshold rigidity for talin unfolding and its sensitivity S = d log k_threshold / d log p
# (Supplementary Note, PDF p. 25), computed with the clutch model of clutch_talin_sim. Our code.
#
# k_threshold: the substrate rigidity at which the integrin density has increased by the given fraction
# (10%) over its basal value. The density is the time average over the run; it is computed on a log-spaced
# grid of Young's moduli and the first upward crossing is interpolated linearly in log E. Because
# k_sub = c E r_a, d log k_threshold = d log E_threshold, so S is the same for either.
# S: k_threshold is computed with the parameter `param` multiplied by each of `factors`, and S is the slope
# of a least-squares line through log k_threshold against log p.
import importlib.util
import math
from pathlib import Path

import numpy as np

_P = Path(__file__).resolve().parent.parent / "clutch_talin_sim" / "model.py"
_spec = importlib.util.spec_from_file_location("elosegui2016_clutch_talin_sim", _P)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)


def threshold(p, settings):
    grid = np.geomspace(float(settings["E_min"]), float(settings["E_max"]), int(settings["n_grid"]))
    target = p["dint"] * (1.0 + p["increase"])
    prev = None
    for E in grid:
        d = _base.simulate(dict(p, E=float(E)), settings)["dint_mean"]
        if d >= target:
            if prev is None:
                return float(E)
            (E0, d0) = prev
            w = (target - d0) / (d - d0)
            return float(math.exp(math.log(E0) + w * (math.log(E) - math.log(E0))))
        prev = (float(E), d)
    return float("nan")


def run(inputs, settings):
    p = dict(inputs)
    param = settings["param"]
    factors = [float(f) for f in settings["factors"]]
    logs_p, logs_k, e_ref = [], [], float("nan")
    for f in factors:
        q = dict(p)
        q[param] = p[param] * f
        Et = threshold(q, settings)
        if f == 1.0:
            e_ref = Et
        if math.isfinite(Et):
            logs_p.append(math.log(q[param]))
            logs_k.append(math.log(Et))
    S = float(np.polyfit(logs_p, logs_k, 1)[0]) if len(logs_p) >= 2 else float("nan")
    return {"S": S, "E_threshold": e_ref}
