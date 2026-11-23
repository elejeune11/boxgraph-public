# Myosin activity of maximal traction on a rigid substrate (Fig. 5(A)): F_opt = argmax_F T*(F, tau,
# omega) with T* from the steady state S31-S36 (rigid_steady_state, loaded from that model's file,
# smallest admissible root). T* is computed on n_grid log-spaced F in [F_min, F_max]; the optimum
# is then refined by a bounded scalar search between the neighbours of the largest grid value.
import importlib.util
from pathlib import Path

import numpy as np
from scipy.optimize import minimize_scalar

_spec = importlib.util.spec_from_file_location(
    "alonsomatilla2023_rigid_steady_state",
    Path(__file__).resolve().parent.parent / "rigid_steady_state" / "model.py")
_rs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_rs)


def run(inputs, settings):
    tau, om = inputs["tau"], inputs["omega"]
    sub = {"n_scan": settings.get("n_scan", 400), "root": "smallest_ve"}

    def T(F):
        t = _rs.run({"F": float(F), "tau": tau, "omega": om}, sub)["T"]
        return -np.inf if not np.isfinite(t) else t

    Fs = np.geomspace(settings["F_min"], settings["F_max"], int(settings["n_grid"]))
    Ts = np.array([T(F) for F in Fs])
    k = int(np.argmax(Ts))
    lo, hi = Fs[max(k - 1, 0)], Fs[min(k + 1, len(Fs) - 1)]
    r = minimize_scalar(lambda F: -T(F), bounds=(lo, hi), method="bounded",
                        options={"xatol": settings.get("xatol", 1e-4)})
    Fopt, Tmax = (r.x, -r.fun) if -r.fun >= Ts[k] else (Fs[k], Ts[k])
    return {"Fopt": float(Fopt), "Tmax": float(Tmax)}
