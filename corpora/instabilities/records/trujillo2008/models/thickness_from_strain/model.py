# Reader's reconstruction (not printed): free isotropic swelling l/l0 = 1/(1 - e), then equibiaxial
# in-plane compression by the linear strain e at a free surface, thickness strain 2 nu e / (1 - nu).


def run(inputs, settings):
    e, nu = inputs["e"], inputs["nu"]
    swell = 1.0 / (1.0 - e)
    return {"h_ratio": swell * (1.0 + 2.0 * nu * e / (1.0 - nu))}


def symbolic():
    import sympy as sp
    e, nu = sp.symbols("e nu", positive=True)
    return {"h_ratio": (1 + 2 * nu * e / (1 - nu)) / (1 - e)}
