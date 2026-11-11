import math


def run(inputs, settings):
    eh_r0 = inputs["k1"] * math.exp(inputs["k2"] * inputs["r0"]) + inputs["k3"]
    c0 = math.sqrt(2.0 / 3.0 * eh_r0 / inputs["rho"])
    return {"c0": c0, "t_transit": inputs["L"] / c0}
