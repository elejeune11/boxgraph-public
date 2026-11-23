import math


def run(inputs, settings):
    s, sc, n = inputs["sigma"], inputs["sigma_c"], inputs["n"]
    if s < sc:
        return {"phi_ratio": 1.0}
    return {"phi_ratio": 1.0 + 5.0 * math.erf(n * (s - sc))}
