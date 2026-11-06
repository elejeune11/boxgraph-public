def run(inputs, settings):
    z1, z2 = inputs["Z0_d1"], inputs["Z0_d2"]
    zl = z1 * z2 / (z1 + z2)
    z0 = inputs["Z0_m"]
    return {"Gamma": (zl - z0) / (zl + z0)}


def symbolic():
    import sympy as sp
    zm, z1, z2 = sp.symbols("Z0_m Z0_d1 Z0_d2", positive=True)
    zl = z1 * z2 / (z1 + z2)
    return {"Gamma": (zl - zm) / (zl + zm)}
