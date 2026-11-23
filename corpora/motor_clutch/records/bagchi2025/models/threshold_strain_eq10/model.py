import math


def run(inputs, settings):
    s = inputs["sigma"]
    z = (inputs["x"] - inputs["mu"]) / s
    g = math.exp(-0.5 * z * z) / (s * math.sqrt(2 * math.pi))
    return {"eps_th": inputs["alpha"] + inputs["gamma"] * (inputs["delta"] - g)}


def symbolic():
    import sympy as sp
    alpha, gamma, delta, sigma, mu, x = sp.symbols("alpha gamma delta sigma mu x", real=True)
    g = sp.exp(-sp.Rational(1, 2) * ((x - mu) / sigma) ** 2) / (sigma * sp.sqrt(2 * sp.pi))
    return {"eps_th": alpha + gamma * (delta - g)}
