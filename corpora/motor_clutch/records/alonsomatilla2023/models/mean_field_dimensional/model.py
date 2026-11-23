# The mean-field model (Eqs. 3-4) in dimensional parameters: the groups of Table 2 are formed,
# the time-averaged T* and n_b* computed by mean_field's solver (loaded from that model's file),
# and T = T* nc Fb. ks in pN/um is converted to pN/nm.
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "alonsomatilla2023_mean_field", Path(__file__).resolve().parent.parent / "mean_field" / "model.py")
_mf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mf)


def groups(i):
    F = i["nm"] * i["Fm"] / (i["nc"] * i["Fb"])
    tau = i["kon"] / i["koff"]
    om = i["vu"] * i["kc"] / (i["Fb"] * i["koff"])
    return F, tau, om


def run(inputs, settings):
    F, tau, om = groups(inputs)
    K = inputs["ks"] * 1e-3 / (inputs["nc"] * inputs["kc"])
    Ts, nb = _mf._solve(F, tau, om, K, settings)
    return {"T": Ts * inputs["nc"] * inputs["Fb"]}
