# Eq. 2-4, Plv = Plv0 + elv (Vlv - Vlv0), solved for elv. Port units: mmHg, ml, mmHg/ml. No I/O.


def run(inputs, settings):
    return {"elv": (inputs["Plv"] - inputs["Plv0"]) / (inputs["Vlv"] - inputs["Vlv0"])}


def symbolic():
    import sympy as sp
    Plv, Vlv, Plv0, Vlv0 = sp.symbols("Plv Vlv Plv0 Vlv0", positive=True)
    return {"elv": (Plv - Plv0) / (Vlv - Vlv0)}
