"""Eqs. 2-3: AIC and SC, with the RSS recovered from the RMSE definition RMSE = sqrt(RSS/(N - 1))."""
import math


def run(inputs, settings):
    n = inputs["N"]
    rss = inputs["RMSE"] ** 2 * (n - 1)  # mmHg^2
    return {"AIC": n * math.log(rss) + 2 * inputs["P"],
            "SC": n * math.log(rss) + inputs["P"] * math.log(n)}


def symbolic():
    import sympy as sp
    RMSE, N, P = sp.symbols("RMSE N P", positive=True)
    rss = RMSE**2 * (N - 1)
    return {"AIC": N * sp.log(rss) + 2 * P, "SC": N * sp.log(rss) + P * sp.log(N)}
