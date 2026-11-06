# Eq. 4, Plv = Plv0 + elv (Vlv - Vlv0), solved for elv; mmHg/ml.
# A helper for the relation to Suga et al.'s instantaneous pressure-volume ratio.

def run(inputs, settings):
    return {"elv": (inputs["Plv"] - inputs["Plv0"]) / (inputs["Vlv"] - inputs["Vlv0"])}


def symbolic():
    import sympy as sp
    Plv, Plv0, Vlv, Vlv0 = sp.symbols("Plv Plv0 Vlv Vlv0", positive=True)
    return {"elv": (Plv - Plv0) / (Vlv - Vlv0)}
