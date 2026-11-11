import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "wan2002_stenosis_eq15", Path(__file__).resolve().parent.parent / "stenosis_dp_eq15" / "model.py")
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)


def run(inputs, settings):
    b, _ = base.bracket(inputs)
    S0, S1, Q, L = inputs["S0"], inputs["S1"], inputs["Q"], inputs["L"]
    N = -S1 ** 2 * Q ** 2 * b / (S0 ** 2 * Q * L)       # Eq. 17 with Q0 = Q1 = Q
    return {"N": N, "dp": -inputs["rho"] * N * Q * L / S1 ** 2}
