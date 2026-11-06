# E(t) = P(t) / [V(t) - Vd], in mmHg/ml.

def run(inputs, settings):
    return {"E": inputs["P"] / (inputs["V"] - inputs["Vd"])}


def symbolic():
    import sympy as sp
    P, V, Vd = sp.symbols("P V Vd", positive=True)
    return {"E": P / (V - Vd)}
