import math


def bracket(inputs):
    """Kv/Re0 + (Kt/2)(S0/S1 - 1)^2 of Eq. 15, with Kv of Eq. 16, and V0."""
    S0, S1 = inputs["S0"], inputs["S1"]
    V0 = inputs["Q"] / S0
    D0 = 2.0 * math.sqrt(S0 / math.pi)
    Re0 = V0 * D0 / inputs["nu"]
    Kv = inputs["cv"] * inputs["L"] / D0 * (S0 / S1) ** 2
    return Kv / Re0 + inputs["Kt"] / 2.0 * (S0 / S1 - 1.0) ** 2, V0


def run(inputs, settings):
    b, V0 = bracket(inputs)
    return {"dp": inputs["rho"] * V0 * V0 * b}
