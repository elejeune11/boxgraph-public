import math

from scipy.special import jn_zeros


def run(inputs, settings):
    tau = inputs["nu"] / (2 * math.pi * inputs["HR"] * inputs["R"] ** 2)
    n_max = int(settings.get("n_max", 100))
    for n, b in enumerate(jn_zeros(0, n_max), start=1):
        if 1 / b**2 < tau:
            return {"n": float(n)}
    return {"n": float("nan")}
