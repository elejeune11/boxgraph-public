# Load-free velocity of maximal traction in the high-motor limit on a rigid substrate (inset of
# Fig. 5(B)): omega_opt = argmax_omega T*(tau, omega), T* from S55 and S57 (rigid_high_motor,
# loaded from that model's file). T* is computed on n_grid log-spaced omega in
# [omega_min, omega_max]; the optimum is refined by a bounded search in log omega between the
# neighbours of the largest grid value.
import importlib.util
import math
from pathlib import Path

import numpy as np
from scipy.optimize import minimize_scalar

_spec = importlib.util.spec_from_file_location(
    "alonsomatilla2023_rigid_high_motor",
    Path(__file__).resolve().parent.parent / "rigid_high_motor" / "model.py")
_hm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_hm)


def run(inputs, settings):
    tau = inputs["tau"]

    def T(lw):
        return _hm.run({"tau": tau, "omega": math.exp(lw)}, {})["T"]

    lws = np.linspace(math.log(settings["omega_min"]), math.log(settings["omega_max"]), int(settings["n_grid"]))
    Ts = np.array([T(x) for x in lws])
    k = int(np.argmax(Ts))
    lo, hi = lws[max(k - 1, 0)], lws[min(k + 1, len(lws) - 1)]
    r = minimize_scalar(lambda x: -T(x), bounds=(lo, hi), method="bounded", options={"xatol": 1e-6})
    return {"omega_opt": float(math.exp(r.x)), "Tmax": float(-r.fun)}
