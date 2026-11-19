"""Least-squares fit (in degrees) of K so that alpha(P_B R^3/K) matches the measured opening angles."""
import importlib.util
import math
import pathlib

from scipy.optimize import minimize_scalar

_spec = importlib.util.spec_from_file_location(
    "trushko2020_elastica", pathlib.Path(__file__).resolve().parent.parent / "fold_elastica" / "elastica.py")
E = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E)


def run(inputs, settings):
    tab = E.table(1.0, 80.0, float(settings.get("step_deg", 0.5)))
    xs, ys = inputs["Phi"]["x"], inputs["Phi"]["y"]

    def cost(logK):
        K = math.exp(logK)
        s = 0.0
        for x, y in zip(xs, ys):
            a = E.interp(tab, 4, 0, x / K)
            if a is None:
                return 1e12
            s += (math.degrees(a) - y) ** 2
        return s

    res = minimize_scalar(cost, bounds=(math.log(0.02), math.log(20.0)), method="bounded",
                          options={"xatol": 1e-8})
    return {"K": math.exp(res.x)}
