# The rigid-substrate steady state S31-S36 (rigid_steady_state, loaded from that model's file)
# written in the clutch stiffness parameter of Fig. 3: omega = omega' beta_c (caption). It is
# the K -> oo limit of the curves of Fig. 3, where K = K'/beta_c.
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "alonsomatilla2023_rigid_steady_state",
    Path(__file__).resolve().parent.parent / "rigid_steady_state" / "model.py")
_rs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_rs)


def run(inputs, settings):
    om = inputs["omega_prime"] * inputs["beta_c"]
    out = _rs.run({"F": inputs["F"], "tau": inputs["tau"], "omega": om},
                  {"n_scan": settings.get("n_scan", 400), "root": "smallest_ve"})
    return {"T": out["T"], "nb": out["nb"]}
