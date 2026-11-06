# Eqs. 2.16-2.18 (left-hand form) with gamma = r_d1/r_d2 (Eq. 2.17 as printed).
# Dividing by r_d2: eta = (gamma^2 + 1)/(gamma^xi + 1)^(2/xi).


def run(inputs, settings):
    xi, g = inputs["xi"], inputs["gamma"]
    return {"eta": (1.0 + g ** 2) / (1.0 + g ** xi) ** (2.0 / xi)}


def symbolic():
    import sympy as sp
    xi, gamma = sp.symbols("xi gamma", positive=True)
    return {"eta": (1 + gamma ** 2) / (1 + gamma ** xi) ** (2 / xi)}
