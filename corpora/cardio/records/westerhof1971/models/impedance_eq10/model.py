import math


def run(inputs, settings):
    q = inputs["Qf"] / inputs["f"]
    dmod = (math.sqrt(1.0 + 1.0 / q**2) - 1.0) * 100.0
    phase = math.degrees(math.atan(1.0 / q))
    return {"Q": q, "dmod": dmod, "phase": phase}


def symbolic():
    import sympy as sp
    Qf, f = sp.symbols("Qf f", positive=True)
    q = Qf / f
    return {"Q": q, "dmod": (sp.sqrt(1 + 1 / q**2) - 1) * 100, "phase": sp.atan(1 / q) * 180 / sp.pi}
