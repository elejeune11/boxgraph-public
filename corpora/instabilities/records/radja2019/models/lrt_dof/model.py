def run(inputs, settings):
    return {"dof": inputs["n_complex"] - inputs["n_simple"]}


def symbolic():
    import sympy as sp
    a, b = sp.symbols("n_complex n_simple")
    return {"dof": a - b}
