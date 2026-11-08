def run(inputs, settings):
    return {"count": inputs["C"] * inputs["N"]}


def symbolic():
    import sympy as sp
    C, N = sp.symbols("C N", positive=True)
    return {"count": C * N}
