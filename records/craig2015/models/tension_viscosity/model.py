def run(inputs, settings):
    tension = inputs["Tbar"] * inputs["X"]
    return {"tension": tension, "eta": tension / inputs["grad"] / inputs["h"]}


def symbolic():
    import sympy as sp
    Tbar, X, grad, h = sp.symbols("Tbar X grad h", positive=True)
    return {"tension": Tbar * X, "eta": Tbar * X / grad / h}
