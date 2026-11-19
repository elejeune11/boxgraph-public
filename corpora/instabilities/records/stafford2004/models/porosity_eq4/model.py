"""Eq. 4: Ef = E0 (1 - a P)^n. Ef in the unit of E0 (GPa); P, a, n dimensionless."""


def run(inputs, settings):
    return {"Ef": inputs["E0"] * (1 - inputs["a"] * inputs["P"]) ** inputs["n"]}


def symbolic():
    import sympy as sp

    E0, P, a, n = sp.symbols("E0 P a n", positive=True)
    return {"Ef": E0 * (1 - a * P) ** n}
