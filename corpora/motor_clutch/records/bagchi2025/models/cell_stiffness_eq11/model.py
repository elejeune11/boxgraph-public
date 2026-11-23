import math


def run(inputs, settings):
    s = inputs["sigma"]
    z = (inputs["x"] - inputs["mu"]) / s
    g = math.exp(-0.5 * z * z) / (s * math.sqrt(2 * math.pi))
    return {"kc": inputs["gamma"] * (inputs["omega"] + inputs["delta"] - g)}


def symbolic():
    import sympy as sp
    gamma, omega, delta, sigma, mu, x = sp.symbols("gamma omega delta sigma mu x", real=True)
    g = sp.exp(-sp.Rational(1, 2) * ((x - mu) / sigma) ** 2) / (sigma * sp.sqrt(2 * sp.pi))
    return {"kc": gamma * (omega + delta - g)}
