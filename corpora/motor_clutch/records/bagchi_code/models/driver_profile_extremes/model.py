# Our port of the drivers' lines 223-258 (control version). The prefactor of the second Gaussian uses s,
# as the C++ does.
import math


def run(inputs, settings):
    n = int(round(inputs["n"]))
    s = inputs["s"]
    s1 = inputs["s1"]
    uv = (n // 2) + 1
    vect = []
    vect1 = []
    for node_index in range(n + 1):
        vect.append(1 * (1 / (s * math.sqrt(2 * math.pi))) * math.exp(-(((node_index + 1 - uv) / s) ** 2.0) / 2))
        vect1.append(1 * (1 / (s * math.sqrt(2 * math.pi))) * math.exp(-(((node_index + 1 - uv) / s1) ** 2.0) / 2))
    return {"max_ND": max(vect), "min_ND": min(vect), "max_ND1": max(vect1), "min_ND1": min(vect1)}
