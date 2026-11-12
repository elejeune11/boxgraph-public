# n sections of t um each, in mm (1 mm = 1000 um).


def run(inputs, settings):
    return {"T": inputs["n"] * inputs["t"] / 1000.0}


def symbolic():
    import sympy as sp

    n, t = sp.symbols("n t", positive=True)
    return {"T": n * t / 1000}
