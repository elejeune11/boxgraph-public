import math


def _bending_stiffness(layers):
    # layers: list of (plane-strain modulus, thickness), bottom first; returns D about the neutral axis
    z = 0.0
    rows = []
    for E, h in layers:
        rows.append((E, h, z + h / 2))
        z += h
    stretch = sum(E * h for E, h, _ in rows)
    zn = sum(E * h * zc for E, h, zc in rows) / stretch
    return sum(E * (h**3 / 12 + h * (zc - zn) ** 2) for E, h, zc in rows)


def run(inputs, settings):
    Em_bar = inputs["Em"] / (1 - inputs["nu_m"] ** 2)
    E1_bar = inputs["E1"] / (1 - inputs["nu_1"] ** 2)
    Ep_bar = inputs["Ep"] / (1 - inputs["nu_p"] ** 2)
    t = inputs["t"] * 1e-9
    t1 = inputs["t1"] * 1e-9
    layers = [(E1_bar, t1), (Em_bar, t)] if t1 > 0 else [(Em_bar, t)]
    D = _bending_stiffness(layers)
    D0 = _bending_stiffness([(Em_bar, t)])
    L = 2 * math.pi * (4 * D / Ep_bar) ** (1 / 3)
    L0 = 2 * math.pi * (4 * D0 / Ep_bar) ** (1 / 3)
    return {"L": L * 1e6, "factor": L / L0}
