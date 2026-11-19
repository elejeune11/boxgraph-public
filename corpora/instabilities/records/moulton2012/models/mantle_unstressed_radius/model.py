# Appendix E: the unstressed mantle radius at time t is gamma(t) a0, with gamma = gamma0 + rate * t
# (Fig. 5 caption: gamma = 1 + 0.05t). Nondimensional units.


def run(inputs, settings):
    return {"R": (inputs["gamma0"] + inputs["gamma_rate"] * inputs["t"]) * inputs["a0"]}


def symbolic():
    import sympy as sp
    gamma0, gamma_rate, t, a0 = sp.symbols("gamma0 gamma_rate t a0", positive=True)
    return {"R": (gamma0 + gamma_rate * t) * a0}
