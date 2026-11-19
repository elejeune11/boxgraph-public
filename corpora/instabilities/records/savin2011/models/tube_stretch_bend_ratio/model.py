# SI p. 8: kt ro^2 = 4/(1 + (ri/ro)^2) bt, with x = ri/ro.


def run(inputs, settings):
    return {"ratio": 4.0 / (1.0 + inputs["x"] ** 2)}


def symbolic():
    import sympy as sp
    x = sp.symbols("x", positive=True)
    return {"ratio": 4 / (1 + x**2)}
