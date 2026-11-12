# fold MBF = MBF(stimulated) / MBF(baseline). MBF in mL/min/g; output dimensionless.


def run(inputs, settings):
    return {"fold": inputs["MBFx"] / inputs["MBF0"]}


def symbolic():
    import sympy as sp
    MBFx, MBF0 = sp.symbols("MBFx MBF0", positive=True)
    return {"fold": MBFx / MBF0}
