# |v| = 2 A f with A = eps * D / 2 (the edge of a cell of diameter D, stretched by eps). um, Hz -> um/s.


def run(inputs, settings):
    A = inputs["eps"] * inputs["D"] / 2.0
    return {"v": 2.0 * A * inputs["f"]}


def symbolic():
    import sympy as sp
    eps, D, f = sp.symbols("eps D f", positive=True)
    return {"v": 2 * (eps * D / 2) * f}
