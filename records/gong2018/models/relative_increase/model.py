# increase = (V2 - V1) / V1, in percent.

def run(inputs, settings):
    return {"increase": 100.0 * (inputs["V2"] - inputs["V1"]) / inputs["V1"]}


def symbolic():
    import sympy as sp
    V1, V2 = sp.symbols("V1 V2", positive=True)
    return {"increase": 100 * (V2 - V1) / V1}
