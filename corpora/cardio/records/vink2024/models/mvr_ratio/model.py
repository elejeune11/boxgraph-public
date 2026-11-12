# MVR = MBV(stimulated) / MBV(baseline). Both MBV in mL/mL; MVR dimensionless.


def run(inputs, settings):
    return {"MVR": inputs["MBVx"] / inputs["MBV0"]}


def symbolic():
    import sympy as sp
    MBVx, MBV0 = sp.symbols("MBVx MBV0", positive=True)
    return {"MVR": MBVx / MBV0}
