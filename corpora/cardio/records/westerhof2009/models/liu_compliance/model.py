import math


def run(inputs, settings):
    b, SV, P = inputs["b"], inputs["SV"], inputs["P"]
    As, Ad, Zc = inputs["As"], inputs["Ad"], inputs["Zc"]
    Ps, Pd = inputs["Ps"], inputs["Pd"]
    den = ((As + Ad) / Ad - Zc * SV / Ad) * (math.exp(b * Ps) - math.exp(b * Pd))
    return {"C": b * SV * math.exp(b * P) / den}


def symbolic():
    import sympy as sp
    b = sp.Symbol("b")
    SV, P, As, Ad, Zc, Ps, Pd = sp.symbols("SV P As Ad Zc Ps Pd", positive=True)
    den = ((As + Ad) / Ad - Zc * SV / Ad) * (sp.exp(b * Ps) - sp.exp(b * Pd))
    return {"C": b * SV * sp.exp(b * P) / den}
