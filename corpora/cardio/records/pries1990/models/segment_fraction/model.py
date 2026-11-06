# Percentage of a network's segments: 100 * NINV / Nseg.


def run(inputs, settings):
    return {"fraction": 100.0 * inputs["NINV"] / inputs["Nseg"]}


def symbolic():
    import sympy as sp
    NINV, Nseg = sp.symbols("NINV Nseg", positive=True)
    return {"fraction": 100 * NINV / Nseg}
