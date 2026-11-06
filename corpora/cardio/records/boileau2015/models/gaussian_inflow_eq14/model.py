# Eq. 14 (p. 15): Qin(t) = amp exp(-k (t - t0)^2), with amp = 10^-6 m^3/s, k = 10000 s^-2, t0 = 0.05 s.
import math


def run(inputs, settings):
    return {"Q": inputs["amp"] * math.exp(-inputs["k"] * (inputs["t"] - inputs["t0"]) ** 2)}


def symbolic():
    import sympy as sp
    amp, k, t0, t = sp.symbols("amp k t0 t", positive=True)
    return {"Q": amp * sp.exp(-k * (t - t0) ** 2)}
