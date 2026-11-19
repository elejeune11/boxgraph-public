import math


def run(inputs, settings):
    return {"lam": 2 * math.pi * inputs["t"] * (inputs["r"] / 3.0) ** (1.0 / 3.0)}
