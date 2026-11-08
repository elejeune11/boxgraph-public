import math

# Q [ml/min] -> m^3/s: 1e-6/60; v [m/s] -> cm/s: 100.
ML_PER_MIN_TO_M3_PER_S = 1e-6 / 60
M_TO_CM = 100.0


def run(inputs, settings):
    a_v = 8 * inputs["a"] * ML_PER_MIN_TO_M3_PER_S * M_TO_CM / math.pi
    return {"a_v": a_v, "b_v": inputs["gamma"] - 2}


def symbolic():
    import sympy as sp
    a, gamma = sp.symbols("a gamma", positive=True)
    return {"a_v": 8 * a * sp.Rational(1, 60) * sp.Rational(1, 10 ** 6) * 100 / sp.pi, "b_v": gamma - 2}
