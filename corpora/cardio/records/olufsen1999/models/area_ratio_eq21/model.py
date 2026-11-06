# Eq. 21 as printed: eta = (1 + gamma)/(1 + gamma^(xi/2))^(2/xi), gamma = (r_d2/r_d1)^2 (Eq. 20).


def run(inputs, settings):
    xi, g = inputs["xi"], inputs["gamma"]
    return {"eta": (1.0 + g) / (1.0 + g ** (xi / 2.0)) ** (2.0 / xi)}


def symbolic():
    import sympy as sp
    xi, gamma = sp.symbols("xi gamma", positive=True)
    return {"eta": (1 + gamma) / (1 + gamma ** (xi / 2)) ** (2 / xi)}
