# Eq. 5-12: the prescribed sinusoidal air chamber pressure.
import math


def run(inputs, settings):
    return {"Ps": inputs["Ps0"] + inputs["Psa"] * math.sin(2.0 * math.pi * inputs["t"] / inputs["T"])}


def symbolic():
    import sympy as sp
    Ps0, Psa, T, t = sp.symbols("Ps0 Psa T t", real=True)
    return {"Ps": Ps0 + Psa * sp.sin(2 * sp.pi * t / T)}
