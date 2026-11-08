def run(inputs, settings):
    return {"perfusion": inputs["Q"] / (inputs["V"] * inputs["rho"])}


def symbolic():
    import sympy as sp
    Q, V, rho = sp.symbols("Q V rho", positive=True)
    return {"perfusion": Q / (V * rho)}
