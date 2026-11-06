def run(inputs, settings):
    return {"tau": inputs["R"] * inputs["Ctot"] / inputs["k"]}


def symbolic():
    import sympy as sp
    R, C, k = sp.symbols("R Ctot k", positive=True)
    return {"tau": R * C / k}
