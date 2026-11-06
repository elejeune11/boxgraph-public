"""Residual volume compliance = total compliance minus arterial segment compliances (p. 3)."""


def run(inputs, settings):
    return {"Cres": inputs["Ctot"] - inputs["Csum"]}


def symbolic():
    import sympy as sp

    Ctot, Csum = sp.symbols("Ctot Csum", positive=True)
    return {"Cres": Ctot - Csum}
