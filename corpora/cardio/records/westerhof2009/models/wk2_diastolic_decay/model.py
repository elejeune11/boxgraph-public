import math


def run(inputs, settings):
    return {"Pdia": inputs["Pes"] * math.exp(-inputs["t"] / (inputs["R"] * inputs["C"]))}


def symbolic():
    import sympy as sp
    Pes, R, C, t = sp.symbols("Pes R C t", positive=True)
    return {"Pdia": Pes * sp.exp(-t / (R * C))}
