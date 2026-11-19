import math


def run(inputs, settings):
    x = (inputs["t"] - inputs["t0"]) / inputs["T"]
    return {"I_myo": inputs["Ic"] + inputs["I"] * (math.exp(math.exp(x) - 1.0) - 1.0)}


def symbolic():
    import sympy as sp
    Ic, I, t0, T, t = sp.symbols("Ic I t0 T t", real=True)
    return {"I_myo": Ic + I * (sp.exp(sp.exp((t - t0) / T) - 1) - 1)}
