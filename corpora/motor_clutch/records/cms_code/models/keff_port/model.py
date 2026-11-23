# Port of cms2Dv1_0.m lines 310-315 (our code): Keff = 0 with no engaged clutch, else the series stiffness.


def run(inputs, settings):
    n = inputs["n_eng"]
    if n == 0:
        return {"Keff": 0.0}
    return {"Keff": (1 / inputs["Kcell"] + 1 / (n * inputs["Kc"]) + 1 / inputs["Ksub"]) ** -1}


def symbolic():
    import sympy as sp
    Kcell, n_eng, Kc, Ksub = sp.symbols("Kcell n_eng Kc Ksub", positive=True)
    return {"Keff": 1 / (1 / Kcell + 1 / (n_eng * Kc) + 1 / Ksub)}
