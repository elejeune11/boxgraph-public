# Eqs. 5-7 of the paper, as printed. D in micrometres, HD as a fraction.
import math


def eta045(D):
    return 220.0 * math.exp(-1.3 * D) + 3.2 - 2.44 * math.exp(-0.06 * D ** 0.645)


def shape_C(D):
    s = 1.0 / (1.0 + 1e-11 * D ** 12)
    return (0.8 + math.exp(-0.075 * D)) * (-1.0 + s) + s


def eta_vitro(D, HD):
    C = shape_C(D)
    return 1.0 + (eta045(D) - 1.0) * ((1.0 - HD) ** C - 1.0) / ((1.0 - 0.45) ** C - 1.0)


def run(inputs, settings):
    return {"eta_vitro": eta_vitro(inputs["D"], inputs["HD"])}
