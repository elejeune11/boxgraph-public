def run(inputs, settings):
    return {"PR": 2 * inputs["gamma"] * 1e4}  # dyne/cm -> dyne*um/cm^2 is 1e4


def symbolic():
    import sympy as sp
    gamma = sp.symbols("gamma", positive=True)
    return {"PR": 2 * gamma * 10**4}
