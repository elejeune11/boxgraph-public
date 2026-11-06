def run(inputs, settings):
    return {"At": inputs["Nb"] / inputs["rate"]}


def symbolic():
    import sympy as sp
    Nb, rate = sp.symbols("Nb rate", positive=True)
    return {"At": Nb / rate}
