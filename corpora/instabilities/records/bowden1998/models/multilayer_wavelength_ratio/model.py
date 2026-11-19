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
    # the composite-plate reconstruction of multilayer_wavelength, with t1 = (t1/t) t and E1 = (E1/Ep) Ep
    Em_bar = inputs["Em"] / (1 - inputs["nu_m"] ** 2)
    E1 = inputs["E1_over_Ep"] * inputs["Ep"]
    E1_bar = E1 / (1 - inputs["nu_1"] ** 2)
    Ep_bar = inputs["Ep"] / (1 - inputs["nu_p"] ** 2)
    t = inputs["t"] * 1e-9
    t1 = inputs["t1_over_t"] * t
    layers = [(E1_bar, t1), (Em_bar, t)] if t1 > 0 else [(Em_bar, t)]
    D = _bending_stiffness(layers)
    L = 2 * math.pi * (4 * D / Ep_bar) ** (1 / 3)
    return {"L": L * 1e6}
